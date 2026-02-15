import sys
import os
from PySide6.QtWidgets import QApplication
from app.core.app import AppController
from app.utils.theme import ThemeManager
from app.views.login_view import LoginWindow
from app.core.database import DatabaseManager
import logging

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(app_dir, "hotel_restaurant.db")
    db = DatabaseManager(db_path)
    db.initialize()
    app = QApplication(sys.argv)
    ThemeManager(app).apply_light()
    controller = AppController(db, app)
    login = LoginWindow(controller)
    login.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
