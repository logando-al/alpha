import sys
import time
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from alpha.gui import AlphaInitializerWindow
from alpha.splash import AlphaSplashScreen
from alpha.utils import get_resource_path
from alpha.update import check_for_updates_blocking, show_forced_update_dialog


class UpdateCheckDialog(QDialog):
    """Loading dialog shown while checking for updates."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ALPHA Init")
        self.setFixedSize(300, 100)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                border: 2px solid #A020F0;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QProgressBar {
                background-color: #2D2D2D;
                border: none;
                border-radius: 3px;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #A020F0;
                border-radius: 3px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.label = QLabel("Checking for updates...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress)


def main():
    app = QApplication(sys.argv)
    
    # ===== SHOW UPDATE CHECK DIALOG =====
    update_dialog = UpdateCheckDialog()
    update_dialog.show()
    app.processEvents()  # Ensure dialog is displayed
    
    # Perform update check (blocking, but dialog is visible)
    is_update, new_version, release_url = check_for_updates_blocking()
    
    # Close the update dialog
    update_dialog.close()
    
    if is_update:
        # Force update - show dialog, open browser, exit
        show_forced_update_dialog(new_version, release_url)
        return  # Won't reach here, sys.exit called in dialog
    
    # ===== SPLASH SCREEN =====
    icon_path = get_resource_path("alpha/resources/icon.png")
    splash = None
    
    if icon_path.exists():
        pixmap = QPixmap(str(icon_path))
        if not pixmap.isNull():
             # Basic Scaling
             if pixmap.width() > 500:
                 pixmap = pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
             # Create Custom Splash
             splash = AlphaSplashScreen(pixmap)
             splash.show()
             
             # Simulate Loading Steps
             steps = [
                 (10, "Loading configuration..."),
                 (30, "Checking dependencies..."),
                 (60, "Initializing UI components..."),
                 (90, "Preparing workspace..."),
                 (100, "Ready!")
             ]
             
             for progress, msg in steps:
                 splash.set_progress(progress)
                 splash.showMessage(msg, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft, Qt.GlobalColor.white)
                 app.processEvents()
                 time.sleep(0.3)  # Fake delay

    # ===== MAIN WINDOW =====
    window = AlphaInitializerWindow()
    window.show()
    
    if splash:
        splash.finish(window)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
