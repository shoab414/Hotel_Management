import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QMessageBox, QDoubleSpinBox, QHeaderView, QTabWidget, QDateEdit, QTextEdit
from PySide6.QtCore import Qt, QDate
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
        self.price = QDoubleSpinBox()
        self.price.setMaximum(100000.0)
        self.price.setDecimals(2)
        self.threshold = QSpinBox()
        self.threshold.setMaximum(100000)
        ok = QPushButton("Save")
        ok.clicked.connect(self.accept)
        f.addRow("Name", self.name)
        f.addRow("Quantity", self.qty)
        f.addRow("Unit", self.unit)
        f.addRow("Price per Unit", self.price)
        f.addRow("Threshold", self.threshold)
        f.addRow(ok)

class ConsumptionDialog(QDialog):
    def __init__(self, parent=None, item_name=""):
        super().__init__(parent)
        self.setWindowTitle(f"Record Consumption - {item_name}")
        f = QFormLayout(self)
        self.qty_consumed = QDoubleSpinBox()
        self.qty_consumed.setMaximum(100000.0)
        self.qty_consumed.setDecimals(2)
        self.price = QDoubleSpinBox()
        self.price.setMaximum(100000.0)
        self.price.setDecimals(2)
        self.consumption_date = QDateEdit()
        self.consumption_date.setDate(QDate.currentDate())
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(80)
        ok = QPushButton("Record")
        ok.clicked.connect(self.accept)
        f.addRow("Quantity Consumed", self.qty_consumed)
        f.addRow("Price per Unit", self.price)
        f.addRow("Date", self.consumption_date)
        f.addRow("Notes", self.notes)
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
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Stock Management Tab
        stock_widget = QWidget()
        stock_layout = QVBoxLayout(stock_widget)
        
        top = QHBoxLayout()
        top.setSpacing(12)
        self.btn_add = QPushButton("Add Item")
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_update = QPushButton("Update Stock")
        self.btn_delete = QPushButton("Delete Item")
        top.addWidget(self.btn_add)
        top.addWidget(self.btn_update)
        top.addWidget(self.btn_delete)
        self.alert_lbl = QLabel("")
        self.alert_lbl.setObjectName("LoginMessage")
        top.addWidget(self.alert_lbl, 1)
        stock_layout.addLayout(top)
        
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID","Name","Qty","Unit","Price/Unit","Total Price","Threshold"])
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        stock_layout.addWidget(self.table)
        
        self.tabs.addTab(stock_widget, "Stock Management")
        
        # Consumption Tracking Tab
        consumption_widget = QWidget()
        consumption_layout = QVBoxLayout(consumption_widget)
        
        # Item selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Item:"))
        self.item_selector = QComboBox()
        selector_layout.addWidget(self.item_selector)
        selector_layout.addStretch()
        consumption_layout.addLayout(selector_layout)
        
        # Date range filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Date:"))
        filter_layout.addWidget(QLabel("From:"))
        self.filter_date_from = QDateEdit()
        self.filter_date_from.setDate(QDate.currentDate().addDays(-30))
        self.filter_date_from.dateChanged.connect(self.filter_consumption_by_date)
        filter_layout.addWidget(self.filter_date_from)
        filter_layout.addWidget(QLabel("To:"))
        self.filter_date_to = QDateEdit()
        self.filter_date_to.setDate(QDate.currentDate())
        self.filter_date_to.dateChanged.connect(self.filter_consumption_by_date)
        filter_layout.addWidget(self.filter_date_to)
        self.btn_reset_filter = QPushButton("Reset")
        self.btn_reset_filter.clicked.connect(self.reset_consumption_filter)
        filter_layout.addWidget(self.btn_reset_filter)
        filter_layout.addStretch()
        consumption_layout.addLayout(filter_layout)
        
        consumption_top = QHBoxLayout()
        consumption_top.setSpacing(12)
        self.btn_record_consumption = QPushButton("Record Consumption")
        self.btn_record_consumption.setObjectName("PrimaryButton")
        self.btn_delete_consumption = QPushButton("Delete Record")
        consumption_top.addWidget(self.btn_record_consumption)
        consumption_top.addWidget(self.btn_delete_consumption)
        consumption_top.addStretch()
        consumption_layout.addLayout(consumption_top)
        
        self.consumption_table = QTableWidget(0, 8)
        self.consumption_table.setHorizontalHeaderLabels(["ID","Item","Qty Consumed","Unit","Price","Total Value","Date","Notes"])
        self.consumption_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        consumption_layout.addWidget(self.consumption_table)
        
        # Summary section
        summary_label = QLabel("Consumption Summary")
        summary_label.setObjectName("PageTitle")
        consumption_layout.addWidget(summary_label)
        
        self.summary_table = QTableWidget(0, 4)
        self.summary_table.setHorizontalHeaderLabels(["Item Name","Total Qty Consumed","Unit","Total Amount Spent (₹)"])
        self.summary_table.setMaximumHeight(200)
        self.summary_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        consumption_layout.addWidget(self.summary_table)
        
        self.tabs.addTab(consumption_widget, "Consumption Tracking")
        
        v.addWidget(self.tabs)
        
        self.btn_add.clicked.connect(self.add_item)
        self.btn_update.clicked.connect(self.update_stock)
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_record_consumption.clicked.connect(self.record_consumption)
        self.btn_delete_consumption.clicked.connect(self.delete_consumption_record)
        self.refresh()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id,name,qty,unit,price,total_price,threshold FROM Inventory ORDER BY name")
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        alerts = []
        for i, r in enumerate(rows):
            self.table.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.table.setItem(i,1,QTableWidgetItem(r["name"]))
            self.table.setItem(i,2,QTableWidgetItem(str(r["qty"])))
            self.table.setItem(i,3,QTableWidgetItem(r["unit"]))
            self.table.setItem(i,4,QTableWidgetItem(f"₹{r['price']:.2f}" if r["price"] else "₹0.00"))
            # Use stored total_price or calculate it if not available
            total_price = r["total_price"] if r["total_price"] else (float(r["qty"]) * float(r["price"]) if r["price"] else 0)
            self.table.setItem(i,5,QTableWidgetItem(f"₹{total_price:.2f}"))
            self.table.setItem(i,6,QTableWidgetItem(str(r["threshold"])))
            if r["qty"] <= r["threshold"]:
                alerts.append(r["name"])
        self.alert_lbl.setText("Low stock: " + ", ".join(alerts) if alerts else "")
        
        # Refresh consumption tracking
        self.refresh_consumption_table()
        
        # Refresh item selector combo box
        self.item_selector.blockSignals(True)
        self.item_selector.clear()
        cur.execute("SELECT id, name FROM Inventory ORDER BY name")
        items = cur.fetchall()
        for item in items:
            self.item_selector.addItem(item["name"], item["id"])
        self.item_selector.blockSignals(False)

    def add_item(self):
        dlg = InventoryDialog(self)
        if dlg.exec():
            if not dlg.name.text().strip():
                QMessageBox.warning(self, "Validation", "Item name is required.")
                return
            if not dlg.unit.text().strip():
                QMessageBox.warning(self, "Validation", "Unit is required.")
                return
            
            # Calculate total price
            qty = dlg.qty.value()
            price = dlg.price.value()
            total_price = qty * price
            
            conn = self.controller.db.connect()
            cur = conn.cursor()
            cur.execute("INSERT INTO Inventory(name,qty,unit,price,total_price,threshold) VALUES(?,?,?,?,?,?)",
                        (dlg.name.text().strip(), qty, dlg.unit.text().strip(), price, total_price, dlg.threshold.value()))
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", "Item added successfully.")

    def update_stock(self):
        logging.info("update_stock method called.")
        row = self.table.currentRow()
        if row < 0:
            logging.warning("No item selected for stock update.")
            QMessageBox.warning(self, "Selection", "Please select an item to update.")
            return
        
        try:
            item_id = int(self.table.item(row,0).text())
            logging.info(f"Selected item ID for update: {item_id}")
            dlg = InventoryDialog(self)
            dlg.name.setText(self.table.item(row,1).text())
            dlg.qty.setValue(float(self.table.item(row,2).text()))
            dlg.unit.setText(self.table.item(row,3).text())
            price_text = self.table.item(row,4).text().replace("₹","").strip()
            dlg.price.setValue(float(price_text) if price_text else 0)
            threshold_text = self.table.item(row,6).text()
            dlg.threshold.setValue(int(float(threshold_text)) if threshold_text else 0)
            
            if dlg.exec():
                # Calculate total price
                qty = dlg.qty.value()
                price = dlg.price.value()
                total_price = qty * price
                
                logging.info(f"InventoryDialog accepted for item ID: {item_id}. New values: Name={dlg.name.text()}, Qty={qty}, Unit={dlg.unit.text()}, Price={price}, Total={total_price}, Threshold={dlg.threshold.value()}")
                conn = self.controller.db.connect()
                cur = conn.cursor()
                cur.execute("UPDATE Inventory SET name=?, qty=?, unit=?, price=?, total_price=?, threshold=? WHERE id=?",
                            (dlg.name.text().strip(), qty, dlg.unit.text().strip(), price, total_price, dlg.threshold.value(), item_id))
                conn.commit()
                logging.info(f"Database update committed for item ID: {item_id}.")
                self.refresh()
                QMessageBox.information(self, "Success", "Stock updated successfully.")
            else:
                logging.info(f"InventoryDialog cancelled for item ID: {item_id}.")
        except Exception as e:
            logging.error(f"Error in update_stock: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to update stock: {str(e)}")

    def delete_item(self):
        logging.info("delete_item method called.")
        row = self.table.currentRow()
        if row < 0:
            logging.warning("No item selected for deletion.")
            QMessageBox.warning(self, "Selection", "Please select an item to delete.")
            return

        item_id = int(self.table.item(row, 0).text())
        item_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(self, "Confirm Deletion",
                                     f"Are you sure you want to delete '{item_name}' from inventory?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_inventory_item(item_id)
                QMessageBox.information(self, "Success", f"Item '{item_name}' deleted successfully.")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete item: {e}")
        else:
            logging.info(f"Deletion of item '{item_name}' (ID: {item_id}) cancelled by user.")

    def record_consumption(self):
        # Get selected item from combo box
        if self.item_selector.count() == 0:
            QMessageBox.warning(self, "No Items", "There are no items in inventory. Please add items first.")
            return
        
        item_id = self.item_selector.currentData()
        item_name = self.item_selector.currentText()
        
        if not item_name:
            QMessageBox.warning(self, "Selection", "Please select an item to record consumption.")
            return
        
        # Get item price from database
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT price, qty FROM Inventory WHERE id = ?", (item_id,))
        item = cur.fetchone()
        item_price = item["price"] if item and item["price"] else 0
        available_qty = item["qty"] if item else 0
        
        dlg = ConsumptionDialog(self, item_name)
        dlg.price.setValue(item_price)
        
        if dlg.exec():
            if dlg.qty_consumed.value() <= 0:
                QMessageBox.warning(self, "Validation", "Quantity consumed must be greater than 0.")
                return
            
            # Validate consumption doesn't exceed available quantity
            if dlg.qty_consumed.value() > available_qty:
                QMessageBox.warning(
                    self, 
                    "Insufficient Stock", 
                    f"Cannot consume {dlg.qty_consumed.value()} {item_name}.\nOnly {available_qty} units available in inventory."
                )
                return
            
            total_value = dlg.qty_consumed.value() * dlg.price.value()
            created_at = QDate.currentDate().toString(Qt.ISODate) + "T00:00:00"
            
            conn = self.controller.db.connect()
            cur = conn.cursor()
            
            # Insert consumption record
            cur.execute("""
                INSERT INTO InventoryConsumption(inventory_id, qty_consumed, consumption_date, price, total_value, notes, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
            """, (item_id, dlg.qty_consumed.value(), dlg.consumption_date.date().toString(Qt.ISODate), 
                  dlg.price.value(), total_value, dlg.notes.toPlainText(), created_at))
            
            # Decrease inventory quantity
            cur.execute("""
                UPDATE Inventory 
                SET qty = qty - ?, total_price = qty * price
                WHERE id = ?
            """, (dlg.qty_consumed.value(), item_id))
            
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", f"Consumption recorded for {item_name}.\nInventory quantity decreased by {dlg.qty_consumed.value()} units.")

    def delete_consumption_record(self):
        row = self.consumption_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a consumption record to delete.")
            return
        
        record_id = int(self.consumption_table.item(row,0).text())
        item_name = self.consumption_table.item(row,1).text()
        
        reply = QMessageBox.question(self, "Confirm Deletion",
                                     f"Are you sure you want to delete this consumption record for '{item_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.controller.db.connect()
                cur = conn.cursor()
                cur.execute("DELETE FROM InventoryConsumption WHERE id=?", (record_id,))
                conn.commit()
                QMessageBox.information(self, "Success", "Consumption record deleted successfully.")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {e}")

    def refresh_consumption_table(self):
        """Refresh the consumption tracking table with date filtering"""
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        date_from = self.filter_date_from.date().toString(Qt.ISODate)
        date_to = self.filter_date_to.date().toString(Qt.ISODate)
        
        # Populate consumption details table
        cur.execute("""
            SELECT ic.id, i.name, ic.qty_consumed, i.unit, ic.price, ic.total_value, ic.consumption_date, ic.notes
            FROM InventoryConsumption ic
            JOIN Inventory i ON ic.inventory_id = i.id
            WHERE ic.consumption_date >= ? AND ic.consumption_date <= ?
            ORDER BY ic.consumption_date DESC
        """, (date_from, date_to))
        consumption_rows = cur.fetchall()
        self.consumption_table.setRowCount(len(consumption_rows))
        for i, r in enumerate(consumption_rows):
            self.consumption_table.setItem(i,0,QTableWidgetItem(str(r["id"])))
            self.consumption_table.setItem(i,1,QTableWidgetItem(r["name"]))
            self.consumption_table.setItem(i,2,QTableWidgetItem(str(r["qty_consumed"])))
            self.consumption_table.setItem(i,3,QTableWidgetItem(r["unit"]))
            self.consumption_table.setItem(i,4,QTableWidgetItem(f"₹{r['price']:.2f}"))
            self.consumption_table.setItem(i,5,QTableWidgetItem(f"₹{r['total_value']:.2f}"))
            self.consumption_table.setItem(i,6,QTableWidgetItem(r["consumption_date"]))
            self.consumption_table.setItem(i,7,QTableWidgetItem(r["notes"] if r["notes"] else ""))
        
        # Populate consumption summary table
        cur.execute("""
            SELECT i.name, i.unit, SUM(ic.qty_consumed) as total_qty, SUM(ic.total_value) as total_spent
            FROM InventoryConsumption ic
            JOIN Inventory i ON ic.inventory_id = i.id
            WHERE ic.consumption_date >= ? AND ic.consumption_date <= ?
            GROUP BY ic.inventory_id, i.name, i.unit
            ORDER BY i.name
        """, (date_from, date_to))
        summary_rows = cur.fetchall()
        self.summary_table.setRowCount(len(summary_rows))
        
        total_amount_spent = 0
        for i, r in enumerate(summary_rows):
            self.summary_table.setItem(i,0,QTableWidgetItem(r["name"]))
            self.summary_table.setItem(i,1,QTableWidgetItem(f"{r['total_qty']:.2f}"))
            self.summary_table.setItem(i,2,QTableWidgetItem(r["unit"]))
            total_amount_spent += r['total_spent'] if r['total_spent'] else 0
            self.summary_table.setItem(i,3,QTableWidgetItem(f"₹{r['total_spent']:.2f}" if r['total_spent'] else "₹0.00"))
        
        # Add total row
        if len(summary_rows) > 0:
            self.summary_table.insertRow(self.summary_table.rowCount())
            total_row = self.summary_table.rowCount() - 1
            self.summary_table.setItem(total_row, 0, QTableWidgetItem("TOTAL"))
            self.summary_table.setItem(total_row, 1, QTableWidgetItem(""))
            self.summary_table.setItem(total_row, 2, QTableWidgetItem(""))
            self.summary_table.setItem(total_row, 3, QTableWidgetItem(f"₹{total_amount_spent:.2f}"))
            
            # Make total row bold
            for col in range(4):
                item = self.summary_table.item(total_row, col)
                if item:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

    def filter_consumption_by_date(self):
        """Update consumption table when date filter changes"""
        self.refresh_consumption_table()

    def reset_consumption_filter(self):
        """Reset date filter to default (last 30 days)"""
        self.filter_date_from.blockSignals(True)
        self.filter_date_to.blockSignals(True)
        self.filter_date_from.setDate(QDate.currentDate().addDays(-30))
        self.filter_date_to.setDate(QDate.currentDate())
        self.filter_date_from.blockSignals(False)
        self.filter_date_to.blockSignals(False)
        self.refresh_consumption_table()
