from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QComboBox,
    QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QEasingCurve, QPropertyAnimation, QMargins, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QPieSeries, QValueAxis, QBarCategoryAxis

import calendar
import datetime
from typing import Optional, List, Dict, Any


def apply_shadow(widget, blur=16, x_offset=0, y_offset=2, color=Qt.GlobalColor.lightGray):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(x_offset)
    shadow.setYOffset(y_offset)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)


class AnimatedCard(QFrame):
    """KPI Card with fade-in + hover-grow + full colored background"""
    def __init__(self, title: str, value: str | int, color: str = "#2196F3"):
        super().__init__()
        self.color = color
        self.setObjectName("kpi_card")
        # Convert hex color to lighter shade for gradient
        light_color = self._lighten_color(color, 40)
        self.setStyleSheet(f"""
            QFrame#kpi_card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}, stop:1 {light_color});
                border-radius: 16px;
                border: none;
            }}
            QLabel {{ background: transparent; }}
            QLabel#kpi_title {{ color: #ffffff; font-size: 12px; font-weight: 500; background: transparent; }}
            QLabel#kpi_value {{ color: #ffffff; font-size: 36px; font-weight: 700; background: transparent; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("kpi_title")
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        title_lbl.setStyleSheet("background: transparent; color: #ffffff;")

        self.value_lbl = QLabel(str(value))
        self.value_lbl.setObjectName("kpi_value")
        self.value_lbl.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.value_lbl.setStyleSheet("background: transparent; color: #ffffff;")

        layout.addWidget(title_lbl)
        layout.addWidget(self.value_lbl)
        layout.addStretch()

        # shadow
        apply_shadow(self, blur=20, y_offset=8, color=QColor(0, 0, 0, 100))

        # fade in
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity", self)
        self.fade_anim.setDuration(700)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_anim.start()

        # hover grow animation
        self.base_size = QSize(280, 120)
        self.setMinimumSize(self.base_size)
        self.setMaximumSize(self.base_size)
        self.scale_anim = QPropertyAnimation(self, b"maximumSize", self)
        self.scale_anim.setDuration(150)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        self.scale_anim.stop()
        self.scale_anim.setStartValue(self.maximumSize())
        self.scale_anim.setEndValue(QSize(self.base_size.width() + 8, self.base_size.height() + 8))
        self.scale_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.scale_anim.stop()
        self.scale_anim.setStartValue(self.maximumSize())
        self.scale_anim.setEndValue(self.base_size)
        self.scale_anim.start()
        super().leaveEvent(event)

    @staticmethod
    def _lighten_color(hex_color: str, amount: int) -> str:
        """Lighten a hex color by the specified amount"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f"#{r:02x}{g:02x}{b:02x}"


class TopItemCard(QFrame):
    def __init__(self, rank: int, name: str, qty: int, value: float):
        super().__init__()
        self.setObjectName("top_item_card")
        self.setStyleSheet("""
            QFrame#top_item_card { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #fafafa); border-radius: 12px; border: 1px solid #e0e0e0; }
            QLabel#rank_circle {
                color: white; font-weight: 700;
                border-radius: 20px; min-width: 40px; min-height: 40px;
                qproperty-alignment: AlignCenter;
            }
            QLabel#item_name { color: #000000; font-weight: 600; font-size: 14px; }
            QLabel#qty_lbl { color: #888888; font-size: 12px; }
            QLabel#value_lbl { color: #2196F3; font-weight: 700; font-size: 14px; }
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(16)

        rank_lbl = QLabel(str(rank))
        rank_lbl.setObjectName("rank_circle")
        rank_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8"]
        color = rank_colors[(rank - 1) % len(rank_colors)]
        rank_lbl.setStyleSheet(f"""
            QLabel#rank_circle {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}, stop:1 {color});
            }}
        """)
        rank_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

        left = QVBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setObjectName("item_name")
        name_lbl.setFont(QFont("Segoe UI", 13))
        qty_lbl = QLabel(f"Qty: {qty}")
        qty_lbl.setObjectName("qty_lbl")
        left.addWidget(name_lbl)
        left.addWidget(qty_lbl)

        val_lbl = QLabel(f"${value:,.2f}")
        val_lbl.setObjectName("value_lbl")
        val_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

        h.addWidget(rank_lbl)
        h.addLayout(left)
        h.addStretch()
        h.addWidget(val_lbl)

        apply_shadow(self, blur=18, y_offset=3)


class LowStockCard(QFrame):
    def __init__(self, name: str, sku: str, qty: int, min_qty: int):
        super().__init__()
        self.setObjectName("low_stock_card")
        self.setStyleSheet("""
            QFrame#low_stock_card { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #fafafa); border-radius: 12px; border: 1px solid #ffcccc; }
            QLabel#item_name { color: #000000; font-weight: 600; }
            QLabel#sku_lbl { color: #ff6b6b; font-size: 12px; }
            QLabel#qty_lbl { color: #ff5252; font-weight: 700; }
            QLabel#sub_lbl { color: #999999; font-size: 11px; }
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(14)

        left = QVBoxLayout()
        item_name_lbl = QLabel(name)
        item_name_lbl.setObjectName("item_name")
        left.addWidget(item_name_lbl)
        sku_lbl = QLabel(sku)
        sku_lbl.setObjectName("sku_lbl")
        left.addWidget(sku_lbl)

        right = QVBoxLayout()
        qty_lbl = QLabel(f"{qty} / {min_qty}")
        qty_lbl.setObjectName("qty_lbl")
        right.addWidget(qty_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        sub_lbl = QLabel("Current / Min")
        sub_lbl.setObjectName("sub_lbl")
        right.addWidget(sub_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        h.addLayout(left)
        h.addStretch()
        h.addLayout(right)

        apply_shadow(self, blur=12, y_offset=3, color=QColor(0, 0, 0))


class MonthlySalesReportPage(QWidget):
    def __init__(self, supply_manager=None, month_year: Optional[str] = None):
        super().__init__()
        self.supply = supply_manager  # Use self.supply consistently
        if month_year:
            self.month_year = month_year
        else:
            self.month_year = datetime.date.today().strftime("%Y-%m")
        self.selected_date = None  # Holds current clicked date or None

        self.setWindowTitle("Monthly Inventory Report")
        self.init_ui()
        self.load_and_render()

    def init_ui(self):
        main_container = QVBoxLayout(self)
        main_container.setContentsMargins(0, 0, 0, 0)
        # Overall page background and default fonts
        self.setStyleSheet("""
            QWidget { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f7f9fc, stop:1 #ffffff); font-family: 'Segoe UI'; }
            QLabel#page_title { color: #0f172a; font-size: 22px; font-weight: 700; }
            QLabel#page_subtitle { color: #6b7280; font-size: 13px; }
        """)
        
        # Scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #ffffff; }
            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #cccccc;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #999999; }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: #ffffff;")
        self.main_layout = QVBoxLayout(scroll_widget)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Monthly Inventory Report")
        title.setObjectName("page_title")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.subtitle = QLabel(self._friendly_month(self.month_year))
        self.subtitle.setObjectName("page_subtitle")
        left = QVBoxLayout()
        left.addWidget(title)
        left.addWidget(self.subtitle)
        header.addLayout(left)
        header.addStretch()

        # Month combo
        self.month_combo = QComboBox()
        self.month_combo.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QComboBox:hover { border: 1px solid #999999; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                selection-background-color: #e0e0e0;
            }
        """)
        self._populate_month_combo()
        self.month_combo.setCurrentText(self.month_year)
        self.month_combo.currentTextChanged.connect(self.on_month_changed)
        header.addWidget(self.month_combo)

        # Back
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff5252;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #ff6464; }
            QPushButton:pressed { background-color: #cc3d3d; }
        """)
        back_btn.clicked.connect(self.on_back_clicked)
        header.addWidget(back_btn)
        self.main_layout.addLayout(header)

        # KPI row
        kpi_row = QHBoxLayout()
        self.kpi_total_items = AnimatedCard("Total Items in Stock", "—", color="#2196F3")
        self.kpi_total_value = AnimatedCard("Total Inventory Value", "—", color="#4CAF50")
        self.kpi_low_stock = AnimatedCard("Low Stock Items", "—", color="#FF9800")
        self.kpi_categories = AnimatedCard("Active Categories", "—", color="#9C27B0")
        for c in (self.kpi_total_items, self.kpi_total_value, self.kpi_low_stock, self.kpi_categories):
            kpi_row.addWidget(c)
        self.main_layout.addLayout(kpi_row)

        # Charts row
        charts = QHBoxLayout()
        self.line_chart_view = QChartView()
        self.line_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.line_chart_view.setMinimumHeight(400)
        # Overlay label shown when there is no movement data
        self.line_empty_label = QLabel("No movement data for this month", self.line_chart_view)
        self.line_empty_label.setStyleSheet("color: #888888; font-size: 14px; background: transparent;")
        self.line_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.line_empty_label.hide()
        self.pie_chart_view = QChartView()
        self.pie_chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.pie_chart_view.setMinimumHeight(400)
        self._wrap_chart(self.line_chart_view, "Monthly Stock Movement", charts)
        self._wrap_chart(self.pie_chart_view, "Value by Category", charts)
        self.main_layout.addLayout(charts, 1)

        # Top items & low stock
        bottom = QHBoxLayout()
        self.top_items_holder = QVBoxLayout()
        top_frame = QFrame()
        top_frame.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f5f5f5); border-radius: 12px; border: 1px solid #e0e0e0;")
        top_layout = QVBoxLayout(top_frame)
        top_label = QLabel("Top 5 Items by Value")
        top_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 14px;")
        top_layout.addWidget(top_label)
        top_layout.addLayout(self.top_items_holder)
        bottom.addWidget(top_frame, 2)
        
        self.low_stock_holder = QVBoxLayout()
        low_frame = QFrame()
        low_frame.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f5f5f5); border-radius: 12px; border: 1px solid #e0e0e0;")
        low_layout = QVBoxLayout(low_frame)
        low_label = QLabel("Low Stock Alerts")
        low_label.setStyleSheet("color: #000000; font-weight: bold; font-size: 14px;")
        low_layout.addWidget(low_label)
        low_layout.addLayout(self.low_stock_holder)
        bottom.addWidget(low_frame, 1)
        self.main_layout.addLayout(bottom)

        self.main_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        main_container.addWidget(scroll)

    def _wrap_chart(self, chart_view, title, layout):
        frame = QFrame()
        frame.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffffff, stop:1 #f5f5f5); border-radius: 12px; border: 1px solid #e0e0e0;")
        box = QVBoxLayout(frame)
        box.setContentsMargins(10, 10, 10, 10)
        # header area
        header = QFrame()
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffffff, stop:1 #f3f4f6); border-top-left-radius: 12px; border-top-right-radius: 12px;")
        hbox = QHBoxLayout(header)
        hbox.setContentsMargins(12, 8, 12, 8)
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #0f172a;")
        hbox.addWidget(title_lbl)
        hbox.addStretch()
        box.addWidget(header)

        # Style the chart view
        chart_view.setStyleSheet("background-color: transparent; border: none;")
        chart_view.setContentsMargins(8, 8, 8, 8)
        box.addWidget(chart_view)
        layout.addWidget(frame)
        try:
            apply_shadow(frame, blur=14, y_offset=6, color=QColor(0,0,0,40))
        except Exception:
            pass

    def _friendly_month(self, ym: str):
        y, m = ym.split("-")
        return f"{calendar.month_name[int(m)]} {y}"

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

    def _fetch_one(self, q, p=None):
        db = self._db()
        if not db:
            return None
        try:
            if hasattr(db, "fetch_one"):
                return db.fetch_one(q, p)
            if hasattr(db, "fetch_query"):
                rows = db.fetch_query(q, p)
                return rows[0] if rows else None
        except Exception as e:
            print("[ERROR] Fetch failed (one):", e)
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
            print("[ERROR] Fetch failed (all):", e)
        return []

    def load_and_render(self):
        self.subtitle.setText(self._friendly_month(self.month_year))

        # Parse month_year to get start and end dates
        year, month = self.month_year.split("-")
        month_start = f"{year}-{month}-01"
        # Get last day of month
        next_month = datetime.datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d") + datetime.timedelta(days=32)
        month_end = next_month.replace(day=1) - datetime.timedelta(days=1)
        month_end_str = month_end.strftime("%Y-%m-%d")

        # KPI cards - filter by month
        total_items = self._fetch_one(f"""
            SELECT SUM(quantity) AS t FROM supplies 
            WHERE last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
        """) or {}
        total_value = self._fetch_one(f"""
            SELECT SUM(quantity * price) AS v FROM supplies 
            WHERE last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
        """) or {}
        low_stock = self._fetch_one(f"""
            SELECT COUNT(*) AS c FROM supplies 
            WHERE quantity <= min_quantity 
            AND last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
        """) or {}
        categories = self._fetch_one(f"""
            SELECT COUNT(DISTINCT category) AS c FROM supplies 
            WHERE last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
        """) or {}
        self.kpi_total_items.value_lbl.setText(str(total_items.get("t") or 0))
        self.kpi_total_value.value_lbl.setText(f"${(total_value.get('v') or 0):,.2f}")
        self.kpi_low_stock.value_lbl.setText(str(low_stock.get("c") or 0))
        self.kpi_categories.value_lbl.setText(str(categories.get("c") or 0))

        # Charts - render monthly total value trend (last 12 months)
        self._render_monthly_trend(self._fetch_all(f"""
            SELECT DATE_FORMAT(last_updated, '%Y-%m') AS ym,
               DATE_FORMAT(last_updated, '%b %Y') AS label,
               SUM(quantity * price) AS total_value
            FROM supplies
            GROUP BY DATE_FORMAT(last_updated, '%Y-%m')
            ORDER BY DATE_FORMAT(last_updated, '%Y-%m') ASC
            LIMIT 12
        """))

        self._render_pie_chart(self._fetch_all(f"""
            SELECT category, SUM(quantity*price) AS total_value
            FROM supplies 
            WHERE last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
            GROUP BY category
        """))

        self._render_top_items(self._fetch_all(f"""
            SELECT name, quantity, (quantity*price) AS value
            FROM supplies 
            WHERE last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
            ORDER BY value DESC LIMIT 5
        """))

        self._render_low_stock(self._fetch_all(f"""
            SELECT name, sku, quantity, min_quantity
            FROM supplies 
            WHERE quantity <= min_quantity
            AND last_updated BETWEEN '{month_start}' AND '{month_end_str} 23:59:59'
            ORDER BY quantity ASC
        """))

    def _render_line_chart(self, data: List[Dict[str, Any]]):
        # Build a mapping day->value from returned data (prefer net_qty if available)
        day_map: Dict[int, float] = {}
        for r in data:
            try:
                day_raw = r.get("day")
                if day_raw is None:
                    continue
                day_int = int(str(day_raw))
                if r.get("net_qty") is not None:
                    day_map[day_int] = float(r.get("net_qty") or 0)
                else:
                    day_map[day_int] = float(r.get("net_value") or 0)
            except Exception:
                continue

        # Determine number of days in selected month
        try:
            y, m = self.month_year.split("-")
            last_day = calendar.monthrange(int(y), int(m))[1]
        except Exception:
            last_day = 31

        labels = [str(d) for d in range(1, last_day + 1)]
        values = [float(day_map.get(d, 0.0)) for d in range(1, last_day + 1)]

        # If all values are zero, show an overlay label so user knows there's no movement
        try:
            if all(v == 0 for v in values):
                self.line_empty_label.show()
                try:
                    self.line_empty_label.resize(self.line_chart_view.size())
                except Exception:
                    pass
            else:
                self.line_empty_label.hide()
                try:
                    self.line_empty_label.resize(self.line_chart_view.size())
                except Exception:
                    pass
        except Exception:
            self.line_empty_label.hide()

        series = QLineSeries()
        for i, v in enumerate(values):
            # x as day number (1..last_day)
            series.append(i + 1, v)

        # Enhanced styling
        series.setColor(QColor("#2196F3"))
        p = series.pen()
        p.setWidth(3)
        series.setPen(p)

        chart = QChart()
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        chart.setTitleBrush(QBrush(QColor("#000000")))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().hide()

        # Create axes first and add to chart, then add series and attach
        axis_x = QValueAxis()
        axis_x.setRange(1, last_day)
        axis_x.setLabelFormat("%d")
        axis_x.setLabelsColor(QColor("#000000"))
        axis_x.setGridLineVisible(False)
        axis_x.setLineVisible(True)
        axis_x.setLinePen(QPen(QColor("#e0e0e0"), 1))
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        axis_y = QValueAxis()
        min_v = min(values) if values else 0
        max_v = max(values) if values else 0
        if min_v == 0 and max_v == 0:
            axis_y.setRange(-10, 10)
        else:
            pad_low = min_v * 0.2 if min_v < 0 else 0
            pad_high = max_v * 0.2 if max_v > 0 else 0
            axis_y.setRange(min_v - abs(pad_low), max_v + abs(pad_high))
        axis_y.setLabelsColor(QColor("#000000"))
        axis_y.setGridLineVisible(True)
        axis_y.setGridLinePen(QPen(QColor("#f0f0f0"), 1))
        axis_y.setLineVisible(True)
        axis_y.setLinePen(QPen(QColor("#e0e0e0"), 1))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        # Now add series and attach to axes
        chart.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        chart.setMargins(QMargins(10, 10, 10, 10))
        self.line_chart_view.setChart(chart)

    def _render_monthly_trend(self, rows: List[Dict[str, Any]]):
        """Render a monthly total-value trend (last 12 months) with simple animations and hover tooltips.

        This version aligns the 12-month window to the currently selected `self.month_year`,
        limits the SQL to that range, and scales large currency values to thousands (k) for
        clearer axis labels.
        """
        # Build list of 12 months ending at selected month_year (chronological)
        try:
            end_year, end_month = self.month_year.split("-")
            end_dt = datetime.date(int(end_year), int(end_month), 1)
        except Exception:
            end_dt = datetime.date.today().replace(day=1)

        months = []
        d = end_dt
        for _ in range(12):
            months.append(d)
            # step back one month
            d = (d - datetime.timedelta(days=1)).replace(day=1)
        months = list(reversed(months))

        labels = [m.strftime("%b %Y") for m in months]
        keys = [m.strftime("%Y-%m") for m in months]

        # Map rows returned from SQL: rows expected to include 'ym' and 'total_value'
        row_map = {r.get("ym"): float(r.get("total_value") or 0.0) for r in rows}
        values = [float(row_map.get(k, 0.0)) for k in keys]

        # Store for tooltip mapping
        self._trend_labels = labels
        self._trend_values = values

        series = QLineSeries()
        for i, v in enumerate(values):
            series.append(i + 1, v)
        series.setColor(QColor("#3F51B5"))
        p = series.pen()
        p.setWidth(3)
        series.setPen(p)
        try:
            series.setPointsVisible(True)
        except Exception:
            pass

        chart = QChart()
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        chart.setTitleBrush(QBrush(QColor("#000000")))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().hide()

        # X axis with month labels
        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        axis_x.setLabelsColor(QColor("#000000"))
        try:
            axis_x.setLabelsAngle(-30)
        except Exception:
            pass
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)

        # Y axis
        axis_y = QValueAxis()
        min_v = min(values) if values else 0
        max_v = max(values) if values else 0

        # If values are large, scale down to thousands and label accordingly
        scale = 1.0
        unit_label = ""
        if max_v > 50000:
            scale = 1000.0
            unit_label = " (k)"
            values = [v / scale for v in values]
            # update series data points to scaled values
            series = QLineSeries()
            for i, v in enumerate(values):
                series.append(i + 1, v)
            series.setColor(QColor("#3F51B5"))
            p = series.pen()
            p.setWidth(3)
            series.setPen(p)
            try:
                series.setPointsVisible(True)
            except Exception:
                pass

            # swap into chart (remove previous add if any)
            # we'll add series below after axis creation

        if min_v == 0 and max_v == 0:
            axis_y.setRange(0, 10)
        else:
            # use scaled extents when appropriate
            min_s = min(values) if values else 0
            max_s = max(values) if values else 0
            pad = max(1.0, (max_s - min_s) * 0.12)
            axis_y.setRange(max(0, min_s - pad), max_s + pad)
        # show labels with thousand separators (no direct suffix support)
        try:
            axis_y.setLabelFormat("%.0f")
        except Exception:
            pass
        # add unit to chart title for clarity
        if unit_label:
            chart.setTitle("Monthly Stock Movement" + unit_label)
        axis_y.setLabelsColor(QColor("#000000"))
        axis_y.setGridLineVisible(True)
        axis_y.setGridLinePen(QPen(QColor("#f0f0f0"), 1))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        chart.addSeries(series)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        chart.setMargins(QMargins(10, 10, 10, 10))
        self.line_chart_view.setChart(chart)

        # Tooltip label for hover
        if not hasattr(self, "trend_tooltip"):
            self.trend_tooltip = QLabel("", self.line_chart_view)
            self.trend_tooltip.setStyleSheet("background:#111827; color: #ffffff; padding:6px; border-radius:6px;")
            self.trend_tooltip.setFont(QFont("Segoe UI", 9))
            self.trend_tooltip.hide()

        # Connect hover event
        try:
            series.hovered.connect(self._on_trend_point_hover)
            # keep reference for mapping
            self._trend_chart = chart
            self._trend_series = series
        except Exception:
            pass

    def _on_trend_point_hover(self, point: QPointF, state: bool):
        try:
            if not hasattr(self, "_trend_chart"):
                return
            chart = self._trend_chart
            series = self._trend_series
            if not state:
                self.trend_tooltip.hide()
                return
            # Find index by x value (x was i+1)
            idx = int(round(point.x())) - 1
            if idx < 0 or idx >= len(self._trend_labels):
                self.trend_tooltip.hide()
                return
            label = self._trend_labels[idx]
            val = self._trend_values[idx]
            txt = f"{label}\n${val:,.2f}"
            self.trend_tooltip.setText(txt)
            # Map chart coordinate to widget position
            posf = chart.mapToPosition(point, series)
            # posf is in chart coords; translate relative to view
            x = int(posf.x()) + 10
            y = int(posf.y()) - 30
            self.trend_tooltip.move(max(6, x), max(6, y))
            self.trend_tooltip.adjustSize()
            self.trend_tooltip.show()
        except Exception:
            pass

    def _render_pie_chart(self, rows: List[Dict[str, Any]]):
        series = QPieSeries()
        total = sum(float(r.get("total_value") or 0) for r in rows) or 1
        colors = ["#2196F3", "#4CAF50", "#FF9800", "#F44336", "#9C27B0", 
                  "#00BCD4", "#E91E63", "#8BC34A", "#009688", "#3F51B5"]
        
        for idx, r in enumerate(rows):
            label = r.get("category") or "Uncategorized"
            value = float(r.get("total_value") or 0)
            s = series.append(label, value)
            pct = int((value / total) * 100)
            s.setLabelVisible(True)
            s.setLabel(f"{label} ({pct}%)")
            s.setLabelFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            s.setColor(QColor(colors[idx % len(colors)]))
            s.setBorderColor(QColor("#ffffff"))
            s.setBorderWidth(2)
        
        chart = QChart()
        chart.setBackgroundBrush(QBrush(QColor("#ffffff")))
        chart.setTitleBrush(QBrush(QColor("#000000")))
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.addSeries(series)
        
        legend = chart.legend()
        legend.setVisible(True)
        legend.setLabelColor(QColor("#000000"))
        legend.setFont(QFont("Segoe UI", 10))
        
        self.pie_chart_view.setChart(chart)

    def _render_top_items(self, rows: List[Dict[str, Any]]):
        while self.top_items_holder.count():
            it = self.top_items_holder.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
        for i, r in enumerate(rows, start=1):
            card = TopItemCard(
                rank=i,
                name=r.get("name", ""),
                qty=int(r.get("quantity") or 0),
                value=float(r.get("value") or 0.0)
            )
            self.top_items_holder.addWidget(card)

    def _render_low_stock(self, rows: List[Dict[str, Any]]):
        while self.low_stock_holder.count():
            it = self.low_stock_holder.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
        for r in rows:
            card = LowStockCard(
                name=r.get("name", ""),
                sku=r.get("sku", ""),
                qty=int(r.get("quantity") or 0),
                min_qty=int(r.get("min_quantity") or 0)
            )
            self.low_stock_holder.addWidget(card)

    def _render_sales_table(self, rows: List[Dict[str, Any]]):
        self.sales_table.setRowCount(0)
        grand = 0.0
        if not rows:
            row = self.sales_table.rowCount()
            self.sales_table.insertRow(row)
            self.sales_table.setItem(row, 0, QTableWidgetItem("None"))
            self.sales_table.setSpan(row, 0, 1, self.sales_table.columnCount())
            return
        for r in rows:
            row = self.sales_table.rowCount()
            self.sales_table.insertRow(row)
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(r.get("item_name", ""))))
            self.sales_table.setItem(row, 1, QTableWidgetItem(str(r.get("category", ""))))
            self.sales_table.setItem(row, 2, QTableWidgetItem(str(r.get("supplier", ""))))
            price = float(r.get("price") or 0)
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"${price:,.2f}"))
            tin = int(r.get("total_in") or 0)
            tout = int(r.get("total_out") or 0)
            sales = float(r.get("total_sales") or (tout * price))
            grand += sales
            self.sales_table.setItem(row, 4, QTableWidgetItem(str(tin)))
            self.sales_table.setItem(row, 5, QTableWidgetItem(str(tout)))
            self.sales_table.setItem(row, 6, QTableWidgetItem(f"${sales:,.2f}"))
        if self.sales_table.rowCount() > 0:
            row = self.sales_table.rowCount()
            self.sales_table.insertRow(row)
            self.sales_table.setItem(row, 0, QTableWidgetItem("Grand Total"))
            self.sales_table.setSpan(row, 0, 1, 6)
            self.sales_table.setItem(row, 6, QTableWidgetItem(f"${grand:,.2f}"))

    def _render_inventory_table(self, rows: List[Dict[str, Any]]):
        """Render current inventory by month in table format with reconciliation data"""
        self.inventory_table.setRowCount(0)
        
        if not rows:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem("No inventory data for this month"))
            self.inventory_table.setSpan(row, 0, 1, self.inventory_table.columnCount())
            return
        
        total_value = 0.0
        for r in rows:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            
            # Item Name
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(r.get("name", ""))))
            
            # Current Stock (blue)
            qty = int(r.get("current_stock") or 0)
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setForeground(QColor("#1976D2"))
            self.inventory_table.setItem(row, 1, qty_item)
            
            # Stock Value (green)
            value = float(r.get("stock_value") or 0)
            total_value += value
            value_item = QTableWidgetItem(f"${value:,.2f}")
            value_item.setForeground(QColor("#2E7D32"))
            self.inventory_table.setItem(row, 2, value_item)
            
            # Variance (color-coded)
            variance = int(r.get("variance") or 0)
            var_item = QTableWidgetItem("")
            if variance == 0:
                var_item.setForeground(QColor("#4CAF50"))
                var_item.setText("✓ OK")
            elif variance > 0:
                var_item.setForeground(QColor("#FF9800"))
                var_item.setText(f"⚠ +{variance}")
            else:
                var_item.setForeground(QColor("#F44336"))
                var_item.setText(f"⚠ {variance}")
            self.inventory_table.setItem(row, 3, var_item)
            
            # Category
            self.inventory_table.setItem(row, 4, QTableWidgetItem(str(r.get("category", ""))))
            
            # Alternate row colors
            if row % 2 == 0:
                for col in range(self.inventory_table.columnCount()):
                    if self.inventory_table.item(row, col):
                        self.inventory_table.item(row, col).setBackground(QColor("#f9f9f9"))
        
        # Add total row
        if self.inventory_table.rowCount() > 0:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem("📊 TOTAL"))
            total_item = QTableWidgetItem(f"${total_value:,.2f}")
            total_item.setForeground(QColor("#1565C0"))
            total_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.inventory_table.setItem(row, 2, total_item)

    def on_month_changed(self, month):
        self.month_year = month
        self.selected_date = None  # Reset date on month change
        self.load_and_render()

    def on_back_clicked(self):
        self.close()

    def on_date_clicked(self, date_str):
        """Call this when calendar date is picked, with format YYYY-MM-DD."""
        self.selected_date = date_str
        self.load_and_render()