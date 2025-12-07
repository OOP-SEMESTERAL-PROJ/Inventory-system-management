import sys
import pathlib
import unittest

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))

from modules.supply_manager import SupplyManager


class DummyDB:
    def __init__(self):
        self.last_execute = None
        self.queries = []

    def fetch_all(self, q, p=None):
        return []

    def fetch_one(self, q, p=None):
        return None

    def execute(self, q, p=None):
        self.last_execute = (q, p)
        self.queries.append((q, p))
        return True


class SupplyManagerTests(unittest.TestCase):
    def test_to_dict_tuple_and_none(self):
        db = DummyDB()
        sm = SupplyManager(db)
        row = (1, 'SKU1', 'Apple', 'Fruit', 'Supplier', 10, 5, 2.5, None)
        d = sm._to_dict(row)
        self.assertEqual(d['id'], 1)
        self.assertEqual(d['name'], 'Apple')
        self.assertIsNone(sm._to_dict(None))

    def test_add_supply_calls_db_execute(self):
        db = DummyDB()
        sm = SupplyManager(db)
        sm.add_supply('TestItem', 'Cat', 'Supp', 3, 1.5, sku=None, min_quantity=2)
        self.assertIsNotNone(db.last_execute)
        q, params = db.last_execute
        self.assertIn('INSERT INTO supplies', q)
        self.assertEqual(params[1], 'TestItem')
        self.assertEqual(int(params[4]), 3)


if __name__ == '__main__':
    unittest.main()
