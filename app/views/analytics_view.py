from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QDateEdit, QPushButton
from PySide6.QtCore import QDate, Qt
from PySide6.QtCharts import QChartView, QChart, QBarSeries, QBarSet, QPieSeries, QLineSeries, QValueAxis
import datetime

class AnalyticsView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        v = QVBoxLayout(self)
        v.setSpacing(20)
        page_title = QLabel("Reports")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Sales analytics and revenue insights")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)
        self.tabs = QTabWidget()
        v.addWidget(self.tabs, 1)
        self._setup_daily()
        self._setup_weekly()
        self._setup_monthly()

    def _setup_daily(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        filter_bar = QHBoxLayout()
        self.daily_date = QDateEdit()
        self.daily_date.setDate(QDate.currentDate())
        self.daily_refresh = QPushButton("Refresh")
        filter_bar.addWidget(QLabel("Date"))
        filter_bar.addWidget(self.daily_date)
        filter_bar.addWidget(self.daily_refresh)
        layout.addLayout(filter_bar)
        self.daily_chart = QChartView()
        layout.addWidget(self.daily_chart, 1)
        self.daily_refresh.clicked.connect(self._refresh_daily)
        self.tabs.addTab(w, "Daily")
        self._refresh_daily()

    def _setup_weekly(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        self.weekly_chart = QChartView()
        layout.addWidget(self.weekly_chart, 1)
        self.tabs.addTab(w, "Weekly")
        self._refresh_weekly()

    def _setup_monthly(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        self.monthly_chart = QChartView()
        layout.addWidget(self.monthly_chart, 1)
        self.tabs.addTab(w, "Monthly")
        self._refresh_monthly()

    def _refresh_daily(self):
        date = self.daily_date.date().toPython()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT MenuItems.category AS cat, SUM(OrderDetails.qty*OrderDetails.price) AS amt
            FROM Payments 
            JOIN Orders ON Payments.order_id=Orders.id
            JOIN OrderDetails ON OrderDetails.order_id=Orders.id
            JOIN MenuItems ON OrderDetails.item_id=MenuItems.id
            WHERE DATE(Payments.paid_at)=DATE(?)
            GROUP BY cat
        """, (date.isoformat(),))
        series = QPieSeries()
        for r in cur.fetchall():
            series.append(r["cat"], float(r["amt"] or 0))
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Category-wise revenue")
        self.daily_chart.setChart(chart)

    def _refresh_weekly(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        start = datetime.date.today() - datetime.timedelta(days=6)
        series = QBarSeries()
        s = QBarSet("Orders")
        for i in range(7):
            day = start + datetime.timedelta(days=i)
            cur.execute("SELECT COUNT(*) AS c FROM Orders WHERE DATE(created_at)=DATE(?)", (day.isoformat(),))
            s.append(float(cur.fetchone()["c"]))
        series.append(s)
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Orders per day")
        axis_x = QValueAxis()
        axis_x.setRange(0,6)
        axis_y = QValueAxis()
        axis_y.setRange(0, max([s.at(i) for i in range(s.count())] + [5]))
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        self.weekly_chart.setChart(chart)

    def _refresh_monthly(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        series = QLineSeries()
        for d in range(1, 31):
            cur.execute("""
                SELECT COALESCE(SUM(amount+gst),0) AS s 
                FROM Payments 
                WHERE strftime('%Y-%m',paid_at)=strftime('%Y-%m','now') AND CAST(strftime('%d',paid_at) AS INTEGER)=?
            """, (d,))
            val = cur.fetchone()["s"] or 0
            series.append(d, float(val))
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Monthly revenue")
        axis_x = QValueAxis()
        axis_x.setRange(1, 31)
        axis_y = QValueAxis()
        axis_y.setRange(0, max([p.y() for p in series.pointsVector()] + [1000]))
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        self.monthly_chart.setChart(chart)
