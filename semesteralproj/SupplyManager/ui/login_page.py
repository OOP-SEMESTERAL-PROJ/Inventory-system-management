from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit,
    QFrame, QMessageBox, QDialog, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class LoginPage(QWidget):
    def __init__(self, supply_manager=None, db_manager=None):
        super().__init__()
        self.supply_manager = supply_manager
        self.db = db_manager

        self.setWindowTitle("School Supplies Inventory - Login")
        self.resize(900, 650)

        self.build_ui()
        self.apply_style()

    # ----------------------------------------------------
    # UI SETUP
    # ----------------------------------------------------
    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title Icon
        title_label = QLabel("📘")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 60))

        name_label = QLabel("School Supplies Inventory System")
        name_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle
        subtitle = QLabel("Login to your account")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(title_label)
        main_layout.addWidget(name_label)
        main_layout.addWidget(subtitle)

        # Card
        self.card = QFrame()
        self.card.setFixedSize(450, 400)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        # Username
        user_label = QLabel("Username")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        self.username.setcolor = "black"

        # Password
        pass_label = QLabel("Password")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)

        # Note: role will be detected automatically from the users table after authentication

        # Login Button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.clicked.connect(self.login_clicked)

        # Forgot Password Link
        self.forgot_btn = QPushButton("Forgot Password?")
        self.forgot_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #A66BFF;
                border: none;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton:hover {
                color: #8F54E8;
                text-decoration: underline;
            }
        """)
        self.forgot_btn.clicked.connect(self.open_forgot_password)

        # Add widgets
        card_layout.addWidget(user_label)
        card_layout.addWidget(self.username)
        card_layout.addWidget(pass_label)
        card_layout.addWidget(self.password)
        # (No role selector; role is auto-detected)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(self.forgot_btn)

        main_layout.addWidget(self.card)

    # ----------------------------------------------------
    # CSS STYLE
    # ----------------------------------------------------
    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F9F3FD;
                font-family: 'Segoe UI';
            }

            QFrame#card {
                background-color: white;
                border-radius: 20px;
                border: 2px solid #E6DFFF;
            }

            QLabel {
                color: #000000; /* make label text black */
            }

            QLineEdit {
                padding: 12px;
                font-size: 15px;
                border: 2px solid #D8CCFF;
                border-radius: 10px;
                background-color: #FBF9FF;
                color: #000000; /* make input text black */
                min-height: 30px;
            }

            QLineEdit:focus {
                border: 2px solid #9B51E0;
                background-color: white;
            }

            /* Role dropdown styling */
            QComboBox {
                padding: 10px;
                font-size: 15px;
                border: 2px solid #D8CCFF;
                border-radius: 10px;
                background-color: #FBF9FF;
                color: #000000; /* ensure text is black */
                min-height: 30px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: none;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #E6DFFF;
            }

            QPushButton {
                padding: 12px;
                font-size: 17px;
                font-weight: bold;
                color: white;
                border-radius: 12px;
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #A66BFF, stop:1 #FF6A3D
                );
            }

            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8F54E8, stop:1 #E2582D
                );
            }
        """)
        self.card.setObjectName("card")

    # ----------------------------------------------------
    # BUTTON ACTIONS
    # ----------------------------------------------------
    def login_admin(self):
        self.authenticate()

    def login_clicked(self):
        # Use selected role when authenticating
        self.authenticate()

    # ----------------------------------------------------
    # AUTHENTICATION (Admin-only)
    # ----------------------------------------------------
    def authenticate(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Input", "Please enter username and password.")
            return

        # Find user by username/password and use stored role
        query = """
            SELECT * FROM users 
            WHERE username=%s AND password=%s
        """

        user = self.db.fetch_one(query, (username, password))
        print("USER FOUND:", user)

        if not user:
            QMessageBox.critical(
                self,
                "Login Failed",
                "Incorrect username or password."
            )
            return

        # OPEN LANDING PAGE with correct role and user id
        from .landing import LandingPage
        user_role = user.get('role') if isinstance(user, dict) else None
        user_id = user.get('id') if isinstance(user, dict) else None

        self.main_window = LandingPage(self.supply_manager, user_role=user_role, user_id=user_id)
        self.main_window.show()
        self.close()

    # ====================================================
    # FORGOT PASSWORD
    # ====================================================
    def open_forgot_password(self):
        """Open the forgot password dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Forgot Password")
        dialog.setFixedSize(400, 250)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #F9F3FD;
            }
            QLabel {
                color: #000000;
            }
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #D8CCFF;
                border-radius: 8px;
                background-color: #FBF9FF;
                color: #000000;
            }
            QLineEdit:focus {
                border: 2px solid #9B51E0;
                background-color: white;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                color: white;
                border-radius: 8px;
                background-color: #A66BFF;
                border: none;
            }
            QPushButton:hover {
                background-color: #8F54E8;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Reset Your Password")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Info
        info = QLabel("Enter your username to reset your password.")
        info.setFont(QFont("Segoe UI", 11))
        layout.addWidget(info)

        # Username input
        user_label = QLabel("Username")
        user_input = QLineEdit()
        user_input.setPlaceholderText("Enter your username")
        layout.addWidget(user_label)
        layout.addWidget(user_input)

        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #999999;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)

        reset_btn = QPushButton("Send Reset Link")
        reset_btn.clicked.connect(lambda: self.handle_password_reset(user_input.text().strip(), dialog))

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def handle_password_reset(self, username: str, dialog: QDialog):
        """Handle password reset by username"""
        if not username:
            QMessageBox.warning(dialog, "Missing Input", "Please enter your username.")
            return

        try:
            # Check if user exists
            user = self.db.fetch_one("SELECT id, password FROM users WHERE username=%s", (username,))

            if not user:
                QMessageBox.information(
                    dialog,
                    "Account Not Found",
                    f"No account found with username '{username}'.\n\nPlease check and try again."
                )
                return

            # For demo purposes, show the current password (in production, send email with reset link)
            current_password = user.get('password', 'N/A')
            
            QMessageBox.information(
                dialog,
                "Password Reset",
                f"✓ Password reset successful!\n\n"
                f"Your password is: {current_password}\n\n"
                f"Please use this to login and then change it in settings."
            )
            dialog.close()

        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"An error occurred: {str(e)}")
            print(f"[ERROR] Password reset failed: {e}")
