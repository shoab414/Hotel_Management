from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QLabel, QMessageBox
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
        page_subtitle = QLabel("View orders and generate invoices")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)
        top = QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(QLabel("Payment method"))
        self.method = QComboBox()
        self.method.addItems(["Cash","Card","UPI"])
        self.method.setMinimumWidth(120)
        top.addWidget(self.method)
        self.btn_invoice = QPushButton("Generate Invoice PDF")
        self.btn_invoice.setObjectName("PrimaryButton")
        top.addWidget(self.btn_invoice)
        top.addStretch()
        v.addLayout(top)
        self.orders = QTableWidget(0,4)
        self.orders.setHorizontalHeaderLabels(["Order ID","Items","Amount","Status"])
        v.addWidget(self.orders)
        self.btn_invoice.clicked.connect(self.generate_invoice)
        self.refresh()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT Orders.id AS oid, COUNT(OrderDetails.id) AS items, COALESCE(SUM(OrderDetails.qty*OrderDetails.price),0) AS amt, Orders.status AS st
            FROM Orders LEFT JOIN OrderDetails ON Orders.id=OrderDetails.order_id
            GROUP BY Orders.id ORDER BY Orders.id DESC LIMIT 20
        """)
        rows = cur.fetchall()
        self.orders.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.orders.setItem(i,0,QTableWidgetItem(str(r["oid"])))
            self.orders.setItem(i,1,QTableWidgetItem(str(r["items"])))
            self.orders.setItem(i,2,QTableWidgetItem(f"{r['amt']:.2f}"))
            self.orders.setItem(i,3,QTableWidgetItem(r["st"]))

    def generate_invoice(self):
        row = self.orders.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select an order to generate invoice.")
            return
        oid = int(self.orders.item(row,0).text())
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT MenuItems.name AS name, OrderDetails.qty AS qty, OrderDetails.price AS price FROM OrderDetails JOIN MenuItems ON OrderDetails.item_id=MenuItems.id WHERE order_id=?", (oid,))
        items = cur.fetchall()
        cur.execute("SELECT COALESCE(SUM(qty*price),0) AS amt FROM OrderDetails WHERE order_id=?", (oid,))
        amt = float(cur.fetchone()["amt"] or 0)
        gst = round(amt*0.18,2)
        total = amt + gst
        html = "<h2>Invoice</h2>"
        html += f"<p>Order #{oid} - {datetime.datetime.now().isoformat()}</p>"
        html += "<table border='1' cellspacing='0' cellpadding='4'><tr><th>Item</th><th>Qty</th><th>Price</th></tr>"
        for it in items:
            html += f"<tr><td>{it['name']}</td><td>{it['qty']}</td><td>{it['price']:.2f}</td></tr>"
        html += "</table>"
        html += f"<p>Subtotal: ₹{amt:.2f}</p><p>GST (18%): ₹{gst:.2f}</p><h3>Total: ₹{total:.2f}</h3>"
        html += f"<p>Payment Method: {self.method.currentText()}</p>"
        doc = QTextDocument()
        doc.setHtml(html)
        pdf_path = os.path.join(os.getcwd(), f"invoice_{oid}.pdf")
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(pdf_path)
        doc.print(printer)
        QMessageBox.information(self, "Invoice", f"Invoice saved as invoice_{oid}.pdf")
