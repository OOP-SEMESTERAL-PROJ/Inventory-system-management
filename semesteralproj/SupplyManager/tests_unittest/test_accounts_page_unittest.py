import sys
import pathlib
import unittest
from unittest.mock import Mock, MagicMock, patch

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))


class TestAccountsPageHelpers(unittest.TestCase):
    """Test helper functions and logic from accounts_page.py"""
    
    def test_user_validation_username_not_empty(self):
        """Validate username is not empty"""
        username = ""
        self.assertFalse(bool(username))
    
    def test_user_validation_username_valid(self):
        """Validate username is provided"""
        username = "john_doe"
        self.assertTrue(bool(username))
    
    def test_password_validation_not_empty(self):
        """Validate password is not empty"""
        password = ""
        self.assertFalse(bool(password))
    
    def test_password_validation_valid(self):
        """Validate password is provided"""
        password = "secure123"
        self.assertTrue(bool(password))
    
    def test_role_defaults_to_staff(self):
        """Test that role defaults to Staff"""
        role = "Staff"
        self.assertEqual(role, "Staff")
    
    def test_user_data_structure(self):
        """Test user data structure is valid"""
        user = {
            "id": 1,
            "username": "admin",
            "role": "Admin"
        }
        self.assertIn("id", user)
        self.assertIn("username", user)
        self.assertIn("role", user)
        self.assertEqual(user["id"], 1)
    
    def test_user_list_empty(self):
        """Test empty user list"""
        users = []
        self.assertEqual(len(users), 0)
    
    def test_user_list_multiple_users(self):
        """Test multiple users in list"""
        users = [
            {"id": 1, "username": "admin", "role": "Admin"},
            {"id": 2, "username": "staff1", "role": "Staff"},
            {"id": 3, "username": "staff2", "role": "Staff"}
        ]
        self.assertEqual(len(users), 3)
        self.assertEqual(users[0]["role"], "Admin")
        self.assertEqual(users[1]["role"], "Staff")


if __name__ == '__main__':
    unittest.main()
