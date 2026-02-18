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

    def menu_item_name_exists(self, name, exclude_id=None):
        """Check if a menu item with the same name already exists (case-insensitive)."""
        conn = self.db.connect()
        cursor = conn.cursor()
        if exclude_id is not None:
            cursor.execute(
                "SELECT 1 FROM MenuItems WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND id != ? LIMIT 1",
                (name, exclude_id)
            )
        else:
            cursor.execute(
                "SELECT 1 FROM MenuItems WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) LIMIT 1",
                (name,)
            )
        return cursor.fetchone() is not None

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
            # Check if menu item is referenced in OrderDetails
            cursor.execute("SELECT COUNT(*) as count FROM OrderDetails WHERE item_id = ?", (item_id,))
            result = cursor.fetchone()
            reference_count = result['count'] if result else 0
            
            if reference_count > 0:
                # First delete all OrderDetails referencing this menu item
                cursor.execute("DELETE FROM OrderDetails WHERE item_id = ?", (item_id,))
                logging.info(f"Deleted {reference_count} order detail(s) referencing menu item ID: {item_id}")
            
            # Now delete the menu item
            cursor.execute("DELETE FROM MenuItems WHERE id = ?", (item_id,))
            rows_deleted = cursor.rowcount
            
            if rows_deleted == 0:
                raise ValueError(f"Menu item with ID {item_id} not found.")
            
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



