import sys
import pathlib
import unittest

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))

from ui.inventory_page import _parse_int


class TestParseInt(unittest.TestCase):
    def test_none(self):
        self.assertEqual(_parse_int(None), 0)

    def test_empty(self):
        self.assertEqual(_parse_int(''), 0)

    def test_int_string(self):
        self.assertEqual(_parse_int('42'), 42)

    def test_float_string(self):
        self.assertEqual(_parse_int('42.9'), 42)

    def test_invalid_with_default(self):
        self.assertEqual(_parse_int('abc', default=7), 7)

    def test_int_input(self):
        self.assertEqual(_parse_int(5), 5)


if __name__ == '__main__':
    unittest.main()
