import os
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import QFile

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self._base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def apply_light(self):
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

    def apply_dark(self):
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

    def _apply_qss(self, path):
        f = QFile(path)
        if f.open(QFile.ReadOnly | QFile.Text):
            qss = f.readAll().data().decode("utf-8")
            self.app.setStyleSheet(qss)
