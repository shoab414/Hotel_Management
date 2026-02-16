"""Inventory Management Module - Manage stock and track consumption."""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog,
    QFormLayout, QLabel, QMessageBox, QDoubleSpinBox, QHeaderView,
    QTabWidget, QDateEdit, QTextEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QShowEvent

# Constants
MAX_SPINBOX_VALUE = 100000.0
MAX_SPINBOX_INT = 100000
NOTES_MAX_HEIGHT = 80
DECIMALS = 2


class InventoryDialog(QDialog):
    """Dialog for adding or editing inventory items."""

    def __init__(self, parent=None):
        """Initialize inventory item dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Inventory Item")
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface for inventory dialog."""
        form_layout = QFormLayout(self)
        
        self.name = QLineEdit()
        self.qty = QDoubleSpinBox()
        self.qty.setMaximum(MAX_SPINBOX_VALUE)
        self.qty.setDecimals(DECIMALS)
        
        self.unit = QLineEdit()
        
        self.price = QDoubleSpinBox()
        self.price.setMaximum(MAX_SPINBOX_VALUE)
        self.price.setDecimals(DECIMALS)
        
        self.threshold = QSpinBox()
        self.threshold.setMaximum(MAX_SPINBOX_INT)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        
        form_layout.addRow("Name", self.name)
        form_layout.addRow("Quantity", self.qty)
        form_layout.addRow("Unit", self.unit)
        form_layout.addRow("Price per Unit", self.price)
        form_layout.addRow("Threshold", self.threshold)
        form_layout.addRow(save_button)


