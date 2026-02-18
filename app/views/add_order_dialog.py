from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QListWidget, QListWidgetItem, QLineEdit
from PySide6.QtCore import Qt
import logging
import datetime
from app.utils.message import MessageBox

class AddOrderDialog(QDialog):
    def __init__(self, table_id, controller, parent=None):
        super().__init__(parent)
        self.table_id = table_id
        self.controller = controller
        self.setWindowTitle(f"Add Order for Table {self.get_table_number(table_id)}")
        self.setMinimumSize(600, 500)

        self.selected_items = {} # {menu_item_id: quantity}

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel(f"Add New Order for Table {self.get_table_number(table_id)}")
        self.title_label.setObjectName("PageTitle")
        self.layout.addWidget(self.title_label)

        # Search and Menu Items
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search menu items...")
        self.search_input.textChanged.connect(self.filter_menu_items)
        self.layout.addWidget(self.search_input)

        self.menu_list = QListWidget()
        self.menu_list.itemDoubleClicked.connect(self.add_item_to_order)
        self.layout.addWidget(self.menu_list)

        # Selected Items Display
        self.selected_items_label = QLabel("Selected Items:")
        self.layout.addWidget(self.selected_items_label)
        self.selected_items_list = QListWidget()
        self.layout.addWidget(self.selected_items_list)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.btn_add_to_order = QPushButton("Add Selected to Order")
        self.btn_add_to_order.setObjectName("PrimaryButton")
        self.btn_add_to_order.clicked.connect(self.add_item_to_order)
        self.btn_remove_from_order = QPushButton("Remove from Order")
        self.btn_remove_from_order.clicked.connect(self.remove_item_from_order)
        self.btn_save_order = QPushButton("Save Order")
        self.btn_save_order.setObjectName("PrimaryButton")
        self.btn_save_order.clicked.connect(self.save_order)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)

        self.button_layout.addWidget(self.btn_add_to_order)
        self.button_layout.addWidget(self.btn_remove_from_order)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_save_order)
        self.button_layout.addWidget(self.btn_cancel)
        self.layout.addLayout(self.button_layout)

        self.load_menu_items()
        self.update_selected_items_display()

    def get_table_number(self, table_id):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT number FROM Tables WHERE id = ?", (table_id,))
        result = cur.fetchone()
        return result['number'] if result else "N/A"

    def load_menu_items(self):
        self.menu_list.clear()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price FROM MenuItems ORDER BY name")
        self.all_menu_items = cur.fetchall()
        self.filter_menu_items()

    def filter_menu_items(self):
        self.menu_list.clear()
        search_text = self.search_input.text().strip().lower()
        for item in self.all_menu_items:
            if search_text in item['name'].lower():
                list_item = QListWidgetItem(f"{item['name']} (₹{item['price']:.2f})")
                list_item.setData(Qt.UserRole, item['id'])
                self.menu_list.addItem(list_item)

    def add_item_to_order(self):
        selected_item = self.menu_list.currentItem()
        if not selected_item:
            MessageBox.warning(self, "No Item Selected", "Please select a menu item to add.")
            return

        menu_item_id = selected_item.data(Qt.UserRole)
        
        # Prompt for quantity
        quantity, ok = QSpinBox(self).value, True # Placeholder, will replace with QInputDialog
        
        # For now, let's use a simple spinbox for quantity
        spinbox = QSpinBox(self)
        spinbox.setMinimum(1)
        spinbox.setMaximum(100)
        spinbox.setValue(1)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Quantity")
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(QLabel(f"Enter quantity for {selected_item.text()}:"))
        dialog_layout.addWidget(spinbox)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        dialog_layout.addWidget(ok_button)
        
        if dialog.exec() == QDialog.Accepted:
            quantity = spinbox.value()
            if menu_item_id in self.selected_items:
                self.selected_items[menu_item_id] += quantity
            else:
                self.selected_items[menu_item_id] = quantity
            self.update_selected_items_display()
        
    def remove_item_from_order(self):
        selected_item = self.selected_items_list.currentItem()
        if not selected_item:
            MessageBox.warning(self, "No Item Selected", "Please select an item to remove from the order.")
            return
        
        menu_item_id = selected_item.data(Qt.UserRole)
        if menu_item_id in self.selected_items:
            del self.selected_items[menu_item_id]
            self.update_selected_items_display()

    def update_selected_items_display(self):
        self.selected_items_list.clear()
        conn = self.controller.db.connect()
        cur = conn.cursor()
        for item_id, quantity in self.selected_items.items():
            cur.execute("SELECT name, price FROM MenuItems WHERE id = ?", (item_id,))
            item_info = cur.fetchone()
            if item_info:
                list_item = QListWidgetItem(f"{quantity}x {item_info['name']} (₹{item_info['price']:.2f} each)")
                list_item.setData(Qt.UserRole, item_id)
                self.selected_items_list.addItem(list_item)

    def save_order(self):
        if not self.selected_items:
            MessageBox.warning(self, "No Items", "Please add items to the order before saving.")
            return

        conn = self.controller.db.connect()
        cur = conn.cursor()
        try:
            logging.info(f"Attempting to save order for table_id: {self.table_id} with items: {self.selected_items}")
            # Create a new order (include created_at and use valid status)
            created_at = datetime.datetime.now().isoformat()
            cur.execute("INSERT INTO Orders (table_id, status, created_at) VALUES (?, ?, ?)", (self.table_id, "Open", created_at))
            order_id = cur.lastrowid
            logging.info(f"New order created with ID: {order_id}")

            # Add order items
            for menu_item_id, quantity in self.selected_items.items():
                cur.execute("SELECT price FROM MenuItems WHERE id = ?", (menu_item_id,))
                item_price_result = cur.fetchone()
                if not item_price_result:
                    raise ValueError(f"Menu item with ID {menu_item_id} not found.")
                item_price = item_price_result['price']
                cur.execute("INSERT INTO OrderDetails (order_id, item_id, qty, price, kitchen_status) VALUES (?, ?, ?, ?, ?)",
                            (order_id, menu_item_id, quantity, item_price, "Pending"))
                logging.info(f"Added item {menu_item_id} (qty: {quantity}, price: {item_price}) to order {order_id}")
            
            # Update table status to Occupied if it was Available
            cur.execute("UPDATE Tables SET status = 'Occupied' WHERE id = ? AND status = 'Available'", (self.table_id,))
            logging.info(f"Table {self.table_id} status updated to 'Occupied' if it was 'Available'.")

            conn.commit()
            logging.info(f"Order {order_id} for Table {self.get_table_number(self.table_id)} saved successfully.")
            MessageBox.success(self, "Order Saved", f"Order {order_id} for Table {self.get_table_number(self.table_id)} has been saved.")
            self.accept() # Close the dialog
        except Exception as e:
            conn.rollback()
            logging.error(f"Failed to save order for table {self.table_id}: {e}", exc_info=True)
            MessageBox.error(self, "Error Saving Order", f"Failed to save order: {e}")


