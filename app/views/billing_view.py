from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView, QLineEdit, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
import datetime


class BillingView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        v = QVBoxLayout(self)
        v.setSpacing(12)
        page_title = QLabel("Billing")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("View paid orders and invoices")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)

        # Filter bar: search by Order ID and payment type
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(8)
        filter_bar.addWidget(QLabel("Order ID:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter order id...")
        self.search_input.setMaximumWidth(150)
        filter_bar.addWidget(self.search_input)

        filter_bar.addWidget(QLabel("Payment Type:"))
        self.method_filter = QComboBox()
        self.method_filter.addItems(["All","Cash","Card","UPI"])
        self.method_filter.setMaximumWidth(140)
        filter_bar.addWidget(self.method_filter)

        self.btn_refresh = QPushButton("Refresh")
        filter_bar.addWidget(self.btn_refresh)
        filter_bar.addStretch()
        v.addLayout(filter_bar)

        # Totals per payment type
        totals_bar = QHBoxLayout()
        totals_bar.setSpacing(12)
        self.total_cash_lbl = QLabel("Cash: ₹0.00")
        self.total_card_lbl = QLabel("Card: ₹0.00")
        self.total_upi_lbl = QLabel("UPI: ₹0.00")
        totals_bar.addWidget(self.total_cash_lbl)
        totals_bar.addWidget(self.total_card_lbl)
        totals_bar.addWidget(self.total_upi_lbl)
        totals_bar.addStretch()
        v.addLayout(totals_bar)

        # Orders table with Date, Method, Items, Actions
        self.orders = QTableWidget(0, 8)
        self.orders.setHorizontalHeaderLabels(["Payment ID", "Order ID", "Table", "Date", "Method", "Items", "Amount", "Action"])
        self.orders.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.orders.setColumnWidth(5, 320)
        self.orders.setColumnWidth(6, 120)
        v.addWidget(self.orders)

        # Connect signals
        self.btn_refresh.clicked.connect(self.refresh)
        self.search_input.returnPressed.connect(self.refresh)
        self.method_filter.currentTextChanged.connect(self.refresh)

        self.refresh()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        """Load all paid orders with payment information"""
        conn = self.controller.db.connect()
        cur = conn.cursor()
        # Build filtered query based on search and payment type
        base_q = """
            SELECT 
                Payments.id AS payment_id,
                Orders.id AS order_id,
                COALESCE(Tables.number, 'N/A') AS table_num,
                Payments.paid_at AS payment_date,
                Payments.amount,
                Payments.gst,
                Payments.method
            FROM Payments
            JOIN Orders ON Payments.order_id = Orders.id
            LEFT JOIN Tables ON Orders.table_id = Tables.id
        """

        where_clauses = []
        params = []
        search_text = (self.search_input.text() if hasattr(self, 'search_input') else "").strip()
        if search_text:
            # allow numeric order id search
            where_clauses.append("Orders.id = ?")
            try:
                params.append(int(search_text))
            except ValueError:
                params.append(search_text)

        payment_type = (self.method_filter.currentText() if hasattr(self, 'method_filter') else "All")
        if payment_type and payment_type != "All":
            where_clauses.append("Payments.method = ?")
            params.append(payment_type)

        if where_clauses:
            base_q += " WHERE " + " AND ".join(where_clauses)

        base_q += " ORDER BY Payments.paid_at DESC"
        cur.execute(base_q, tuple(params))
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
            # Method
            self.orders.setItem(i, 4, QTableWidgetItem(p["method"]))
            
            # Get items for this order
            cur.execute("""
                SELECT MenuItems.name, OrderDetails.qty
                FROM OrderDetails
                JOIN MenuItems ON OrderDetails.item_id = MenuItems.id
                WHERE OrderDetails.order_id = ?
            """, (p["order_id"],))
            items = cur.fetchall()
            items_text = ", ".join([f"{item['name']} x{item['qty']}" for item in items])
            self.orders.setItem(i, 5, QTableWidgetItem(items_text))
            
            # Amount (with GST)
            total = p["amount"] + p["gst"]
            self.orders.setItem(i, 6, QTableWidgetItem(f"₹{total:.2f}"))
            
            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, pid=p["payment_id"]: self.delete_payment(pid))
            self.orders.setCellWidget(i, 7, delete_btn)

        # Update totals per method (ignoring filters to show overall totals)
        try:
            cur.execute("SELECT method, COALESCE(SUM(amount+gst),0) AS total FROM Payments GROUP BY method")
            totals = {r['method']: r['total'] for r in cur.fetchall()}
            self.total_cash_lbl.setText(f"Cash: ₹{totals.get('Cash', 0.0):.2f}")
            self.total_card_lbl.setText(f"Card: ₹{totals.get('Card', 0.0):.2f}")
            self.total_upi_lbl.setText(f"UPI: ₹{totals.get('UPI', 0.0):.2f}")
        except Exception:
            # Fallback to zeroes
            self.total_cash_lbl.setText("Cash: ₹0.00")
            self.total_card_lbl.setText("Card: ₹0.00")
            self.total_upi_lbl.setText("UPI: ₹0.00")

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
