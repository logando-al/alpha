import pytest
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLineEdit, QComboBox, QCheckBox, QLabel
from PyQt6.QtCore import Qt, QThread

# We are importing modules that DO NOT EXIST yet
def test_mainwindow_initialization(qtbot):
    """Test that the MainWindow initializes with correct title and widgets."""
    from alpha.gui import AlphaInitializerWindow
    
    window = AlphaInitializerWindow()
    qtbot.addWidget(window)
    
    # Assert Title
    assert "ALPHA Initializer" in window.windowTitle()
    
    # Assert Widgets Existence
    assert window.findChild(QLineEdit, "input_project_name")
    assert window.findChild(QLineEdit, "input_target_dir")
    assert window.findChild(QComboBox, "combo_stack")
    assert window.findChild(QCheckBox, "check_docker")
    assert window.findChild(QPushButton, "btn_initialize")
    
    # Assert Default State
    stack_combo = window.findChild(QComboBox, "combo_stack")
    assert stack_combo.count() > 0 # Should have items populated

def test_ui_framework_visibility(qtbot):
    """Test that UI Framework dropdown appears only for JS stacks."""
    from alpha.gui import AlphaInitializerWindow
    
    window = AlphaInitializerWindow()
    qtbot.addWidget(window)
    
    stack_combo = window.findChild(QComboBox, "combo_stack")
    ui_combo = window.findChild(QComboBox, "combo_ui_framework")
    
    # Select Django (Should hide/disable UI Framework)
    # Note: We need to know the index or text. Assuming "Django" is in the list.
    # For TDD we just assert the logic *if* we could select it.
    
    # Implementation detail: Use qtbot to simulate interaction if possible
    # or direct calls.
    
    # Let's say index 0 is Django (Python)
    stack_combo.setCurrentIndex(0) 
    # Verify ui_combo is disabled or hidden
    assert not ui_combo.isEnabled() or not ui_combo.isVisible()

def test_worker_thread_logic(qtbot):
    """Test the worker thread signal emission."""
    from alpha.gui import ProjectGeneratorWorker
    
    # Mock config
    config = {"project_name": "Test", "stack": "django"}
    
    worker = ProjectGeneratorWorker(config)
    
    # Mock the finished signal
    with qtbot.waitSignal(worker.finished, timeout=1000) as blocker:
        worker.start()
    
    # Success
    assert blocker.signal_triggered
