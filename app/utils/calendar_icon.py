"""
Utility to apply custom calendar icons to QDateEdit widgets.
"""
from PySide6.QtWidgets import QDateEdit
from PySide6.QtGui import QIcon
from pathlib import Path


def register_calendar_resources() -> None:
    """
    Register and initialize calendar icon resources at application startup.
    This prepares calendar icon resources for use throughout the application.
    """
    current_dir = Path(__file__).parent.parent
    icon_path = current_dir / "resources" / "calendar.png"
    
    if not icon_path.exists():
        print(f"Warning: Calendar icon not found at {icon_path}")
    else:
        # Store the icon path as a global resource for later use
        pass


def apply_calendar_icon(date_edit: QDateEdit) -> None:
    """
    Apply a custom calendar icon to a QDateEdit widget's drop-down button.

    Args:
        date_edit: QDateEdit widget to customize
    """
    if not isinstance(date_edit, QDateEdit):
        return

    # Get the path to the calendar icon
    current_dir = Path(__file__).parent.parent
    icon_path = current_dir / "resources" / "calendar.png"

    if icon_path.exists():
        # Convert path to forward slashes and use raw string for stylesheet
        icon_path_str = str(icon_path).replace("\\", "/")
        
        # Enable calendar popup
        date_edit.setCalendarPopup(True)
        
        # Apply stylesheet with proper image URL syntax
        stylesheet = f"""
            QDateEdit {{
                padding-right: 2px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: 1px solid #cccccc;
                padding: 2px;
                image: url("{icon_path_str}");
                background-color: #f5f5f5;
            }}
            QDateEdit::drop-down:hover {{
                background-color: #e8e8e8;
            }}
        """
        date_edit.setStyleSheet(stylesheet)
    else:
        print(f"Warning: Calendar icon not found at {icon_path}")


