from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
                             QPushButton, QListWidget, QListWidgetItem, QLineEdit,
                             QTabWidget, QWidget, QScrollArea, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import logging
import datetime
from app.utils.message import MessageBox

class AddOrderDialog(QDialog):
    def __init__(self, table_id, controller, parent=None):
        super().__init__(parent)
        self.table_id = table_id
        self.controller = controller
        self.setWindowTitle(f"Add Order for Table {self.get_table_number(table_id)}")
        self.setMinimumSize(1000, 800)

        self.selected_items = {} # {menu_item_id: quantity}
        self.category_lists = {} # {category: QListWidget}

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel(f"Add New Order for Table {self.get_table_number(table_id)}")
        self.title_label.setObjectName("PageTitle")
        self.layout.addWidget(self.title_label)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search menu items...")
        self.search_input.textChanged.connect(self.filter_menu_items)
        self.layout.addWidget(self.search_input)

        # Main content layout (menu and selected items side by side)
        main_content = QHBoxLayout()

        # Left side - Menu tabs
        menu_container = QWidget()
        menu_layout = QVBoxLayout(menu_container)
        menu_label = QLabel("Available Items:")
        menu_label_font = QFont()
        menu_label_font.setBold(True)
        menu_label_font.setPointSize(10)
        menu_label.setFont(menu_label_font)
        menu_layout.addWidget(menu_label)

        self.menu_tabs = QTabWidget()
        menu_layout.addWidget(self.menu_tabs)
        main_content.addWidget(menu_container, 1)

        # Right side - Selected Items Display
        selected_container = QFrame()
        selected_container.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        selected_layout = QVBoxLayout(selected_container)

        self.selected_items_label = QLabel("Selected Items:")
        selected_label_font = QFont()
        selected_label_font.setBold(True)
        selected_label_font.setPointSize(10)
        self.selected_items_label.setFont(selected_label_font)
        selected_layout.addWidget(self.selected_items_label)

        self.selected_items_list = QListWidget()
        self.selected_items_list.setMinimumWidth(280)
        self.selected_items_list.setSpacing(5)
        selected_layout.addWidget(self.selected_items_list)

        # Summary section
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(5, 5, 5, 5)

        self.summary_label = QLabel("Total Items: 0")
        self.summary_label.setFont(QFont("Arial", 9))
        summary_layout.addWidget(self.summary_label)

        self.total_price_label = QLabel("Total: ₹0.00")
        total_price_font = QFont()
        total_price_font.setBold(True)
        total_price_font.setPointSize(11)
        self.total_price_label.setFont(total_price_font)
        summary_layout.addWidget(self.total_price_label)

        selected_layout.addWidget(summary_frame)

        main_content.addWidget(selected_container, 0)

        self.layout.addLayout(main_content, 1)

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
        # Clear existing tabs
        self.menu_tabs.clear()
        self.category_lists.clear()

        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, category FROM MenuItems WHERE active = 1 ORDER BY category, name")
        self.all_menu_items = cur.fetchall()

        # Group items by category
        categories = {}
        for item in self.all_menu_items:
            category = item['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        # Create tabs for each category
        for category in sorted(categories.keys()):
            list_widget = QListWidget()
            list_widget.itemDoubleClicked.connect(self.add_item_to_order)

            for item in categories[category]:
                list_item = QListWidgetItem(f"{item['name']} (₹{item['price']:.2f})")
                list_item.setData(Qt.UserRole, item['id'])
                list_widget.addItem(list_item)

            self.category_lists[category] = list_widget
            self.menu_tabs.addTab(list_widget, category)

        self.filter_menu_items()

    def filter_menu_items(self):
        search_text = self.search_input.text().strip().lower()

        for category, list_widget in self.category_lists.items():
            # Hide items that don't match search
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item_text = item.text().lower()
                item.setHidden(not (search_text in item_text))

            # Show tab only if it has visible items
            if search_text:
                has_visible = any(not list_widget.item(i).isHidden()
                                 for i in range(list_widget.count()))
                tab_index = self.menu_tabs.indexOf(list_widget)
                if tab_index >= 0:
                    self.menu_tabs.setTabVisible(tab_index, has_visible)
            else:
                # Show all tabs when search is empty
                tab_index = self.menu_tabs.indexOf(list_widget)
                if tab_index >= 0:
                    self.menu_tabs.setTabVisible(tab_index, True)

    def add_item_to_order(self):
        # Get the current tab's list widget
        current_widget = self.menu_tabs.currentWidget()
        if not isinstance(current_widget, QListWidget):
            MessageBox.warning(self, "No Item Selected", "Please select a menu item to add.")
            return

        selected_item = current_widget.currentItem()
        if not selected_item:
            MessageBox.warning(self, "No Item Selected", "Please select a menu item to add.")
            return

        menu_item_id = selected_item.data(Qt.UserRole)

        # Prompt for quantity
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

        total_items = 0
        total_price = 0.0

        for item_id, quantity in self.selected_items.items():
            cur.execute("SELECT name, price FROM MenuItems WHERE id = ?", (item_id,))
            item_info = cur.fetchone()
            if item_info:
                item_total = item_info['price'] * quantity
                total_items += quantity
                total_price += item_total

                # Create detailed item display
                item_text = f"{quantity}x {item_info['name']}\n₹{item_info['price']:.2f} each → ₹{item_total:.2f}"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.UserRole, item_id)

                # Style the item
                list_item.setSizeHint(list_item.sizeHint() + 10)

                self.selected_items_list.addItem(list_item)

        # Update summary
        self.summary_label.setText(f"Total Items: {total_items}")
        self.total_price_label.setText(f"Total: ₹{total_price:.2f}")

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


