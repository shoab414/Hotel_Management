from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QPushButton, QFrame
from PySide6.QtCore import QTimer, Qt, QDate
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
import datetime

class DashboardView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.cards = {}
        v = QVBoxLayout(self)
        v.setSpacing(24)

        page_title = QLabel("Dashboard")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Overview of your operations")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)

        # Stats row - 5 compact cards in one line
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        for name in ["Today Sales", "Weekly Sales", "Monthly Sales", "Active Orders", "Room Occupancy"]:
            card = QFrame()
            card.setObjectName("StatCard")
            card.setFixedHeight(90)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 12, 16, 12)
            card_layout.setSpacing(4)
            title = QLabel(name)
            lbl = QLabel("0")
            lbl.setObjectName("StatValue")
            card_layout.addWidget(title)
            card_layout.addWidget(lbl)
            stats_row.addWidget(card, 1)
            self.cards[name] = lbl
        v.addLayout(stats_row)

        # Chart - main focus
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(320)
        v.addWidget(self.chart_view, 1)

        # Quick access - 2 rows of 3
        quick_grid = QGridLayout()
        quick_grid.setSpacing(12)
        self.btn_rooms = QPushButton("Rooms")
        self.btn_reservations = QPushButton("Reservations")
        self.btn_pos = QPushButton("Restaurant")
        self.btn_billing = QPushButton("Billing")
        self.btn_inventory = QPushButton("Inventory")
        self.btn_reports = QPushButton("Reports")
        buttons = [
            (self.btn_rooms, 0, 0), (self.btn_reservations, 0, 1), (self.btn_pos, 0, 2),
            (self.btn_billing, 1, 0), (self.btn_inventory, 1, 1), (self.btn_reports, 1, 2),
        ]
        for b, row, col in buttons:
            b.setObjectName("TileButton")
            b.setFixedHeight(48)
            quick_grid.addWidget(b, row, col)
        v.addLayout(quick_grid)
        self.timer = QTimer(self)
        self.timer.setInterval(3000)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.timer.start()
        self.btn_rooms.clicked.connect(lambda: self.controller.main_window._switch(1))
        self.btn_reservations.clicked.connect(lambda: self.controller.main_window._switch(1))
        self.btn_pos.clicked.connect(lambda: self.controller.main_window._switch(2))
        self.btn_billing.clicked.connect(lambda: self.controller.main_window._switch(3))
        self.btn_inventory.clicked.connect(lambda: self.controller.main_window._switch(4))
        self.btn_reports.clicked.connect(lambda: self.controller.main_window._switch(5))

    def refresh(self):
        db = self.controller.db
        conn = db.connect()
        cur = conn.cursor()
        today = datetime.date.today().isoformat()
        cur.execute("SELECT COALESCE(SUM(amount+gst),0) AS s FROM Payments WHERE DATE(paid_at)=DATE(?)", (today,))
        self.cards["Today Sales"].setText(f"₹{cur.fetchone()['s']:.2f}")
        cur.execute("SELECT COALESCE(SUM(amount+gst),0) AS s FROM Payments WHERE DATE(paid_at)>=DATE(?)", ((datetime.date.today()-datetime.timedelta(days=7)).isoformat(),))
        self.cards["Weekly Sales"].setText(f"₹{cur.fetchone()['s']:.2f}")
        cur.execute("SELECT COALESCE(SUM(amount+gst),0) AS s FROM Payments WHERE strftime('%Y-%m',paid_at)=strftime('%Y-%m','now')")
        self.cards["Monthly Sales"].setText(f"₹{cur.fetchone()['s']:.2f}")
        cur.execute("SELECT COUNT(*) AS c FROM Orders WHERE status IN ('Open','InKitchen','Served')")
        self.cards["Active Orders"].setText(str(cur.fetchone()["c"]))
        cur.execute("SELECT COUNT(*) AS total, SUM(CASE WHEN status='Occupied' THEN 1 ELSE 0 END) AS occ FROM Rooms")
        r = cur.fetchone()
        occ = 0 if r["total"] == 0 else int((r["occ"] or 0)/r["total"]*100)
        self.cards["Room Occupancy"].setText(f"{occ}%")
        self._build_revenue_chart()

    def _build_revenue_chart(self):
        db = self.controller.db
        conn = db.connect()
        cur = conn.cursor()
        chart = QChart()
        series = QLineSeries()
        for i in range(0, 14):
            day = datetime.date.today() - datetime.timedelta(days=13-i)
            cur.execute("SELECT COALESCE(SUM(amount+gst),0) AS s FROM Payments WHERE DATE(paid_at)=DATE(?)", (day.isoformat(),))
            val = cur.fetchone()["s"] or 0
            series.append(i, float(val))
        chart.addSeries(series)
        axis_x = QValueAxis()
        axis_x.setRange(0, 13)
        axis_x.setTickCount(14)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        axis_y.setRange(0, max([p.y() for p in series.pointsVector()] + [1000]))
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        chart.setTitle("Revenue (Last 14 days)")
        self.chart_view.setChart(chart)
