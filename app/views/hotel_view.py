from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QTabWidget, QMessageBox
from PySide6.QtCore import Qt
import datetime

class RoomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room")
        f = QFormLayout(self)
        self.number = QLineEdit()
        self.category = QComboBox()
        self.category.addItems(["Standard","Deluxe","Suite"])
        self.status = QComboBox()
        self.status.addItems(["Available","Occupied","Cleaning"])
        self.rate = QSpinBox()
        self.rate.setMaximum(100000)
        ok = QPushButton("Save")
        ok.clicked.connect(self.accept)
        f.addRow("Number", self.number)
        f.addRow("Category", self.category)
        f.addRow("Status", self.status)
        f.addRow("Rate", self.rate)
        f.addRow(ok)

class ReservationDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.setWindowTitle("Reservation")
        self.db = db
        f = QFormLayout(self)
        self.customer = QLineEdit()
        self.customer.setPlaceholderText("Guest name")
        self.room = QComboBox()
        self.room.setMinimumWidth(200)
        self.check_in = QLineEdit()
        self.check_in.setPlaceholderText("YYYY-MM-DD")
        self.check_out = QLineEdit()
        self.check_out.setPlaceholderText("YYYY-MM-DD")
        ok = QPushButton("Save")
        ok.clicked.connect(self.accept)
        f.addRow("Customer Name", self.customer)
        f.addRow("Room", self.room)
        f.addRow("Check-in", self.check_in)
        f.addRow("Check-out", self.check_out)
        f.addRow(ok)
        if db:
            self._load_rooms()

    def _load_rooms(self):
        conn = self.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT number, category, status, rate FROM Rooms ORDER BY number")
        self.room.clear()
        for r in cur.fetchall():
            self.room.addItem(f"{r['number']} ({r['category']} - ₹{r['rate']:.0f}) [{r['status']}]", r["number"])

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
        cur.execute("SELECT number, category, rate FROM Rooms WHERE status='Available' ORDER BY number")
        self.room.clear()
        for r in cur.fetchall():
            self.room.addItem(f"{r['number']} ({r['category']} - ₹{r['rate']:.0f})", r["number"])

