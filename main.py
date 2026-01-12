import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from alpha.gui import AlphaInitializerWindow
from alpha.splash import AlphaSplashScreen
from alpha.utils import get_resource_path

def main():
    app = QApplication(sys.argv)
    
    # Splash Screen - Use cross-platform resource path
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
                 time.sleep(0.3) # Fake delay

    window = AlphaInitializerWindow()
    window.show()
    
    if splash:
        splash.finish(window)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
