import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, 
    QCheckBox, QFileDialog, QMessageBox, QProgressBar,
    QFrame, QDialog, QListWidget, QFormLayout, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from alpha.initializer import ProjectInitializer

class ProjectGeneratorWorker(QThread):
    finished = pyqtSignal(bool, str) # Success, Message

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initializer = ProjectInitializer()

    def run(self):
        try:
            self.initializer.generate_project(self.config)
            self.finished.emit(True, f"Project '{self.config['project_name']}' created successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))

class StackEditorDialog(QDialog):
    def __init__(self, parent=None, initializer=None):
        super().__init__(parent)
        self.setWindowTitle("Stack Manager")
        self.setGeometry(150, 150, 700, 500)
        self.initializer = initializer
        self._setup_ui()
        self._populate_list()
        self._apply_styles()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        # Left: List
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Available Stacks"))
        self.list_stacks = QListWidget()
        self.list_stacks.currentItemChanged.connect(self._on_stack_selected)
        left_layout.addWidget(self.list_stacks)
        
        btn_add = QPushButton("Add New Stack")
        btn_add.clicked.connect(self._on_add_new)
        left_layout.addWidget(btn_add)
        
        layout.addLayout(left_layout, 1)

        # Right: Details
        self.group_details = QGroupBox("Stack Configuration")
        form_layout = QFormLayout(self.group_details)
        
        self.input_name = QLineEdit()
        self.input_cmd = QLineEdit()
        self.input_docker_base = QLineEdit()
        self.input_docker_port = QLineEdit()
        self.input_docker_cmd = QLineEdit()
        
        form_layout.addRow("Stack Name:", self.input_name)
        form_layout.addRow("Init Command:", self.input_cmd)
        form_layout.addRow("Docker Base (Opt):", self.input_docker_base)
        form_layout.addRow("Docker Port (Opt):", self.input_docker_port)
        form_layout.addRow("Docker Cmd (Opt):", self.input_docker_cmd)
        
        btn_save = QPushButton("Save Stack")
        btn_save.clicked.connect(self._save_stack)
        form_layout.addRow(btn_save)
        
        btn_delete = QPushButton("Delete Stack")
        btn_delete.clicked.connect(self._delete_stack)
        # Style delete button red later
        form_layout.addRow(btn_delete)

        layout.addWidget(self.group_details, 2)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; color: white; }
            QLabel { color: white; }
            QGroupBox { color: #A020F0; font-weight: bold; border: 1px solid #3E3E3E; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
            QLineEdit { background-color: #2D2D2D; color: white; padding: 5px; border: 1px solid #3E3E3E; }
            QListWidget { background-color: #2D2D2D; color: white; border: 1px solid #3E3E3E; }
            QPushButton { background-color: #3E3E3E; color: white; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #4E4E4E; }
        """)

    def _populate_list(self):
        self.list_stacks.clear()
        stacks = self.initializer.get_available_stacks()
        self.list_stacks.addItems(stacks)

    def _on_stack_selected(self, current, previous):
        if not current:
            return
            
        stack_name = current.text()
        self.input_name.setText(stack_name)
        
        # Load config from commands.json if available
        config = self.initializer.commands_config.get("stacks", {}).get(stack_name, {})
        
        self.input_cmd.setText(config.get("init_command", ""))
        self.input_docker_base.setText(config.get("docker_base", ""))
        self.input_docker_port.setText(config.get("docker_port", ""))
        self.input_docker_cmd.setText(config.get("docker_cmd", ""))
        
        # Disable name editing for existing? Maybe allow copy?
        # For simplicity, if it's a default stack not in JSON, these will be empty/readonly logic needed?
        # We'll allow editing, which essentially overrides defaults if we save.

    def _on_add_new(self):
        self.list_stacks.clearSelection()
        self.input_name.clear()
        self.input_name.setFocus()
        self.input_cmd.clear()
        self.input_docker_base.clear()
        self.input_docker_port.clear()
        self.input_docker_cmd.clear()

    def _save_stack(self):
        name = self.input_name.text().strip()
        cmd = self.input_cmd.text().strip()
        
        if not name or not cmd:
            QMessageBox.warning(self, "Invalid", "Name and Init Command are required.")
            return
            
        config = {
            "init_command": cmd,
            "docker_base": self.input_docker_base.text().strip(),
            "docker_port": self.input_docker_port.text().strip(),
            "docker_cmd": self.input_docker_cmd.text().strip()
        }
        
        self.initializer.save_stack_config(name, config)
        QMessageBox.information(self, "Saved", f"Stack '{name}' saved successfully.")
        self._populate_list()

    def _delete_stack(self):
        name = self.input_name.text().strip()
        if not name: return
        
        if name not in self.initializer.commands_config.get("stacks", {}):
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete default/internal stacks, only custom configurations.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", f"Delete config for '{name}'?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.initializer.delete_stack_config(name)
            self._populate_list()
            self._on_add_new()

class AlphaInitializerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ALPHA Initializer")
        self.setGeometry(100, 100, 600, 450)
        
        # Initialize Backend
        self.initializer = ProjectInitializer()
        self.worker = None

        # Setup UI
        self._setup_ui()
        self._apply_styles()
        self._populate_stacks()

    def _setup_ui(self):
        # Icon
        from PyQt6.QtGui import QIcon
        icon_path = Path(__file__).parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel("Start New Project")
        header.setObjectName("header")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        # Project Name
        layout.addWidget(QLabel("Project Name:"))
        self.input_name = QLineEdit()
        self.input_name.setObjectName("input_project_name")
        self.input_name.setPlaceholderText("e.g., MyAwesomeApp")
        layout.addWidget(self.input_name)

        # Target Directory
        layout.addWidget(QLabel("Target Directory:"))
        dir_layout = QHBoxLayout()
        self.input_dir = QLineEdit()
        self.input_dir.setObjectName("input_target_dir")
        btn_browse = QPushButton("Browse")
        btn_browse.clicked.connect(self._browse_dir)
        dir_layout.addWidget(self.input_dir)
        dir_layout.addWidget(btn_browse)
        layout.addLayout(dir_layout)

        # Tech Stack
        layout.addWidget(QLabel("Tech Stack:"))
        stack_layout = QHBoxLayout()
        self.combo_stack = QComboBox()
        self.combo_stack.setObjectName("combo_stack")
        self.combo_stack.currentTextChanged.connect(self._on_stack_changed)
        
        btn_manage = QPushButton("Manage")
        btn_manage.setToolTip("Add/Edit Custom Stacks")
        btn_manage.clicked.connect(self._open_stack_manager)
        btn_manage.setFixedWidth(80) # Small button
        
        stack_layout.addWidget(self.combo_stack)
        stack_layout.addWidget(btn_manage)
        layout.addLayout(stack_layout)

        # UI Framework (Hidden by default)
        self.lbl_ui = QLabel("UI Framework:")
        self.combo_ui = QComboBox()
        self.combo_ui.setObjectName("combo_ui_framework")
        self.combo_ui.addItems(["None", "Tailwind CSS", "Bootstrap", "DaisyUI", "Shadcn"])
        layout.addWidget(self.lbl_ui)
        layout.addWidget(self.combo_ui)
        
        # Initial Visibility
        self.lbl_ui.hide()
        self.combo_ui.hide()

        # Docker
        self.check_docker = QCheckBox("Containerize with Docker")
        self.check_docker.setObjectName("check_docker")
        layout.addWidget(self.check_docker)

        # Spacer
        layout.addStretch()

        # Action Button
        self.btn_init = QPushButton("Initialize Project")
        self.btn_init.setObjectName("btn_initialize")
        self.btn_init.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_init.clicked.connect(self._start_generation)
        layout.addWidget(self.btn_init)
        
        # Progress Bar (Hidden initially)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        self.progress.hide()
        layout.addWidget(self.progress)

    def _apply_styles(self):
        # Dark Mode + Purple Accent
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            #header {
                font-size: 24px;
                font-weight: bold;
                color: #A020F0;
                margin-bottom: 10px;
            }
            QLineEdit, QComboBox {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #3E3E3E;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3E3E3E;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #4E4E4E;
            }
            #btn_initialize {
                background-color: #A020F0;
                color: white;
                font-weight: bold;
                padding: 12px;
                font-size: 15px;
            }
            #btn_initialize:hover {
                background-color: #B030FF;
            }
            #btn_initialize:disabled {
                background-color: #555555;
            }
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)

    def _populate_stacks(self):
        self.combo_stack.clear()
        stacks = self.initializer.get_available_stacks()
        if not stacks:
            stacks = ["django", "fastapi", "react", "vue", "node", "nextjs"]
        self.combo_stack.addItems(stacks)

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        if d:
            self.input_dir.setText(d)
    
    def _open_stack_manager(self):
        dialog = StackEditorDialog(self, self.initializer)
        dialog.exec()
        # Refresh stacks on close in case changes happened
        self._populate_stacks()

    def _on_stack_changed(self, text):
        is_js = text.lower() in ["react", "vue", "nextjs", "node"]
        if is_js:
            self.lbl_ui.show()
            self.combo_ui.show()
            self.combo_ui.setEnabled(True)
        else:
            self.lbl_ui.hide()
            self.combo_ui.hide()
            self.combo_ui.setEnabled(False)

    def _start_generation(self):
        name = self.input_name.text().strip()
        target = self.input_dir.text().strip()
        
        if not name or not target:
            QMessageBox.warning(self, "Missing Info", "Please enter a project name and target directory.")
            return

        stack = self.combo_stack.currentText()
        use_docker = self.check_docker.isChecked()
        ui_fw = self.combo_ui.currentText() if self.combo_ui.isEnabled() else None
        
        config = {
            "project_name": name,
            "target_dir": target,
            "stack": stack,
            "use_docker": use_docker,
            "ui_framework": ui_fw
        }

        # UI State: Busy
        self.btn_init.setEnabled(False)
        self.progress.show()
        
        # Threading
        self.worker = ProjectGeneratorWorker(config)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, success, message):
        self.btn_init.setEnabled(True)
        self.progress.hide()
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", f"Generation Failed:\n{message}")
