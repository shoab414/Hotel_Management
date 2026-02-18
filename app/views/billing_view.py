from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
import datetime
import os

class BillingView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        v = QVBoxLayout(self)
        v.setSpacing(20)
        page_title = QLabel("Billing")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("View paid orders and invoices")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)
        
        # Top bar with refresh
        top = QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(QLabel("Payment method"))
        self.method = QComboBox()
        self.method.addItems(["Cash","Card","UPI"])
        self.method.setMinimumWidth(120)
        top.addWidget(self.method)
        self.btn_refresh = QPushButton("Refresh")
        top.addWidget(self.btn_refresh)
        top.addStretch()
        v.addLayout(top)
        
        # Orders table with Date, Items, Actions
        self.orders = QTableWidget(0, 6)
        self.orders.setHorizontalHeaderLabels(["Payment ID", "Order ID", "Table", "Date", "Items", "Action"])
        self.orders.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.orders.setColumnWidth(4, 300)
        v.addWidget(self.orders)
        
        self.btn_refresh.clicked.connect(self.refresh)
        self.refresh()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        """Load all paid orders with payment information"""
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                Payments.id AS payment_id,
                Orders.id AS order_id,
                COALESCE(Tables.number, 'N/A') AS table_num,
                Payments.paid_at AS payment_date,
                Payments.amount,
                Payments.gst
            FROM Payments
            JOIN Orders ON Payments.order_id = Orders.id
            LEFT JOIN Tables ON Orders.table_id = Tables.id
            ORDER BY Payments.paid_at DESC
        """)
        payments = cur.fetchall()
        self.orders.setRowCount(len(payments))
        
        for i, p in enumerate(payments):
            # Payment ID
            self.orders.setItem(i, 0, QTableWidgetItem(str(p["payment_id"])))
            # Order ID
            self.orders.setItem(i, 1, QTableWidgetItem(str(p["order_id"])))
            # Table
            self.orders.setItem(i, 2, QTableWidgetItem(str(p["table_num"])))
            # Date
            self.orders.setItem(i, 3, QTableWidgetItem(p["payment_date"]))
            
            # Get items for this order
            cur.execute("""
                SELECT MenuItems.name, OrderDetails.qty
                FROM OrderDetails
                JOIN MenuItems ON OrderDetails.item_id = MenuItems.id
                WHERE OrderDetails.order_id = ?
            """, (p["order_id"],))
            items = cur.fetchall()
            items_text = ", ".join([f"{item['name']} x{item['qty']}" for item in items])
            self.orders.setItem(i, 4, QTableWidgetItem(items_text))
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, pid=p["payment_id"]: self.delete_payment(pid))
            self.orders.setCellWidget(i, 5, delete_btn)

    def delete_payment(self, payment_id):
        """Delete a payment record"""
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this payment record?")
        if reply != QMessageBox.Yes:
            return
        
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        # Get order_id before deleting payment
        cur.execute("SELECT order_id FROM Payments WHERE id=?", (payment_id,))
        result = cur.fetchone()
        if not result:
            QMessageBox.warning(self, "Error", "Payment not found.")
            return
        
        order_id = result["order_id"]
        
        # Delete payment record
        cur.execute("DELETE FROM Payments WHERE id=?", (payment_id,))
        
        # Reset order status to Served (not Paid)
        cur.execute("UPDATE Orders SET status='Served' WHERE id=?", (order_id,))
        
        conn.commit()
        self.refresh()
        QMessageBox.information(self, "Success", "Payment record deleted.")
