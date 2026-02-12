from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt
from services.auth_service import AuthService
import logging

class LoginWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.auth = AuthService(controller.db)
        self.setWindowTitle("Hotel Suite — Login")
        self.setFixedSize(420, 440)
        self.setObjectName("LoginWindow")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setMinimumWidth(340)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(40, 36, 40, 36)
        self.title = QLabel("Hotel Suite")
        self.title.setObjectName("LoginTitle")
        self.subtitle = QLabel("Management System")
        self.subtitle.setObjectName("LoginSubtitle")
        card_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.subtitle, alignment=Qt.AlignCenter)
        card_layout.addSpacing(8)
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(44)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setMinimumHeight(44)
        self.message = QLabel("")
        self.message.setObjectName("LoginMessage")
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("PrimaryButton")
        self.login_btn.setMinimumHeight(44)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.message, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.login_btn)
        layout.addWidget(card)
        self.login_btn.clicked.connect(self.submit)

    def submit(self):
        u = self.username.text().strip()
        p = self.password.text().strip()
        user = self.auth.login(u, p)
        if user:
            logging.getLogger("auth").info("Login success for %s", u)
            self.hide()
            self.controller.login_success(user)
        else:
            self.message.setText("Invalid credentials")
