import sys
import os

# Ensure current directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("Starting application...")

# -----------------------------
# Import Database and Supply Manager
# -----------------------------
from database.Db_manager import DatabaseManager
from modules.supply_manager import SupplyManager

# Import PyQt6 and UI
from PyQt6.QtWidgets import QApplication

# ---------- DATABASE CONFIG ----------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "supply_db"
}

try:
    # Initialize DatabaseManager
    print("Initializing DatabaseManager...")
    db_manager = DatabaseManager(db_config)
    if not db_manager.connected:
        print("[ERROR] Database connection failed. Check MySQL service.")
        sys.exit(1)
    print("[OK] Database connected successfully.")

    # Create tables if not existing
    db_manager.create_tables()

    # Ensure default admin exists
    existing_admin = db_manager.fetch_one(
        "SELECT * FROM users WHERE username=%s",
        ("admin",)
    )

    if not existing_admin:
        print("Creating default admin account...")
        db_manager.add_user("admin", "admin123", "Admin")
        print(" Default admin created.")

    # Initialize QApplication
    print("Creating QApplication...")
    app = QApplication(sys.argv)

    # Initialize SupplyManager
    print("Initializing SupplyManager...")
    supply_manager = SupplyManager(db_manager)

    # -----------------------------
    # OPEN LOGIN PAGE FIRST
    # -----------------------------
    print("Opening Login Page...")

    from ui.login_page import LoginPage

    login_page = LoginPage(supply_manager, db_manager)
    login_page.show()

    print("Starting app event loop...")
    sys.exit(app.exec())

except Exception as e:
    print(f"❌ Error starting application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
