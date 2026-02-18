from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QSpinBox, QDialog, QFormLayout, QLabel, QMessageBox, QDoubleSpinBox, QHeaderView, QCheckBox, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
import logging

from app.core.database import DatabaseManager
from app.utils.message import MessageBox

class MenuManagementView(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Menu Management")
        logging.info("MenuManagementView initialized.")

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("Menu Management")
        self.title_label.setObjectName("PageTitle")
        self.layout.addWidget(self.title_label)

        # Filter and Search Section
        filter_layout = QHBoxLayout()
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(["Starter", "Main Course", "Dessert", "Drinks", "Chinese", "Italian", "Non-Veg", "Veg"])
        filter_layout.addWidget(QLabel("Category:"))
        filter_layout.addWidget(self.category_filter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search menu items...")
        filter_layout.addWidget(self.search_input)
        self.layout.addLayout(filter_layout)

        # Menu Items Table
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(5)
        self.menu_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Active"])
        self.menu_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.menu_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.menu_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.menu_table)       

        # Add/Edit Form Section
        form_layout = QFormLayout()
        self.item_id_label = QLabel("ID: (New)")
        self.item_name_input = QLineEdit()
        self.item_category_combo = QComboBox()
        # Fixed categories for menu items
        self.MENU_CATEGORIES = ["Starter", "Main Course", "Dessert", "Drinks", "Chinese", "Italian", "Non-Veg", "Veg"]
        self.item_category_combo.addItems(self.MENU_CATEGORIES)
        self.item_price_input = QDoubleSpinBox()
        self.item_price_input.setMinimum(0.0)
        self.item_price_input.setMaximum(9999.99)
        self.item_price_input.setPrefix("₹")
        self.item_active_checkbox = QCheckBox("Active")

        form_layout.addRow("ID:", self.item_id_label)
        form_layout.addRow("Name:", self.item_name_input)
        form_layout.addRow("Category:", self.item_category_combo)
        form_layout.addRow("Price:", self.item_price_input)
        form_layout.addRow("", self.item_active_checkbox)
        self.layout.addLayout(form_layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.add_new_button = QPushButton("Add New Dish")
        self.save_changes_button = QPushButton("Save Changes")
        self.delete_button = QPushButton("Delete Dish")

        button_layout.addWidget(self.add_new_button)
        button_layout.addWidget(self.save_changes_button)
        button_layout.addWidget(self.delete_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # Connect signals
        self.add_new_button.clicked.connect(self._add_new_dish)
        self.save_changes_button.clicked.connect(self._save_changes)
        self.delete_button.clicked.connect(self._delete_dish)
        self.menu_table.itemSelectionChanged.connect(self._item_selected)
        self.category_filter.currentIndexChanged.connect(self._load_menu_items)
        self.search_input.textChanged.connect(self._load_menu_items)

        # Initial data load
        self._load_categories()
        self.refresh()

    def _add_new_dish(self):
        logging.info("Add New Dish button clicked.")
        name = self.item_name_input.text().strip()
        category = self.item_category_combo.currentText()
        price = self.item_price_input.value()
        active = self.item_active_checkbox.isChecked()

        if not name:
            MessageBox.warning(self, "Input Error", "Please provide a name for the dish.")
            return
        if category not in self.MENU_CATEGORIES:
            MessageBox.warning(self, "Input Error", "Please select a valid category (Starter, Lunch, Breakfast, Dinner, Sweets).")
            return

        try:
            # Check duplicate name before adding
            if self.controller.menu_item_name_exists(name, exclude_id=None):
                MessageBox.warning(self, "Duplicate Dish", f"A dish with the name '{name}' already exists in the menu. Please use a different name.")
                return
            self.controller.add_menu_item(name, category, price, active)
            MessageBox.info(self, "Success", f"Dish '{name}' added successfully.")
            self.refresh()
            self._clear_form()
        except Exception as e:
            MessageBox.critical(self, "Error", f"Failed to add dish: {e}")

    def _save_changes(self):
        logging.info("Save Changes button clicked.")
        item_id_text = self.item_id_label.text().replace("ID: ", "")
        if item_id_text == "(New)":
            MessageBox.warning(self, "Selection Error", "Please select an existing dish to save changes.")
            return

        try:
            item_id = int(item_id_text)
        except ValueError:
            MessageBox.critical(self, "Error", "Invalid item ID.")
            return

        name = self.item_name_input.text().strip()
        category = self.item_category_combo.currentText()
        price = self.item_price_input.value()
        active = self.item_active_checkbox.isChecked()

        if not name:
            MessageBox.warning(self, "Input Error", "Please provide a name for the dish.")
            return
        if category not in self.MENU_CATEGORIES:
            MessageBox.warning(self, "Input Error", "Please select a valid category (Starter, Lunch, Breakfast, Dinner, Sweets).")
            return

        try:
            # Check duplicate name when updating (exclude current item)
            if self.controller.menu_item_name_exists(name, exclude_id=item_id):
                MessageBox.warning(self, "Duplicate Dish", f"A dish with the name '{name}' already exists in the menu. Please use a different name.")
                return
            self.controller.update_menu_item(item_id, name, category, price, active)
            MessageBox.info(self, "Success", f"Dish '{name}' (ID: {item_id}) updated successfully.")
            self.refresh()
            self._clear_form()
        except Exception as e:
            MessageBox.critical(self, "Error", f"Failed to update dish: {e}")

    def _delete_dish(self):
        logging.info("Delete Dish button clicked.")
        # Prefer getting item_id from selected row so delete always works when a row is selected
        selected = self.menu_table.selectedItems()
        if selected:
            row = selected[0].row()
            item_id_text = self.menu_table.item(row, 0).text()
            dish_name = self.menu_table.item(row, 1).text()
        else:
            item_id_text = self.item_id_label.text().replace("ID: ", "").strip()
            dish_name = self.item_name_input.text().strip() or f"ID: {item_id_text}"
            if item_id_text == "(New)" or not item_id_text:
                MessageBox.warning(self, "Selection Error", "Please select a dish from the table to delete.")
                return

        try:
            item_id = int(item_id_text)
        except ValueError:
            MessageBox.critical(self, "Error", "Invalid item ID. Please select a dish from the table.")
            return

        confirmed = MessageBox.confirm(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{dish_name}' (ID: {item_id})?",
            confirm_text="Yes", cancel_text="No"
        )
        if not confirmed:
            return
        try:
            self.controller.delete_menu_item(item_id)
            MessageBox.info(self, "Success", f"Dish '{dish_name}' deleted successfully.")
            self.refresh()
            self._clear_form()
        except Exception as e:
            MessageBox.critical(self, "Error", f"Failed to delete dish: {e}")

    def _item_selected(self):
        selected_items = self.menu_table.selectedItems()
        if not selected_items:
            self._clear_form()
            return

        row = selected_items[0].row()
        item_id = self.menu_table.item(row, 0).text()
        name = self.menu_table.item(row, 1).text()
        category = self.menu_table.item(row, 2).text()
        price_text = self.menu_table.item(row, 3).text().replace("₹", "")
        active_text = self.menu_table.item(row, 4).text()

        self.item_id_label.setText(f"ID: {item_id}")
        self.item_name_input.setText(name)
        # Match category (case-insensitive for existing DB data)
        idx = self.item_category_combo.findText(category, Qt.MatchFixedString)
        if idx < 0:
            for i in range(self.item_category_combo.count()):
                if self.item_category_combo.itemText(i).lower() == category.lower():
                    idx = i
                    break
        if idx >= 0:
            self.item_category_combo.setCurrentIndex(idx)
        else:
            self.item_category_combo.setCurrentIndex(0)
        self.item_price_input.setValue(float(price_text))
        self.item_active_checkbox.setChecked(active_text == "Yes")





    def _load_categories(self):
        # Filter: All Categories + fixed list (keep selection if possible)
        current_filter = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(self.MENU_CATEGORIES)
        idx = self.category_filter.findText(current_filter)
        if idx >= 0:
            self.category_filter.setCurrentIndex(idx)
        # item_category_combo is already set in __init__ with MENU_CATEGORIES; do not clear it on refresh

    def refresh(self):
        logging.info("MenuManagementView refresh called.")
        self._load_categories()
        self._load_menu_items()
        self._clear_form()

    def _load_menu_items(self):
        logging.info("Loading menu items with category filter: %s, search text: %s", self.category_filter.currentText(), self.search_input.text().strip())
        self.menu_table.setRowCount(0)
        selected_category = self.category_filter.currentText()
        search_text = self.search_input.text().strip()

        conn = self.controller.db.connect()
        cur = conn.cursor()

        query = "SELECT id, name, category, price, active FROM MenuItems"
        params = []
        conditions = []

        if selected_category != "All Categories":
            conditions.append("category = ?")
            params.append(selected_category)
        
        if search_text:
            conditions.append("name LIKE ?")
            params.append(f"%{search_text}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY category, name"
        
        cur.execute(query, params)
        menu_items = cur.fetchall()

        self.menu_table.setRowCount(len(menu_items))
        for row_idx, item in enumerate(menu_items):
            self.menu_table.setItem(row_idx, 0, QTableWidgetItem(str(item['id'])))
            self.menu_table.setItem(row_idx, 1, QTableWidgetItem(item['name']))
            self.menu_table.setItem(row_idx, 2, QTableWidgetItem(item['category']))
            self.menu_table.setItem(row_idx, 3, QTableWidgetItem(f"₹{item['price']:.2f}"))
            active_status = "Yes" if item['active'] else "No"
            self.menu_table.setItem(row_idx, 4, QTableWidgetItem(active_status))
        
        self.menu_table.resizeColumnsToContents()
        self.menu_table.resizeRowsToContents()

    def _clear_form(self):
        self.item_id_label.setText("ID: (New)")
        self.item_name_input.clear()
        self.item_category_combo.setCurrentIndex(0)  # First fixed category (Starter)
        self.item_price_input.setValue(0.0)
        self.item_active_checkbox.setChecked(True)
        self.menu_table.clearSelection()
