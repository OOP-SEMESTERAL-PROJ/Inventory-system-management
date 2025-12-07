import os
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QGraphicsDropShadowEffect,
    QHeaderView, QScrollArea, QMessageBox, QDialog
)
from PyQt6.QtGui import QColor, QCursor, QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from .dialog_page import AddProductDialog, UpdateProductDialog  # your existing dialogs

# ---------------- Utility ----------------
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

# ---------------- Hover Frame ----------------
class HoverFrame(QFrame):
    def __init__(self, scale_factor=1.05):
        super().__init__()
        self.scale_factor = scale_factor
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(150)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._original_rect = None

    def enterEvent(self, event):
        if self._original_rect is None:
            self._original_rect = self.geometry()
        rect = self._original_rect
        new_width = int(rect.width() * self.scale_factor)
        new_height = int(rect.height() * self.scale_factor)
        new_rect = QRect(rect.x() - (new_width - rect.width())//2,
                         rect.y() - (new_height - rect.height())//2,
                         new_width,
                         new_height)
        self.anim.stop()
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(new_rect)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._original_rect is None:
            return
        self.anim.stop()
        self.anim.setStartValue(self.geometry())
        self.anim.setEndValue(self._original_rect)
        self.anim.start()
        super().leaveEvent(event)

# ---------------- Inventory Page ----------------
class InventoryPage(QWidget):
    def __init__(self, supply_manager):
        super().__init__()
        self.supply_manager = supply_manager
        # soft gradient background and base font
        self.setStyleSheet("""
            QWidget { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f3f6fb, stop:1 #ffffff); font-family: 'Segoe UI', Arial; }
        """)
        self.initUI()
        self.refresh_inventory()

    def initUI(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Summary cards
        self.card_layout = QHBoxLayout()
        self.card_layout.setSpacing(20)
        layout.addLayout(self.card_layout)

        self.total_items_card = self.create_card("Total Items", "#3498DB")
        self.low_stock_card = self.create_card("Low Stock", "#E74C3C")
        self.total_value_card = self.create_card("Total Value", "#2ECC71")
        self.card_layout.addWidget(self.total_items_card)
        self.card_layout.addWidget(self.low_stock_card)
        self.card_layout.addWidget(self.total_value_card)

        # Add button
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Item")
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_btn.setStyleSheet(self.button_style("#3498DB"))
        self.add_btn.setFixedSize(140, 40)
        self.add_btn.clicked.connect(self.add_item)
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_btn)
        layout.addLayout(btn_layout)

        # Table container
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 15px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 60))
        table_frame.setGraphicsEffect(shadow)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(10, 10, 10, 10)
        table_frame.setMinimumHeight(480)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "SKU", "Name", "Category", "Quantity", "Min Qty", "Status",
            "Price", "Supplier", "Last Updated", "Actions"
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Bigger, more readable table styles
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; font-size: 15px; color: #1F2937; }
            QTableWidget::item:selected { background-color: #DFF3FF; color: #0f172a; }
            QHeaderView::section { background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8fafc, stop:1 #eef2ff); font-weight: 700; padding: 10px; color: #0f172a; border: none; }
            QTableWidget::item:hover { background-color: #fbfdff; }
            QTableWidget { alternate-background-color: #fbfcfd; }
        """)
        self.table.setFont(QFont("Segoe UI", 11))
        # make rows taller by default and header taller
        try:
            self.table.verticalHeader().setDefaultSectionSize(48)
        except Exception:
            pass
        try:
            self.table.horizontalHeader().setFixedHeight(48)
        except Exception:
            pass
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    # ---------------- Card Styling ----------------
    def create_card(self, title, color):
        frame = HoverFrame(scale_factor=1.04)
        frame.setMinimumSize(220, 110)
        value_lbl = QLabel("0")
        value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        frame_layout = QVBoxLayout(frame)
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 11))
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addStretch()
        frame_layout.addWidget(title_lbl)
        frame_layout.addWidget(value_lbl)
        frame_layout.addStretch()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 45))
        frame.setGraphicsEffect(shadow)

        # compute a lighter tint for the gradient stop
        try:
            hex_c = color.lstrip('#')
            r = int(hex_c[0:2], 16)
            g = int(hex_c[2:4], 16)
            b = int(hex_c[4:6], 16)
            lr = min(255, r + 40)
            lg = min(255, g + 40)
            lb = min(255, b + 40)
            light = f"#{lr:02x}{lg:02x}{lb:02x}"
        except Exception:
            light = "#ffffff"

        # colored left accent plus gradient background using the accent color
        frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}, stop:1 {light});
                border-radius: 14px;
                border: 1px solid rgba(15,23,42,0.06);
                padding-left: 12px;
                margin: 2px;
            }}
        """)

        # Title and value label styles (white for contrast) -- ensure transparent backgrounds
        title_lbl.setStyleSheet("background: transparent; color: rgba(255,255,255,0.95); font-weight: 600; border: none;")
        value_lbl.setStyleSheet(f"background: transparent; color: rgba(255,255,255,0.98); font-size: 20px; font-weight: 800; border: none;")

        # small colored badge on the left using frame border-left
        try:
            existing = frame.styleSheet()
            frame.setStyleSheet(existing + f" QFrame {{ border-left: 8px solid {color}; }}")
        except Exception:
            pass

        frame.value_label = value_lbl
        return frame

    def button_style(self, color="#34495E"):
        return f"""
            QPushButton {{
                background-color: {color};
                border: none;
                color: white;
                border-radius: 10px;
                font-size: 14px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,0,0,0.06);
            }}
        """

    # ---------------- Refresh ----------------
    def refresh_inventory(self):
        supplies = self.supply_manager.get_supplies() or []
        self.load_table(supplies)
        self.update_cards(supplies)

    # ---------------- Load Table ----------------
    def load_table(self, supplies):
        self.table.setRowCount(len(supplies))
        for row, item in enumerate(supplies):
            # Fill table
            for col_index, key in enumerate(["sku","name","category","quantity","min_quantity","","price","supplier","last_updated"]):
                if col_index !=5:
                    text = str(item.get(key,""))
                    if key=="price":
                        text = f"${float(text):.2f}"
                    if key=="last_updated" and isinstance(item.get("last_updated"), (datetime.date, datetime.datetime)):
                        text = item.get("last_updated").strftime("%Y-%m-%d %H:%M:%S")
                    self.table.setItem(row, col_index, QTableWidgetItem(text))

            # Status
            status_item = QLabel()
            qty = int(item.get("quantity",0))
            min_qty = int(item.get("min_quantity",5))
            if qty <= min_qty:
                status_item.setText("🔴 Low Stock")
                status_item.setStyleSheet("color: #C0392B; font-weight: bold;")
            else:
                status_item.setText("✅ In Stock")
                status_item.setStyleSheet("color: #27AE60; font-weight: bold;")
            status_item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setCellWidget(row,5,status_item)

            # Actions
            edit_btn = QPushButton("✏️")
            delete_btn = QPushButton("🗑️")
            edit_btn.setFixedWidth(36)
            delete_btn.setFixedWidth(36)
            edit_btn.clicked.connect(lambda _, i=item: self.edit_item(i))
            delete_btn.clicked.connect(lambda _, i=item: self.delete_item(i))
            container = QFrame()
            hbox = QHBoxLayout(container)
            hbox.addWidget(edit_btn)
            hbox.addWidget(delete_btn)
            hbox.setContentsMargins(0,0,0,0)
            hbox.setSpacing(5)
            self.table.setCellWidget(row,9,container)
            # ensure row has increased height for readability
            try:
                self.table.setRowHeight(row, 48)
            except Exception:
                pass

    # ---------------- Update Cards ----------------
    def update_cards(self, supplies):
        total_items = sum(int(item.get("quantity",0)) for item in supplies)
        low_stock = sum(1 for item in supplies if int(item.get("quantity",0)) <= int(item.get("min_quantity",5)))
        total_value = sum(int(item.get("quantity",0))*float(item.get("price",0.0)) for item in supplies)
        self.total_items_card.value_label.setText(str(total_items))
        self.low_stock_card.value_label.setText(str(low_stock))
        self.total_value_card.value_label.setText(f"${total_value:.2f}")

    # ---------------- Add / Edit / Delete ----------------
    def add_item(self):
        dialog = AddProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            existing = self.supply_manager.get_supply_by_name(data.get("name",""))
            if existing:
                new_qty = existing["quantity"] + int(data.get("quantity",0))
                self.supply_manager.update_supply(existing["id"], new_qty, float(data.get("price",0)), int(data.get("min_quantity",5)))
            else:
                self.supply_manager.add_supply(
                    data.get("name",""), data.get("category",""), data.get("supplier",""),
                    int(data.get("quantity",0)), float(data.get("price",0)), data.get("sku",""), int(data.get("min_quantity",5))
                )
            self.refresh_inventory()

    def edit_item(self,item):
        dialog = UpdateProductDialog(self,item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.supply_manager.update_supply(
                item["id"], int(data.get("quantity",item["quantity"])),
                float(data.get("price", item.get("price",0))),
                int(data.get("min_quantity",item.get("min_quantity",5)))
            )
            self.refresh_inventory()

    def delete_item(self,item):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {item.get('name')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.supply_manager.delete_supply(item["id"])
            self.refresh_inventory()
    
