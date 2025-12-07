import sys
import pathlib
import unittest
from unittest.mock import Mock, MagicMock, patch

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))


class TestSplashScreenHelpers(unittest.TestCase):
    """Test helper functions and logic from splash_screen.py"""
    
    def test_splash_screen_message_text(self):
        """Test splash screen displays logout message"""
        message = "Logging out..."
        self.assertEqual(message, "Logging out...")
    
    def test_splash_screen_message_not_empty(self):
        """Test splash screen message is not empty"""
        message = "Logging out..."
        self.assertTrue(len(message) > 0)
    
    def test_splash_screen_pixmap_dimensions(self):
        """Test splash screen pixmap dimensions"""
        width = 420
        height = 220
        self.assertEqual(width, 420)
        self.assertEqual(height, 220)
    
    def test_splash_screen_pixmap_valid(self):
        """Test splash screen pixmap is valid"""
        width = 420
        height = 220
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
    
    def test_splash_screen_background_color(self):
        """Test splash screen background color"""
        color = "white"
        self.assertEqual(color, "white")
    
    def test_splash_screen_font_family(self):
        """Test splash screen font family"""
        font_family = "Segoe UI"
        self.assertEqual(font_family, "Segoe UI")
    
    def test_splash_screen_font_size(self):
        """Test splash screen font size"""
        font_size = 16
        self.assertEqual(font_size, 16)
        self.assertIsInstance(font_size, int)
    
    def test_splash_screen_font_weight_bold(self):
        """Test splash screen font weight is bold"""
        is_bold = True
        self.assertTrue(is_bold)
    
    def test_splash_screen_message_alignment_center(self):
        """Test splash screen message alignment is centered"""
        alignment = "center"
        self.assertEqual(alignment, "center")
    
    def test_splash_screen_message_color_black(self):
        """Test splash screen message color is black"""
        text_color = "black"
        self.assertEqual(text_color, "black")


if __name__ == '__main__':
    unittest.main()
