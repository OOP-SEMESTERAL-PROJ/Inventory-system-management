import os
from PyQt6.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout
from PyQt6.uic import loadUi


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load dialog.ui
        ui_path = os.path.join(os.path.dirname(__file__), "dialog.ui")
        loadUi(ui_path, self)

        # Add Min Quantity field if it doesn't exist
        # Map alternate widget names from Designer to our expected names
        # Some .ui files use different generated names (e.g. nameEntry_11 for Min Qty)
        if hasattr(self, "nameEntry_11") and not hasattr(self, "minQtyEntry"):
            self.minQtyEntry = getattr(self, "nameEntry_11")
        if hasattr(self, "nameEntry_3") and not hasattr(self, "skuEntry"):
            self.skuEntry = getattr(self, "nameEntry_3")

        if not hasattr(self, "minQtyEntry"):
            self._add_min_qty_field()

        # Connect buttons
        self.pushButton.clicked.connect(self.accept)     # Add Item
        self.pushButton_2.clicked.connect(self.reject)   # Cancel

    def _add_min_qty_field(self):
        """Add Min Quantity input field programmatically"""
        try:
            # Create label and input field
            min_qty_label = QLabel("Min Quantity:")
            self.minQtyEntry = QLineEdit()
            self.minQtyEntry.setText("5")
            self.minQtyEntry.setPlaceholderText("Enter minimum quantity")
            
            # Find the main layout and add the new fields
            if hasattr(self, "verticalLayout"):
                # Insert before the buttons
                self.verticalLayout.insertWidget(self.verticalLayout.count() - 2, min_qty_label)
                self.verticalLayout.insertWidget(self.verticalLayout.count() - 2, self.minQtyEntry)
            elif hasattr(self, "centralwidget"):
                layout = self.centralwidget.layout()
                if layout:
                    layout.insertWidget(layout.count() - 1, min_qty_label)
                    layout.insertWidget(layout.count() - 1, self.minQtyEntry)
        except Exception as e:
            print(f"Could not add Min Quantity field: {e}")

    def get_data(self):
        # Map the Designer widget names from dialog.ui to logical fields
        return {
            "sku": getattr(self, "skuEntry", "").text().strip() if hasattr(self, "skuEntry") else None,
            "name": getattr(self, "nameEntry", getattr(self, "nameEntry_3", "")).text().strip() if hasattr(self, "nameEntry") or hasattr(self, "nameEntry_3") else "",
            "category": getattr(self, "nameEntry_8", "").text().strip() if hasattr(self, "nameEntry_8") else "",
            "supplier": getattr(self, "nameEntry_9", "").text().strip() if hasattr(self, "nameEntry_9") else "",
            "quantity": getattr(self, "qtyEntry", "").text().strip() if hasattr(self, "qtyEntry") else "",
            "price": getattr(self, "priceEntry", "").text().strip() if hasattr(self, "priceEntry") else "",
            "min_quantity": getattr(self, "minQtyEntry", "").text().strip() if hasattr(self, "minQtyEntry") else "5",
        }


