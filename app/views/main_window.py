import logging
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from app.utils.theme import ThemeManager
from .dashboard_view import DashboardView
from .hotel_view import HotelView

from .inventory_view import InventoryView
from .analytics_view import AnalyticsView
from .billing_view import BillingView
from .table_view import TableView
from .guest_view import GuestView
from .menu_management_view import MenuManagementView

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Hotel & Restaurant Management")
        self.resize(1280, 850)
        self.theme = ThemeManager(self.controller.app)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        self.stack = QStackedWidget()
        content_wrap = QWidget()
        content_wrap.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.addWidget(self.stack, 1)
        wrap = QWidget()
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar)
        layout.addWidget(content_wrap, 1)
        self.setCentralWidget(wrap)
        self._build_sidebar()
        self._build_pages()

    def _build_sidebar(self):
        v = QVBoxLayout(self.sidebar)
        v.setContentsMargins(20, 24, 20, 24)
        v.setSpacing(4)
        title = QLabel("Hotel Suite")
        title.setObjectName("SidebarTitle")
        subtitle = QLabel("Management System")
        subtitle.setObjectName("SidebarSubtitle")
        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(28)
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_hotel = QPushButton("Hotel")
        self.btn_tables = QPushButton("Tables")
        self.btn_guests = QPushButton("Guests")
        self.btn_billing = QPushButton("Billing")
        self.btn_inventory = QPushButton("Inventory")
        self.btn_menu_management = QPushButton("Menu")
        self.btn_reports = QPushButton("Reports")
        self.btn_theme = QPushButton("Toggle Theme")
        self.btn_theme.setObjectName("ThemeButton")
        for b in [self.btn_dashboard, self.btn_hotel, self.btn_tables, self.btn_guests, self.btn_billing, self.btn_inventory, self.btn_menu_management, self.btn_reports]:
            b.setCheckable(True)
            b.setObjectName("NavButton")
            v.addWidget(b)
        v.addStretch(1)
        v.addWidget(self.btn_theme)
        self.btn_dashboard.clicked.connect(lambda: self._switch(0))
        self.btn_hotel.clicked.connect(lambda: self._switch(1))
        self.btn_tables.clicked.connect(lambda: self._switch(2))
        self.btn_guests.clicked.connect(lambda: self._switch(3))
        self.btn_billing.clicked.connect(lambda: self._switch(4))
        self.btn_inventory.clicked.connect(lambda: self._switch(5))
        self.btn_menu_management.clicked.connect(lambda: self._switch(6))
        self.btn_reports.clicked.connect(lambda: self._switch(7))
        self.btn_theme.clicked.connect(self._toggle_theme)
        self.btn_dashboard.setChecked(True)

    def _build_pages(self):
        self.page_dashboard = DashboardView(self.controller)
        self.page_hotel = HotelView(self.controller)
        self.page_tables = TableView(self.controller)
        self.page_guests = GuestView(self.controller)
        self.page_billing = BillingView(self.controller)
        self.page_inventory = InventoryView(self.controller)
        self.page_menu_management = MenuManagementView(self.controller)
        self.page_reports = AnalyticsView(self.controller)
        for p in [self.page_dashboard, self.page_hotel, self.page_tables, self.page_guests, self.page_billing, self.page_inventory, self.page_menu_management, self.page_reports]:
            self.stack.addWidget(p)

    def _switch(self, index):
        old = self.stack.currentIndex()
        self.stack.setCurrentIndex(index)
        current_widget = self.stack.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
        self._animate_transition(old, index)
        for i, b in enumerate([self.btn_dashboard, self.btn_hotel, self.btn_tables, self.btn_guests, self.btn_billing, self.btn_inventory, self.btn_menu_management, self.btn_reports]):
            b.setChecked(i == index)

    def _animate_transition(self, old, new):
        w = self.stack.currentWidget()
        anim = QPropertyAnimation(w, b"geometry")
        start_rect = QRect(w.x()+20, w.y(), w.width(), w.height())
        anim.setStartValue(start_rect)
        anim.setEndValue(QRect(w.x(), w.y(), w.width(), w.height()))
        anim.setDuration(180)
        anim.start()

    def _toggle_theme(self):
        is_dark = self.controller.app.property("dark_mode")
        if is_dark:
            self.theme.apply_light()
        else:
            self.theme.apply_dark()
