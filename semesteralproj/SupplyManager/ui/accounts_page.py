from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QHBoxLayout, QMessageBox

class AccountsPage(QWidget):
    def __init__(self, supply_manager):
        super().__init__()
        self.manager = supply_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role"])
        layout.addWidget(self.table)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter password")

        self.add_btn = QPushButton("Add Staff")
        self.add_btn.clicked.connect(self.add_user)

        row = QHBoxLayout()
        row.addWidget(self.username)
        row.addWidget(self.password)
        row.addWidget(self.add_btn)

        layout.addLayout(row)

        self.load_users()

    def load_users(self):
        users = self.manager.get_users()
        self.table.setRowCount(len(users))
        for i, u in enumerate(users):
            self.table.setItem(i, 0, QTableWidgetItem(str(u["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(u["username"]))
            self.table.setItem(i, 2, QTableWidgetItem(u["role"]))

    def add_user(self):
        self.manager.create_user(
            self.username.text(),
            self.password.text(),
            role="Staff"
        )
        QMessageBox.information(self, "Success", "Staff added!")
        self.load_users()
