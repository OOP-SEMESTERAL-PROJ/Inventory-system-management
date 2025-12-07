from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

class LogoutSplashScreen(QSplashScreen):
    def __init__(self):
        pixmap = QPixmap(420, 220)
        pixmap.fill(Qt.GlobalColor.white)

        super().__init__(pixmap)
        self.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))

        self.showMessage(
            "Logging out...",
            Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.black
        )
