from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QTabWidget, QGridLayout, QMessageBox, QHeaderView
from PySide6.QtCore import Qt
import datetime
from app.views.table_management_dialog import TableManagementDialog
from .checkout_dialog import CheckoutDialog
from app.utils.message import MessageBox
import logging

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
    def __init__(self, parent=None, db=None, edit_mode=False, customer_name="", customer_phone="", customer_email=""):
        super().__init__(parent)
        self.setWindowTitle("Reservation" if not edit_mode else "Edit Reservation")
        self.db = db
        self.setMinimumWidth(400)
        f = QFormLayout(self)
        
        # Customer Details Section
        customer_label = QLabel("<b>Customer Details</b>")
        f.addRow(customer_label)
        
        self.customer = QLineEdit()
        self.customer.setPlaceholderText("Guest name")
        if edit_mode:
            self.customer.setText(customer_name)
        f.addRow("Customer Name *:", self.customer)
        
        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("Phone number")
        if edit_mode:
            self.customer_phone.setText(customer_phone or "")
        f.addRow("Phone:", self.customer_phone)
        
        self.customer_email = QLineEdit()
        self.customer_email.setPlaceholderText("Email address")
        if edit_mode:
            self.customer_email.setText(customer_email or "")
        f.addRow("Email:", self.customer_email)
        
        # Reservation Details Section
        res_label = QLabel("<b>Reservation Details</b>")
        f.addRow(res_label)
        
        self.room = QComboBox()
        self.room.setMinimumWidth(200)
        f.addRow("Room *:", self.room)
        
        self.check_in = QLineEdit()
        self.check_in.setPlaceholderText("YYYY-MM-DD")
        f.addRow("Check-in *:", self.check_in)
        
        self.check_out = QLineEdit()
        self.check_out.setPlaceholderText("YYYY-MM-DD")
        f.addRow("Check-out:", self.check_out)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok = QPushButton("Save")
        ok.setObjectName("PrimaryButton")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        button_layout.addWidget(ok)
        button_layout.addWidget(cancel)
        f.addRow(button_layout)
        
        if db:
            self._load_rooms()

    def _load_rooms(self):
        conn = self.db.connect()
        cur = conn.cursor()
        # Load only available rooms by default, but show status indicator
        cur.execute("SELECT number, category, status, rate FROM Rooms ORDER BY status DESC, number")
        self.room.clear()
        available_count = 0
        for r in cur.fetchall():
            status_indicator = "✓" if r['status'] == "Available" else "✗"
            self.room.addItem(f"{status_indicator} {r['number']} ({r['category']} - ₹{r['rate']:.0f}) [{r['status']}]", r["number"])
            if r['status'] == "Available":
                available_count += 1
        
        # If no rooms available, add warning option
        if available_count == 0:
            self.room.insertItem(0, "⚠ No Room Available", None)
    
    def set_room(self, room_number):
        """Set the selected room by room number"""
        for i in range(self.room.count()):
            if self.room.itemData(i) == room_number:
                self.room.setCurrentIndex(i)
                return

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
        self.btn_res_update = QPushButton("Update Details")
        self.btn_res_delete = QPushButton("Delete")
        self.btn_check_in = QPushButton("Check-in")
        self.btn_check_out = QPushButton("Check-out")
        self.res_search = QLineEdit()
        self.res_search.setPlaceholderText("Search by customer or room...")
        res_bar.addWidget(self.btn_add_res)
        res_bar.addWidget(self.btn_res_update)
        res_bar.addWidget(self.btn_res_delete)
        res_bar.addWidget(self.btn_check_in)
        res_bar.addWidget(self.btn_check_out)
        res_bar.addWidget(self.res_search, 1)
        res_layout.addLayout(res_bar)
        self.reservations = QTableWidget(0, 8)
        self.reservations.setHorizontalHeaderLabels(["ID","Customer","Phone","Email","Room","Check-in","Check-out","Status"])
        self.reservations.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.reservations.setSelectionBehavior(QTableWidget.SelectRows)
        self.reservations.setSelectionMode(QTableWidget.ExtendedSelection)  # Allow multiple selection
        res_layout.addWidget(self.reservations)
        self.tabs.addTab(res_tab, "Reservations")

        

        self.btn_add_room.clicked.connect(self.add_room)
        self.btn_edit_room.clicked.connect(self.edit_room)
        self.btn_delete_room.clicked.connect(self.delete_room)
        self.btn_add_res.clicked.connect(self.add_reservation)
        self.btn_res_update.clicked.connect(self.res_update_details)
        self.btn_res_delete.clicked.connect(self.res_delete_reservation)
        self.btn_check_in.clicked.connect(self.check_in)
        self.btn_check_out.clicked.connect(self.check_out)
        self.res_search.textChanged.connect(self.refresh)
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
        # Reservations tab: Show ALL reservations that went through 'Reserved' status
        # This includes: Reserved, CheckedIn (from reservations), CheckedOut (from reservations), Cancelled
        # We exclude walk-ins by checking: if status='CheckedIn' with check_out IS NULL, it's a walk-in (exclude it)
        # But if status='CheckedIn' and check_out IS NOT NULL, it was checked out (was a reservation, include it)
        # OR if status is Reserved/Cancelled/CheckedOut, include it
        # Actually simpler: Get all reservation IDs that are walk-ins, then exclude them
        if term:
            like = f"%{term}%"
            cur.execute("""
                SELECT r.id AS id, c.name AS customer, c.phone AS phone, c.email AS email,
                       rm.number AS room, r.check_in AS ci, r.check_out AS co, r.status AS status
                FROM Reservations r
                JOIN Customers c ON r.customer_id = c.id
                JOIN Rooms rm ON r.room_id = rm.id
                WHERE r.id NOT IN (
                    SELECT r3.id FROM Reservations r3
                    WHERE r3.status = 'CheckedIn' 
                    AND r3.check_out IS NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM Reservations r4 
                        WHERE r4.customer_id = r3.customer_id 
                        AND r4.room_id = r3.room_id 
                        AND r4.id < r3.id
                        AND r4.status = 'Reserved'
                    )
                )
                AND (c.name LIKE ? OR rm.number LIKE ? OR c.phone LIKE ? OR c.email LIKE ?)
                ORDER BY r.id DESC
            """, (like, like, like, like))
        else:
            cur.execute("""
                SELECT r.id AS id, c.name AS customer, c.phone AS phone, c.email AS email,
                       rm.number AS room, r.check_in AS ci, r.check_out AS co, r.status AS status
                FROM Reservations r
                JOIN Customers c ON r.customer_id = c.id
                JOIN Rooms rm ON r.room_id = rm.id
                WHERE r.id NOT IN (
                    SELECT r3.id FROM Reservations r3
                    WHERE r3.status = 'CheckedIn' 
                    AND r3.check_out IS NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM Reservations r4 
                        WHERE r4.customer_id = r3.customer_id 
                        AND r4.room_id = r3.room_id 
                        AND r4.id < r3.id
                        AND r4.status = 'Reserved'
                    )
                )
                ORDER BY r.id DESC
            """)
        rows = cur.fetchall()
        self.reservations.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.reservations.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.reservations.setItem(i,1,QTableWidgetItem(r["customer"]))
            self.reservations.setItem(i,2,QTableWidgetItem(r["phone"] or ""))
            self.reservations.setItem(i,3,QTableWidgetItem(r["email"] or ""))
            self.reservations.setItem(i,4,QTableWidgetItem(r["room"]))
            self.reservations.setItem(i,5,QTableWidgetItem(r["ci"]))
            self.reservations.setItem(i,6,QTableWidgetItem(r["co"] or ""))
            self.reservations.setItem(i,7,QTableWidgetItem(r["status"]))
        
        



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
            
            # Check if no room is selected or "No Room Available" option selected
            if not room_number or room_number == "⚠":
                conn = self.controller.db.connect()
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) as count FROM Rooms WHERE status='Available'")
                result = cur.fetchone()
                available_rooms = result['count'] if result else 0
                if available_rooms == 0:
                    MessageBox.warning(self, "No Room Available", "All rooms are currently occupied.\nPlease try again later.")
                else:
                    MessageBox.warning(self, "Validation Required", "Please select a room for reservation.")
                return
            
            if not dlg.check_in.text().strip():
                QMessageBox.warning(self, "Validation", "Check-in date is required.")
                return
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("SELECT id, status FROM Rooms WHERE number=?", (str(room_number),))
            room_row = cur.fetchone()
            if not room_row:
                MessageBox.error(self, "Room Error", "Selected room not found.")
                return
            
            # Validate room is available before creating reservation
            if room_row["status"] != "Available":
                MessageBox.warning(self, "Room Not Available", 
                                 f"Room {room_number} is currently {room_row['status']}.\nPlease select another room.")
                return
            
            room_id = room_row["id"]
            # Create customer with details
            customer_name = dlg.customer.text().strip()
            customer_phone = dlg.customer_phone.text().strip() or None
            customer_email = dlg.customer_email.text().strip() or None
            cur.execute("INSERT INTO Customers(name, phone, email) VALUES(?, ?, ?)", 
                       (customer_name, customer_phone, customer_email))
            cust_id = cur.lastrowid
            check_out_val = dlg.check_out.text().strip() or None
            cur.execute("INSERT INTO Reservations(customer_id,room_id,check_in,check_out,status) VALUES(?,?,?,?,?)",
                        (cust_id, room_id, dlg.check_in.text().strip(), check_out_val, "Reserved"))
            conn.commit()
            self.refresh()
            MessageBox.success(self, "Reservation Created", "Reservation created successfully!")


    def res_update_details(self):
        """Update customer and reservation details"""
        selected_rows = self.reservations.selectionModel().selectedRows()
        if not selected_rows:
            MessageBox.warning(self, "Selection Required", "Please select a reservation to update.")
            return
        
        # Get first selected row
        row = selected_rows[0].row()
        res_id = int(self.reservations.item(row,0).text())
        customer_name = self.reservations.item(row,1).text()
        customer_phone = self.reservations.item(row,2).text()
        customer_email = self.reservations.item(row,3).text()
        
        # Get customer ID and reservation details
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT customer_id, check_in, check_out FROM Reservations WHERE id=?", (res_id,))
        res_row = cur.fetchone()
        if not res_row:
            MessageBox.error(self, "Error", "Reservation not found.")
            return
        
        customer_id = res_row["customer_id"]
        check_in_date = res_row["check_in"]
        check_out_date = res_row["check_out"]
        
        # Create edit dialog
        dlg = ReservationDialog(self, self.controller.db, edit_mode=True, 
                               customer_name=customer_name, 
                               customer_phone=customer_phone, 
                               customer_email=customer_email)
        dlg.check_in.setText(check_in_date or "")
        dlg.check_out.setText(check_out_date or "")
        
        # Load current room
        room_number = self.reservations.item(row,4).text()
        dlg.set_room(room_number)
        
        if dlg.exec():
            new_name = dlg.customer.text().strip()
            if not new_name:
                MessageBox.warning(self, "Validation Required", "Customer name is required.")
                return
            
            try:
                # Update customer details
                cur.execute("UPDATE Customers SET name=?, phone=?, email=? WHERE id=?", 
                           (new_name, dlg.customer_phone.text().strip() or None, 
                            dlg.customer_email.text().strip() or None, customer_id))
                
                # Update reservation dates if changed
                new_check_in = dlg.check_in.text().strip()
                new_check_out = dlg.check_out.text().strip()
                if new_check_in or new_check_out:
                    cur.execute("UPDATE Reservations SET check_in=?, check_out=? WHERE id=?", 
                               (new_check_in or check_in_date, new_check_out or check_out_date, res_id))
                
                conn.commit()
                self.refresh()
                MessageBox.success(self, "Update Successful", "Reservation details updated successfully!")
            except Exception as e:
                conn.rollback()
                MessageBox.error(self, "Update Failed", f"Failed to update reservation: {e}")
                logging.error(f"Reservation update error: {e}")

    def res_delete_reservation(self):
        """Delete reservation(s)"""
        selected_rows = self.reservations.selectionModel().selectedRows()
        if not selected_rows:
            MessageBox.warning(self, "Selection Required", "Please select reservation(s) to delete.")
            return
        
        count = len(selected_rows)
        reply = MessageBox.question(self, "Confirm Deletion", 
                                   f"Are you sure you want to delete {count} reservation(s)?\nThis action cannot be undone.")
        if reply != QMessageBox.Yes:
            return
        
        conn = self.controller.db.connect()
        cur = conn.cursor()
        deleted_count = 0
        
        try:
            # Collect all reservation IDs first (before deletion)
            res_ids_to_delete = []
            customer_room_map = {}
            
            for index in selected_rows:
                row = index.row()
                res_id = int(self.reservations.item(row,0).text())
                res_ids_to_delete.append(res_id)
                
                # Get customer and room IDs for each reservation
                cur.execute("SELECT customer_id, room_id FROM Reservations WHERE id=?", (res_id,))
                res_row = cur.fetchone()
                if res_row:
                    customer_room_map[res_id] = {
                        'customer_id': res_row["customer_id"],
                        'room_id': res_row["room_id"]
                    }
            
            # Delete all reservations
            for res_id in res_ids_to_delete:
                if res_id in customer_room_map:
                    customer_id = customer_room_map[res_id]['customer_id']
                    room_id = customer_room_map[res_id]['room_id']
                    
                    # Delete reservation
                    cur.execute("DELETE FROM Reservations WHERE id=?", (res_id,))
                    
                    # Set room to Available
                    cur.execute("UPDATE Rooms SET status='Available' WHERE id=?", (room_id,))
                    deleted_count += 1
            
            # Check and delete customers with no remaining reservations
            customer_ids_to_check = set([customer_room_map[r]['customer_id'] for r in res_ids_to_delete if r in customer_room_map])
            for customer_id in customer_ids_to_check:
                cur.execute("SELECT COUNT(*) as count FROM Reservations WHERE customer_id=?", (customer_id,))
                other_res = cur.fetchone()["count"]
                if other_res == 0:
                    # Delete customer if no other reservations
                    cur.execute("DELETE FROM Customers WHERE id=?", (customer_id,))
            
            conn.commit()
            self.refresh()
            MessageBox.success(self, "Deletion Successful", f"{deleted_count} reservation(s) deleted successfully!")
        except Exception as e:
            conn.rollback()
            MessageBox.error(self, "Deletion Failed", f"Failed to delete reservation(s): {e}")
            logging.error(f"Reservation delete error: {e}")
            import traceback
            logging.error(traceback.format_exc())

    def check_in(self):
        """Check in selected reservation(s)"""
        selected_rows = self.reservations.selectionModel().selectedRows()
        if not selected_rows:
            MessageBox.warning(self, "Selection Required", "Please select reservation(s) to check in.")
            return
        
        conn = self.controller.db.connect()
        cur = conn.cursor()
        checked_in_count = 0
        
        try:
            for index in selected_rows:
                row = index.row()
                res_id = int(self.reservations.item(row,0).text())
                room_number = self.reservations.item(row,4).text()  # Room is at index 4
                
                # Ensure reservation has a check_out set (so it isn't treated as a walk-in and hidden)
                cur.execute("SELECT check_out FROM Reservations WHERE id=?", (res_id,))
                rrow = cur.fetchone()
                if rrow and (rrow["check_out"] is None or not str(rrow["check_out"]).strip()):
                    # set a default planned check_out if missing (tomorrow)
                    default_co = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
                    cur.execute("UPDATE Reservations SET check_out=? WHERE id=?", (default_co, res_id))

                # Update reservation status
                cur.execute("UPDATE Reservations SET status='CheckedIn' WHERE id=?", (res_id,))
                
                # Update room status
                cur.execute("UPDATE Rooms SET status='Occupied' WHERE number=?", (room_number,))
                checked_in_count += 1
            
            conn.commit()
            self.refresh()
            MessageBox.success(self, "Check-in Successful", f"{checked_in_count} reservation(s) checked in successfully!")
        except Exception as e:
            conn.rollback()
            MessageBox.error(self, "Check-in Failed", f"Failed to check in reservation(s): {e}")
            logging.error(f"Reservation check-in error: {e}")

    def check_out(self):
        """Check out selected reservation(s)"""
        selected_rows = self.reservations.selectionModel().selectedRows()
        if not selected_rows:
            MessageBox.warning(self, "Selection Required", "Please select reservation(s) to check out.")
            return
        
        conn = self.controller.db.connect()
        cur = conn.cursor()
        checked_out_count = 0
        
        try:
            for index in selected_rows:
                row = index.row()
                res_id = int(self.reservations.item(row,0).text())
                # Use CheckoutDialog to calculate bill and finalize checkout for each reservation
                dlg = CheckoutDialog(self, self.controller.db, reservation_id=res_id)
                if dlg.exec():
                    checked_out_count += 1

            conn.commit()
            self.refresh()
            MessageBox.success(self, "Check-out Successful", f"{checked_out_count} reservation(s) checked out successfully!")
        except Exception as e:
            conn.rollback()
            MessageBox.error(self, "Check-out Failed", f"Failed to check out reservation(s): {e}")
            logging.error(f"Reservation check-out error: {e}")

    
