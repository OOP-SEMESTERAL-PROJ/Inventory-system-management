import datetime
from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, 
    QSpinBox, QTextEdit, QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtWidgets import QGraphicsOpacityEffect

class StockRequestPage(QWidget):
    def __init__(self, supply_manager=None, user_id: int = None, user_role: str = None):
        super().__init__()
        self.supply = supply_manager
        self.user_id = user_id
        self.user_role = user_role
        self.setWindowTitle("Stock Requests")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header with icon and title
        header_layout = QHBoxLayout()
        title = QLabel("📦 Stock Requests")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #000000;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # If staff or student show request form
        if self.user_role in ("staff", "student"):
            form_frame = QFrame()
            form_frame.setStyleSheet("""
                QFrame { 
                    border-radius: 14px; 
                    padding: 18px; 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFE5B4, stop:0.5 #FFECD1, stop:1 #FFD699);
                    border: 2px solid #FFD580;
                }
                QFrame QLabel { color: #000000; font-weight: 500; }
                QFrame QComboBox { color: #000000; }
                QFrame QSpinBox { color: #000000; }
                QFrame QTextEdit { color: #000000; }
            """)
            form_layout = QVBoxLayout(form_frame)
            form_layout.setSpacing(12)

            form_title = QLabel("📝 Request Stock Item")
            form_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            form_title.setStyleSheet("color: #000000;")
            form_layout.addWidget(form_title)

            # Item selection
            item_layout = QHBoxLayout()
            item_label = QLabel("Item:")
            item_label.setStyleSheet("color: #000000; font-weight: 600;")
            item_layout.addWidget(item_label)
            self.item_combo = QComboBox()
            self.item_combo.setMinimumWidth(220)
            self.item_combo.setStyleSheet("""
                QComboBox { color: #000000; padding: 8px; border: 1px solid #ddd; border-radius: 6px; background-color: white; }
                QComboBox::drop-down { border: none; }
                QComboBox QAbstractItemView { color: #000000; background-color: white; }
            """)
            item_layout.addWidget(self.item_combo)
            form_layout.addLayout(item_layout)

            # Quantity
            qty_layout = QHBoxLayout()
            qty_label = QLabel("Quantity:")
            qty_label.setStyleSheet("color: #000000; font-weight: 600;")
            qty_layout.addWidget(qty_label)
            self.qty_spinbox = QSpinBox()
            self.qty_spinbox.setMinimum(1)
            self.qty_spinbox.setMaximum(1000)
            self.qty_spinbox.setFixedWidth(120)
            self.qty_spinbox.setStyleSheet("color: #000000; border: 1px solid #ddd; border-radius: 6px; padding: 6px;")
            qty_layout.addWidget(self.qty_spinbox)
            qty_layout.addStretch()
            form_layout.addLayout(qty_layout)

            # Reason
            reason_label = QLabel("Reason:")
            reason_label.setStyleSheet("color: #000000; font-weight: 600;")
            form_layout.addWidget(reason_label)
            self.reason_text = QTextEdit()
            self.reason_text.setMaximumHeight(85)
            self.reason_text.setStyleSheet("color: #000000; border: 1px solid #ddd; border-radius: 6px; padding: 8px;")
            form_layout.addWidget(self.reason_text)

            # Submit
            submit_btn = QPushButton("✓ Submit Request")
            submit_btn.setMinimumHeight(40)
            submit_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            submit_btn.setStyleSheet("""
                QPushButton { 
                    color: white; 
                    border: none; 
                    border-radius: 8px; 
                    padding: 10px 20px; 
                    font-weight: bold; 
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #45a049);
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #45a049, stop:1 #3d8b40);
                }
            """)
            submit_btn.clicked.connect(self.submit_request)
            form_layout.addWidget(submit_btn)

            main_layout.addWidget(form_frame)

        # Table title with icon
        table_title = QLabel("📋 " + ("My Requests" if self.user_role in ("staff", "student") else "All Requests"))
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_title.setStyleSheet("color: #000000; margin-top:12px;")
        main_layout.addWidget(table_title)

        # Requests table with enhanced styling
        self.requests_table = QTableWidget(0, 7 if self.user_role in ("admin", "student") else 6)
        self.requests_table.setAlternatingRowColors(True)
        self.requests_table.setStyleSheet("""
            QTableWidget { 
                background-color: #ffffff; 
                color: #000000; 
                border: 2px solid #E8E8E8; 
                border-radius: 10px;
                gridline-color: #f0f0f0;
            }
            QHeaderView::section { 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #667eea, stop:1 #764ba2); 
                color: white; 
                padding: 12px; 
                border: none; 
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item { 
                padding: 10px; 
                border-bottom: 1px solid #f0f0f0; 
                color: #000000;
            }
            QTableWidget::item:selected { 
                background-color: #E3F2FD; 
                color: #000000;
            }
            QTableWidget { 
                alternate-background-color: #f9f9f9; 
            }
        """)
        # Configure columns and headers based on role
        if self.user_role and self.user_role.lower() == 'admin':
            # Admin sees who requested plus an action column
            self.requests_table.setColumnCount(8)
            headers = ["Item", "Quantity", "Reason", "Status", "Requested By", "Created", "Updated", "Action"]
        elif self.user_role and self.user_role.lower() == 'student':
            # Student sees their requests and can receive (action column)
            self.requests_table.setColumnCount(7)
            headers = ["Item", "Quantity", "Reason", "Status", "Created", "Updated", "Action"]
        else:
            # Staff (or other) sees their requests without an action column
            self.requests_table.setColumnCount(6)
            headers = ["Item", "Quantity", "Reason", "Status", "Created", "Updated"]

        self.requests_table.setHorizontalHeaderLabels(headers)
        # Save the action column index for use when inserting widgets
        self.action_col = headers.index("Action") if "Action" in headers else None

        self.requests_table.setColumnWidth(0, 160)
        self.requests_table.setColumnWidth(1, 100)
        self.requests_table.setColumnWidth(2, 180)
        self.requests_table.setColumnWidth(3, 110)
        # Put table inside a scroll area to keep layout compact and scrollable
        self.table_container = QWidget()
        table_container_layout = QVBoxLayout(self.table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        table_container_layout.addWidget(self.requests_table)

        self.requests_scroll = QScrollArea()
        self.requests_scroll.setWidgetResizable(True)
        self.requests_scroll.setWidget(self.table_container)
        self.requests_scroll.setMaximumHeight(380)
        self.requests_scroll.setStyleSheet("QScrollArea { border: none; }")

        main_layout.addWidget(self.requests_scroll)

        main_layout.addStretch()

        # subtle fade-in animation for the table container (avoid applying to whole page)
        try:
            effect = QGraphicsOpacityEffect(self.table_container)
            self.table_container.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setDuration(550)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            self._init_anim = anim
        except Exception:
            # Fallback: ignore animation errors to avoid paint conflicts
            pass

    def _flash_table_then(self, fn_after: callable):
        """Temporarily flash the table container background, call fn_after(), then restore."""
        try:
            original_style = self.table_container.styleSheet()
            # apply a subtle highlight
            self.table_container.setStyleSheet(original_style + "\nbackground-color: #fffdf0;")

            # perform DB operation shortly after flash begins to keep UI responsive
            def run_and_restore():
                try:
                    fn_after()
                finally:
                    # restore original style after a short delay so user sees the flash
                    QTimer.singleShot(260, lambda: self.table_container.setStyleSheet(original_style))

            # call operation on next event loop iteration
            QTimer.singleShot(80, run_and_restore)
        except Exception as e:
            print(f"[ERROR] Flash animation failed: {e}")

    def load_data(self):
        """Load items and requests from database"""
        try:
            db = self.supply.db if self.supply else None
            if not db:
                return
            
            # Load items for combo box (only for staff/student)
            if hasattr(self, 'item_combo'):
                items = db.fetch_query("SELECT id, name FROM supplies ORDER BY name")
                for item in items:
                    self.item_combo.addItem(item['name'], item['id'])
            
            # Load requests
            self.load_requests()
        except Exception as e:
            print(f"[ERROR] Failed to load data: {e}")

    def load_requests(self):
        """Load requests from database"""
        try:
            db = self.supply.db if self.supply else None
            if not db:
                return
            
            # Build query based on role
            if self.user_role in ("staff", "student"):
                query = f"""
                    SELECT sr.id, s.name, sr.quantity_requested, sr.reason, sr.status, 
                           sr.created_at, sr.updated_at
                    FROM stock_requests sr
                    LEFT JOIN supplies s ON sr.item_id = s.id
                    WHERE sr.requested_by = {self.user_id}
                    ORDER BY sr.created_at DESC
                """
            else:  # admin
                query = """
                    SELECT sr.id, s.name, sr.quantity_requested, sr.reason, sr.status, 
                           sr.created_at, sr.updated_at, sr.requested_by
                    FROM stock_requests sr
                    LEFT JOIN supplies s ON sr.item_id = s.id
                    ORDER BY sr.created_at DESC
                """
            
            requests = db.fetch_query(query)
            self.requests_table.setRowCount(0)
            
            for idx, req in enumerate(requests):
                self.requests_table.insertRow(idx)
                
                # Item
                self.requests_table.setItem(idx, 0, QTableWidgetItem(req.get('name', 'N/A')))
                
                # Quantity
                self.requests_table.setItem(idx, 1, QTableWidgetItem(str(req.get('quantity_requested', 0))))
                
                # Reason
                self.requests_table.setItem(idx, 2, QTableWidgetItem(req.get('reason', '')))
                
                # Status with color coding
                status = req.get('status', 'pending')
                status_item = QTableWidgetItem(status.upper())
                if status == 'approved':
                    status_item.setForeground(QColor('#2E7D32'))
                elif status == 'rejected':
                    status_item.setForeground(QColor('#C62828'))
                else:
                    status_item.setForeground(QColor('#F57C00'))
                self.requests_table.setItem(idx, 3, status_item)
                
                # Determine where to place extra columns (requested_by for admin)
                col = 4
                if self.user_role and self.user_role.lower() == 'admin':
                    # Show requested_by (username if present, else id)
                    requested_by = req.get('requested_by') or req.get('requested_by_username') or ''
                    self.requests_table.setItem(idx, col, QTableWidgetItem(str(requested_by)))
                    col += 1

                # Created
                created = req.get('created_at', '')
                if created:
                    created = str(created).split('.')[0]
                self.requests_table.setItem(idx, col, QTableWidgetItem(created))
                col += 1

                # Updated
                updated = req.get('updated_at', '')
                if updated:
                    updated = str(updated).split('.')[0]
                self.requests_table.setItem(idx, col, QTableWidgetItem(updated))

                # Action column: admin gets Approve/Reject, student gets Receive when approved
                if self.user_role and self.user_role.lower() == 'admin':
                    action_layout = QHBoxLayout()

                    approve_btn = QPushButton("✓ Approve")
                    approve_btn.setMaximumWidth(100)
                    approve_btn.setStyleSheet("""
                        QPushButton { 
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4CAF50, stop:1 #45a049); 
                            color: white; 
                            border: none; 
                            border-radius: 6px; 
                            padding: 6px 10px;
                            font-weight: bold;
                            font-size: 11px;
                        }
                        QPushButton:hover { 
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #45a049, stop:1 #3d8b40); 
                        }
                    """)
                    approve_btn.clicked.connect(lambda checked, r_id=req['id']: self.approve_request(r_id))

                    reject_btn = QPushButton("✗ Reject")
                    reject_btn.setMaximumWidth(100)
                    reject_btn.setStyleSheet("""
                        QPushButton { 
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #F44336, stop:1 #E53935); 
                            color: white; 
                            border: none; 
                            border-radius: 6px; 
                            padding: 6px 10px;
                            font-weight: bold;
                            font-size: 11px;
                        }
                        QPushButton:hover { 
                            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #E53935, stop:1 #C62828); 
                        }
                    """)
                    reject_btn.clicked.connect(lambda checked, r_id=req['id']: self.reject_request(r_id))

                    container = QWidget()
                    container_layout = QHBoxLayout(container)
                    container_layout.setContentsMargins(0, 0, 0, 0)
                    container_layout.setSpacing(6)
                    container_layout.addWidget(approve_btn)
                    container_layout.addWidget(reject_btn)

                    # place in the computed action column
                    if self.action_col is not None:
                        self.requests_table.setCellWidget(idx, self.action_col, container)
                elif self.user_role == "student":
                    # Students can mark their approved requests as received
                    if status == 'approved':
                        receive_btn = QPushButton("📦 Receive")
                        receive_btn.setMaximumWidth(110)
                        receive_btn.setStyleSheet("""
                            QPushButton { 
                                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1976D2, stop:1 #1565C0); 
                                color: white; 
                                border: none; 
                                border-radius: 6px; 
                                padding: 6px 10px;
                                font-weight: bold;
                                font-size: 11px;
                            }
                            QPushButton:hover { 
                                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1565C0, stop:1 #0D47A1); 
                            }
                        """)
                        receive_btn.clicked.connect(lambda checked, r_id=req['id']: self.receive_request(r_id))
                        container = QWidget()
                        container_layout = QHBoxLayout(container)
                        container_layout.setContentsMargins(0, 0, 0, 0)
                        container_layout.addWidget(receive_btn)
                        if self.action_col is not None:
                            self.requests_table.setCellWidget(idx, self.action_col, container)
                    else:
                        # Empty placeholder for other statuses
                        if self.action_col is not None:
                            self.requests_table.setItem(idx, self.action_col, QTableWidgetItem(""))
                    
        except Exception as e:
            print(f"[ERROR] Failed to load requests: {e}")

    def submit_request(self):
        """Submit a stock request"""
        try:
            item_id = self.item_combo.currentData()
            quantity = self.qty_spinbox.value()
            reason = self.reason_text.toPlainText().strip()
            
            if not item_id or quantity <= 0:
                QMessageBox.warning(self, "Invalid Input", "Please select an item and enter a quantity.")
                return
            
            db = self.supply.db if self.supply else None
            if not db:
                return
            
            query = """
                INSERT INTO stock_requests (item_id, requested_by, quantity_requested, reason, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """
            params = (item_id, self.user_id, quantity, reason)
            db.execute_query(query, params)
            
            QMessageBox.information(self, "Success", "Stock request submitted successfully!")
            self.qty_spinbox.setValue(1)
            self.reason_text.clear()
            self.load_requests()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to submit request: {e}")
            print(f"[ERROR] Failed to submit request: {e}")

    def approve_request(self, request_id: int):
        """Approve a stock request, remove quantity from supplies, and delete the request"""
        def _do_approve():
            try:
                db = self.supply.db if self.supply else None
                if not db:
                    return

                # Fetch request details to get item_id and quantity
                req = db.fetch_one("SELECT item_id, quantity_requested FROM stock_requests WHERE id=%s", (request_id,))
                if not req:
                    QMessageBox.warning(self, "Not Found", "Request not found.")
                    return

                item_id = req.get('item_id')
                qty = int(req.get('quantity_requested') or 0)

                # Update supplies quantity (subtract the requested quantity)
                if item_id and qty > 0:
                    db.execute_query("UPDATE supplies SET quantity = quantity - %s WHERE id = %s", (qty, item_id))

                # Delete the request after approval
                db.execute_query("DELETE FROM stock_requests WHERE id = %s", (request_id,))

                QMessageBox.information(self, "Success", "Request approved, inventory updated, and request removed!")
                self.load_requests()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to approve request: {e}")

        # Flash the table while performing DB changes for a smoother UX
        self._flash_table_then(_do_approve)

    def reject_request(self, request_id: int):
        """Reject a stock request"""
        def _do_reject():
            try:
                db = self.supply.db if self.supply else None
                if not db:
                    return

                # Delete the request so it is removed from the table
                db.execute_query("DELETE FROM stock_requests WHERE id = %s", (request_id,))

                QMessageBox.information(self, "Success", "Request rejected and removed!")
                self.load_requests()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to reject request: {e}")

        self._flash_table_then(_do_reject)

    def receive_request(self, request_id: int):
        """Mark a student's approved request as received and remove supplies quantity"""
        def _do_receive():
            try:
                db = self.supply.db if self.supply else None
                if not db:
                    return

                # Fetch request details to get item_id and quantity
                req = db.fetch_one("SELECT item_id, quantity_requested, status, requested_by FROM stock_requests WHERE id=%s", (request_id,))
                if not req:
                    QMessageBox.warning(self, "Not Found", "Request not found.")
                    return

                # Ensure only the requesting student can mark received
                if req.get('requested_by') != self.user_id:
                    QMessageBox.warning(self, "Unauthorized", "You can only receive your own requests.")
                    return

                if req.get('status') != 'approved':
                    QMessageBox.information(self, "Not Ready", "Request is not approved yet.")
                    return

                item_id = req.get('item_id')
                qty = int(req.get('quantity_requested') or 0)

                # Update supplies quantity (subtract the requested quantity)
                if item_id and qty > 0:
                    update_q = "UPDATE supplies SET quantity = quantity - %s WHERE id = %s"
                    db.execute_query(update_q, (qty, item_id))

                # Mark request as received
                db.execute_query("UPDATE stock_requests SET status='received', updated_at=NOW() WHERE id=%s", (request_id,))

                QMessageBox.information(self, "Success", "Marked as received and inventory updated.")
                self.load_requests()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to mark received: {e}")

        self._flash_table_then(_do_receive)
