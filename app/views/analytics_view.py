from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QLabel, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QDate, Qt
from app.utils.calendar_icon import apply_calendar_icon
from PySide6.QtCharts import QChartView, QChart, QBarSeries, QBarSet, QPieSeries, QLineSeries, QValueAxis, QBarCategoryAxis
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
        self._setup_dishes()
        self._setup_hotel_report()
        self._setup_guest_report()

    def _setup_daily(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        filter_bar = QHBoxLayout()
        self.daily_date = QDateEdit()
        self.daily_date.setCalendarPopup(True)
        self.daily_date.setDisplayFormat('yyyy-MM-dd')
        self.daily_date.setDate(QDate.currentDate())
        self.daily_date.setMinimumWidth(140)
        self.daily_date.setToolTip("Click the calendar icon to select date")
        apply_calendar_icon(self.daily_date)
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

    def _setup_dishes(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        filter_bar = QHBoxLayout()
        self.dishes_date = QDateEdit()
        self.dishes_date.setCalendarPopup(True)
        self.dishes_date.setDisplayFormat('yyyy-MM-dd')
        self.dishes_date.setDate(QDate.currentDate())
        self.dishes_date.setMinimumWidth(140)
        self.dishes_date.setToolTip("Click the calendar icon to select date")
        apply_calendar_icon(self.dishes_date)
        filter_bar.addWidget(QLabel("Date:"))
        filter_bar.addWidget(self.dishes_date)
        self.dishes_refresh = QPushButton("Refresh")
        filter_bar.addWidget(QLabel("Most Ordered Dishes"))
        filter_bar.addWidget(self.dishes_refresh)
        filter_bar.addStretch()
        layout.addLayout(filter_bar)

        # Table for dishes: Rank, Dish, Times Ordered
        self.dishes_table = QTableWidget(0, 3)
        self.dishes_table.setHorizontalHeaderLabels(["Rank", "Dish", "Times Ordered"])
        layout.addWidget(self.dishes_table, 1)

        self.dishes_refresh.clicked.connect(self._refresh_dishes)
        self.dishes_date.dateChanged.connect(self._refresh_dishes)
        self.tabs.addTab(w, "Dishes")
        self._refresh_dishes()

    def _refresh_daily(self):
        date = self.daily_date.date().toPython()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT MenuItems.category AS cat, SUM(OrderDetails.qty*OrderDetails.price) AS amt
            FROM Orders
            JOIN OrderDetails ON OrderDetails.order_id=Orders.id
            JOIN MenuItems ON OrderDetails.item_id=MenuItems.id
            WHERE Orders.status='Paid' AND DATE(Orders.created_at)=DATE(?)
            GROUP BY cat
        """, (date.isoformat(),))
        series = QPieSeries()
        rows = cur.fetchall()
        if rows:
            for r in rows:
                series.append(r["cat"] or "Uncategorized", float(r["amt"] or 0))
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
                SELECT COALESCE(SUM(OrderDetails.qty*OrderDetails.price),0) AS s 
                FROM Orders
                JOIN OrderDetails ON OrderDetails.order_id=Orders.id
                WHERE Orders.status='Paid' AND strftime('%Y-%m',Orders.created_at)=strftime('%Y-%m','now') AND CAST(strftime('%d',Orders.created_at) AS INTEGER)=?
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

    def _refresh_dishes(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        # Filter by selected date (per-day counts)
        sel_date = self.dishes_date.date().toPython()
        cur.execute("""
            SELECT MenuItems.name, SUM(OrderDetails.qty) AS total_qty
            FROM Orders
            JOIN OrderDetails ON OrderDetails.order_id=Orders.id
            JOIN MenuItems ON OrderDetails.item_id=MenuItems.id
            WHERE Orders.status='Paid' AND DATE(Orders.created_at)=DATE(?)
            GROUP BY MenuItems.id, MenuItems.name
            ORDER BY total_qty DESC
            LIMIT 100
        """, (sel_date.isoformat(),))
        rows = cur.fetchall()

        # Populate table
        self.dishes_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            rank_item = QTableWidgetItem(str(i+1))
            name_item = QTableWidgetItem(r["name"])
            times_item = QTableWidgetItem(str(r["total_qty"] or 0))
            self.dishes_table.setItem(i, 0, rank_item)
            self.dishes_table.setItem(i, 1, name_item)
            self.dishes_table.setItem(i, 2, times_item)
        if not rows:
            # show a single row with 'No data'
            self.dishes_table.setRowCount(1)
            self.dishes_table.setItem(0, 0, QTableWidgetItem("-"))
            self.dishes_table.setItem(0, 1, QTableWidgetItem("No data for selected date"))
            self.dishes_table.setItem(0, 2, QTableWidgetItem("0"))
    def _setup_hotel_report(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        
        # Date range filter
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("From:"))
        self.hotel_date_from = QDateEdit()
        self.hotel_date_from.setCalendarPopup(True)
        self.hotel_date_from.setDisplayFormat('yyyy-MM-dd')
        self.hotel_date_from.setDate(QDate.currentDate().addDays(-30))
        self.hotel_date_from.setMinimumWidth(140)
        apply_calendar_icon(self.hotel_date_from)
        filter_bar.addWidget(self.hotel_date_from)
        
        filter_bar.addWidget(QLabel("To:"))
        self.hotel_date_to = QDateEdit()
        self.hotel_date_to.setCalendarPopup(True)
        self.hotel_date_to.setDisplayFormat('yyyy-MM-dd')
        self.hotel_date_to.setDate(QDate.currentDate())
        self.hotel_date_to.setMinimumWidth(140)
        apply_calendar_icon(self.hotel_date_to)
        filter_bar.addWidget(self.hotel_date_to)
        
        self.hotel_refresh = QPushButton("Refresh")
        filter_bar.addWidget(self.hotel_refresh)
        filter_bar.addStretch()
        layout.addLayout(filter_bar)
        
        # Hotel statistics table
        self.hotel_stats_table = QTableWidget(0, 6)
        self.hotel_stats_table.setHorizontalHeaderLabels(["Room Number", "Category", "Reservations", "Revenue (₹)", "Occupancy %", "Status"])
        self.hotel_stats_table.setMaximumHeight(300)
        layout.addWidget(QLabel("Room-wise Report"))
        layout.addWidget(self.hotel_stats_table)
        
        # Summary info
        self.hotel_summary_layout = QHBoxLayout()
        self.hotel_total_revenue = QLabel("Total Hotel Revenue: ₹0.00")
        self.hotel_total_revenue.setObjectName("StatValue")
        self.hotel_occupancy_rate = QLabel("Average Occupancy: 0%")
        self.hotel_occupancy_rate.setObjectName("StatValue")
        self.hotel_total_reservations = QLabel("Total Reservations: 0")
        self.hotel_total_reservations.setObjectName("StatValue")
        
        self.hotel_summary_layout.addWidget(self.hotel_total_revenue)
        self.hotel_summary_layout.addWidget(self.hotel_occupancy_rate)
        self.hotel_summary_layout.addWidget(self.hotel_total_reservations)
        self.hotel_summary_layout.addStretch()
        layout.addLayout(self.hotel_summary_layout)
        
        self.hotel_refresh.clicked.connect(self._refresh_hotel_report)
        self.hotel_date_from.dateChanged.connect(self._refresh_hotel_report)
        self.hotel_date_to.dateChanged.connect(self._refresh_hotel_report)
        self.tabs.addTab(w, "Hotel Report")
        self._refresh_hotel_report()

    def _setup_guest_report(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        
        # Date range filter
        filter_bar = QHBoxLayout()
        filter_bar.addWidget(QLabel("From:"))
        self.guest_date_from = QDateEdit()
        self.guest_date_from.setCalendarPopup(True)
        self.guest_date_from.setDisplayFormat('yyyy-MM-dd')
        self.guest_date_from.setDate(QDate.currentDate().addDays(-30))
        self.guest_date_from.setMinimumWidth(140)
        apply_calendar_icon(self.guest_date_from)
        filter_bar.addWidget(self.guest_date_from)
        
        filter_bar.addWidget(QLabel("To:"))
        self.guest_date_to = QDateEdit()
        self.guest_date_to.setCalendarPopup(True)
        self.guest_date_to.setDisplayFormat('yyyy-MM-dd')
        self.guest_date_to.setDate(QDate.currentDate())
        self.guest_date_to.setMinimumWidth(140)
        apply_calendar_icon(self.guest_date_to)
        filter_bar.addWidget(self.guest_date_to)
        
        self.guest_refresh = QPushButton("Refresh")
        filter_bar.addWidget(self.guest_refresh)
        filter_bar.addStretch()
        layout.addLayout(filter_bar)
        
        # Guest details table
        self.guest_table = QTableWidget(0, 8)
        self.guest_table.setHorizontalHeaderLabels(["Guest Name", "Phone", "Email", "Document Type", "Document Number", "Check-in", "Check-out", "Room"])
        layout.addWidget(QLabel("Guest Check-in Report"))
        layout.addWidget(self.guest_table, 1)
        
        # Summary info
        self.guest_summary_layout = QHBoxLayout()
        self.guest_total_checkins = QLabel("Total Check-ins: 0")
        self.guest_total_checkins.setObjectName("StatValue")
        self.guest_verified = QLabel("Document Verified: 0")
        self.guest_verified.setObjectName("StatValue")
        self.guest_avg_stay = QLabel("Average Stay: 0 days")
        self.guest_avg_stay.setObjectName("StatValue")
        
        self.guest_summary_layout.addWidget(self.guest_total_checkins)
        self.guest_summary_layout.addWidget(self.guest_verified)
        self.guest_summary_layout.addWidget(self.guest_avg_stay)
        self.guest_summary_layout.addStretch()
        layout.addLayout(self.guest_summary_layout)
        
        self.guest_refresh.clicked.connect(self._refresh_guest_report)
        self.guest_date_from.dateChanged.connect(self._refresh_guest_report)
        self.guest_date_to.dateChanged.connect(self._refresh_guest_report)
        self.tabs.addTab(w, "Guest Report")
        self._refresh_guest_report()

    def _refresh_hotel_report(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        date_from = self.hotel_date_from.date().toString('yyyy-MM-dd')
        date_to = self.hotel_date_to.date().toString('yyyy-MM-dd')
        
        # Get all rooms with their reservation and revenue data
        cur.execute("""
            SELECT r.id, r.number, r.category, r.status, r.rate,
                   COUNT(DISTINCT res.id) as reservation_count,
                   COALESCE(SUM(Payments.amount + Payments.gst), 0) as total_revenue
            FROM Rooms r
            LEFT JOIN Reservations res ON res.room_id = r.id 
                AND DATE(res.check_in) >= ? AND DATE(res.check_in) <= ?
            LEFT JOIN Payments ON Payments.reservation_id = res.id
            GROUP BY r.id, r.number, r.category, r.status, r.rate
            ORDER BY r.number
        """, (date_from, date_to))
        
        rooms = cur.fetchall()
        self.hotel_stats_table.setRowCount(len(rooms))
        
        total_revenue = 0
        total_reservations = 0
        total_days = (self.hotel_date_to.date().toPython() - self.hotel_date_from.date().toPython()).days + 1
        
        for i, room in enumerate(rooms):
            res_count = room['reservation_count'] or 0
            revenue = float(room['total_revenue'] or 0)
            total_revenue += revenue
            total_reservations += res_count
            
            # Calculate occupancy percentage
            occupancy = (res_count * 100 / total_days) if total_days > 0 else 0
            
            self.hotel_stats_table.setItem(i, 0, QTableWidgetItem(room['number']))
            self.hotel_stats_table.setItem(i, 1, QTableWidgetItem(room['category']))
            self.hotel_stats_table.setItem(i, 2, QTableWidgetItem(str(res_count)))
            self.hotel_stats_table.setItem(i, 3, QTableWidgetItem(f"₹{revenue:.2f}"))
            self.hotel_stats_table.setItem(i, 4, QTableWidgetItem(f"{occupancy:.1f}%"))
            self.hotel_stats_table.setItem(i, 5, QTableWidgetItem(room['status']))
        
        # Update summary
        total_occupancy = (total_reservations * 100 / (len(rooms) * total_days)) if (len(rooms) * total_days) > 0 else 0
        self.hotel_total_revenue.setText(f"Total Hotel Revenue: ₹{total_revenue:.2f}")
        self.hotel_occupancy_rate.setText(f"Average Occupancy: {total_occupancy:.1f}%")
        self.hotel_total_reservations.setText(f"Total Reservations: {total_reservations}")

    def _refresh_guest_report(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        date_from = self.guest_date_from.date().toString('yyyy-MM-dd')
        date_to = self.guest_date_to.date().toString('yyyy-MM-dd')
        
        # Get guest check-in details with document information
        cur.execute("""
            SELECT 
                c.name, c.phone, c.email, c.document_type, c.document_number,
                res.check_in, res.check_out, rm.number as room_number,
                CAST(JULIANDAY(COALESCE(res.check_out, 'now')) - JULIANDAY(res.check_in) AS INTEGER) as stay_days
            FROM Reservations res
            JOIN Customers c ON res.customer_id = c.id
            LEFT JOIN Rooms rm ON res.room_id = rm.id
            WHERE res.status IN ('CheckedIn', 'CheckedOut')
                AND DATE(res.check_in) >= ? AND DATE(res.check_in) <= ?
            ORDER BY res.check_in DESC
        """, (date_from, date_to))
        
        guests = cur.fetchall()
        self.guest_table.setRowCount(len(guests))
        
        total_guests = 0
        verified_guests = 0
        total_stay_days = 0
        
        for i, guest in enumerate(guests):
            total_guests += 1
            if guest['document_type'] and guest['document_number']:
                verified_guests += 1
            
            stay_days = guest['stay_days'] or 0
            total_stay_days += stay_days
            
            self.guest_table.setItem(i, 0, QTableWidgetItem(guest['name'] or ""))
            self.guest_table.setItem(i, 1, QTableWidgetItem(guest['phone'] or ""))
            self.guest_table.setItem(i, 2, QTableWidgetItem(guest['email'] or ""))
            self.guest_table.setItem(i, 3, QTableWidgetItem(guest['document_type'] or ""))
            self.guest_table.setItem(i, 4, QTableWidgetItem(guest['document_number'] or ""))
            self.guest_table.setItem(i, 5, QTableWidgetItem(guest['check_in'] or ""))
            self.guest_table.setItem(i, 6, QTableWidgetItem(guest['check_out'] or ""))
            self.guest_table.setItem(i, 7, QTableWidgetItem(guest['room_number'] or ""))
        
        # Update summary
        avg_stay = (total_stay_days / total_guests) if total_guests > 0 else 0
        self.guest_total_checkins.setText(f"Total Check-ins: {total_guests}")
        self.guest_verified.setText(f"Document Verified: {verified_guests}")
        self.guest_avg_stay.setText(f"Average Stay: {avg_stay:.1f} days")
        
        if not guests:
            self.guest_table.setRowCount(1)
            self.guest_table.setItem(0, 0, QTableWidgetItem("No data for selected date range"))
