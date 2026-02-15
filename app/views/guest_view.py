from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QTabWidget, QGridLayout, QMessageBox
from PySide6.QtCore import Qt
import datetime
import logging
import csv, os
from app.utils.message import MessageBox # Assuming MessageBox is in utils

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

class GuestView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        cust_layout = QVBoxLayout(self)
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

        self.btn_add_cust.clicked.connect(self.add_customer)
        self.btn_edit_cust.clicked.connect(self.edit_customer)
        self.btn_delete_cust.clicked.connect(self.delete_customer)
        self.btn_cust_checkin.clicked.connect(self.customer_check_in)
        self.btn_cust_checkout.clicked.connect(self.customer_check_out)
        self.customer_search.textChanged.connect(self.refresh_customers)
        self.btn_export_cust.clicked.connect(self.export_customers_csv)
        self.refresh_customers()

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
                MessageBox.warning(self, "Room Unavailable", "Selected room is not available.")
                return
            room_id = room_row["id"]
            cur.execute("INSERT INTO Reservations(customer_id,room_id,check_in,check_out,status) VALUES(?,?,?,?,?)",
                        (cust_id, room_id, dlg.check_in.text(), dlg.check_out.text(), "CheckedIn"))
            cur.execute("UPDATE Rooms SET status='Occupied' WHERE id=?", (room_id,))
            conn.commit()
            self.refresh_customers() # Refresh customer list after check-in
            MessageBox.success(self, "Check-in Successful", "Customer checked in successfully!")

    def customer_check_out(self):
        row = self.customers.currentRow()
        if row < 0:
            MessageBox.warning(self, "Selection Required", "Please select a customer to check out.")
            return
        cust_id = int(self.customers.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, room_id FROM Reservations WHERE customer_id=? AND status='CheckedIn' ORDER BY id DESC LIMIT 1", (cust_id,))
        res = cur.fetchone()
        if not res:
            MessageBox.warning(self, "No Active Stay", "No active stay found for this customer.")
            return
        cur.execute("UPDATE Reservations SET status='CheckedOut', check_out=? WHERE id=?", (datetime.date.today().isoformat(), res["id"]))
        cur.execute("UPDATE Rooms SET status='Cleaning' WHERE id=?", (res["room_id"],))
        conn.commit()
        self.refresh_customers()
        # self.refresh_rooms() # This would be handled by a RoomView if it existed
