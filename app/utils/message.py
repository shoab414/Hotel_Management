"""
Message box utility module providing styled dialogs for the hotel management system.

This module provides a MessageBox class with static methods for displaying
styled information, warning, error, success, and confirmation dialogs with
consistent branding and user experience.
"""
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QPushButton, QWidget
from PySide6.QtCore import Qt


class MessageBox:
    """Provides styled message dialogs with consistent branding.
    
    All methods are static and return the dialog execution result. Message boxes
    are themed with Hotel Management System colors and styling."""
    @staticmethod
    def _create_base_stylesheet(button_color: str, hover_color: str) -> str:
        """Create base stylesheet for message box with given button colors.
        
        Args:
            button_color: Main button background color (hex format).
            hover_color: Button hover state background color (hex format).
            
        Returns:
            Complete QSS stylesheet string for message box.
        """
        return f"""
            QMessageBox {{
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }}
            QMessageBox QLabel#qt_msgbox_label {{
                color: #374151;
            }}
            QMessageBox QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    @staticmethod
    def info(parent: QWidget, title: str, message: str, 
             detailed_text: Optional[str] = None) -> int:
        """Show a styled information message dialog.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title and header text.
            message: Main message text displayed to user.
            detailed_text: Optional detailed text for expandable details section.
            
        Returns:
            Dialog execution result code.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#2563EB; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
        msg.setStyleSheet(MessageBox._create_base_stylesheet("#2563EB", "#1D4ED8"))
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def warning(parent: QWidget, title: str, message: str, 
                detailed_text: Optional[str] = None) -> int:
        """Show a styled warning message dialog.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title and header text.
            message: Main warning message displayed to user.
            detailed_text: Optional detailed text for expandable details section.
            
        Returns:
            Dialog execution result code.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#D97706; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
        msg.setStyleSheet(MessageBox._create_base_stylesheet("#D97706", "#B45309"))
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def error(parent: QWidget, title: str, message: str, 
              detailed_text: Optional[str] = None) -> int:
        """Show a styled error message dialog.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title and header text.
            message: Main error message displayed to user.
            detailed_text: Optional detailed text for expandable details section.
            
        Returns:
            Dialog execution result code.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#DC2626; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
        msg.setStyleSheet(MessageBox._create_base_stylesheet("#DC2626", "#B91C1C"))
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def success(parent: QWidget, title: str, message: str, 
                detailed_text: Optional[str] = None) -> int:
        """Show a styled success message dialog.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title and header text.
            message: Main success message displayed to user.
            detailed_text: Optional detailed text for expandable details section.
            
        Returns:
            Dialog execution result code.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#059669; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
        msg.setStyleSheet(MessageBox._create_base_stylesheet("#059669", "#047857"))
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def confirm(parent: QWidget, title: str, message: str, 
                confirm_text: str = "Confirm", cancel_text: str = "Cancel") -> bool:
        """Show a styled confirmation dialog with custom button labels.
        
        Args:
            parent: Parent widget for the dialog.
            title: Dialog title and header text.
            message: Main message asking for user confirmation.
            confirm_text: Label text for the confirmation button (default: "Confirm").
            cancel_text: Label text for the cancel button (default: "Cancel").
            
        Returns:
            True if user clicked confirm button, False if cancelled.
        """
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#7C3AED; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
            QMessageBox QLabel#qt_msgbox_label {
                color: #374151;
            }
            QMessageBox QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
                border: 1px solid #D1D5DB;
            }
            QMessageBox QPushButton:hover {
                background-color: #F3F4F6;
            }
        """)
        
        confirm_btn = QPushButton(confirm_text)
        confirm_btn.setStyleSheet("""
            background-color: #7C3AED;
            color: white;
            border: none;
        """)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        
        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setStyleSheet("""
            background-color: #F3F4F6;
            color: #374151;
            border: 1px solid #D1D5DB;
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        
        msg.addButton(confirm_btn, QMessageBox.AcceptRole)
        msg.addButton(cancel_btn, QMessageBox.RejectRole)
        
        return msg.exec() == QMessageBox.AcceptRole