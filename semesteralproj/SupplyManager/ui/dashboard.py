import os
import sys
import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QDialog,
    QWidget, QScrollArea, QFrame, QGraphicsDropShadowEffect, QToolTip,
    QTableWidgetItem, QLabel, QPushButton, QTableWidget, QMessageBox,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QCursor, QPainter
from PyQt6.uic import loadUi

from PyQt6.QtCharts import (
    QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis,
    QPieSeries, QPieSlice
)

def _parse_int(value, default=0):
    try:
        if value is None:
            return default
        s = str(value).strip()
        if s == "":
            return default
        if "." in s:
            return int(float(s))
        return int(s)
    except Exception:
        return default

# Import dialog pages
try:
    from .dialog_page import AddProductDialog, UpdateProductDialog
except ImportError:
    from dialog_page import AddProductDialog, UpdateProductDialog

# Import SupplyManager and DatabaseManager
try:
    from ..modules.supply_manager import SupplyManager
    from ..database.Db_manager import DatabaseManager
except ImportError:
    from modules.supply_manager import SupplyManager
    from database.Db_manager import DatabaseManager


class Dashboard(QMainWindow):
    def __init__(self, supply_manager: SupplyManager):
        super().__init__()
        self.supply_manager = supply_manager

        # Load dashboard UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "dashboard.ui")
        loadUi(ui_path, self)

        # Make central widget scrollable
        try:
            central_widget = getattr(self, "centralwidget", QWidget())
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            try:
                central_widget.adjustSize()
                minsize = central_widget.sizeHint()
                min_h = max(minsize.height(), 1800)
                min_w = minsize.width() if minsize.width() > 0 else 960
                central_widget.setMinimumSize(min_w, min_h)
            except Exception:
                central_widget.setMinimumSize(960, 1800)

            scroll.setWidget(central_widget)
            self.setCentralWidget(scroll)
        except Exception:
            pass

        # Connect Add Product button
        if hasattr(self, "addProductBtn"):
            try:
                self.addProductBtn.clicked.connect(self.open_add_product_dialog)
            except Exception:
                pass

        # Layouts for charts
        self.graph_layout = QVBoxLayout()
        self.pie_layout = QVBoxLayout()

        if hasattr(self, "graphFrame"):
            try:
                self.graphFrame.setLayout(self.graph_layout)
            except:
                pass

        if hasattr(self, "graphFrame_2"):
            try:
                self.graphFrame_2.setLayout(self.pie_layout)
            except:
                pass

        self.apply_card_shadow()
        self.setup_inventory_table()
        self.refresh_dashboard()
        self.setup_searchbar()

