from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QTabWidget, QGridLayout, QMessageBox
from PySide6.QtCore import Qt
import logging
from app.views.table_management_dialog import TableManagementDialog
from app.utils.message import MessageBox # Assuming MessageBox is in utils

class TableView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        tables_layout = QVBoxLayout(self)
        tables_layout.setSpacing(16)
        self.tables_grid = QGridLayout()
        self.tables_grid.setSpacing(10)
        tables_layout.addLayout(self.tables_grid)
        tables_layout.addStretch()
        self.refresh_tables()

    def refresh_tables(self):
        # Clear existing buttons
        while self.tables_grid.count():
            item = self.tables_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater() # Schedule for deletion
            del item # Delete the layout item

        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, number, status FROM Tables ORDER BY number")
        tables = cur.fetchall()

        row = 0
        col = 0
        for table in tables:
            btn = QPushButton(f"Table {table['number']}\n({table['status']})")
            btn.setFixedSize(100, 80)
            btn.setProperty("class", "table-button")
            if table['status'] == 'Available':
                btn.setStyleSheet("background-color: #4CAF50; color: white;") # Green
            elif table['status'] == 'Occupied':
                btn.setStyleSheet("background-color: #FFC107; color: black;") # Amber
            elif table['status'] == 'Cleaning':
                btn.setStyleSheet("background-color: #9E9E9E; color: white;") # Grey
            else:
                btn.setStyleSheet("background-color: #2196F3; color: white;") # Blue (default)
            btn.clicked.connect(lambda checked, t=table: self.open_table_management(t['id']))
            logging.info(f"Connected click signal for Table {table['number']} (ID: {table['id']}, Status: {table['status']})")
            self.tables_grid.addWidget(btn, row, col)
            col += 1
            if col > 4: # Max 5 tables per row
                col = 0
                row += 1

    def open_table_management(self, table_id):
        logging.info(f"Attempting to open TableManagementDialog for table_id: {table_id}")
        dlg = TableManagementDialog(table_id, self.controller, self)
        logging.info(f"TableManagementDialog instance created for table_id: {table_id}")
        dlg.exec()
        logging.info(f"TableManagementDialog for table_id: {table_id} closed.")
        self.refresh_tables() # Refresh tables display after dialog closes
