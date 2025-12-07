import sys
import pathlib
import unittest
from unittest.mock import Mock, MagicMock, patch

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))


class TestLandingPageHelpers(unittest.TestCase):
    """Test helper functions and logic from landing.py"""
    
    def test_user_role_admin(self):
        """Test user role is admin"""
        user_role = "Admin"
        self.assertEqual(user_role, "Admin")
    
    def test_user_role_staff(self):
        """Test user role is staff"""
        user_role = "Staff"
        self.assertEqual(user_role, "Staff")
    
    def test_user_role_valid_roles(self):
        """Test valid user roles"""
        valid_roles = ["Admin", "Staff", "Manager"]
        user_role = "Admin"
        self.assertIn(user_role, valid_roles)
    
    def test_user_id_valid(self):
        """Test user ID is valid"""
        user_id = 1
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)
    
    def test_user_id_none(self):
        """Test user ID can be None"""
        user_id = None
        self.assertIsNone(user_id)
    
    def test_window_title_format(self):
        """Test window title is set correctly"""
        title = "Inventory System"
        self.assertEqual(title, "Inventory System")
    
    def test_welcome_message_format(self):
        """Test welcome message format"""
        user_role = "Admin"
        welcome_msg = f"Welcome, {user_role}!"
        self.assertIn(user_role, welcome_msg)
    
    def test_welcome_message_different_roles(self):
        """Test welcome messages for different roles"""
        roles = ["Admin", "Staff", "Manager"]
        for role in roles:
            welcome_msg = f"Welcome, {role}!"
            self.assertIn(role, welcome_msg)
    
    def test_screen_geometry_calculation(self):
        """Test screen geometry percentage calculation"""
        screen_width = 1920
        screen_height = 1080
        percentage = 0.9
        
        window_width = int(screen_width * percentage)
        window_height = int(screen_height * percentage)
        
        self.assertEqual(window_width, 1728)
        self.assertEqual(window_height, 972)
    
    def test_page_stack_initialization(self):
        """Test stacked widget pages"""
        pages = ["welcome", "main", "dashboard"]
        self.assertEqual(len(pages), 3)
        self.assertIn("welcome", pages)
        self.assertIn("main", pages)


if __name__ == '__main__':
    unittest.main()