# ============================
    # Search Bar Setup and Filter
    # ============================
    def setup_searchbar(self):
        """Setup search bar and category filter"""
        if hasattr(self, "lineEdit"):
            self.lineEdit.setPlaceholderText("Search by name or SKU...")
            self.lineEdit.textChanged.connect(self.filter_inventory)
        
        if hasattr(self, "comboBox"):
            self.comboBox.clear()
            self.comboBox.addItem("All Categories")
            self.categories = set()
            supplies = self.supply_manager.get_supplies()
            for item in supplies:
                category = item.get("category", "Other")
                if category not in self.categories:
                    self.categories.add(category)
                    self.comboBox.addItem(category)
            self.comboBox.currentTextChanged.connect(self.filter_inventory)
        
        # Store all supplies for filtering
        self.all_supplies = self.supply_manager.get_supplies()


    def filter_inventory(self):
        """Filter table by search text and category"""
        if not hasattr(self, "inventoryTable"):
            return

        search_text = self.lineEdit.text().lower().strip() if hasattr(self, "lineEdit") else ""
        selected_category = self.comboBox.currentText() if hasattr(self, "comboBox") else "All Categories"

        table = self.inventoryTable
        
        for row, item in enumerate(self.all_supplies):
            sku = item.get("sku", "").lower()
            name = item.get("name", "").lower()
            supplier = item.get("supplier", "").lower()
            category = item.get("category", "Other")

            # Check if matches search text
            matches_search = (
                search_text == "" or
                search_text in sku or
                search_text in name or
                search_text in supplier
            )

            # Check if matches category
            matches_category = (
                selected_category == "All Categories" or
                category == selected_category
            )

            # Show/hide row based on filters
            table.setRowHidden(row, not (matches_search and matches_category))


    # ============================
    # Card Styling
    # ============================
    def style_card(self, frame: QFrame, top_gradient_start="#3aa0ff", top_gradient_end="#005eff"):
        frame.setStyleSheet(f"""
            QFrame#{frame.objectName()} {{
                background-color: white;
                border-radius: 20px;
                border-top: 5px solid qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 {top_gradient_start}, stop:1 {top_gradient_end}
                );
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 80))
        frame.setGraphicsEffect(shadow)

    def apply_card_shadow(self):
        for name in dir(self):
            if name.startswith("card"):
                frame = getattr(self, name)
                if isinstance(frame, QFrame):
                    try:
                        self.style_card(frame)
                    except:
                        pass


    # ============================
    # Add / Edit Dialog
    # ============================
    def open_add_product_dialog(self):
        dialog = AddProductDialog(self)
        result = dialog.exec()

        if result == QDialog.DialogCode.Rejected:
            return

        data = dialog.get_data()
        if not data.get("name"):
            if hasattr(self, "outputBox"):
                self.outputBox.append("⚠️ Product name required!")
            return

        qty = _parse_int(data.get("quantity", 0), 0)
        price = 0.0
        try:
            price = float(str(data.get("price", "")).strip()) if str(data.get("price", "")).strip() != "" else 0.0
        except Exception:
            price = 0.0
        min_qty = _parse_int(data.get("min_quantity", 5), 5)
        sku = data.get("sku", None)

        # Check if product exists
        existing = self.supply_manager.get_supply_by_name(data["name"])
        if existing:
            new_qty = existing["quantity"] + qty
            self.supply_manager.update_supply(existing["id"], new_qty, price, min_qty)
        else:
            self.supply_manager.add_supply(
                data["name"], data["category"], data["supplier"], qty, price, sku, min_qty
            )

        self.refresh_dashboard()


    # ============================
    # Refresh dashboard
    # ============================
    def refresh_dashboard(self):
        try:
            self.load_inventory_to_table()
        except Exception as e:
            print("load_inventory_to_table failed:", e)

        try:
            self.update_graph()
        except Exception as e:
            print("update_graph failed:", e)

        # Update summary cards
        try:
            self.update_summary_cards()
        except Exception as e:
            print("update_summary_cards failed:", e)


    # ============================
    # Summary Cards
    # ============================
    def update_summary_cards(self):
        supplies = self.supply_manager.get_supplies()
        if not supplies:
            return

        # Total items
        total_items = sum(item.get("quantity", 0) for item in supplies)
        if hasattr(self, "items"):
            self.items.setText(str(total_items))

        # Low stock
        low_stock_count = sum(1 for item in supplies if item.get("quantity", 0) <= item.get("min_quantity", 5))
        if hasattr(self, "lowstock"):
            self.lowstock.setText(str(low_stock_count))

        # Total value
        total_value = sum(item.get("quantity", 0) * item.get("price", 0.0) for item in supplies)
        if hasattr(self, "value"):
            self.value.setText(f"${total_value:.2f}")

        # Distinct categories
        distinct_categories = set(item.get("category", "Other") for item in supplies)
        if hasattr(self, "category"):
            self.category.setText(str(len(distinct_categories)))


    # ============================
    # Inventory Table Setup
    # ============================
    def setup_inventory_table(self):
        if not hasattr(self, "inventoryTable"):
            print("Warning: inventoryTable not found in UI.")
            return

        table: QTableWidget = self.inventoryTable
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "SKU", "Name", "Category", "Quantity", "Min Qty", "Status",
            "Price", "Supplier", "Last Updated", "Actions"
        ])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setWordWrap(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget {
                background: #ffffff;
                border-radius: 8px;
                font-size: 13px;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 4px;
                background-color: white;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: #b3d9ff;
                color: black;
            }
            QHeaderView::section {
                background-color: #f5f5fb;
                padding: 6px;
                font-weight: 600;
                border: none;
                color: black;
            }
        """)
        table.horizontalHeader().setDefaultSectionSize(140)
        table.horizontalHeader().setStretchLastSection(True)


    # ============================
    # Create category pill
    # ============================
    def create_category_pill(self, text, bg="#e8f4ff", fg="#035596"):
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {fg};
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: 600;
            }}
        """)
        return lbl


    # ============================
    # Load table data
    # ============================
    def load_inventory_to_table(self):
        if not hasattr(self, "inventoryTable"):
            return

        table: QTableWidget = self.inventoryTable
        supplies = self.supply_manager.get_supplies()
        table.setRowCount(len(supplies))

        for row, item in enumerate(supplies):
            sku_item = QTableWidgetItem(item.get("sku", ""))
            sku_item.setBackground(QColor(255, 255, 255))
            sku_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 0, sku_item)

            name_item = QTableWidgetItem(item.get("name", ""))
            name_item.setBackground(QColor(255, 255, 255))
            name_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 1, name_item)

            cat = item.get("category", "Other")
            pill = self.create_category_pill(cat)
            table.setCellWidget(row, 2, pill)

            qty_item = QTableWidgetItem(str(item.get("quantity", 0)))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setBackground(QColor(255, 255, 255))
            qty_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 3, qty_item)

            min_qty_item = QTableWidgetItem(str(item.get("min_quantity", 5)))
            min_qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            min_qty_item.setBackground(QColor(255, 255, 255))
            min_qty_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 4, min_qty_item)

            status_item = QTableWidgetItem()
            if item["quantity"] <= item.get("min_quantity", 5):
                status_item.setText("🔴 Low Stock")
                status_item.setBackground(QColor(255, 228, 196))
                status_item.setForeground(QColor(168, 93, 0))
            else:
                status_item.setText("✅ In Stock")
                status_item.setBackground(QColor(209, 247, 214))
                status_item.setForeground(QColor(26, 127, 55))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 5, status_item)

            price_item = QTableWidgetItem(f"${item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            price_item.setBackground(QColor(255, 255, 255))
            price_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 6, price_item)

            supplier_item = QTableWidgetItem(item.get("supplier", ""))
            supplier_item.setBackground(QColor(255, 255, 255))
            supplier_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 7, supplier_item)

            last_updated = item.get("last_updated", "N/A")
            if last_updated and last_updated != "N/A":
                try:
                    if isinstance(last_updated, datetime.datetime):
                        last_updated = last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(last_updated, datetime.date):
                        last_updated = last_updated.strftime("%Y-%m-%d") + " 00:00:00"
                    else:
                        last_updated = str(last_updated)
                except Exception:
                    last_updated = str(last_updated)
            updated_item = QTableWidgetItem(last_updated)
            updated_item.setBackground(QColor(255, 255, 255))
            updated_item.setForeground(QColor(0, 0, 0))
            table.setItem(row, 8, updated_item)

            # Action buttons
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedWidth(36)
            edit_btn.clicked.connect(self._make_edit_handler(item["id"]))

            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedWidth(36)
            delete_btn.clicked.connect(self._make_delete_handler(item["id"]))

            action_container = QWidget()
            action_layout = QHBoxLayout(action_container)
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(6)
            table.setCellWidget(row, 9, action_container)


    # Button callback helpers
    def _make_edit_handler(self, item_id):
        return lambda: self.edit_item(item_id)

    def _make_delete_handler(self, item_id):
        return lambda: self._confirm_delete_and_refresh(item_id)

    # Delete confirm
    def _confirm_delete_and_refresh(self, item_id):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.supply_manager.delete_supply(item_id)
            self.refresh_dashboard()

    # Edit item
    def edit_item(self, item_id):
        item = self.supply_manager.get_supply_by_id(item_id)
        if not item:
            return
        dialog = UpdateProductDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            qty = _parse_int(data.get("quantity", item["quantity"]), item["quantity"])
            try:
                price = float(str(data.get("price", item["price"])).strip())
            except Exception:
                price = item.get("price", 0.0)
            min_qty = _parse_int(data.get("min_quantity", item.get("min_quantity", 5)), item.get("min_quantity", 5))
            self.supply_manager.update_supply(item_id, qty, price, min_qty)
            self.refresh_dashboard()


    # ============================
    # Charts (Bar + Pie)
    # ============================
    def update_graph(self):
        supplies = self.supply_manager.get_supplies()
        if not supplies:
            return

        names = [item["name"] for item in supplies]
        quantities = [item["quantity"] for item in supplies]

        # Bar chart
        bar_set = QBarSet("Stock Quantity")
        bar_set.append(quantities)
        try:
            bar_set.hovered.connect(lambda status, i: self.show_bar_tooltip(status, i, quantities, names))
        except:
            pass

        series = QBarSeries()
        series.append(bar_set)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("📊 Stock Quantity by Product")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        axis_x = QBarCategoryAxis()
        axis_x.append(names)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, max(quantities) + 10)
        axis_y.setTitleText("Quantity")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        bar_view = QChartView(chart)
        bar_view.setRenderHints(QPainter.RenderHint.Antialiasing)
        bar_view.setMinimumSize(500, 350)

        # Pie chart
        category_totals = {}
        for item in supplies:
            category = item["category"]
            category_totals[category] = category_totals.get(category, 0) + item["quantity"]

        pie_series = QPieSeries()
        for cat, qty in category_totals.items():
            slice = QPieSlice(f"{cat} ({qty})", qty)
            slice.setLabelVisible(True)
            pie_series.append(slice)

        pie_chart = QChart()
        pie_chart.addSeries(pie_series)
        pie_chart.setTitle("📊 Stock Distribution by Category")
        pie_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        pie_view = QChartView(pie_chart)
        pie_view.setRenderHints(QPainter.RenderHint.Antialiasing)
        pie_view.setMinimumSize(300, 350)

        # Replace old charts
        for layout in (self.graph_layout, self.pie_layout):
            for i in reversed(range(layout.count())):
                w = layout.itemAt(i).widget()
                if w:
                    w.setParent(None)

        self.graph_layout.addWidget(bar_view)
        self.pie_layout.addWidget(pie_view)

    def show_bar_tooltip(self, status, index, quantities, names):
        if status:
            QToolTip.showText(
                QCursor.pos(),
                f"{names[index]}: {quantities[index]} in stock"
            )
        else:
            QToolTip.hideText()


# ============================
# Main Entry
# ============================
if __name__ == "__main__":
    app = QApplication(sys.argv)

    db = DatabaseManager({
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "supply_db"
    })

    manager = SupplyManager(db)

    dashboard = Dashboard(manager)
    dashboard.showMaximized()

    sys.exit(app.exec())
