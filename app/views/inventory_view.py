from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QSpinBox, QDoubleSpinBox, QDialog, QFormLayout, QLineEdit, QComboBox, QLabel, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent

class InventoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inventory Item")
        f = QFormLayout(self)
        self.name = QLineEdit()
        self.qty = QDoubleSpinBox()
        self.qty.setMaximum(100000.0)
        self.qty.setDecimals(2)
        self.unit = QLineEdit()
        self.threshold = QSpinBox()
        self.threshold.setMaximum(100000)
        ok = QPushButton("Save")
        ok.clicked.connect(self.accept)
        f.addRow("Name", self.name)
        f.addRow("Quantity", self.qty)
        f.addRow("Unit", self.unit)
        f.addRow("Threshold", self.threshold)
        f.addRow(ok)

class InventoryView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        v = QVBoxLayout(self)
        v.setSpacing(20)
        page_title = QLabel("Inventory")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Manage stock and track low inventory alerts")
        page_subtitle.setObjectName("PageSubtitle")
        v.addWidget(page_title)
        v.addWidget(page_subtitle)
        top = QHBoxLayout()
        top.setSpacing(12)
        self.btn_add = QPushButton("Add Item")
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_update = QPushButton("Update Stock")
        top.addWidget(self.btn_add)
        top.addWidget(self.btn_update)
        self.alert_lbl = QLabel("")
        self.alert_lbl.setObjectName("LoginMessage")
        top.addWidget(self.alert_lbl, 1)
        v.addLayout(top)
        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels(["ID","Name","Qty","Unit","Threshold"])
        v.addWidget(self.table)
        self.btn_add.clicked.connect(self.add_item)
        self.btn_update.clicked.connect(self.update_stock)
        self.refresh()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id,name,qty,unit,threshold FROM Inventory ORDER BY name")
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        alerts = []
        for i, r in enumerate(rows):
            self.table.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.table.setItem(i,1,QTableWidgetItem(r["name"]))
            self.table.setItem(i,2,QTableWidgetItem(str(r["qty"])))
            self.table.setItem(i,3,QTableWidgetItem(r["unit"]))
            self.table.setItem(i,4,QTableWidgetItem(str(r["threshold"])))
            if r["qty"] <= r["threshold"]:
                alerts.append(r["name"])
        self.alert_lbl.setText("Low stock: " + ", ".join(alerts) if alerts else "")

    def add_item(self):
        dlg = InventoryDialog(self)
        if dlg.exec():
            if not dlg.name.text().strip():
                QMessageBox.warning(self, "Validation", "Item name is required.")
                return
            if not dlg.unit.text().strip():
                QMessageBox.warning(self, "Validation", "Unit is required.")
                return
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("INSERT INTO Inventory(name,qty,unit,threshold) VALUES(?,?,?,?)",
                        (dlg.name.text().strip(), dlg.qty.value(), dlg.unit.text().strip(), dlg.threshold.value()))
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", "Item added successfully.")

    def update_stock(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select an item to update.")
            return
        item_id = int(self.table.item(row,0).text())
        dlg = InventoryDialog(self)
        dlg.name.setText(self.table.item(row,1).text())
        dlg.qty.setValue(float(self.table.item(row,2).text()))
        dlg.unit.setText(self.table.item(row,3).text())
        dlg.threshold.setValue(int(self.table.item(row,4).text()))
        if dlg.exec():
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("UPDATE Inventory SET name=?, qty=?, unit=?, threshold=? WHERE id=?",
                        (dlg.name.text().strip(), float(dlg.qty.value()), dlg.unit.text().strip(), dlg.threshold.value(), item_id))
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", "Stock updated successfully.")
