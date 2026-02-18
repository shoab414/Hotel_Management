from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QTextEdit
import datetime

class CheckoutDialog(QDialog):
    def __init__(self, parent=None, db=None, reservation_id=None):
        super().__init__(parent)
        self.setWindowTitle("Finalize Checkout & Bill")
        self.db = db
        self.reservation_id = reservation_id
        self.setMinimumWidth(500)
        self._load_data()
        self._build_ui()

    def _load_data(self):
        conn = self.db.connect()
        cur = conn.cursor()
        # Load reservation, customer and room
        cur.execute("SELECT r.id, r.customer_id, r.room_id, r.check_in, r.check_out, r.status, c.name AS customer_name, c.phone AS customer_phone, c.email AS customer_email, rm.number AS room_number, rm.rate AS room_rate FROM Reservations r JOIN Customers c ON r.customer_id=c.id JOIN Rooms rm ON r.room_id=rm.id WHERE r.id = ?", (self.reservation_id,))
        self.res = cur.fetchone()
        if not self.res:
            raise RuntimeError("Reservation not found")
        # Compute checkout date (today)
        self.checkout_date = datetime.date.today()
        try:
            self.check_in_date = datetime.date.fromisoformat(self.res['check_in'])
        except Exception:
            self.check_in_date = self.checkout_date
        self.nights = max(1, (self.checkout_date - self.check_in_date).days)
        # Room charges
        self.room_rate = float(self.res['room_rate'] or 0.0)
        self.room_total = self.room_rate * self.nights
        # Orders: sum unpaid orders for this customer
        cur.execute("SELECT id FROM Orders WHERE customer_id = ? AND status NOT IN ('Paid','Cancelled')", (self.res['customer_id'],))
        order_rows = cur.fetchall()
        self.unpaid_orders = [r['id'] for r in order_rows]
        self.orders_total = 0.0
        self.order_lines = []
        for oid in self.unpaid_orders:
            cur.execute("SELECT SUM(qty * price) AS total FROM OrderDetails WHERE order_id = ?", (oid,))
            tot = cur.fetchone()['total'] or 0.0
            self.orders_total += float(tot)
            # fetch items for description
            cur.execute("SELECT mi.name, od.qty FROM OrderDetails od JOIN MenuItems mi ON od.item_id = mi.id WHERE od.order_id = ?", (oid,))
            items = cur.fetchall()
            items_desc = ", ".join([f"{it['name']} x{it['qty']}" for it in items])
            self.order_lines.append((oid, items_desc, tot))
        self.grand_total = self.room_total + self.orders_total

    def _build_ui(self):
        v = QVBoxLayout(self)
        f = QFormLayout()
        f.addRow("Customer:", QLabel(f"{self.res['customer_name']} ({self.res['customer_phone'] or ''})"))
        f.addRow("Email:", QLabel(self.res['customer_email'] or ""))
        f.addRow("Room:", QLabel(f"{self.res['room_number']}"))
        f.addRow("Check-in:", QLabel(self.res['check_in'] or ""))
        f.addRow("Check-out (final):", QLabel(self.checkout_date.isoformat()))
        f.addRow("Nights:", QLabel(str(self.nights)))
        f.addRow("Rate per night:", QLabel(f"₹{self.room_rate:.2f}"))
        f.addRow("Room total:", QLabel(f"₹{self.room_total:.2f}"))
        # Orders summary
        orders_text = "No unpaid orders." if not self.order_lines else "\n".join([f"Order {oid}: {desc} (₹{tot:.2f})" for oid, desc, tot in self.order_lines])
        orders_widget = QTextEdit()
        orders_widget.setReadOnly(True)
        orders_widget.setPlainText(orders_text)
        f.addRow("Unpaid Orders:", orders_widget)
        f.addRow("Orders total:", QLabel(f"₹{self.orders_total:.2f}"))
        f.addRow("Grand total:", QLabel(f"₹{self.grand_total:.2f}"))
        v.addLayout(f)

        btns = QHBoxLayout()
        self.btn_confirm = QPushButton("Pay & Checkout")
        self.btn_cancel = QPushButton("Cancel")
        self.btn_confirm.clicked.connect(self._finalize)
        self.btn_cancel.clicked.connect(self.reject)
        btns.addStretch()
        btns.addWidget(self.btn_confirm)
        btns.addWidget(self.btn_cancel)
        v.addLayout(btns)

    def _finalize(self):
        conn = self.db.connect()
        cur = conn.cursor()
        try:
            # Record payments for unpaid orders (per-order) and mark as Paid
            for oid, desc, tot in self.order_lines:
                amount = float(tot or 0.0)
                if amount <= 0:
                    continue
                cur.execute("INSERT INTO Payments(order_id, amount, gst, method, paid_at) VALUES(?,?,?,?,?)",
                            (oid, amount, 0.0, 'Cash', datetime.date.today().isoformat()))
                cur.execute("UPDATE Orders SET status='Paid' WHERE id=?", (oid,))
            # Update reservation
            cur.execute("UPDATE Reservations SET status='CheckedOut', check_out=? WHERE id=?", (self.checkout_date.isoformat(), self.reservation_id))
            # Free room
            cur.execute("UPDATE Rooms SET status='Available' WHERE id=?", (self.res['room_id'],))
            conn.commit()
            QMessageBox.information(self, "Checkout Complete", f"Customer checked out. Total charged: ₹{self.grand_total:.2f}")
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Checkout Failed", f"Failed to finalize checkout: {e}")
            raise
