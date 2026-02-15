from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
import datetime

class POSView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        v = QVBoxLayout(self)
        v.setSpacing(20)
        page_title = QLabel("Restaurant POS")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Point of sale for table and room orders")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)
        top = QHBoxLayout()
        top.setSpacing(16)
        top.addWidget(QLabel("Order for"))
        self.order_type = QComboBox()
        self.order_type.addItems(["Table", "Room Guest"])
        self.order_type.setMinimumWidth(120)
        self.order_type.currentTextChanged.connect(self._on_order_type_changed)
        top.addWidget(self.order_type)
        self.lbl_tables = QLabel("Table")
        top.addWidget(self.lbl_tables)
        self.tables = QListWidget()
        self.tables.setMinimumWidth(180)
        top.addWidget(self.tables, 1)
        self.lbl_guest = QLabel("Guest")
        self.room_guests = QComboBox()
        self.room_guests.setMinimumWidth(200)
        self.room_guests.addItem("— Select guest —", None)
        top.addWidget(self.lbl_guest)
        top.addWidget(self.room_guests)
        top.addWidget(QLabel("Category"))
        self.categories = QComboBox()
        self.categories.addItems(["All","Starter","Main","Dessert"])
        self.categories.setMinimumWidth(140)
        top.addWidget(self.categories)
        v.addLayout(top)
        mid = QHBoxLayout()
        mid.setSpacing(16)
        self.menu = QTableWidget(0,3)
        self.menu.setHorizontalHeaderLabels(["Item","Category","Price"])
        self.cart = QTableWidget(0,3)
        self.cart.setHorizontalHeaderLabels(["Item","Qty","Price"])
        self.cart.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        mid.addWidget(self.menu,2)
        mid.addWidget(self.cart,1)
        v.addLayout(mid)
        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        self.btn_add = QPushButton("Add to Cart")
        self.btn_open = QPushButton("Open Order")
        self.btn_kitchen = QPushButton("Send to Kitchen")
        self.btn_pay = QPushButton("Pay")
        self.btn_pay.setObjectName("PrimaryButton")
        self.btn_bill = QPushButton("Generate Bill")
        self.total_lbl = QLabel("Total: ₹0.00")
        bottom.addWidget(self.btn_add)
        bottom.addWidget(self.btn_open)
        bottom.addWidget(self.btn_kitchen)
        bottom.addWidget(self.btn_pay)
        bottom.addWidget(self.btn_bill)
        bottom.addWidget(self.total_lbl)
        v.addLayout(bottom)

        self.categories.currentTextChanged.connect(self.load_menu)
        self.btn_add.clicked.connect(self.add_to_cart)
        self.btn_open.clicked.connect(self.open_order)
        self.btn_kitchen.clicked.connect(self.send_kitchen)
        self.btn_pay.clicked.connect(self.pay)
        self.btn_bill.clicked.connect(self.generate_bill)
        self.current_order_id = None
        self.load_tables()
        self.load_room_guests()
        self.load_menu()
        self._on_order_type_changed("Table")

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.load_tables()
        self.load_room_guests()

    def _on_order_type_changed(self, text):
        is_table = text == "Table"
        self.tables.setVisible(is_table)
        self.lbl_tables.setVisible(is_table)
        self.room_guests.setVisible(not is_table)
        self.lbl_guest.setVisible(not is_table)

    def load_tables(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT number, status FROM Tables ORDER BY number")
        self.tables.clear()
        for r in cur.fetchall():
            self.tables.addItem(f"Table {r['number']} ({r['status']})")

    def load_room_guests(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id AS cust_id, c.name AS name, rm.number AS room
            FROM Customers c
            JOIN Reservations r ON r.customer_id = c.id AND r.status = 'CheckedIn'
            JOIN Rooms rm ON rm.id = r.room_id
            ORDER BY rm.number
        """)
        self.room_guests.clear()
        self.room_guests.addItem("— Select guest —", None)
        for r in cur.fetchall():
            self.room_guests.addItem(f"{r['name']} (Room {r['room']})", r["cust_id"])

    def load_menu(self):
        cat = self.categories.currentText()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        if cat == "All":
            cur.execute("SELECT name, category, price FROM MenuItems WHERE active=1 ORDER BY category,name")
        else:
            cur.execute("SELECT name, category, price FROM MenuItems WHERE active=1 AND category=? ORDER BY name", (cat,))
        rows = cur.fetchall()
        self.menu.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.menu.setItem(i,0,QTableWidgetItem(r["name"]))
            self.menu.setItem(i,1,QTableWidgetItem(r["category"]))
            self.menu.setItem(i,2,QTableWidgetItem(f"{r['price']:.2f}"))

    def add_to_cart(self):
        row = self.menu.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a menu item to add.")
            return
        item = self.menu.item(row,0).text()
        price = float(self.menu.item(row,2).text())
        qty = 1
        self.cart.insertRow(self.cart.rowCount())
        self.cart.setItem(self.cart.rowCount()-1,0,QTableWidgetItem(item))
        self.cart.setItem(self.cart.rowCount()-1,1,QTableWidgetItem(str(qty)))
        self.cart.setItem(self.cart.rowCount()-1,2,QTableWidgetItem(f"{price:.2f}"))
        self.update_total()

    def update_total(self):
        total = 0.0
        for i in range(self.cart.rowCount()):
            qty = int(self.cart.item(i,1).text())
            price = float(self.cart.item(i,2).text())
            total += qty*price
        gst = round(total*0.18,2)
        self.total_lbl.setText(f"Total: ₹{total+gst:.2f} (GST ₹{gst:.2f})")

    def open_order(self):
        if self.cart.rowCount() == 0:
            QMessageBox.warning(self, "Cart", "Add items to cart first.")
            return
        conn = self.controller.db.connect()
        cur = conn.cursor()
        table_id = None
        customer_id = None
        if self.order_type.currentText() == "Table":
            if self.tables.currentRow() < 0:
                QMessageBox.warning(self, "Selection", "Please select a table.")
                return
            table_number = int(self.tables.currentItem().text().split()[1])
            cur.execute("SELECT id FROM Tables WHERE number=?", (table_number,))
            row = cur.fetchone()
            if not row:
                return
            table_id = row["id"]
            cur.execute("UPDATE Tables SET status='Occupied' WHERE id=?", (table_id,))
        else:
            customer_id = self.room_guests.currentData()
            if not customer_id:
                QMessageBox.warning(self, "Selection", "Please select a room guest.")
                return
        cur.execute("INSERT INTO Orders(table_id,customer_id,status,created_at) VALUES(?,?,?,?)",
                    (table_id, customer_id, "Open", datetime.datetime.now().isoformat()))
        self.current_order_id = cur.lastrowid
        for i in range(self.cart.rowCount()):
            name = self.cart.item(i,0).text()
            cur.execute("SELECT id, price FROM MenuItems WHERE name=?", (name,))
            item = cur.fetchone()
            cur.execute("INSERT INTO OrderDetails(order_id,item_id,qty,price,kitchen_status) VALUES(?,?,?,?,?)",
                        (self.current_order_id, item["id"], int(self.cart.item(i,1).text()), item["price"], "Pending"))
        conn.commit()
        self.load_tables()
        self.load_room_guests()
        QMessageBox.information(self, "Order", f"Order #{self.current_order_id} created.")

    def send_kitchen(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Order", "Open an order first.")
            return
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("UPDATE Orders SET status='InKitchen' WHERE id=?", (self.current_order_id,))
        cur.execute("UPDATE OrderDetails SET kitchen_status='Cooking' WHERE order_id=?", (self.current_order_id,))
        conn.commit()

    def pay(self):
        if not self.current_order_id:
            QMessageBox.warning(self, "Order", "Open an order first.")
            return
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT table_id FROM Orders WHERE id=?", (self.current_order_id,))
        row = cur.fetchone()
        table_id = row["table_id"] if row else None
        cur.execute("SELECT SUM(qty*price) AS amt FROM OrderDetails WHERE order_id=?", (self.current_order_id,))
        amt = cur.fetchone()["amt"] or 0
        gst = round(amt*0.18,2)
        cur.execute("INSERT INTO Payments(order_id,amount,gst,method,paid_at) VALUES(?,?,?,?,?)",
                    (self.current_order_id, amt, gst, "Cash", datetime.datetime.now().isoformat()))
        cur.execute("UPDATE Orders SET status='Paid' WHERE id=?", (self.current_order_id,))
        if table_id:
            cur.execute("UPDATE Tables SET status='Available' WHERE id=?", (table_id,))
        conn.commit()
        self.current_order_id = None
        self.cart.setRowCount(0)
        self.update_total()
        self.load_tables()
        QMessageBox.information(self, "Payment", "Payment completed.")

    def generate_bill(self):
        """Generate invoice PDF for current order, or switch to Billing if none."""
        if self.current_order_id:
            from PySide6.QtGui import QTextDocument
            from PySide6.QtPrintSupport import QPrinter
            import os
            oid = self.current_order_id
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("SELECT MenuItems.name AS name, OrderDetails.qty AS qty, OrderDetails.price AS price FROM OrderDetails JOIN MenuItems ON OrderDetails.item_id=MenuItems.id WHERE order_id=?", (oid,))
            items = cur.fetchall()
            cur.execute("SELECT COALESCE(SUM(qty*price),0) AS amt FROM OrderDetails WHERE order_id=?", (oid,))
            amt = float(cur.fetchone()["amt"] or 0)
            gst = round(amt*0.18,2)
            total = amt + gst
            html = "<h2>Restaurant Bill</h2>"
            html += f"<p>Order #{oid} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"
            html += "<table border='1' cellspacing='0' cellpadding='4'><tr><th>Item</th><th>Qty</th><th>Price</th></tr>"
            for it in items:
                html += f"<tr><td>{it['name']}</td><td>{it['qty']}</td><td>₹{it['price']:.2f}</td></tr>"
            html += "</table>"
            html += f"<p>Subtotal: ₹{amt:.2f}</p><p>GST (18%): ₹{gst:.2f}</p><h3>Total: ₹{total:.2f}</h3>"
            doc = QTextDocument()
            doc.setHtml(html)
            pdf_path = os.path.join(os.getcwd(), f"bill_order_{oid}.pdf")
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(pdf_path)
            doc.print(printer)
            QMessageBox.information(self, "Bill", f"Bill saved as bill_order_{oid}.pdf")
            self.controller.main_window._switch(3)
            self.controller.main_window.page_billing.refresh()
        else:
            self.controller.main_window._switch(3)
