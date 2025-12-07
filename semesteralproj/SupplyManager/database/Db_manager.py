import mysql.connector
import sys
import time
import hashlib


class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None
        self.connected = False
        self.connect()

    # -----------------------------------------------------
    # CONNECT TO MYSQL
    # -----------------------------------------------------
    def connect(self):
        try:
            print("Trying to connect to MySQL...")
            self.conn = mysql.connector.connect(
                host=self.config.get("host", "localhost"),
                user=self.config.get("user", "root"),
                password=self.config.get("password", ""),
                database=self.config.get("database"),
                autocommit=True,
                connection_timeout=5
            )
            self.cursor = self.conn.cursor(dictionary=True)
            self.connected = True
            print("[OK] Database connected successfully.")
        except mysql.connector.Error as err:
            self.conn = None
            self.cursor = None
            self.connected = False
            print(f"[ERROR] MySQL connection error: {err}")
        except Exception as e:
            self.conn = None
            self.cursor = None
            self.connected = False
            print(f"[ERROR] Unexpected database error: {e}")

    def ensure_connection(self):
        """Reconnect if connection is lost."""
        if self.conn is None or not self.connected:
            print("[WARNING] Lost database connection. Reconnecting...")
            self.connect()

    # -----------------------------------------------------
    # CREATE TABLES
    # -----------------------------------------------------
    def create_tables(self):
        self.ensure_connection()
        if not self.connected:
            print("[WARNING] Cannot create tables — not connected.")
            return False

        try:
            # SUPPLIES TABLE
            create_supplies_table = """
            CREATE TABLE IF NOT EXISTS supplies (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sku VARCHAR(20),
                name VARCHAR(255) NOT NULL,
                category VARCHAR(255),
                supplier VARCHAR(255),
                quantity INT DEFAULT 0,
                min_quantity INT DEFAULT 5,
                threshold INT DEFAULT 10,
                price DECIMAL(10,2) DEFAULT 0.00,
                last_updated DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_supplies_table)

            # TRANSACTIONS TABLE
            create_transactions_table = """
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_id INT,
                type ENUM('IN','OUT'),
                qty INT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_transactions_table)

            # MONTHLY REPORT TABLE
            create_monthly_report = """
            CREATE TABLE IF NOT EXISTS monthly_reports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                month_year VARCHAR(7),   -- format 2025-01
                item_id INT,
                total_in INT DEFAULT 0,
                total_out INT DEFAULT 0,
                current_stock INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_monthly_report)

            # STOCK RECONCILIATION TABLE
            create_reconciliation_table = """
            CREATE TABLE IF NOT EXISTS stock_reconciliation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                month_year VARCHAR(7),
                item_id INT,
                recorded_qty INT DEFAULT 0,
                actual_qty INT DEFAULT 0,
                variance INT DEFAULT 0,
                reconciled_by VARCHAR(255),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_reconciliation_table)

            # STOCK REQUESTS TABLE (if not exists)
            create_stock_requests_table = """
            CREATE TABLE IF NOT EXISTS stock_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_id INT,
                quantity INT,
                requested_by INT,
                status VARCHAR(50),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_stock_requests_table)

            print("[OK] Tables created: supplies, transactions, monthly_reports, stock_reconciliation, stock_requests")
            return True

        except mysql.connector.Error as err:
            print(f"[ERROR] Failed to create tables: {err}")
            return False

    # -----------------------------------------------------
    # BASIC DB OPERATIONS
    # -----------------------------------------------------
    def execute_query(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"[ERROR] Query execution failed: {err}")
            return False

    def fetch_query(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"[ERROR] Fetch failed: {err}")
            return []

    def fetch_one(self, query, params=None):
        self.ensure_connection()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"❌ Fetch-one failed: {err}")
            return None

    # -----------------------------------------------------
    # COMPATIBILITY ALIASES (Fixes SupplyManager Errors)
    # -----------------------------------------------------
    def fetch_all(self, query, params=None):
        """Alias for fetch_query (required by SupplyManager)."""
        return self.fetch_query(query, params)

    def execute(self, query, params=None):
        """Alias for execute_query (required by SupplyManager)."""
        return self.execute_query(query, params)

    # -----------------------------------------------------
    # MONTHLY REPORT FUNCTIONS
    # -----------------------------------------------------
    def generate_monthly_report(self, month_year):
        """
        month_year → '2025-01'
        """
        print(f"📊 Generating monthly report for {month_year}...")

        query = """
        SELECT 
            item_id,
            SUM(CASE WHEN type='IN' THEN qty ELSE 0 END) AS total_in,
            SUM(CASE WHEN type='OUT' THEN qty ELSE 0 END) AS total_out
        FROM transactions
        WHERE DATE_FORMAT(timestamp,'%Y-%m') = %s
        GROUP BY item_id
        """

        result = self.fetch_query(query, (month_year,))

        for row in result:
            insert_q = """
            INSERT INTO monthly_reports (month_year, item_id, total_in, total_out)
            VALUES (%s, %s, %s, %s)
            """
            self.execute_query(insert_q, (
                month_year,
                row["item_id"],
                row["total_in"],
                row["total_out"]
            ))

        print(f"[OK] Monthly report for {month_year} generated.")
        return True

    def get_month_report(self, month_year):
        query = "SELECT * FROM monthly_reports WHERE month_year=%s"
        return self.fetch_query(query, (month_year,))

    # -----------------------------------------------------
    # CLOSE CONNECTION
    # -----------------------------------------------------
    def close(self):
        if self.cursor:
            try: 
                self.cursor.close()
            except:
                pass

        if self.conn:
            try: 
                self.conn.close()
            except:
                pass

        print("🔒 Database connection closed.")
