from PySide6.QtWidgets import QApplication
from app.views.main_window import MainWindow
import logging

class AppController:
    def __init__(self, db, app: QApplication):
        self.db = db
        self.app = app
        self.current_user = None
        self.main_window = None

    def login_success(self, user_record):
        logging.info(f"Login successful for user: {user_record['username']}")
        self.current_user = user_record
        self.main_window = MainWindow(self)
        self.main_window.show()

    def add_menu_item(self, name, category, price, active):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO MenuItems (name, category, price, active) VALUES (?, ?, ?, ?)",
                (name, category, price, 1 if active else 0)
            )
            conn.commit()
            logging.info(f"Menu item '{name}' added successfully.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error adding menu item '{name}': {e}")
            raise

    def update_menu_item(self, item_id, name, category, price, active):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE MenuItems SET name = ?, category = ?, price = ?, active = ? WHERE id = ?",
                (name, category, price, 1 if active else 0, item_id)
            )
            conn.commit()
            logging.info(f"Menu item '{name}' (ID: {item_id}) updated successfully.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error updating menu item '{name}' (ID: {item_id}): {e}")
            raise

    def delete_menu_item(self, item_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM MenuItems WHERE id = ?", (item_id,))
            conn.commit()
            logging.info(f"Menu item with ID: {item_id} deleted successfully.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error deleting menu item with ID: {item_id}: {e}")
            raise

    def delete_inventory_item(self, item_id):
        conn = self.db.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Inventory WHERE id = ?", (item_id,))
            conn.commit()
            logging.info(f"Inventory item with ID: {item_id} deleted successfully.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error deleting inventory item with ID: {item_id}: {e}")
            raise



