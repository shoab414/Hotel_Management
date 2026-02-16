"""
Login view module for user authentication in the hotel management system.

This module provides the LoginWindow class which displays a login form
for user authentication before accessing the main application.
"""
import logging
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt
from app.services.auth_service import AuthService

if TYPE_CHECKING:
    from app.core.app import AppController


class LoginWindow(QWidget):
    """User login window for authentication.
    
    Provides a login form where users enter credentials to access the
    hotel management system."""
    
    def __init__(self, controller: "AppController") -> None:
        """Initialize the login window.
        
        Args:
            controller: The main application controller instance.
        """
        super().__init__()
        self.controller = controller
        self.auth = AuthService(controller.db)
        
        self.setWindowTitle("Hotel Suite — Login")
        self.setFixedSize(420, 440)
        self.setObjectName("LoginWindow")
        
        # Setup UI components
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(24)
        
        login_card = self._create_login_card()
        main_layout.addWidget(login_card)
        
        # Connect signals
        self.login_btn.clicked.connect(self.submit)

    def _create_login_card(self) -> QFrame:
        """Create the login card frame with all form elements.
        
        Returns:
            QFrame containing the complete login form.
        """
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setMinimumWidth(340)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(40, 36, 40, 36)
        
        # Title section
        self._setup_title_section(card_layout)
        
        # Input fields
        card_layout.addSpacing(8)
        self._setup_input_fields(card_layout)
        
        # Message and button
        self._setup_action_section(card_layout)
        
        return card

    def _setup_title_section(self, layout: QVBoxLayout) -> None:
        """Setup title and subtitle labels.
        
        Args:
            layout: Parent layout to add title elements to.
        """
        self.title = QLabel("Hotel Suite")
        self.title.setObjectName("LoginTitle")
        
        self.subtitle = QLabel("Management System")
        self.subtitle.setObjectName("LoginSubtitle")
        
        layout.addWidget(self.title, alignment=Qt.AlignCenter)
        layout.addWidget(self.subtitle, alignment=Qt.AlignCenter)

    def _setup_input_fields(self, layout: QVBoxLayout) -> None:
        """Setup username and password input fields.
        
        Args:
            layout: Parent layout to add input fields to.
        """
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(44)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setMinimumHeight(44)
        
        layout.addWidget(self.username)
        layout.addWidget(self.password)

    def _setup_action_section(self, layout: QVBoxLayout) -> None:
        """Setup message label and login button.
        
        Args:
            layout: Parent layout to add action elements to.
        """
        self.message = QLabel("")
        self.message.setObjectName("LoginMessage")
        
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("PrimaryButton")
        self.login_btn.setMinimumHeight(44)
        
        layout.addWidget(self.message, alignment=Qt.AlignCenter)
        layout.addWidget(self.login_btn)

    def submit(self) -> None:
        """Handle login form submission.
        
        Validates credentials and either proceeds to main window or
        displays error message.
        """
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        user = self.auth.login(username, password)
        if user:
            logging.getLogger("auth").info("Login success for %s", username)
            self.hide()
            self.controller.login_success(user)
        else:
            self.message.setText("Invalid credentials")
