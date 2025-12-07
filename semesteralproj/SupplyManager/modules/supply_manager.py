from datetime import datetime

class SupplyManager:
    def __init__(self, db):
        self.db = db

    # -----------------------------------------------------
    # SUPPLIES
    # -----------------------------------------------------
    def _to_dict(self, row):
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        return {
            "id": row[0],
            "sku": row[1],
            "name": row[2],
            "category": row[3],
            "supplier": row[4],
            "quantity": row[5],
            "min_quantity": row[6],
            "price": row[7],
            "last_updated": row[8],
            "created_at": row[9] if len(row) > 9 else None
        }

    def get_supplies(self):
        rows = self.db.fetch_all("SELECT * FROM supplies ORDER BY id ASC")
        return rows  # Already dict format from DatabaseManager

    def get_supply_by_id(self, supply_id):
        return self.db.fetch_one("SELECT * FROM supplies WHERE id=%s", (supply_id,))

    def get_supply_by_name(self, name):
        return self.db.fetch_one(
            "SELECT * FROM supplies WHERE LOWER(name)=LOWER(%s)",
            (name,)
        )

    def add_supply(self, name, category, supplier, quantity, price, sku=None, min_quantity=5):
        if not sku:
            sku = f"{name[:3].upper()}-{int(quantity):04d}"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.execute("""
            INSERT INTO supplies (sku, name, category, supplier, quantity, min_quantity, price, last_updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (sku, name, category, supplier, int(quantity), int(min_quantity), float(price), now))

    def update_supply(self, supply_id, quantity, price, min_quantity=None):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if min_quantity is not None:
            self.db.execute("""
                UPDATE supplies
                SET quantity=%s, price=%s, min_quantity=%s, last_updated=%s
                WHERE id=%s
            """, (int(quantity), float(price), int(min_quantity), now, supply_id))
        else:
            self.db.execute("""
                UPDATE supplies
                SET quantity=%s, price=%s, last_updated=%s
                WHERE id=%s
            """, (int(quantity), float(price), now, supply_id))

    def delete_supply(self, supply_id):
        self.db.execute("DELETE FROM supplies WHERE id=%s", (supply_id,))

    # -----------------------------------------------------
    # TRANSACTION LOGS
    # -----------------------------------------------------
    def log_transaction(self, supply_id, action, qty, prev, new, note=""):
        return self.db.log_transaction(supply_id, action, qty, prev, new, note)

    def get_logs(self):
        return self.db.get_logs()

    # -----------------------------------------------------
    # MONTHLY REPORTS
    # -----------------------------------------------------
    def generate_monthly_report(self, month_year):
        return self.db.generate_monthly_report(month_year)

    def get_monthly_reports(self):
        return self.db.get_monthly_reports()
    
    
