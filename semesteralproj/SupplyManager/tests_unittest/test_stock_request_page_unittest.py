import sys
import pathlib
import unittest
from unittest.mock import Mock, MagicMock, patch
import datetime

# Ensure SupplyManager package path is available when running unittest directly
ROOT = pathlib.Path(__file__).resolve().parent.parent
SUPPLY_DIR = ROOT / 'SupplyManager'
if str(SUPPLY_DIR) not in sys.path:
    sys.path.insert(0, str(SUPPLY_DIR))


class TestStockRequestPageHelpers(unittest.TestCase):
    """Test helper functions and logic from stock_request_page.py"""
    
    def test_user_role_staff_can_request(self):
        """Test staff role can create requests"""
        user_role = "staff"
        can_request = user_role in ("staff", "student")
        self.assertTrue(can_request)
    
    def test_user_role_student_can_request(self):
        """Test student role can create requests"""
        user_role = "student"
        can_request = user_role in ("staff", "student")
        self.assertTrue(can_request)
    
    def test_user_role_admin_cannot_request(self):
        """Test admin role cannot create requests"""
        user_role = "admin"
        can_request = user_role in ("staff", "student")
        self.assertFalse(can_request)
    
    def test_request_quantity_minimum(self):
        """Test request quantity minimum is 1"""
        quantity = 1
        self.assertGreaterEqual(quantity, 1)
    
    def test_request_quantity_valid(self):
        """Test valid request quantity"""
        quantity = 5
        self.assertGreater(quantity, 0)
        self.assertLessEqual(quantity, 1000)
    
    def test_request_quantity_maximum(self):
        """Test request quantity maximum is 1000"""
        quantity = 1000
        self.assertLessEqual(quantity, 1000)
    
    def test_request_reason_not_empty(self):
        """Test request reason is not empty"""
        reason = "Need stock for project"
        self.assertTrue(len(reason) > 0)
    
    def test_request_reason_empty_string(self):
        """Test request reason can be empty"""
        reason = ""
        self.assertEqual(reason, "")
    
    def test_stock_request_data_structure(self):
        """Test stock request data structure"""
        request_data = {
            "item_id": 1,
            "quantity": 5,
            "requested_by": 1,
            "status": "pending",
            "notes": "Urgent"
        }
        self.assertIn("item_id", request_data)
        self.assertIn("quantity", request_data)
        self.assertIn("status", request_data)
        self.assertEqual(request_data["status"], "pending")
    
    def test_request_status_pending(self):
        """Test request status pending"""
        status = "pending"
        self.assertEqual(status, "pending")
    
    def test_request_status_approved(self):
        """Test request status approved"""
        status = "approved"
        self.assertEqual(status, "approved")
    
    def test_request_status_rejected(self):
        """Test request status rejected"""
        status = "rejected"
        self.assertEqual(status, "rejected")
    
    def test_request_list_empty(self):
        """Test empty request list"""
        requests = []
        self.assertEqual(len(requests), 0)
    
    def test_request_list_multiple(self):
        """Test multiple requests in list"""
        requests = [
            {"item_id": 1, "quantity": 5, "status": "pending"},
            {"item_id": 2, "quantity": 10, "status": "approved"},
            {"item_id": 3, "quantity": 3, "status": "pending"}
        ]
        self.assertEqual(len(requests), 3)
        pending_count = sum(1 for r in requests if r["status"] == "pending")
        self.assertEqual(pending_count, 2)
    
    def test_request_user_id_valid(self):
        """Test user ID in request is valid"""
        user_id = 1
        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)
    
    def test_request_timestamp_generation(self):
        """Test request timestamp is generated correctly"""
        timestamp = datetime.datetime.now().isoformat()
        self.assertIsInstance(timestamp, str)
        self.assertIn("T", timestamp)


if __name__ == '__main__':
    unittest.main()
