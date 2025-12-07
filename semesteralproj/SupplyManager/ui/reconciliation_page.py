from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox, QMessageBox,
    QGraphicsDropShadowEffect, QScrollArea, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
import datetime
from typing import Optional, List, Dict, Any


def apply_shadow(widget, blur=16, x_offset=0, y_offset=2, color=Qt.GlobalColor.lightGray):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)


class ReconciliationPage(QWidget):
    def __init__(self, supply_manager=None):
        super().__init__()
        self.supply = supply_manager
        self.current_month = datetime.date.today().strftime("%Y-%m")
        self.reconciliation_data = {}  # {item_id: {physical_qty, notes}}
        self.setWindowTitle("📊 Stock Reconciliation")
        self.setGeometry(50, 50, 1400, 800)
        self.setStyleSheet("ReconciliationPage { background-color: #f8f9fa; }")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Frame
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9C27B0, stop:1 #7B1FA2);
                border-radius: 14px;
                padding: 24px;
            }
        """)
        header_frame.setFixedHeight(140)
        apply_shadow(header_frame, blur=16, y_offset=6, color=QColor(0, 0, 0, 100))
        
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(20, 10, 20, 10)
        header.setSpacing(16)
        
        title = QLabel("📊 Stock Reconciliation")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; font-weight: bold;")
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        title.setContentsMargins(8, 0, 8, 0)
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        header.addWidget(title)
        header.addStretch()

        # Month selector
        month_lbl = QLabel("Select Month:")
        month_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        month_lbl.setStyleSheet("color: #ffffff;")
        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                min-width: 120px;
            }
            QComboBox:hover { background-color: #f0f0f0; }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #9C27B0;
            }
        """)
        self._populate_month_combo()
        self.month_combo.setCurrentText(self.current_month)
        self.month_combo.currentTextChanged.connect(self.on_month_changed)
        header.addWidget(month_lbl)
        header.addWidget(self.month_combo)

        # Save button
        save_btn = QPushButton("💾 Save Reconciliation")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 160px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #45a049, stop:1 #3d8b40); }
            QPushButton:pressed { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d8b40, stop:1 #2d6a30); }
        """)
        save_btn.clicked.connect(self.reconcile_and_save)
        header.addWidget(save_btn)

        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5252;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #ff6464; }
            QPushButton:pressed { background-color: #cc3d3d; }
        """)
        back_btn.clicked.connect(self.on_back_clicked)
        header.addWidget(back_btn)

        main_layout.addWidget(header_frame)

        # Table Frame
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        apply_shadow(table_frame, blur=10, y_offset=3, color=QColor(0, 0, 0, 50))
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Item Name",
            "System Qty",
            "Physical Count",
            "Variance",
            "Status",
            "Notes"
        ])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #e8e8e8;
                border: none;
                border-radius: 12px;
            }
            QTableWidget::item {
                padding: 10px 8px;
                color: #000000;
                background-color: #ffffff;
            }
            QTableWidget::item:selected {
                background-color: #e8e8e8;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9C27B0, stop:1 #7B1FA2);
                color: #ffffff;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        self.table.verticalHeader().setVisible(False)
        # Allow text wrapping and let headers resize to contents so long text is readable
        self.table.setWordWrap(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.NoSelection)
        self.table.setColumnWidth(0, 280)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 190)
        self.table.setColumnWidth(3, 160)
        self.table.setColumnWidth(4, 160)
        self.table.setColumnWidth(5, 280)
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.table)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #9C27B0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #7B1FA2;
            }
        """)
        table_layout.addWidget(scroll)
        main_layout.addWidget(table_frame)
        main_layout.addWidget(table_frame)

    def _fit_font(self, text: str, base_size: int = 11, weight=QFont.Weight.Normal) -> QFont:
        """Pick a font size that fits longer text by reducing size slightly.

        Keeps text readable while avoiding truncation; caller should also set a tooltip.
        """
        txt = (text or "")
        length = len(txt)
        size = base_size
        if length > 30:
            # reduce font by 1 step for each ~10 extra chars, lower bound 8
            reduce_by = (length - 30) // 10 + 1
            size = max(8, base_size - reduce_by)
        return QFont("Segoe UI", size, weight)
    def _populate_month_combo(self):
        now = datetime.date.today()
        items = []
        for i in range(12):
            d = (now.replace(day=1) - datetime.timedelta(days=30*i)).replace(day=1)
            items.append(d.strftime("%Y-%m"))
        items = sorted(set(items), reverse=True)
        self.month_combo.addItems(items)

    def _db(self):
        if self.supply and hasattr(self.supply, "db"):
            return self.supply.db
        return None

    def _fetch_all(self, q, p=None):
        db = self._db()
        if not db:
            return []
        try:
            if hasattr(db, "fetch_query"):
                return db.fetch_query(q, p)
            if hasattr(db, "fetch_all"):
                return db.fetch_all(q, p)
        except Exception as e:
            print("[ERROR] Fetch failed:", e)
        return []

    def _fetch_one(self, q, p=None):
        db = self._db()
        if not db:
            return None
        try:
            if hasattr(db, "fetch_one"):
                return db.fetch_one(q, p)
            rows = self._fetch_all(q, p)
            return rows[0] if rows else None
        except Exception as e:
            print("[ERROR] Fetch one failed:", e)
        return None

    def _execute(self, q, p=None):
        db = self._db()
        if not db:
            return False
        try:
            if hasattr(db, "execute_query"):
                db.execute_query(q, p)
                return True
        except Exception as e:
            print("[ERROR] Execute failed:", e)
        return False

    def on_month_changed(self, month):
        self.current_month = month
        self.reconciliation_data = {}
        self.load_data()

    def load_data(self):
        """Load supplies for current month"""
        self.table.setRowCount(0)
        
        year, month = self.current_month.split("-")
        month_start = f"{year}-{month}-01"
        # Get last day of month
        import datetime as dt
        next_month = dt.datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d") + dt.timedelta(days=32)
        month_end = next_month.replace(day=1) - dt.timedelta(days=1)
        month_end_str = month_end.strftime("%Y-%m-%d")

        # Fetch supplies for this month
        supplies = self._fetch_all(f"""
            SELECT id, name, quantity, category, price
            FROM supplies
            WHERE last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
            ORDER BY name ASC
        """)

        for i, supply in enumerate(supplies):
            item_id = supply.get("id")
            name = supply.get("name", "")
            system_qty = int(supply.get("quantity") or 0)
            
            # Check if reconciliation exists for this item in this month
            reconciled = self._fetch_one(f"""
                SELECT actual_qty, notes FROM stock_reconciliation
                WHERE month_year = '{self.current_month}' AND item_id = {item_id}
            """)

            physical_qty = reconciled.get("actual_qty", system_qty) if reconciled else system_qty
            notes = reconciled.get("notes", "") if reconciled else ""
            variance = physical_qty - system_qty

            # Add row
            self.table.insertRow(i)

            # Item name
            name_item = QTableWidgetItem(name)
            name_item.setForeground(QColor("#000000"))
            name_item.setFont(self._fit_font(name, base_size=11, weight=QFont.Weight.Medium))
            name_item.setToolTip(name)
            self.table.setItem(i, 0, name_item)

            # System Qty
            qty_item = QTableWidgetItem(str(system_qty))
            qty_item.setForeground(QColor("#000000"))
            qty_item.setFont(QFont("Segoe UI", 11))
            self.table.setItem(i, 1, qty_item)

            # Physical Count (editable spinbox)
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(10000)
            spinbox.setValue(int(physical_qty))
            spinbox.setStyleSheet("""
                QSpinBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px 10px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QSpinBox:focus {
                    border: 2px solid #9C27B0;
                    background-color: #f8f9fa;
                }
                QSpinBox::up-button {
                    subcontrol-origin: border;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left: 1px solid #e0e0e0;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f5f5f5, stop:1 #eeeeee);
                }
                QSpinBox::down-button {
                    subcontrol-origin: border;
                    subcontrol-position: bottom right;
                    width: 25px;
                    border-left: 1px solid #e0e0e0;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eeeeee, stop:1 #f5f5f5);
                }
                QSpinBox::up-button:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9C27B0, stop:1 #7B1FA2);
                }
                QSpinBox::down-button:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9C27B0, stop:1 #7B1FA2);
                }
            """)
            spinbox.item_id = item_id
            spinbox.system_qty = system_qty
            spinbox.valueChanged.connect(lambda val, ii=i, iid=item_id, sqty=system_qty: self.update_variance(ii, val, sqty))
            self.table.setCellWidget(i, 2, spinbox)

            # Variance (auto-calculated)
            var_item = QTableWidgetItem(str(variance))
            var_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            if variance == 0:
                var_item.setForeground(QColor("#4CAF50"))
                var_item.setText("✓ OK")
            elif variance > 0:
                var_item.setForeground(QColor("#FF9800"))
                var_item.setText(f"⚠ +{variance}")
            else:
                var_item.setForeground(QColor("#F44336"))
                var_item.setText(f"⚠ {variance}")
            self.table.setItem(i, 3, var_item)

            # Status
            status_item = QTableWidgetItem("✓ Complete" if reconciled else "⏳ Pending")
            status_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
            status_item.setForeground(QColor("#2196F3" if reconciled else "#FF9800"))
            self.table.setItem(i, 4, status_item)

            # Notes
            note_item = QTableWidgetItem(notes)
            note_item.setForeground(QColor("#000000"))
            note_item.setFont(self._fit_font(notes, base_size=10))
            note_item.setToolTip(notes)
            self.table.setItem(i, 5, note_item)

            # Alternate row colors
            if i % 2 == 0:
                for col in range(self.table.columnCount()):
                    if col != 2:  # Skip spinbox column
                        if self.table.item(i, col):
                            self.table.item(i, col).setBackground(QColor("#f5f6f8"))

        self.table.resizeColumnsToContents()

    def update_variance(self, row, physical_qty, system_qty):
        """Update variance column when physical count changes"""
        variance = physical_qty - system_qty
        var_item = self.table.item(row, 3)
        
        if variance == 0:
            var_item.setForeground(QColor("#4CAF50"))
            var_item.setText("✓ OK")
        elif variance > 0:
            var_item.setForeground(QColor("#FF9800"))
            var_item.setText(f"⚠ +{variance}")
        else:
            var_item.setForeground(QColor("#F44336"))
            var_item.setText(f"⚠ {variance}")

    def reconcile_and_save(self):
        """Save reconciliation data to database"""
        db = self._db()
        if not db:
            QMessageBox.warning(self, "Error", "Database not connected!")
            return

        try:
            saved_count = 0
            for row in range(self.table.rowCount()):
                # Get item ID from spinbox
                spinbox = self.table.cellWidget(row, 2)
                if not spinbox or not hasattr(spinbox, 'item_id'):
                    continue

                item_id = spinbox.item_id
                physical_qty = spinbox.value()
                notes = self.table.item(row, 5).text() if self.table.item(row, 5) else ""
                system_qty = spinbox.system_qty

                # Delete existing reconciliation for this month/item
                db.execute_query(
                    f"DELETE FROM stock_reconciliation WHERE month_year = '{self.current_month}' AND item_id = {item_id}"
                )

                # Insert new reconciliation record
                db.execute_query(
                    f"""
                    INSERT INTO stock_reconciliation 
                    (month_year, item_id, recorded_qty, actual_qty, variance, reconciled_by, notes, created_at)
                    VALUES ('{self.current_month}', {item_id}, {system_qty}, {physical_qty}, {physical_qty - system_qty}, 'admin', '{notes}', NOW())
                    """
                )

                # Fetch transaction counts for this month to populate monthly_reports
                year, month = self.current_month.split("-")
                month_start = f"{year}-{month}-01"
                import datetime as dt
                next_month = dt.datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d") + dt.timedelta(days=32)
                month_end = next_month.replace(day=1) - dt.timedelta(days=1)
                month_end_str = month_end.strftime("%Y-%m-%d")

                transaction_data = self._fetch_one(f"""
                    SELECT 
                        COUNT(CASE WHEN type='IN' THEN 1 END) AS total_in,
                        COUNT(CASE WHEN type='OUT' THEN 1 END) AS total_out
                    FROM transactions
                    WHERE item_id={item_id} AND created_at BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
                """)
                
                total_in = transaction_data.get('total_in', 0) if transaction_data else 0
                total_out = transaction_data.get('total_out', 0) if transaction_data else 0

                # Check if monthly_reports record exists for this month/item
                existing = self._fetch_one(f"""
                    SELECT id FROM monthly_reports
                    WHERE month_year = '{self.current_month}' AND item_id = {item_id}
                """)

                if existing:
                    # Update existing record
                    db.execute_query(f"""
                        UPDATE monthly_reports
                        SET total_in={total_in}, total_out={total_out}, current_stock={physical_qty}
                        WHERE month_year='{self.current_month}' AND item_id={item_id}
                    """)
                else:
                    # Insert new record
                    db.execute_query(f"""
                        INSERT INTO monthly_reports
                        (month_year, item_id, total_in, total_out, current_stock)
                        VALUES ('{self.current_month}', {item_id}, {total_in}, {total_out}, {physical_qty})
                    """)

                saved_count += 1

            # Flash animation
            self._flash_table()

            QMessageBox.information(
                self,
                "✓ Success",
                f"Saved {saved_count} reconciliation record(s) for {self.current_month}"
            )

            self.load_data()

        except Exception as e:
            print(f"[ERROR] Reconcile failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save reconciliation:\n{str(e)}")

    def _flash_table(self):
        """Flash table with yellow highlight"""
        original_color = self.table.styleSheet()
        
        def reset_color():
            self.table.setStyleSheet(original_color)
        
        # Flash yellow
        self.table.setStyleSheet(original_color + """
            QTableWidget { background-color: #FFFACD; }
        """)
        
        # Reset after 300ms
        QTimer.singleShot(300, reset_color)

    def on_back_clicked(self):
        self.close()
