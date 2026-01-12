from PyQt6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen

class AlphaSplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # We will draw everything manually on the splash
        # or we can add widgets if we really want, but QSplashScreen is a widget.
        
        # Let's just store data to draw
        self.progress = 0
        from alpha.version import __version__
        self.version = f"v{__version__}"
        self.credits = "Developed by logando-al"
        self.license = "Open Source"
        
        # Font Setup
        self.font_main = QFont("Arial", 10)
        self.font_bold = QFont("Arial", 10, QFont.Weight.Bold)
        self.font_small = QFont("Arial", 8)

    def set_progress(self, value):
        self.progress = value
        self.repaint()

    def drawContents(self, painter):
        # Draw the pixmap (icon) effectively handled by super if we don't override paintEvent
        # But drawContents is called by paintEvent over the pixmap.
        
        # Let's draw the overlay info
        r = self.rect()
        w = r.width()
        h = r.height()
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Text Color (White/Purple)
        painter.setPen(QColor("white"))
        
        # Version (Top Right)
        painter.setFont(self.font_bold)
        painter.drawText(r.adjusted(0, 10, -10, 0), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, self.version)
        
        # Credits (Bottom Center - above progress)
        painter.setFont(self.font_main)
        # Position: near bottom
        text_rect = r.adjusted(0, 0, 0, -40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, f"{self.credits} | {self.license}")

        # Progress Bar Logic
        # Draw a sleek line at the very bottom
        bar_h = 4
        bar_y = h - bar_h
        
        # Background of bar
        painter.fillRect(0, bar_y, w, bar_h, QColor("#333333"))
        
        # Fill
        fill_w = int(w * (self.progress / 100.0))
        painter.fillRect(0, bar_y, fill_w, bar_h, QColor("#A020F0")) # Neon Purple