class HotelView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        v = QVBoxLayout(self)
        v.setSpacing(20)
        page_title = QLabel("Hotel")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Manage rooms, reservations, and customers")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)

        self.tabs = QTabWidget()
        v.addWidget(self.tabs, 1)

        # ---- Rooms tab ----
        rooms_tab = QWidget()
        rooms_layout = QVBoxLayout(rooms_tab)
        rooms_layout.setSpacing(16)
        top = QHBoxLayout()
        top.setSpacing(12)
        self.btn_add_room = QPushButton("Add Room")
        self.btn_add_room.setObjectName("PrimaryButton")
        self.btn_edit_room = QPushButton("Edit Room")
        self.btn_delete_room = QPushButton("Delete Room")
        top.addWidget(self.btn_add_room)
        top.addWidget(self.btn_edit_room)
        top.addWidget(self.btn_delete_room)
        top.addStretch()
        rooms_layout.addLayout(top)
        self.rooms = QTableWidget(0, 4)
        self.rooms.setHorizontalHeaderLabels(["Number","Category","Status","Rate"])
        rooms_layout.addWidget(self.rooms)
        self.tabs.addTab(rooms_tab, "Rooms")

        # ---- Reservations tab ----
        res_tab = QWidget()
        res_layout = QVBoxLayout(res_tab)
        res_layout.setSpacing(16)
        res_bar = QHBoxLayout()
        self.btn_add_res = QPushButton("Add Reservation")
        self.btn_add_res.setObjectName("PrimaryButton")
        self.btn_check_in = QPushButton("Check-in")
        self.btn_check_out = QPushButton("Check-out")
        self.res_search = QLineEdit()
        self.res_search.setPlaceholderText("Search by customer or room...")
        res_bar.addWidget(self.btn_add_res)
        res_bar.addWidget(self.btn_check_in)
        res_bar.addWidget(self.btn_check_out)
        res_bar.addWidget(self.res_search, 1)
        res_layout.addLayout(res_bar)
        self.reservations = QTableWidget(0, 5)
        self.reservations.setHorizontalHeaderLabels(["ID","Customer","Room","Check-in","Check-out"])
        res_layout.addWidget(self.reservations)
        self.tabs.addTab(res_tab, "Reservations")

        # ---- Customers tab ----
        cust_tab = QWidget()
        cust_layout = QVBoxLayout(cust_tab)
        cust_layout.setSpacing(16)
        cust_bar = QHBoxLayout()
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Search by name, phone, or email...")
        self.btn_add_cust = QPushButton("Add Customer")
        self.btn_add_cust.setObjectName("PrimaryButton")
        self.btn_edit_cust = QPushButton("Edit")
        self.btn_delete_cust = QPushButton("Delete")
        self.btn_cust_checkin = QPushButton("Check-in")
        self.btn_cust_checkout = QPushButton("Check-out")
        self.btn_export_cust = QPushButton("Export CSV")
        cust_bar.addWidget(self.customer_search, 1)
        cust_bar.addWidget(self.btn_add_cust)
        cust_bar.addWidget(self.btn_edit_cust)
        cust_bar.addWidget(self.btn_delete_cust)
        cust_bar.addWidget(self.btn_cust_checkin)
        cust_bar.addWidget(self.btn_cust_checkout)
        cust_bar.addWidget(self.btn_export_cust)
        cust_layout.addLayout(cust_bar)
        self.customers = QTableWidget(0, 6)
        self.customers.setHorizontalHeaderLabels(["ID","Name","Phone","Email","Current Room","Res Status"])
        cust_layout.addWidget(self.customers)
        self.tabs.addTab(cust_tab, "Customers")

        self.btn_add_room.clicked.connect(self.add_room)
        self.btn_edit_room.clicked.connect(self.edit_room)
        self.btn_delete_room.clicked.connect(self.delete_room)
        self.btn_add_res.clicked.connect(self.add_reservation)
        self.btn_check_in.clicked.connect(self.check_in)
        self.btn_check_out.clicked.connect(self.check_out)
        self.btn_add_cust.clicked.connect(self.add_customer)
        self.btn_edit_cust.clicked.connect(self.edit_customer)
        self.btn_delete_cust.clicked.connect(self.delete_customer)
        self.btn_cust_checkin.clicked.connect(self.customer_check_in)
        self.btn_cust_checkout.clicked.connect(self.customer_check_out)
        self.customer_search.textChanged.connect(self.refresh_customers)
        self.res_search.textChanged.connect(self.refresh)
        self.btn_export_cust.clicked.connect(self.export_customers_csv)
        self.refresh()

    def refresh(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT number,category,status,rate FROM Rooms ORDER BY number")
        rows = cur.fetchall()
        self.rooms.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.rooms.setItem(i,0,QTableWidgetItem(r["number"]))
            self.rooms.setItem(i,1,QTableWidgetItem(r["category"]))
            self.rooms.setItem(i,2,QTableWidgetItem(r["status"]))
            self.rooms.setItem(i,3,QTableWidgetItem(str(r["rate"])))
        term = self.res_search.text().strip()
        if term:
            like = f"%{term}%"
            cur.execute("""
                SELECT Reservations.id AS id, Customers.name AS customer, Rooms.number AS room, Reservations.check_in AS ci, Reservations.check_out AS co
                FROM Reservations JOIN Customers ON Reservations.customer_id=Customers.id JOIN Rooms ON Reservations.room_id=Rooms.id
                WHERE Customers.name LIKE ? OR Rooms.number LIKE ?
                ORDER BY Reservations.id DESC
            """, (like, like))
        else:
            cur.execute("""
                SELECT Reservations.id AS id, Customers.name AS customer, Rooms.number AS room, Reservations.check_in AS ci, Reservations.check_out AS co
                FROM Reservations JOIN Customers ON Reservations.customer_id=Customers.id JOIN Rooms ON Reservations.room_id=Rooms.id
                ORDER BY Reservations.id DESC
            """)
        rows = cur.fetchall()
        self.reservations.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.reservations.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.reservations.setItem(i,1,QTableWidgetItem(r["customer"]))
            self.reservations.setItem(i,2,QTableWidgetItem(r["room"]))
            self.reservations.setItem(i,3,QTableWidgetItem(r["ci"]))
            self.reservations.setItem(i,4,QTableWidgetItem(r["co"] or ""))
        self.refresh_customers()

    def add_room(self):
        dlg = RoomDialog(self)
        if dlg.exec():
            if not dlg.number.text().strip():
                MessageBox.warning(self, "Validation Required", "Please provide a room number.")
                return
            conn = self.controller.db.connect()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO Rooms(number,category,status,rate) VALUES(?,?,?,?)",
                            (dlg.number.text().strip(), dlg.category.currentText(), dlg.status.currentText(), dlg.rate.value()))
                conn.commit()
                self.refresh()
                MessageBox.success(self, "Room Added", "Room has been added successfully!")
            except Exception as e:
                MessageBox.error(self, "Operation Failed", f"Unable to add room: {e}")

    def edit_room(self):
        row = self.rooms.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a room to edit.")
            return
        number = self.rooms.item(row,0).text()
        dlg = RoomDialog(self)
        dlg.number.setText(number)
        dlg.number.setReadOnly(True)
        dlg.category.setCurrentText(self.rooms.item(row,1).text())
        dlg.status.setCurrentText(self.rooms.item(row,2).text())
        dlg.rate.setValue(int(float(self.rooms.item(row,3).text())))
        if dlg.exec():
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("UPDATE Rooms SET category=?, status=?, rate=? WHERE number=?",
                        (dlg.category.currentText(), dlg.status.currentText(), dlg.rate.value(), number))
            conn.commit()
            self.refresh()

    def delete_room(self):
        row = self.rooms.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a room to delete.")
            return
        number = self.rooms.item(row,0).text()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM Rooms WHERE number=?", (number,))
        conn.commit()
        self.refresh()

    def add_reservation(self):
        dlg = ReservationDialog(self, self.controller.db)
        if dlg.exec():
            if not dlg.customer.text().strip():
                QMessageBox.warning(self, "Validation", "Customer name is required.")
                return
            room_number = dlg.room.currentData()
            if not room_number and dlg.room.count() > 0:
                room_number = dlg.room.currentText().split()[0] if dlg.room.currentText() else None
            if not room_number:
                QMessageBox.warning(self, "Validation", "Please select a room.")
                return
            if not dlg.check_in.text().strip() or not dlg.check_out.text().strip():
                QMessageBox.warning(self, "Validation", "Check-in and check-out dates are required.")
                return
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("SELECT id FROM Rooms WHERE number=?", (str(room_number),))
            room_row = cur.fetchone()
            if not room_row:
                QMessageBox.warning(self, "Error", "Selected room not found.")
                return
            room_id = room_row["id"]
            cur.execute("INSERT INTO Customers(name) VALUES(?)", (dlg.customer.text().strip(),))
            cust_id = cur.lastrowid
            cur.execute("INSERT INTO Reservations(customer_id,room_id,check_in,check_out,status) VALUES(?,?,?,?,?)",
                        (cust_id, room_id, dlg.check_in.text().strip(), dlg.check_out.text().strip(), "Reserved"))
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", "Reservation created successfully.")

    def refresh_customers(self):
        """Show only active guests (Reserved/CheckedIn) or customers with no reservations. Hide checked-out."""
        term = self.customer_search.text().strip()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        if term:
            like = f"%{term}%"
            cur.execute("""
                SELECT c.id AS id, c.name AS name, c.phone AS phone, c.email AS email,
                       r.room_id AS room_id, rm.number AS current_room, r.status AS res_status
                FROM Customers c
                LEFT JOIN Reservations r ON r.id = (
                    SELECT id FROM Reservations WHERE customer_id=c.id AND status IN ('Reserved','CheckedIn') ORDER BY id DESC LIMIT 1
                )
                LEFT JOIN Rooms rm ON rm.id = r.room_id
                WHERE (c.name LIKE ? OR c.phone LIKE ? OR c.email LIKE ?)
                AND (r.id IS NOT NULL OR c.id NOT IN (SELECT customer_id FROM Reservations))
                ORDER BY c.id DESC
            """, (like, like, like))
        else:
            cur.execute("""
                SELECT c.id AS id, c.name AS name, c.phone AS phone, c.email AS email,
                       r.room_id AS room_id, rm.number AS current_room, r.status AS res_status
                FROM Customers c
                LEFT JOIN Reservations r ON r.id = (
                    SELECT id FROM Reservations WHERE customer_id=c.id AND status IN ('Reserved','CheckedIn') ORDER BY id DESC LIMIT 1
                )
                LEFT JOIN Rooms rm ON rm.id = r.room_id
                WHERE r.id IS NOT NULL OR c.id NOT IN (SELECT customer_id FROM Reservations)
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
            MessageBox.success(self, "Customer Added", "Customer has been added successfully!")

    def edit_customer(self):
        row = self.customers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a customer to edit.")
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
            self.refresh()
            QMessageBox.information(self, "Success", "Customer updated successfully.")

    def delete_customer(self):
        row = self.customers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a customer to delete.")
            return
        cust_id = int(self.customers.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM Customers WHERE id=?", (cust_id,))
        conn.commit()
        self.refresh()

    def export_customers_csv(self):
        import csv, os
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
        QMessageBox.information(self, "Export", f"Exported {len(rows)} customers to customers_export.csv")

    def customer_check_in(self):
        row = self.customers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a customer.")
            return
        cust_id = int(self.customers.item(row,0).text())
        dlg = CustomerCheckinDialog(self, self.controller.db)
        dlg.check_in.setText(datetime.date.today().isoformat())
        dlg.check_out.setText((datetime.date.today() + datetime.timedelta(days=1)).isoformat())
        if dlg.exec():
            room_number = dlg.room.currentData()
            if not room_number:
                QMessageBox.warning(self, "Validation", "Please select a room.")
                return
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("SELECT id, status FROM Rooms WHERE number=?", (str(room_number),))
            room_row = cur.fetchone()
            if not room_row:
                QMessageBox.warning(self, "Error", "Room not found.")
                return
            if room_row["status"] != "Available":
                QMessageBox.warning(self, "Error", "Selected room is not available.")
                return
            room_id = room_row["id"]
            cur.execute("INSERT INTO Reservations(customer_id,room_id,check_in,check_out,status) VALUES(?,?,?,?,?)",
                        (cust_id, room_id, dlg.check_in.text(), dlg.check_out.text(), "CheckedIn"))
            cur.execute("UPDATE Rooms SET status='Occupied' WHERE id=?", (room_id,))
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", "Customer checked in successfully.")

    def customer_check_out(self):
        row = self.customers.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a customer.")
            return
        cust_id = int(self.customers.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, room_id FROM Reservations WHERE customer_id=? AND status='CheckedIn' ORDER BY id DESC LIMIT 1", (cust_id,))
        res = cur.fetchone()
        if not res:
            QMessageBox.warning(self, "Error", "No active stay found for this customer.")
            return
        cur.execute("UPDATE Reservations SET status='CheckedOut', check_out=? WHERE id=?", (datetime.date.today().isoformat(), res["id"]))
        cur.execute("UPDATE Rooms SET status='Cleaning' WHERE id=?", (res["room_id"],))
        conn.commit()
        self.refresh()
        QMessageBox.information(self, "Success", "Customer checked out successfully.")
    def check_in(self):
        row = self.reservations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a reservation.")
            return
        res_id = int(self.reservations.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("UPDATE Reservations SET status='CheckedIn' WHERE id=?", (res_id,))
        cur.execute("UPDATE Rooms SET status='Occupied' WHERE number=?", (self.reservations.item(row,2).text(),))
        conn.commit()
        self.refresh()
        QMessageBox.information(self, "Success", "Reservation checked in.")

    def check_out(self):
        row = self.reservations.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a reservation.")
            return
        res_id = int(self.reservations.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("UPDATE Reservations SET status='CheckedOut', check_out=? WHERE id=?", (datetime.date.today().isoformat(), res_id))
        cur.execute("UPDATE Rooms SET status='Cleaning' WHERE number=?", (self.reservations.item(row,2).text(),))
        conn.commit()
        self.refresh()
        QMessageBox.information(self, "Success", "Reservation checked out.")