class ConsumptionDialog(QDialog):
    """Dialog for recording inventory consumption."""

    def __init__(self, parent=None, item_name=""):
        """Initialize consumption dialog.
        
        Args:
            parent: Parent widget
            item_name: Name of the inventory item
        """
        super().__init__(parent)
        self.setWindowTitle(f"Record Consumption - {item_name}")
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface for consumption dialog."""
        form_layout = QFormLayout(self)
        
        self.qty_consumed = QDoubleSpinBox()
        self.qty_consumed.setMaximum(MAX_SPINBOX_VALUE)
        self.qty_consumed.setDecimals(DECIMALS)
        
        self.price = QDoubleSpinBox()
        self.price.setMaximum(MAX_SPINBOX_VALUE)
        self.price.setDecimals(DECIMALS)
        
        self.consumption_date = QDateEdit()
        self.consumption_date.setDate(QDate.currentDate())
        
        self.notes = QTextEdit()
        self.notes.setMaximumHeight(NOTES_MAX_HEIGHT)
        
        record_button = QPushButton("Record")
        record_button.clicked.connect(self.accept)
        
        form_layout.addRow("Quantity Consumed", self.qty_consumed)
        form_layout.addRow("Price per Unit", self.price)
        form_layout.addRow("Date", self.consumption_date)
        form_layout.addRow("Notes", self.notes)
        form_layout.addRow(record_button)

class InventoryView(QWidget):
    """Main inventory management view with stock and consumption tracking."""

    def __init__(self, controller):
        """Initialize inventory view.
        
        Args:
            controller: Application controller instance
        """
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface for inventory management."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Add header
        page_title = QLabel("Inventory")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Manage stock and track low inventory alerts")
        page_subtitle.setObjectName("PageSubtitle")
        main_layout.addWidget(page_title)
        main_layout.addWidget(page_subtitle)
        
        # Create tabs
        self.tabs = QTabWidget()
        self._setup_stock_tab()
        self._setup_consumption_tab()
        
        main_layout.addWidget(self.tabs)
        self._connect_signals()
        self.refresh()

    def _setup_stock_tab(self):
        """Set up the stock management tab."""
        stock_widget = QWidget()
        stock_layout = QVBoxLayout(stock_widget)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        self.btn_add = QPushButton("Add Item")
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_update = QPushButton("Update Stock")
        self.btn_delete = QPushButton("Delete Item")
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_update)
        button_layout.addWidget(self.btn_delete)
        
        self.alert_lbl = QLabel("")
        self.alert_lbl.setObjectName("LoginMessage")
        button_layout.addWidget(self.alert_lbl, 1)
        stock_layout.addLayout(button_layout)
        
        # Stock table
        self.table = QTableWidget(0, 7)
        headers = ["ID", "Name", "Qty", "Unit", "Price/Unit", "Total Price", "Threshold"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        stock_layout.addWidget(self.table)
        
        self.tabs.addTab(stock_widget, "Stock Management")

    def _setup_consumption_tab(self):
        """Set up the consumption tracking tab."""
        consumption_widget = QWidget()
        consumption_layout = QVBoxLayout(consumption_widget)
        
        # Item selector
        self._setup_item_selector(consumption_layout)
        
        # Date range filter
        self._setup_date_filter(consumption_layout)
        
        # Consumption control buttons
        self._setup_consumption_buttons(consumption_layout)
        
        # Consumption details table
        self.consumption_table = QTableWidget(0, 8)
        headers = ["ID", "Item", "Qty Consumed", "Unit", "Price", "Total Value", "Date", "Notes"]
        self.consumption_table.setHorizontalHeaderLabels(headers)
        self.consumption_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        consumption_layout.addWidget(self.consumption_table)
        
        # Summary section
        summary_label = QLabel("Consumption Summary")
        summary_label.setObjectName("PageTitle")
        consumption_layout.addWidget(summary_label)
        
        self.summary_table = QTableWidget(0, 4)
        headers = ["Item Name", "Total Qty Consumed", "Unit", "Total Amount Spent (₹)"]
        self.summary_table.setHorizontalHeaderLabels(headers)
        self.summary_table.setMaximumHeight(200)
        self.summary_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        consumption_layout.addWidget(self.summary_table)
        
        self.tabs.addTab(consumption_widget, "Consumption Tracking")

    def _setup_item_selector(self, parent_layout):
        """Set up item selector combo box."""
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Item:"))
        self.item_selector = QComboBox()
        selector_layout.addWidget(self.item_selector)
        selector_layout.addStretch()
        parent_layout.addLayout(selector_layout)

    def _setup_date_filter(self, parent_layout):
        """Set up date range filter for consumption tracking."""
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
        parent_layout.addLayout(filter_layout)

    def _setup_consumption_buttons(self, parent_layout):
        """Set up consumption control buttons."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        self.btn_record_consumption = QPushButton("Record Consumption")
        self.btn_record_consumption.setObjectName("PrimaryButton")
        self.btn_delete_consumption = QPushButton("Delete Record")
        button_layout.addWidget(self.btn_record_consumption)
        button_layout.addWidget(self.btn_delete_consumption)
        button_layout.addStretch()
        parent_layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect all UI signals to their slots."""
        self.btn_add.clicked.connect(self.add_item)
        self.btn_update.clicked.connect(self.update_stock)
        self.btn_delete.clicked.connect(self.delete_item)
        self.btn_record_consumption.clicked.connect(self.record_consumption)
        self.btn_delete_consumption.clicked.connect(self.delete_consumption_record)

    def showEvent(self, event: QShowEvent):
        """Handle show event by refreshing data."""
        super().showEvent(event)
        self.refresh()

    def refresh(self):
        """Refresh inventory tables and alert labels."""
        self._refresh_stock_table()
        self._refresh_item_selector()
        self._refresh_consumption_table()

    def _refresh_stock_table(self):
        """Refresh the stock management table with current inventory."""
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, qty, unit, price, total_price, threshold FROM Inventory ORDER BY name"
        )
        rows = cur.fetchall()
        
        self.table.setRowCount(len(rows))
        low_stock_items = []
        
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row["name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(row["qty"])))
            self.table.setItem(row_idx, 3, QTableWidgetItem(row["unit"]))
            
            price_display = f"₹{row['price']:.2f}" if row["price"] else "₹0.00"
            self.table.setItem(row_idx, 4, QTableWidgetItem(price_display))
            
            # Use stored total_price or calculate
            total_price = row["total_price"] if row["total_price"] else (
                float(row["qty"]) * float(row["price"]) if row["price"] else 0
            )
            total_display = f"₹{total_price:.2f}"
            self.table.setItem(row_idx, 5, QTableWidgetItem(total_display))
            self.table.setItem(row_idx, 6, QTableWidgetItem(str(row["threshold"])))
            
            if row["qty"] <= row["threshold"]:
                low_stock_items.append(row["name"])
        
        # Update alert label
        alert_text = "Low stock: " + ", ".join(low_stock_items) if low_stock_items else ""
        self.alert_lbl.setText(alert_text)

    def _refresh_item_selector(self):
        """Refresh the item selector combo box."""
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        self.item_selector.blockSignals(True)
        self.item_selector.clear()
        
        cur.execute("SELECT id, name FROM Inventory ORDER BY name")
        items = cur.fetchall()
        for item in items:
            self.item_selector.addItem(item["name"], item["id"])
        
        self.item_selector.blockSignals(False)

    def add_item(self):
        """Open dialog to add a new inventory item."""
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
            cur.execute(
                "INSERT INTO Inventory(name,qty,unit,price,total_price,threshold) VALUES(?,?,?,?,?,?)",
                (dlg.name.text().strip(), qty, dlg.unit.text().strip(), 
                 price, total_price, dlg.threshold.value())
            )
            conn.commit()
            self.refresh()
            QMessageBox.information(self, "Success", "Item added successfully.")

    def update_stock(self):
        """Open dialog to update existing inventory item stock."""
        row = self.table.currentRow()
        if row < 0:
            logging.warning("No item selected for stock update.")
            QMessageBox.warning(self, "Selection", "Please select an item to update.")
            return
        
        try:
            item_id = int(self.table.item(row, 0).text())
            logging.info(f"Selected item ID for update: {item_id}")
            
            dlg = InventoryDialog(self)
            dlg.name.setText(self.table.item(row, 1).text())
            dlg.qty.setValue(float(self.table.item(row, 2).text()))
            dlg.unit.setText(self.table.item(row, 3).text())
            
            price_text = self.table.item(row, 4).text().replace("₹", "").strip()
            dlg.price.setValue(float(price_text) if price_text else 0)
            
            threshold_text = self.table.item(row, 6).text()
            dlg.threshold.setValue(int(float(threshold_text)) if threshold_text else 0)
            
            if dlg.exec():
                qty = dlg.qty.value()
                price = dlg.price.value()
                total_price = qty * price
                
                logging.info(f"Updating item ID: {item_id} with new values")
                conn = self.controller.db.connect()
                cur = conn.cursor()
                cur.execute(
                    "UPDATE Inventory SET name=?, qty=?, unit=?, price=?, total_price=?, threshold=? WHERE id=?",
                    (dlg.name.text().strip(), qty, dlg.unit.text().strip(), 
                     price, total_price, dlg.threshold.value(), item_id)
                )
                conn.commit()
                logging.info(f"Database update committed for item ID: {item_id}")
                self.refresh()
                QMessageBox.information(self, "Success", "Stock updated successfully.")
        except Exception as e:
            logging.error(f"Error in update_stock: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to update stock: {str(e)}")

    def delete_item(self):
        """Delete selected inventory item."""
        row = self.table.currentRow()
        if row < 0:
            logging.warning("No item selected for deletion.")
            QMessageBox.warning(self, "Selection", "Please select an item to delete.")
            return

        item_id = int(self.table.item(row, 0).text())
        item_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{item_name}' from inventory?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

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
        """Record consumption for a selected inventory item."""
        if self.item_selector.count() == 0:
            QMessageBox.warning(
                self, "No Items",
                "There are no items in inventory. Please add items first."
            )
            return
        
        item_id = self.item_selector.currentData()
        item_name = self.item_selector.currentText()
        
        if not item_name:
            QMessageBox.warning(self, "Selection", "Please select an item to record consumption.")
            return
        
        # Get item price and quantity from database
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
                QMessageBox.warning(
                    self, "Validation",
                    "Quantity consumed must be greater than 0."
                )
                return
            
            # Validate consumption doesn't exceed available quantity
            if dlg.qty_consumed.value() > available_qty:
                QMessageBox.warning(
                    self, "Insufficient Stock",
                    f"Cannot consume {dlg.qty_consumed.value()} {item_name}.\n"
                    f"Only {available_qty} units available in inventory."
                )
                return
            
            self._save_consumption_record(item_id, item_name, dlg, available_qty)

    def _save_consumption_record(self, item_id, item_name, dialog, available_qty):
        """Save consumption record to database and update inventory.
        
        Args:
            item_id: ID of the inventory item
            item_name: Name of the inventory item
            dialog: ConsumptionDialog instance with user input
            available_qty: Available quantity in inventory
        """
        total_value = dialog.qty_consumed.value() * dialog.price.value()
        created_at = QDate.currentDate().toString(Qt.ISODate) + "T00:00:00"
        
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        # Insert consumption record
        cur.execute(
            """INSERT INTO InventoryConsumption
               (inventory_id, qty_consumed, consumption_date, price, total_value, notes, created_at)
               VALUES(?, ?, ?, ?, ?, ?, ?)""",
            (item_id, dialog.qty_consumed.value(),
             dialog.consumption_date.date().toString(Qt.ISODate),
             dialog.price.value(), total_value,
             dialog.notes.toPlainText(), created_at)
        )
        
        # Decrease inventory quantity
        cur.execute(
            "UPDATE Inventory SET qty = qty - ?, total_price = qty * price WHERE id = ?",
            (dialog.qty_consumed.value(), item_id)
        )
        
        conn.commit()
        self.refresh()
        
        QMessageBox.information(
            self, "Success",
            f"Consumption recorded for {item_name}.\n"
            f"Inventory quantity decreased by {dialog.qty_consumed.value()} units."
        )

    def delete_consumption_record(self):
        """Delete selected consumption record."""
        row = self.consumption_table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Selection",
                "Please select a consumption record to delete."
            )
            return
        
        record_id = int(self.consumption_table.item(row, 0).text())
        item_name = self.consumption_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete this consumption record for '{item_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
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
        """Refresh the consumption tracking table with date filtering."""
        self._refresh_consumption_table()

    def _refresh_consumption_table(self):
        """Refresh consumption details and summary tables."""
        conn = self.controller.db.connect()
        cur = conn.cursor()
        
        date_from = self.filter_date_from.date().toString(Qt.ISODate)
        date_to = self.filter_date_to.date().toString(Qt.ISODate)
        
        # Populate consumption details table
        cur.execute(
            """SELECT ic.id, i.name, ic.qty_consumed, i.unit, ic.price,
                      ic.total_value, ic.consumption_date, ic.notes
               FROM InventoryConsumption ic
               JOIN Inventory i ON ic.inventory_id = i.id
               WHERE ic.consumption_date >= ? AND ic.consumption_date <= ?
               ORDER BY ic.consumption_date DESC""",
            (date_from, date_to)
        )
        consumption_rows = cur.fetchall()
        self.consumption_table.setRowCount(len(consumption_rows))
        
        for row_idx, row in enumerate(consumption_rows):
            self.consumption_table.setItem(row_idx, 0, QTableWidgetItem(str(row["id"])))
            self.consumption_table.setItem(row_idx, 1, QTableWidgetItem(row["name"]))
            self.consumption_table.setItem(row_idx, 2, QTableWidgetItem(str(row["qty_consumed"])))
            self.consumption_table.setItem(row_idx, 3, QTableWidgetItem(row["unit"]))
            self.consumption_table.setItem(row_idx, 4, QTableWidgetItem(f"₹{row['price']:.2f}"))
            self.consumption_table.setItem(row_idx, 5, QTableWidgetItem(f"₹{row['total_value']:.2f}"))
            self.consumption_table.setItem(row_idx, 6, QTableWidgetItem(row["consumption_date"]))
            self.consumption_table.setItem(row_idx, 7, QTableWidgetItem(row["notes"] if row["notes"] else ""))
        
        # Populate consumption summary table
        cur.execute(
            """SELECT i.name, i.unit, SUM(ic.qty_consumed) as total_qty,
                      SUM(ic.total_value) as total_spent
               FROM InventoryConsumption ic
               JOIN Inventory i ON ic.inventory_id = i.id
               WHERE ic.consumption_date >= ? AND ic.consumption_date <= ?
               GROUP BY ic.inventory_id, i.name, i.unit
               ORDER BY i.name""",
            (date_from, date_to)
        )
        summary_rows = cur.fetchall()
        self.summary_table.setRowCount(len(summary_rows))
        
        total_amount_spent = 0
        for row_idx, row in enumerate(summary_rows):
            self.summary_table.setItem(row_idx, 0, QTableWidgetItem(row["name"]))
            self.summary_table.setItem(row_idx, 1, QTableWidgetItem(f"{row['total_qty']:.2f}"))
            self.summary_table.setItem(row_idx, 2, QTableWidgetItem(row["unit"]))
            
            amount = row['total_spent'] if row['total_spent'] else 0
            total_amount_spent += amount
            self.summary_table.setItem(
                row_idx, 3,
                QTableWidgetItem(f"₹{amount:.2f}")
            )
        
        # Add total row if there are items
        if len(summary_rows) > 0:
            self.summary_table.insertRow(self.summary_table.rowCount())
            total_row_idx = self.summary_table.rowCount() - 1
            
            self.summary_table.setItem(total_row_idx, 0, QTableWidgetItem("TOTAL"))
            self.summary_table.setItem(total_row_idx, 1, QTableWidgetItem(""))
            self.summary_table.setItem(total_row_idx, 2, QTableWidgetItem(""))
            self.summary_table.setItem(
                total_row_idx, 3,
                QTableWidgetItem(f"₹{total_amount_spent:.2f}")
            )
            
            # Make total row bold
            for col in range(4):
                item = self.summary_table.item(total_row_idx, col)
                if item:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

    def filter_consumption_by_date(self):
        """Update consumption table when date filter changes."""
        self._refresh_consumption_table()

    def reset_consumption_filter(self):
        """Reset date filter to default (last 30 days)."""
        self.filter_date_from.blockSignals(True)
        self.filter_date_to.blockSignals(True)
        
        self.filter_date_from.setDate(QDate.currentDate().addDays(-30))
        self.filter_date_to.setDate(QDate.currentDate())
        
        self.filter_date_from.blockSignals(False)
        self.filter_date_to.blockSignals(False)
        
        self._refresh_consumption_table()
