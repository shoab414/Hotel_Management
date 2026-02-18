"""Main Application Entry Point - Initializes and runs the Hotel Management System."""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from app.core.app import AppController
from app.utils.theme import ThemeManager
from app.views.login_view import LoginWindow
from app.core.database import DatabaseManager


def setup_logging() -> None:
    """Configure logging for the application."""
    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)


def initialize_database() -> DatabaseManager:
    """Initialize and return database manager.
    
    Returns:
        DatabaseManager instance
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(app_dir, "hotel_restaurant.db")
    db = DatabaseManager(db_path)
    db.initialize()
    return db


def main() -> None:
    """Main application entry point."""
    setup_logging()
    logging.info("Application main function started.")
    
    # Initialize database
    db = initialize_database()
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    logging.info("QApplication initialized.")
    
    # Apply theme
    ThemeManager(app).apply_light()
    
    # Create controller and show login window
    controller = AppController(db, app)
    login = LoginWindow(controller)
    logging.info("Login window created. Showing login window.")
    login.show()
    
    # Run application
    exit_code = app.exec()
    logging.info(f"Application exited with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
