class LoginManager:
    def __init__(self, db_manager):
        self.db = db_manager   # ✅ stores db_manager in self.db

    def check_login(self, username, password):
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        result = self.db.fetch_all(query, (username, password))
        return True if result else False
