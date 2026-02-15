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

        header_label = QLabel("Table Management")
        header_label.setObjectName("HeaderLabel") # For QSS styling
        tables_layout.addWidget(header_label)

        # Add Table Button
        button_layout = QHBoxLayout()
        self.btn_add_table = QPushButton("Add New Table")
        self.btn_add_table.setObjectName("PrimaryButton")
        self.btn_add_table.clicked.connect(self.add_new_table)
        button_layout.addWidget(self.btn_add_table)
        button_layout.addStretch() # Push button to the left
        tables_layout.addLayout(button_layout)

        self.tables_grid = QGridLayout()
        self.tables_grid.setSpacing(15) # Increased spacing for better visual separation
        self.tables_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft) # Align grid to top-left
        tables_layout.addLayout(self.tables_grid)
        tables_layout.addStretch()
        self.refresh_tables()

    def refresh_tables(self):
        logging.debug("refresh_tables called")
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
        logging.debug(f"Fetched {len(tables)} tables from the database.")

        row = 0
        col = 0
        for table in tables:
            logging.debug(f"Processing Table: ID={table['id']}, Number={table['number']}, Status={table['status']}")
            btn = QPushButton(f"Table {table['number']}\n({table['status']})")
            btn.setFixedSize(120, 100) # Slightly larger buttons
            btn.setObjectName("TableButton") # For QSS styling
            if table['status'] == 'Available':
                btn.setStyleSheet("""
                    QPushButton#TableButton {
                        background-color: #66BB6A; /* Light Green */
                        color: white;
                        border-radius: 8px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton#TableButton:hover {
                        background-color: #81C784; /* Lighter Green on hover */
                    }
                """)
            elif table['status'] == 'Occupied':
                btn.setStyleSheet("""
                    QPushButton#TableButton {
                        background-color: #FFA726; /* Orange */
                        color: white;
                        border-radius: 8px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton#TableButton:hover {
                        background-color: #FFB74D; /* Lighter Orange on hover */
                    }
                """)
            elif table['status'] == 'Cleaning':
                btn.setStyleSheet("""
                    QPushButton#TableButton {
                        background-color: #78909C; /* Blue Grey */
                        color: white;
                        border-radius: 8px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton#TableButton:hover {
                        background-color: #90A4AE; /* Lighter Blue Grey on hover */
                    }
                """)
            else: # Default/Unknown status
                btn.setStyleSheet("""
                    QPushButton#TableButton {
                        background-color: #42A5F5; /* Blue */
                        color: white;
                        border-radius: 8px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton#TableButton:hover {
                        background-color: #64B5F6; /* Lighter Blue on hover */
                    }
                """)
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

    def add_new_table(self):
        logging.debug("Add New Table button clicked.")
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT MAX(number) FROM Tables")
        max_table_number = cur.fetchone()[0]
        next_table_number = (max_table_number or 0) + 1

        try:
            cur.execute("INSERT INTO Tables (number, status) VALUES (?, ?)", (next_table_number, "Available"))
            conn.commit()
            MessageBox.success(self, "Table Added", f"Table {next_table_number} added successfully!")
            self.refresh_tables()
        except Exception as e:
            conn.rollback()
            MessageBox.critical(self, "Error", f"Failed to add new table: {e}")
