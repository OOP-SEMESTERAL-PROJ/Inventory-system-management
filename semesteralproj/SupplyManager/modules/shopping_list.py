class ShoppingList:
    def __init__(self, db):
        self.db = db

    def generate(self, min_stock=5):
        low_stock_items = self.db.fetch("SELECT name, quantity FROM supplies WHERE quantity < %s", (min_stock,))
        return low_stock_items
    