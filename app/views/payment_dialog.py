from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
from PySide6.QtCore import Qt

class PaymentDialog(QDialog):
    def __init__(self, parent=None, total_amount=0.0):
        super().__init__(parent)
        self.setWindowTitle("Process Payment")
        self.total_amount = total_amount
        self.payment_method = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Total Amount Display
        total_label = QLabel(f"Amount Due: ₹{self.total_amount:.2f}")
        total_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(total_label, alignment=Qt.AlignCenter)

        # Payment Method Selection
        method_layout = QHBoxLayout()
        method_label = QLabel("Payment Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Cash", "Card", "UPI"])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        main_layout.addLayout(method_layout)

        # Confirmation Button
        self.confirm_button = QPushButton("Confirm Payment")
        self.confirm_button.clicked.connect(self.accept_payment)
        main_layout.addWidget(self.confirm_button)

        self.setLayout(main_layout)

    def accept_payment(self):
        self.payment_method = self.method_combo.currentText()
        QMessageBox.information(self, "Payment Confirmation", 
                                f"Payment of ₹{self.total_amount:.2f} received via {self.payment_method}.")
        self.accept() # Close dialog with accept result

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = PaymentDialog(total_amount=1234.50)
    if dialog.exec() == QDialog.Accepted:
        print(f"Payment confirmed via: {dialog.payment_method}")
    else:
        print("Payment cancelled.")
    sys.exit(app.exec())
