from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, QMessageBox, QTextEdit, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument, QFont
from PySide6.QtPrintSupport import QPrinter
from app.utils.message import MessageBox
from app.views.payment_dialog import PaymentDialog
import datetime
import os
import logging
from app.views.add_order_dialog import AddOrderDialog


class BillPreviewDialog(QDialog):
    """Dialog to display a formatted bill preview before payment."""
    
    def __init__(self, parent=None, table_number="", items_data=None, subtotal=0.0, gst_amount=0.0, grand_total=0.0):
        super().__init__(parent)
        self.setWindowTitle(f"Bill Preview - Table {table_number}")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Create bill display area
        bill_text = QTextEdit()
        bill_text.setReadOnly(True)
        
        # Format bill content
        bill_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; }}
                .table-num {{ text-align: center; font-size: 14px; margin-bottom: 20px; }}
                .bill-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .bill-table th {{ background-color: #f0f0f0; padding: 10px; text-align: left; border-bottom: 2px solid #333; }}
                .bill-table td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                .bill-table tr:last-child td {{ border-bottom: 2px solid #333; }}
                .item-name {{ font-weight: 500; }}
                .qty-price {{ text-align: right; }}
                .total-row {{ font-weight: bold; text-align: right; }}
                .summary {{ margin-top: 20px; font-size: 14px; }}
                .summary-line {{ display: flex; justify-content: space-between; margin: 8px 0; }}
                .summary-line.total {{ font-size: 16px; font-weight: bold; background-color: #f9f9f9; padding: 8px; border: 1px solid #ddd; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">🧾 RESTAURANT BILL</div>
            <div class="table-num">Table #{table_number}</div>
            <div class="table-num" style="font-size: 12px; color: #666;">{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
            
            <table class="bill-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th style="text-align: center; width: 60px;">Qty</th>
                        <th style="text-align: right; width: 80px;">Price</th>
                        <th style="text-align: right; width: 100px;">Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        if items_data:
            for item_name, qty, price, item_total in items_data:
                bill_html += f"""
                    <tr>
                        <td class="item-name">{item_name}</td>
                        <td style="text-align: center;">{qty}</td>
                        <td class="qty-price">₹{price:.2f}</td>
                        <td class="qty-price">₹{item_total:.2f}</td>
                    </tr>
                """
        
        bill_html += f"""
                </tbody>
            </table>
            
            <div class="summary">
                <div class="summary-line">
                    <span>Subtotal:</span>
                    <span>₹{subtotal:.2f}</span>
                </div>
                <div class="summary-line">
                    <span>GST (5%):</span>
                    <span>₹{gst_amount:.2f}</span>
                </div>
                <div class="summary-line total">
                    <span>GRAND TOTAL:</span>
                    <span>₹{grand_total:.2f}</span>
                </div>
            </div>
            
            <div class="footer">
                <p>Thank you for your visit!</p>
                <p>Please proceed to payment counter</p>
            </div>
        </body>
        </html>
        """
        
        bill_text.setHtml(bill_html)
        layout.addWidget(bill_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        continue_btn = QPushButton("Continue to Payment")
        continue_btn.setObjectName("PrimaryButton")
        continue_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(continue_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

class TableManagementDialog(QDialog):
    def __init__(self, table_id, controller, parent=None):
        super().__init__(parent)
        logging.info(f"TableManagementDialog __init__ called for table_id: {table_id}")
        self.table_id = table_id
        self.controller = controller
        self.setWindowTitle(f"Manage Table {self.get_table_number(table_id)}")
        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20) # Add margins
        self.layout.setSpacing(15) # Add spacing between widgets

        self.title_label = QLabel(f"Orders for Table {self.get_table_number(table_id)}")
        self.title_label.setObjectName("PageTitle")
        self.layout.addWidget(self.title_label)

        # Orders Table (now displays individual items from all orders)
        self.orders_table = QTableWidget(0, 4) # Item, Qty, Price, Subtotal
        self.orders_table.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Subtotal"])
        self.orders_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.NoSelection) # No selection needed for individual items
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Distribute columns evenly
        self.layout.addWidget(self.orders_table)

        # Summary Labels
        summary_layout = QFormLayout()
        summary_layout.setContentsMargins(0, 10, 0, 10) # Add vertical padding to summary
        summary_layout.setSpacing(5)
        self.total_label = QLabel("Total: ₹0.00")
        self.gst_label = QLabel("GST (5%): ₹0.00")
        self.grand_total_label = QLabel("Grand Total: ₹0.00")
        
        # Make summary labels bold for emphasis
        font = self.total_label.font()
        font.setBold(True)
        self.total_label.setFont(font)
        self.gst_label.setFont(font)
        self.grand_total_label.setFont(font)

        summary_layout.addRow(self.total_label)
        summary_layout.addRow(self.gst_label)
        summary_layout.addRow(self.grand_total_label)
        self.layout.addLayout(summary_layout)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10) # Spacing between buttons

        # Grouping action buttons
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setSpacing(10)
        self.btn_add_order = QPushButton("Add Order")
        self.btn_add_order.setObjectName("PrimaryButton")
        self.btn_edit_order = QPushButton("Edit Order")
        self.btn_edit_order.setEnabled(False) # Disable edit for now
        self.btn_delete_order = QPushButton("Delete Order")
        self.btn_delete_order.setEnabled(False) # Disable delete for now
        action_buttons_layout.addWidget(self.btn_add_order)
        action_buttons_layout.addWidget(self.btn_edit_order)
        action_buttons_layout.addWidget(self.btn_delete_order)
        self.button_layout.addLayout(action_buttons_layout)
        
        self.button_layout.addStretch() # Spacer to push buttons to ends

        # Grouping payment/bill buttons
        payment_buttons_layout = QHBoxLayout()
        payment_buttons_layout.setSpacing(10)
        self.btn_checkout = QPushButton("Checkout & Pay")
        self.btn_checkout.setObjectName("PrimaryButton")
        self.btn_mark_available = QPushButton("Mark Available") # Mark Available button
        payment_buttons_layout.addWidget(self.btn_checkout)
        payment_buttons_layout.addWidget(self.btn_mark_available) # Add Mark Available button
        self.button_layout.addLayout(payment_buttons_layout)

        self.layout.addLayout(self.button_layout)

        self.refresh_orders() # Re-enable refresh_orders

        # Connect signals
        self.btn_add_order.clicked.connect(self.add_order)
        self.btn_edit_order.clicked.connect(self.edit_order)
        self.btn_delete_order.clicked.connect(self.delete_order)
        self.btn_checkout.clicked.connect(self.checkout_and_pay) # Connect merged Checkout & Pay button
        self.btn_mark_available.clicked.connect(self.mark_table_available) # Connect Mark Available button

    def get_table_number(self, table_id):
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT number FROM Tables WHERE id = ?", (table_id,))
        result = cur.fetchone()
        return result['number'] if result else "N/A"

    def refresh_orders(self):
        logging.info(f"Starting refresh_orders for table_id: {self.table_id}")
        self.orders_table.setRowCount(0) # Clear existing rows
        total_amount = 0.0

        # Fetch all active orders for the table (support both legacy and current status names)
        conn = self.controller.db.connect()
        cur = conn.cursor()
        cur.execute("SELECT id, status FROM Orders WHERE table_id = ? AND status IN ('Open', 'InKitchen', 'Served', 'Pending', 'Preparing', 'Ready')", (self.table_id,))
        orders = cur.fetchall()
        logging.info(f"Fetched {len(orders)} active orders for table_id {self.table_id}: {orders}")

        row_idx = 0
        if not orders:
            logging.info(f"No active orders found for table_id {self.table_id}.")
        for order in orders:
            # Fetch order items
            cur.execute("""
                SELECT od.qty, m.name, od.price
                FROM OrderDetails od
                JOIN MenuItems m ON od.item_id = m.id
                WHERE od.order_id = ?
            """, (order['id'],))
            items = cur.fetchall()
            logging.info(f"Order {order['id']} has {len(items)} items: {items}")

            if not items:
                logging.warning(f"Order {order['id']} has no items. Skipping display for this order.")
                continue

            for item in items:
                item_subtotal = item['qty'] * item['price']
                logging.info(f"  - Item: {item['name']}, Qty: {item['qty']}, Price: {item['price']:.2f}, Subtotal: {item_subtotal:.2f}")
                self.orders_table.insertRow(row_idx)
                self.orders_table.setItem(row_idx, 0, QTableWidgetItem(item['name']))
                self.orders_table.setItem(row_idx, 1, QTableWidgetItem(str(item['qty'])))
                self.orders_table.setItem(row_idx, 2, QTableWidgetItem(f"₹{item['price']:.2f}"))
                self.orders_table.setItem(row_idx, 3, QTableWidgetItem(f"₹{item_subtotal:.2f}"))
                total_amount += item_subtotal
                row_idx += 1
        
        # Calculate GST and Grand Total
        gst_rate = 0.05 # 5% GST
        gst_amount = total_amount * gst_rate
        grand_total = total_amount + gst_amount

        # Update summary labels
        self.total_label.setText(f"Total: ₹{total_amount:.2f}")
        self.gst_label.setText(f"GST ({gst_rate*100:.0f}%): ₹{gst_amount:.2f}")
        self.grand_total_label.setText(f"Grand Total: ₹{grand_total:.2f}")

        self.orders_table.resizeColumnsToContents()
        self.orders_table.resizeRowsToContents()
        logging.info(f"Finished refresh_orders for table_id: {self.table_id}. Total amount: {total_amount:.2f}")

    def add_order(self):
        dialog = AddOrderDialog(self.table_id, self.controller, self)
        if dialog.exec():
            self.refresh_orders()
            self.controller.hotel_view.refresh_tables()

    def edit_order(self):
        MessageBox.info(self, "Edit Order", "Editing individual order items is not yet implemented.")

    def delete_order(self):
        MessageBox.info(self, "Delete Order", "Deleting individual order items is not yet implemented.")



    def checkout_and_pay(self):
        """Combined method that generates bill and processes payment in one workflow."""
        conn = self.controller.db.connect()
        cur = conn.cursor()

        # Fetch all active orders for this table
        cur.execute("""
            SELECT id FROM Orders
            WHERE table_id = ? AND status IN ('Open', 'InKitchen', 'Served', 'Pending', 'Preparing', 'Ready')
        """, (self.table_id,))
        active_order_ids = [row['id'] for row in cur.fetchall()]

        if not active_order_ids:
            MessageBox.info(self, "No Orders", "No active orders to checkout for this table.")
            return

        # Collect all bill items for preview
        all_items = []
        total_bill = 0

        for order_id in active_order_ids:
            cur.execute("""
                SELECT od.qty, m.name, od.price
                FROM OrderDetails od
                JOIN MenuItems m ON od.item_id = m.id
                WHERE od.order_id = ?
            """, (order_id,))
            items = cur.fetchall()
            
            for item in items:
                item_cost = item['qty'] * item['price']
                all_items.append((item['name'], item['qty'], item['price'], item_cost))
                total_bill += item_cost

        # Calculate GST and grand total
        gst_rate = 0.05
        gst_amount = total_bill * gst_rate
        grand_total = total_bill + gst_amount

        # Show bill preview dialog
        bill_preview = BillPreviewDialog(
            parent=self,
            table_number=self.get_table_number(self.table_id),
            items_data=all_items,
            subtotal=total_bill,
            gst_amount=gst_amount,
            grand_total=grand_total
        )
        
        if bill_preview.exec() != QDialog.Accepted:
            return

        # Show payment dialog
        payment_dialog = PaymentDialog(self, total_amount=grand_total)
        if payment_dialog.exec() == QDialog.Accepted:
            payment_method = payment_dialog.payment_method
            try:
                # Record payments and mark orders as paid
                for order_id in active_order_ids:
                    cur.execute("SELECT COALESCE(SUM(qty*price),0) AS amt FROM OrderDetails WHERE order_id = ?", (order_id,))
                    amt = float(cur.fetchone()["amt"] or 0)
                    order_gst = round(amt * gst_rate, 2)
                    # Insert payment record
                    cur.execute("INSERT INTO Payments(order_id, amount, gst, method, paid_at) VALUES(?,?,?,?,?)",
                                (order_id, amt, order_gst, payment_method, datetime.datetime.now().isoformat()))
                    # Mark order paid
                    cur.execute("UPDATE Orders SET status = 'Paid' WHERE id = ?", (order_id,))

                # Update table to available
                cur.execute("UPDATE Tables SET status = ? WHERE id = ?", ("Available", self.table_id))
                conn.commit()
                
                # Generate PDF bill
                html = "<h2>Restaurant Bill</h2>"
                html += f"<p>Table #{self.get_table_number(self.table_id)} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"
                html += "<table border='1' cellspacing='0' cellpadding='4'><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr>"
                
                for order_id in active_order_ids:
                    cur.execute("""
                        SELECT od.qty, m.name, od.price
                        FROM OrderDetails od
                        JOIN MenuItems m ON od.item_id = m.id
                        WHERE od.order_id = ?
                    """, (order_id,))
                    items = cur.fetchall()
                    
                    for item in items:
                        item_cost = item['qty'] * item['price']
                        html += f"<tr><td>{item['name']}</td><td>{item['qty']}</td><td>₹{item['price']:.2f}</td><td>₹{item_cost:.2f}</td></tr>"
                
                html += "</table>"
                html += f"<p>Subtotal: ₹{total_bill:.2f}</p><p>GST ({gst_rate*100:.0f}%): ₹{gst_amount:.2f}</p><h3>Total: ₹{grand_total:.2f}</h3>"
                html += f"<p>Payment Method: {payment_method}</p>"
                
                doc = QTextDocument()
                doc.setHtml(html)
                pdf_path = os.path.join(os.getcwd(), f"bill_table_{self.get_table_number(self.table_id)}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf")
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(pdf_path)
                doc.print(printer)
                
                MessageBox.success(self, "Checkout Complete",
                                  f"Payment of ₹{grand_total:.2f} received via {payment_method}.\n"
                                  f"Table {self.get_table_number(self.table_id)} is now available.\n"
                                  f"Bill saved as {os.path.basename(pdf_path)}")
                self.accept() # Close dialog after successful payment
                self.controller.hotel_view.refresh_tables()
            except Exception as e:
                conn.rollback()
                MessageBox.error(self, "Checkout Error", f"Failed to complete checkout: {e}")
                logging.error(f"Checkout error: {e}", exc_info=True)

    def mark_table_available(self):
        logging.info(f"mark_table_available called for table_id: {self.table_id}")
        if MessageBox.confirm(self, "Confirm Action", 
                              f"Are you sure you want to mark Table {self.get_table_number(self.table_id)} as 'Available' and clear all its active orders?"):
            logging.info(f"User confirmed marking table {self.table_id} as available.")
            conn = self.controller.db.connect()
            cur = conn.cursor()
            try:
                # Update table status to 'Available'
                logging.info(f"Attempting to update Tables status to 'Available' for table_id: {self.table_id}")
                cur.execute("UPDATE Tables SET status = ? WHERE id = ?", ("Available", self.table_id))
                # Update all active orders associated with this table to 'Paid'
                logging.info(f"Attempting to update active Orders status to 'Paid' for table_id: {self.table_id}")
                cur.execute("UPDATE Orders SET status = ? WHERE table_id = ? AND status IN ('Open', 'InKitchen', 'Served', 'Pending', 'Preparing', 'Ready')", ("Paid", self.table_id))
                conn.commit()
                logging.info(f"Table {self.table_id} status updated to 'Available' and active orders marked 'Completed' by manual action.")
                MessageBox.success(self, "Table Status Updated", f"Table {self.get_table_number(self.table_id)} is now 'Available'.")
                self.controller.hotel_view.refresh_tables() # Notify hotel_view to refresh
                self.accept() # Close the dialog
            except Exception as e:
                conn.rollback()
                logging.error(f"Failed to manually update table status or orders for table {self.table_id}: {e}", exc_info=True)
                MessageBox.error(self, "Database Error", f"Failed to mark table available: {e}")
            # Removed conn.close() to prevent premature closing of the database connection
        else:
            logging.info(f"User cancelled marking table {self.table_id} as available.")