class UpdateProductDialog(QDialog):
    """Dialog for updating an existing product with pre-populated fields"""
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item or {}
        self.original_min_qty = self.item.get("min_quantity", 5)

        # Load update.ui
        ui_path = os.path.join(os.path.dirname(__file__), "update.ui")
        loadUi(ui_path, self)

        # Map alternate widget names from Designer to our expected names
        if hasattr(self, "nameEntry_11") and not hasattr(self, "minQtyEntry"):
            self.minQtyEntry = getattr(self, "nameEntry_11")
        if hasattr(self, "nameEntry_3") and not hasattr(self, "skuEntry"):
            self.skuEntry = getattr(self, "nameEntry_3")

        # Add Min Quantity field programmatically only if no widget exists in the UI
        if not hasattr(self, "minQtyEntry"):
            self._add_min_qty_field()

        # Connect buttons (assuming similar button names)
        if hasattr(self, "pushButton"):
            self.pushButton.clicked.connect(self.accept)     # Update Item
        if hasattr(self, "pushButton_2"):
            self.pushButton_2.clicked.connect(self.reject)   # Cancel

        # Pre-populate fields with existing data
        self.populate_fields()

    def _add_min_qty_field(self):
        """Add Min Quantity input field programmatically"""
        try:
            # Create label and input field
            min_qty_label = QLabel("Min Quantity:")
            self.minQtyEntry = QLineEdit()
            self.minQtyEntry.setText(str(self.original_min_qty))
            self.minQtyEntry.setPlaceholderText("Enter minimum quantity")
            
            # Find the main layout and add the new fields
            if hasattr(self, "verticalLayout"):
                # Insert before the buttons
                self.verticalLayout.insertWidget(self.verticalLayout.count() - 2, min_qty_label)
                self.verticalLayout.insertWidget(self.verticalLayout.count() - 2, self.minQtyEntry)
            elif hasattr(self, "centralwidget"):
                layout = self.centralwidget.layout()
                if layout:
                    layout.insertWidget(layout.count() - 1, min_qty_label)
                    layout.insertWidget(layout.count() - 1, self.minQtyEntry)
        except Exception as e:
            print(f"Could not add Min Quantity field: {e}")

    def populate_fields(self):
        """Auto-populate dialog fields with current item data"""
        # SKU field (usually read-only in update dialog)
        if hasattr(self, "skuEntry") and "sku" in self.item:
            sku_entry = getattr(self, "skuEntry")
            sku_entry.setText(str(self.item.get("sku", "")))
            sku_entry.setReadOnly(True)  # Make SKU read-only in update dialog

        # Try to populate each field if it exists in the UI
        if hasattr(self, "nameEntry") and "name" in self.item:
            self.nameEntry.setText(str(self.item.get("name", "")))
        elif hasattr(self, "nameEntry_3") and "name" in self.item:
            self.nameEntry_3.setText(str(self.item.get("name", "")))

        if hasattr(self, "nameEntry_8") and "category" in self.item:
            self.nameEntry_8.setText(str(self.item.get("category", "")))

        if hasattr(self, "nameEntry_9") and "supplier" in self.item:
            self.nameEntry_9.setText(str(self.item.get("supplier", "")))

        if hasattr(self, "qtyEntry") and "quantity" in self.item:
            self.qtyEntry.setText(str(self.item.get("quantity", "")))

        if hasattr(self, "priceEntry") and "price" in self.item:
            self.priceEntry.setText(str(self.item.get("price", "")))

        # Always populate minQtyEntry with the actual value from the item
        if hasattr(self, "minQtyEntry"):
            min_qty_value = self.item.get("min_quantity", 5)
            self.minQtyEntry.setText(str(min_qty_value))

    def get_data(self):
        """Return updated data from the form"""
        # If minQtyEntry widget doesn't exist in UI, return the original min_qty value
        if hasattr(self, "minQtyEntry"):
            min_qty = getattr(self, "minQtyEntry", "").text().strip()
        else:
            min_qty = str(self.original_min_qty)
        
        return {
            "sku": getattr(self, "skuEntry", "").text().strip() if hasattr(self, "skuEntry") else None,
            "name": getattr(self, "nameEntry", getattr(self, "nameEntry_3", "")).text().strip() if hasattr(self, "nameEntry") or hasattr(self, "nameEntry_3") else "",
            "category": getattr(self, "nameEntry_8", "").text().strip() if hasattr(self, "nameEntry_8") else "",
            "supplier": getattr(self, "nameEntry_9", "").text().strip() if hasattr(self, "nameEntry_9") else "",
            "quantity": getattr(self, "qtyEntry", "").text().strip() if hasattr(self, "qtyEntry") else "",
            "price": getattr(self, "priceEntry", "").text().strip() if hasattr(self, "priceEntry") else "",
            "min_quantity": min_qty,
        }

