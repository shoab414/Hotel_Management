"""
Theme management module providing light and dark theme support for the application.

This module manages theme switching between light and dark color schemes,
applying QPalette colors and loading QSS stylesheets for consistent visual appearance
across the entire application.
"""
import os
from typing import Optional
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication


class ThemeManager:
    """Manages application theme switching between light and dark modes.
    
    Applies color palettes and stylesheets to ensure consistent visual
    appearance throughout the application."""
    
    def __init__(self, app: QApplication) -> None:
        """Initialize theme manager with application instance.
        
        Args:
            app: The QApplication instance to apply themes to.
        """
        self.app = app
        self._base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def apply_light(self) -> None:
        """Apply light color theme to the application.
        
        Sets up light palette colors and loads the light stylesheet.
        """
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#F1F5F9"))
        palette.setColor(QPalette.WindowText, QColor("#0F172A"))
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.AlternateBase, QColor("#F8FAFC"))
        palette.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
        palette.setColor(QPalette.ToolTipText, QColor("#1E293B"))
        palette.setColor(QPalette.Text, QColor("#334155"))
        palette.setColor(QPalette.Button, QColor("#FFFFFF"))
        palette.setColor(QPalette.ButtonText, QColor("#334155"))
        palette.setColor(QPalette.BrightText, QColor("#EF4444"))
        palette.setColor(QPalette.Highlight, QColor("#3B82F6"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.app.setPalette(palette)
        self._apply_qss(os.path.join(self._base, "resources", "style.qss"))
        self.app.setProperty("dark_mode", False)

    def apply_dark(self) -> None:
        """Apply dark color theme to the application.
        
        Sets up dark palette colors and loads the dark stylesheet.
        """
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#0F172A"))
        palette.setColor(QPalette.WindowText, QColor("#E2E8F0"))
        palette.setColor(QPalette.Base, QColor("#1E293B"))
        palette.setColor(QPalette.AlternateBase, QColor("#0F172A"))
        palette.setColor(QPalette.ToolTipBase, QColor("#1E293B"))
        palette.setColor(QPalette.ToolTipText, QColor("#E2E8F0"))
        palette.setColor(QPalette.Text, QColor("#E2E8F0"))
        palette.setColor(QPalette.Button, QColor("#1E293B"))
        palette.setColor(QPalette.ButtonText, QColor("#E2E8F0"))
        palette.setColor(QPalette.BrightText, QColor("#EF4444"))
        palette.setColor(QPalette.Highlight, QColor("#3B82F6"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        self.app.setPalette(palette)
        self._apply_qss(os.path.join(self._base, "resources", "style_dark.qss"))
        self.app.setProperty("dark_mode", True)

    def _apply_qss(self, stylesheet_path: str) -> bool:
        """Load and apply QSS stylesheet from file.
        
        Args:
            stylesheet_path: Path to the .qss stylesheet file.
            
        Returns:
            True if stylesheet was loaded successfully, False otherwise.
        """
        stylesheet_file = QFile(stylesheet_path)
        if stylesheet_file.open(QFile.ReadOnly | QFile.Text):
            qss_content = stylesheet_file.readAll().data().decode("utf-8")
            self.app.setStyleSheet(qss_content)
            return True
        return False
