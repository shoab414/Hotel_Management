from PySide6.QtWidgets import QMessageBox, QPushButton
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
import os

class MessageBox:
    @staticmethod
    def info(parent, title, message, detailed_text=None):
        """Show a styled information message"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#2563EB; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
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
                background-color: #2563EB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def warning(parent, title, message, detailed_text=None):
        """Show a styled warning message"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#D97706; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
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
                background-color: #D97706;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #B45309;
            }
        """)
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def error(parent, title, message, detailed_text=None):
        """Show a styled error message"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#DC2626; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
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
                background-color: #DC2626;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #B91C1C;
            }
        """)
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def success(parent, title, message, detailed_text=None):
        """Show a styled success message"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(f"<h3 style='color:#059669; margin:0;'>{title}</h3>")
        msg.setInformativeText(f"<p style='margin:10px 0; color:#374151;'>{message}</p>")
        
        if detailed_text:
            msg.setDetailedText(detailed_text)
        
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
                background-color: #059669;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #047857;
            }
        """)
        
        ok_button = QPushButton("OK")
        ok_button.setCursor(Qt.PointingHandCursor)
        msg.addButton(ok_button, QMessageBox.AcceptRole)
        
        return msg.exec()

    @staticmethod
    def confirm(parent, title, message, confirm_text="Confirm", cancel_text="Cancel"):
        """Show a styled confirmation dialog"""
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