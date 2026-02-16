"""Application Controller - Manages app state and coordinates between database and UI."""

from typing import Optional, Dict, Any
from PySide6.QtWidgets import QApplication
from app.views.main_window import MainWindow
import logging


class AppController:
    """Main application controller for managing state and business logic."""

    def __init__(self, db, app: QApplication):
        """Initialize application controller.
        
        Args:
            db: DatabaseManager instance
            app: QApplication instance
        """
        self.db = db
        self.app = app
        self.current_user: Optional[Dict[str, Any]] = None
        self.main_window: Optional[MainWindow] = None

    def login_success(self, user_record: Dict[str, Any]) -> None:
        """Handle successful user login.
        
        Args:
            user_record: Dictionary containing user information from database
        """
        logging.info(f"Login successful for user: {user_record['username']}")
        self.current_user = user_record
        self.main_window = MainWindow(self)
        self.main_window.show()

    def add_menu_item(self, name: str, category: str, price: float, active: bool) -> None:
        """Add a new menu item.
        
        Args:
            name: Menu item name
            category: Menu item category
            price: Menu item price
            active: Whether item is active (1) or inactive (0)
            
        Raises:
            Exception: If database operation fails
        """
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

    def update_menu_item(self, item_id: int, name: str, category: str, 
                        price: float, active: bool) -> None:
        """Update an existing menu item.
        
        Args:
            item_id: ID of menu item to update
            name: Menu item name
            category: Menu item category
            price: Menu item price
            active: Whether item is active (1) or inactive (0)
            
        Raises:
            Exception: If database operation fails
        """
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

    def delete_menu_item(self, item_id: int) -> None:
        """Delete a menu item.
        
        Args:
            item_id: ID of menu item to delete
            
        Raises:
            Exception: If database operation fails
        """
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

    def delete_inventory_item(self, item_id: int) -> None:
        """Delete an inventory item.
        
        Args:
            item_id: ID of inventory item to delete
            
        Raises:
            Exception: If database operation fails
        """
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



