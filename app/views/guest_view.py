from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QTabWidget, QGridLayout, QMessageBox, QHeaderView, QListWidget, QListWidgetItem, QDoubleSpinBox
from PySide6.QtCore import Qt
import datetime
import logging
import csv, os
from app.utils.message import MessageBox # Assuming MessageBox is in utils
from .checkout_dialog import CheckoutDialog

class CustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer")
        f = QFormLayout(self)
        self.name = QLineEdit()
        self.phone = QLineEdit()
        self.email = QLineEdit()
        ok = QPushButton("Save")
        ok.clicked.connect(self.accept)
        f.addRow("Name", self.name)
        f.addRow("Phone", self.phone)
        f.addRow("Email", self.email)
        f.addRow(ok)

class CustomerCheckinDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Check-in")
        self.db = db
        self.all_rooms_occupied = False
        f = QFormLayout(self)
        self.room = QComboBox()
        self.room.setMinimumWidth(200)
        self.check_in = QLineEdit()
        self.check_out = QLineEdit()
        ok = QPushButton("Check-in")
        ok.clicked.connect(self.accept)
        f.addRow("Room", self.room)
        f.addRow("Check-in (YYYY-MM-DD)", self.check_in)
        f.addRow("Planned Check-out (YYYY-MM-DD)", self.check_out)
        f.addRow(ok)
        if db:
            self._load_available_rooms()

    def _load_available_rooms(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, number, category, rate FROM Rooms WHERE status='Available' ORDER BY number")
        self.room.clear()
        rows = cur.fetchall()
        if not rows:
            # No rooms available - provide an explicit waitlist/no-room option
            self.room.addItem("❌ No Room Available", None)
            self.all_rooms_occupied = True
            return
        self.all_rooms_occupied = False
        for r in rows:
            self.room.addItem(f"{r['number']} ({r['category']} - ₹{r['rate']:.0f})", r["id"])

class AddCustomerOrderDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.setWindowTitle("Add Customer Order")
        self.db = db
        self.selected_items = {} # {menu_item_id: quantity}
        self.menu_items_data = {} # {menu_item_id: {'name': name, 'price': price}}

        main_layout = QVBoxLayout(self)

        # Menu items list
        self.menu_list_widget = QListWidget()
        self.menu_list_widget.itemChanged.connect(self._update_total)
        main_layout.addWidget(self.menu_list_widget)

        # Total price display
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setObjectName("HeaderLabel") # For QSS styling
        main_layout.addWidget(self.total_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Order")
        self.add_button.setObjectName("PrimaryButton")
        self.add_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("SecondaryButton")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self._load_menu_items()

    def _load_menu_items(self):
        if not self.db:
            return
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price FROM MenuItems ORDER BY name")
        for item in cur.fetchall():
            item_id = item['id']
            item_name = item['name']
            item_price = item['price']
            self.menu_items_data[item_id] = {'name': item_name, 'price': item_price}

            list_item = QListWidgetItem(self.menu_list_widget)
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(f"{item_name} (₹{item_price:.2f})")
            quantity_spinbox = QSpinBox()
            quantity_spinbox.setMinimum(0)
            quantity_spinbox.setMaximum(99)
            quantity_spinbox.setValue(0)
            quantity_spinbox.valueChanged.connect(lambda value, item_id=item_id: self._on_quantity_changed(item_id, value))

            item_layout.addWidget(name_label)
            item_layout.addStretch()
            item_layout.addWidget(quantity_spinbox)

            list_item.setSizeHint(item_widget.sizeHint())
            self.menu_list_widget.setItemWidget(list_item, item_widget)

    def _on_quantity_changed(self, item_id, quantity):
        if quantity > 0:
            self.selected_items[item_id] = quantity
        else:
            self.selected_items.pop(item_id, None)
        self._update_total()

    def _update_total(self):
        total = 0.0
        for item_id, quantity in self.selected_items.items():
            if item_id in self.menu_items_data:
                total += self.menu_items_data[item_id]['price'] * quantity
        self.total_label.setText(f"Total: ₹{total:.2f}")

    def get_order_details(self):
        return self.selected_items

class GuestView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        cust_layout = QVBoxLayout(self)
        cust_layout.setSpacing(16)

        header_label = QLabel("Guest Management")
        header_label.setObjectName("HeaderLabel") # For QSS styling
        cust_layout.addWidget(header_label)

        cust_bar = QHBoxLayout()
        cust_bar.setSpacing(10) # Add spacing between elements in the bar
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Search by name, phone, or email...")
        self.customer_search.setObjectName("SearchLineEdit") # For QSS styling
        self.btn_add_cust = QPushButton("Add Customer")
        self.btn_add_cust.setObjectName("PrimaryButton") # For QSS styling
        self.btn_edit_cust = QPushButton("Edit")
        self.btn_edit_cust.setObjectName("SecondaryButton") # For QSS styling
        self.btn_delete_cust = QPushButton("Delete")
        self.btn_delete_cust.setObjectName("DangerButton") # For QSS styling
        self.btn_cust_checkin = QPushButton("Check-in")
        self.btn_cust_checkin.setObjectName("ActionButton") # For QSS styling
        self.btn_cust_checkout = QPushButton("Check-out")
        self.btn_cust_checkout.setObjectName("ActionButton") # For QSS styling
        self.btn_add_order = QPushButton("Add Order")
        self.btn_add_order.setObjectName("ActionButton") # For QSS styling
        self.btn_export_cust = QPushButton("Export CSV")
        self.btn_export_cust.setObjectName("ActionButton") # For QSS styling

        cust_bar.addWidget(self.customer_search, 1)
        cust_bar.addWidget(self.btn_add_cust)
        cust_bar.addWidget(self.btn_edit_cust)
        cust_bar.addWidget(self.btn_delete_cust)
        cust_bar.addWidget(self.btn_cust_checkin)
        cust_bar.addWidget(self.btn_cust_checkout)
        cust_bar.addWidget(self.btn_add_order)
        cust_bar.addWidget(self.btn_export_cust)
        cust_layout.addLayout(cust_bar)

        self.customers = QTableWidget(0, 8)
        self.customers.setHorizontalHeaderLabels(["ID","Name","Phone","Email","Current Room","Res Status","Check-in","Check-out"])
        self.customers.setSelectionBehavior(QTableWidget.SelectRows) # Select entire rows
        self.customers.setEditTriggers(QTableWidget.NoEditTriggers) # Make table read-only
        self.customers.horizontalHeader().setStretchLastSection(True) # Stretch last column
        self.customers.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # Resize columns to content
        cust_layout.addWidget(self.customers)

        # Customer Orders Section
        orders_header_label = QLabel("Customer Orders")
        orders_header_label.setObjectName("HeaderLabel")
        cust_layout.addWidget(orders_header_label)

        self.customer_orders = QTableWidget(0, 5) # Order ID, Date, Total, Status, Details
        self.customer_orders.setHorizontalHeaderLabels(["Order ID", "Date", "Total", "Status", "Items"])
        self.customer_orders.setSelectionBehavior(QTableWidget.SelectRows)
        self.customer_orders.setEditTriggers(QTableWidget.NoEditTriggers)
        self.customer_orders.horizontalHeader().setStretchLastSection(True)
        self.customer_orders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.customer_orders.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        cust_layout.addWidget(self.customer_orders)

        self.btn_add_cust.clicked.connect(self.add_customer)
        self.btn_edit_cust.clicked.connect(self.edit_customer)
        self.btn_delete_cust.clicked.connect(self.delete_customer)
        self.btn_cust_checkin.clicked.connect(self.customer_check_in)
        self.btn_cust_checkout.clicked.connect(self.customer_check_out)
        self.customer_search.textChanged.connect(self.refresh_customers)
        self.btn_export_cust.clicked.connect(self.export_customers_csv)
        self.btn_add_order.clicked.connect(self.add_customer_order)
        self.customers.itemSelectionChanged.connect(self._on_customer_selection_changed)
        self.refresh_customers()

    def refresh_customers(self):
        """Show only currently checked-in guests. Hide reserved and checked-out."""
        term = self.customer_search.text().strip()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        # Show all customers but include current checked-in reservation (if any)
        if term:
            like = f"%{term}%"
            cur.execute("""
                SELECT c.id AS id, c.name AS name, c.phone AS phone, c.email AS email,
                       r.room_id AS room_id, rm.number AS current_room, r.status AS res_status,
                       r.check_in AS check_in, r.check_out AS check_out
                FROM Customers c
                LEFT JOIN Reservations r ON r.customer_id=c.id AND r.status='CheckedIn'
                LEFT JOIN Rooms rm ON rm.id = r.room_id
                WHERE (c.name LIKE ? OR c.phone LIKE ? OR c.email LIKE ?)
                ORDER BY c.id DESC
            """, (like, like, like))
        else:
            cur.execute("""
                SELECT c.id AS id, c.name AS name, c.phone AS phone, c.email AS email,
                       r.room_id AS room_id, rm.number AS current_room, r.status AS res_status,
                       r.check_in AS check_in, r.check_out AS check_out
                FROM Customers c
                LEFT JOIN Reservations r ON r.customer_id=c.id AND r.status='CheckedIn'
                LEFT JOIN Rooms rm ON rm.id = r.room_id
                ORDER BY c.id DESC
            """)
        rows = cur.fetchall()
        self.customers.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.customers.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.customers.setItem(i,1,QTableWidgetItem(r["name"] or ""))
            self.customers.setItem(i,2,QTableWidgetItem(r["phone"] or ""))
            self.customers.setItem(i,3,QTableWidgetItem(r["email"] or ""))
            self.customers.setItem(i,4,QTableWidgetItem(r["current_room"] or ""))
            self.customers.setItem(i,5,QTableWidgetItem(r["res_status"] or ""))
            self.customers.setItem(i,6,QTableWidgetItem(r["check_in"] or ""))
            self.customers.setItem(i,7,QTableWidgetItem(r["check_out"] or ""))
        self.customer_orders.setRowCount(0) # Clear orders when customers are refreshed

    def refresh_customer_orders(self, customer_id):
        self.customer_orders.setRowCount(0) # Clear existing orders
        if not customer_id:
            return

        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                o.id AS order_id,
                o.created_at AS order_date,
                o.status,
                SUM(od.qty * od.price) AS total_amount
            FROM Orders o
            JOIN OrderDetails od ON o.id = od.order_id
            WHERE o.customer_id = ?
            GROUP BY o.id, o.created_at, o.status
            ORDER BY o.created_at DESC, o.id DESC
        """, (customer_id,))
        orders = cur.fetchall()

        self.customer_orders.setRowCount(len(orders))
        for i, order in enumerate(orders):
            self.customer_orders.setItem(i, 0, QTableWidgetItem(str(order["order_id"])))
            self.customer_orders.setItem(i, 1, QTableWidgetItem(order["order_date"]))
            self.customer_orders.setItem(i, 2, QTableWidgetItem(f"₹{order['total_amount']:.2f}"))
            self.customer_orders.setItem(i, 3, QTableWidgetItem(order["status"]))

            # Fetch and display order items for each order
            cur.execute("""
                SELECT mi.name, od.qty AS quantity
                FROM OrderDetails od
                JOIN MenuItems mi ON od.item_id = mi.id
                WHERE od.order_id = ?
            """, (order["order_id"],))
            items = cur.fetchall()
            item_details = ", ".join([f"{item['name']} x{item['quantity']}" for item in items])
            self.customer_orders.setItem(i, 4, QTableWidgetItem(item_details))

    def add_customer(self):
        dlg = CustomerDialog(self)
        if dlg.exec():
            if not dlg.name.text().strip():
                MessageBox.warning(self, "Validation Required", "Customer name is required.")
                return
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("INSERT INTO Customers(name,phone,email) VALUES(?,?,?)",
                        (dlg.name.text().strip(), dlg.phone.text().strip(), dlg.email.text().strip()))
            conn.commit()
            self.refresh_customers()

    def _on_customer_selection_changed(self):
        row = self.customers.currentRow()
        if row >= 0:
            cust_id = int(self.customers.item(row, 0).text())
            self.refresh_customer_orders(cust_id)
        else:
            self.refresh_customer_orders(None) # Clear orders if no customer is selected

    

    def edit_customer(self):
        row = self.customers.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a customer to edit.")
            return
        cust_id = int(self.customers.item(row,0).text())
        dlg = CustomerDialog(self)
        dlg.name.setText(self.customers.item(row,1).text())
        dlg.phone.setText(self.customers.item(row,2).text())
        dlg.email.setText(self.customers.item(row,3).text())
        if dlg.exec():
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("UPDATE Customers SET name=?, phone=?, email=? WHERE id=?",
                        (dlg.name.text().strip(), dlg.phone.text().strip(), dlg.email.text().strip(), cust_id))
            conn.commit()
            self.refresh_customers()
            MessageBox.success(self, "Customer Updated", "Customer information has been updated successfully!")

    def delete_customer(self):
        row = self.customers.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a customer to delete.")
            return
        cust_id = int(self.customers.item(row,0).text())
        if MessageBox.confirm(self, "Confirm Deletion", "Are you sure you want to delete this customer? This action cannot be undone."):
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("DELETE FROM Customers WHERE id=?", (cust_id,))
            conn.commit()
            self.refresh_customers()
            MessageBox.success(self, "Customer Deleted", "Customer has been deleted successfully.")

    def export_customers_csv(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id,name,phone,email FROM Customers ORDER BY id DESC")
        rows = cur.fetchall()
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(app_dir, "customers_export.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ID","Name","Phone","Email"])
            for r in rows:
                w.writerow([r["id"], r["name"], r["phone"] or "", r["email"] or ""])
        MessageBox.info(self, "Export Complete", f"Exported {len(rows)} customers to customers_export.csv")

    def customer_check_in(self):
        row = self.customers.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a customer to check in.")
            return
        cust_id = int(self.customers.item(row,0).text())
        dlg = CustomerCheckinDialog(self, self.controller.db)
        dlg.check_in.setText(datetime.date.today().isoformat())
        
        # Check if all rooms are occupied
        if dlg.all_rooms_occupied:
            MessageBox.warning(self, "No Room Available", 
                              "All rooms are currently occupied.\nNo rooms available for check-in.\n\n" +
                              "Please try again later or contact management.")
            return
        
        if dlg.exec():
            room_id = dlg.room.currentData()
            # Allow check-in without assigning a room (waitlist) when room_id is None
            conn = self.controller.db.connect()
            cur = conn.cursor()
            try:
                if room_id is None:
                    reply = MessageBox.question(self, "No Room Selected", "No rooms are available. Add customer to waitlist without a room?")
                    if reply != QMessageBox.Yes:
                        return

                # If a real room was selected, validate it
                if room_id is not None:
                    cur.execute("SELECT id, status FROM Rooms WHERE id=?", (room_id,))
                    room_row = cur.fetchone()
                    if not room_row:
                        QMessageBox.warning(self, "Error", "Room not found.")
                        return
                    if room_row["status"] != "Available":
                        MessageBox.warning(self, "Room Unavailable", "Selected room is not available.")
                        return

                # If there is an existing Reserved reservation for this customer+room, update it to CheckedIn
                if room_id is not None:
                    cur.execute("SELECT id FROM Reservations WHERE customer_id=? AND room_id=? AND status='Reserved' ORDER BY id DESC LIMIT 1", (cust_id, room_id))
                    existing = cur.fetchone()
                else:
                    existing = None

                if existing:
                    logging.info(f"Updating existing reservation {existing['id']} to CheckedIn for customer {cust_id}")
                    cur.execute("UPDATE Reservations SET status='CheckedIn', check_in=?, check_out=? WHERE id=?",
                                (dlg.check_in.text(), dlg.check_out.text(), existing['id']))
                else:
                    logging.info(f"Creating new reservation as CheckedIn for customer {cust_id} in room {room_id}")
                    cur.execute("INSERT INTO Reservations(customer_id,room_id,check_in,check_out,status) VALUES(?,?,?,?,?)",
                                (cust_id, room_id, dlg.check_in.text(), dlg.check_out.text(), "CheckedIn"))

                # Update room status only if a room was assigned
                if room_id is not None:
                    cur.execute("UPDATE Rooms SET status='Occupied' WHERE id=?", (room_id,))

                conn.commit()
                self.refresh_customers() # Refresh customer list after check-in
                MessageBox.success(self, "Check-in Successful", "Customer checked in successfully!")
                self.refresh_customer_orders(cust_id) # Also refresh orders for the checked-in customer
            except Exception as e:
                conn.rollback()
                logging.error(f"Failed during check-in for customer {cust_id}: {e}", exc_info=True)
                MessageBox.error(self, "Check-in Failed", f"Failed to check in customer: {e}")

    def customer_check_out(self):
        row = self.customers.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a customer to check out.")
            return
        cust_id = int(self.customers.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id FROM Reservations WHERE customer_id=? AND status='CheckedIn' ORDER BY id DESC LIMIT 1", (cust_id,))
        res = cur.fetchone()
        if not res:
            MessageBox.warning(self, "No Active Stay", "No active stay found for this customer.")
            return
        # Open checkout dialog which will calculate bill and finalize
        dlg = CheckoutDialog(self, self.controller.db, reservation_id=res['id'])
        if dlg.exec():
            self.refresh_customers()
            self.refresh_customer_orders(cust_id)

    def add_customer_order(self):
        row = self.customers.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a customer to add an order for.")
            return
        cust_id = int(self.customers.item(row,0).text())
        cust_name = self.customers.item(row,1).text()

        dlg = AddCustomerOrderDialog(self, self.controller.db)
        if dlg.exec():
            order_details = dlg.get_order_details()
            if not order_details:
                MessageBox.info(self, "Order Empty", "No items selected for the order.")
                return

            conn = self.controller.db.connect()
            cur = conn.cursor()
            try:
                # Create a new order record
                cur.execute("INSERT INTO Orders (customer_id, order_date, status) VALUES (?, ?, ?)",
                            (cust_id, datetime.date.today().isoformat(), "Pending"))
                order_id = cur.lastrowid

                # Insert order items
                for item_id, quantity in order_details.items():
                    # Get the price of the menu item
                    cur.execute("SELECT price FROM MenuItems WHERE id = ?", (item_id,))
                    item_price = cur.fetchone()["price"]
                    cur.execute("INSERT INTO OrderDetails (order_id, item_id, qty, price, kitchen_status) VALUES (?, ?, ?, ?, ?)",
                                (order_id, item_id, quantity, item_price, "Pending"))
                conn.commit()
                MessageBox.success(self, "Order Placed", f"Order for {cust_name} placed successfully!")
                self.refresh_customer_orders(cust_id) # Refresh orders after placing a new one
            except Exception as e:
                conn.rollback()
                MessageBox.critical(self, "Order Error", f"Failed to place order: {e}")

    
