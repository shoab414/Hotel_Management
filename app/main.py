import sys
import os
from PySide6.QtWidgets import QApplication
from app.core.app import AppController
from app.utils.theme import ThemeManager
from app.views.login_view import LoginWindow
from app.core.database import DatabaseManager
import logging

def main():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.info("Application main function started.")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(app_dir, "hotel_restaurant.db")
    db = DatabaseManager(db_path)
    db.initialize()
    app = QApplication(sys.argv)
    logging.info("QApplication initialized.")
    ThemeManager(app).apply_light()
    controller = AppController(db, app)
    login = LoginWindow(controller)
    logging.info("Login window created. Showing login window.")
    login.show()
    exit_code = app.exec()
    logging.info(f"Application exited with code: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
