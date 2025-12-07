import sys
import pathlib
import unittest

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))

from database import Db_manager as dbmod


class FakeConnectorError(Exception):
    pass


class TestDatabaseManager(unittest.TestCase):
    def test_connect_failure(self):
        # Monkeypatch mysql.connector.connect to raise an Error by temporarily replacing it
        orig_connect = dbmod.mysql.connector.connect

        def fake_connect(**kwargs):
            raise dbmod.mysql.connector.Error('cannot connect')

        dbmod.mysql.connector.connect = fake_connect
        try:
            config = {'host':'localhost','user':'x','password':'x','database':'x'}
            dm = dbmod.DatabaseManager(config)
            self.assertFalse(dm.connected)
        finally:
            dbmod.mysql.connector.connect = orig_connect

    def test_generate_monthly_report_no_transactions(self):
        class FakeDB(dbmod.DatabaseManager):
            def __init__(self):
                self.config = {}
                self.conn = None
                self.cursor = None
                self.connected = True

            def fetch_query(self, q, p=None):
                return []

            def execute_query(self, q, p=None):
                return True

        dm = FakeDB()
        self.assertTrue(dm.generate_monthly_report('2025-01'))


if __name__ == '__main__':
    unittest.main()
