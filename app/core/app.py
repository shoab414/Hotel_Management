from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow

class AppController:
    def __init__(self, db, app: QApplication):
        self.db = db
        self.app = app
        self.current_user = None
        self.main_window = None

    def login_success(self, user_record):
        self.current_user = user_record
        self.main_window = MainWindow(self)
        self.main_window.show()
