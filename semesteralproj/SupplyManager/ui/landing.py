import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel,
    QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect
from PyQt6.QtGui import QCursor, QScreen

# Existing pages
from .dashboard import Dashboard
from .inventory_page import InventoryPage
from .monthly_report_page import MonthlySalesReportPage   # ✅ NEW IMPORT
from .stock_request_page import StockRequestPage
from .reconciliation_page import ReconciliationPage  # ✅ NEW IMPORT


class LandingPage(QWidget):
    def __init__(self, supply_manager, user_role="Admin", user_id=None):
        super().__init__()
        self.supply_manager = supply_manager
        self.user_role = user_role
        self.user_id = user_id

        self.setWindowTitle("Inventory System")
        self.setStyleSheet("background-color: #F0F2F5;")
        
        # Set window to 90% of available screen size
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        width = int(screen_geometry.width() * 0.9)
        height = int(screen_geometry.height() * 0.9)
        self.resize(width, height)

        self.initUI()

    # =====================================================
    # UI Initialization
    # =====================================================
    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # Main stacked layout (welcome + app)
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # =============================
        # WELCOME PAGE
        # =============================
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_label = QLabel(f"👋 Welcome, {self.user_role}!")
        welcome_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: #34495E;
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_label)

        continue_btn = QPushButton("Continue")
        continue_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        continue_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 12px;
                padding: 12px 32px;
                font-weight: bold;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        continue_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.main_page))
        welcome_layout.addWidget(continue_btn)

        self.stack.addWidget(self.welcome_page)

        # =============================
        # MAIN PAGE
        # =============================
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # -------- Top Bar --------
        top_bar = QHBoxLayout()
        title = QLabel("🗄 Inventory System")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #34495E;")
        top_bar.addWidget(title)
        top_bar.addStretch()

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_with_animation)
        top_bar.addWidget(self.refresh_btn)

        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(logout_btn)

        main_layout.addLayout(top_bar)

        # =============================
        # SIDEBAR MENU
        # =============================
        menu_layout = QHBoxLayout()

        self.dashboard_btn = QPushButton("Dashboard")
        self.requests_btn = QPushButton("Stock Requests")

        # Role-aware menu: students only see requests; staff see dashboard+inventory+requests; admin sees all
        if self.user_role and self.user_role.lower() == 'student':
            # Student: only requests (still include dashboard button but not shown)
            for btn in (self.dashboard_btn, self.requests_btn):
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.setStyleSheet(self.button_style())

            menu_layout.addWidget(self.requests_btn)
            menu_layout.addStretch()

            main_layout.addLayout(menu_layout)

            # Pages: only dashboard (hidden) and requests
            self.pages = QStackedWidget()
            self.dashboard_page = Dashboard(self.supply_manager)
            self.requests_page = StockRequestPage(self.supply_manager, user_id=self.user_id, user_role=self.user_role)
            self.pages.addWidget(self.dashboard_page)
            self.pages.addWidget(self.requests_page)
            main_layout.addWidget(self.pages)

            # Connections
            self.dashboard_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.dashboard_page))
            self.requests_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.requests_page))

            # Default to requests for students
            self.pages.setCurrentWidget(self.requests_page)
        else:
            # Admin and staff
            self.inventory_btn = QPushButton("Inventory")
            self.monthly_btn = QPushButton("Monthly Report")   # ✅ NEW BUTTON
            self.reconciliation_btn = QPushButton("📊 Reconciliation")  # ✅ NEW BUTTON

            for btn in (self.dashboard_btn, self.inventory_btn, self.monthly_btn, self.reconciliation_btn, self.requests_btn):
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.setStyleSheet(self.button_style())

            menu_layout.addWidget(self.dashboard_btn)
            menu_layout.addWidget(self.inventory_btn)
            # Only admin sees monthly report and reconciliation buttons
            if self.user_role and self.user_role.lower() == 'admin':
                menu_layout.addWidget(self.monthly_btn)
                menu_layout.addWidget(self.reconciliation_btn)
            menu_layout.addWidget(self.requests_btn)
            menu_layout.addStretch()

            main_layout.addLayout(menu_layout)

            # Instantiate pages
            self.pages = QStackedWidget()
            self.dashboard_page = Dashboard(self.supply_manager)
            self.inventory_page = InventoryPage(self.supply_manager)
            self.pages.addWidget(self.dashboard_page)
            self.pages.addWidget(self.inventory_page)

            if self.user_role and self.user_role.lower() == 'admin':
                self.monthly_page = MonthlySalesReportPage(self.supply_manager)
                self.pages.addWidget(self.monthly_page)
                self.reconciliation_page = ReconciliationPage(self.supply_manager)
                self.pages.addWidget(self.reconciliation_page)

            self.requests_page = StockRequestPage(self.supply_manager, user_id=self.user_id, user_role=self.user_role)
            self.pages.addWidget(self.requests_page)

            main_layout.addWidget(self.pages)

            # Button connections
            self.dashboard_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.dashboard_page))
            self.inventory_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.inventory_page))
            if hasattr(self, 'monthly_btn'):
                self.monthly_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.monthly_page))
            if hasattr(self, 'reconciliation_btn'):
                self.reconciliation_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.reconciliation_page))
            self.requests_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.requests_page))

            # Default page
            self.pages.setCurrentWidget(self.dashboard_page)

        self.stack.addWidget(self.main_page)

    # =====================================================
    # Button Style
    # =====================================================
    def button_style(self):
        return """
        QPushButton {
            background-color: #3498DB;
            color: white;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980B9;
        }
        """

    # =====================================================
    # Refresh Button Animation
    # =====================================================
    def refresh_with_animation(self):
        anim = QPropertyAnimation(self.refresh_btn, b"geometry")
        rect = self.refresh_btn.geometry()
        anim.setDuration(250)
        anim.setStartValue(rect)
        anim.setKeyValueAt(0.5, rect.adjusted(-5, -5, 5, 5))
        anim.setEndValue(rect)
        anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        anim.start()
        self._anim = anim

        self.refresh_pages()

    def refresh_pages(self):
        # Safely call refresh methods only if the page attributes exist
        if hasattr(self, 'dashboard_page') and hasattr(self.dashboard_page, 'refresh_dashboard'):
            self.dashboard_page.refresh_dashboard()

        if hasattr(self, 'inventory_page') and hasattr(self.inventory_page, 'refresh_inventory'):
            self.inventory_page.refresh_inventory()

    # =====================================================
    # Logout + Splash Screen
    # =====================================================
    def logout(self):
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from .login_page import LoginPage

            # Close this window
            self.close()

            # Open login page
            self.login_window = LoginPage(
                supply_manager=self.supply_manager,
                db_manager=self.supply_manager.db
            )
            self.login_window.show()

    def show_login_page(self):
        """Display login page after logout."""
        from .login_page import LoginPage

        self.login_window = LoginPage(
            supply_manager=self.supply_manager,
            db_manager=self.supply_manager.db
        )
        self.login_window.show()
