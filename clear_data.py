import sqlite3
import os

# Define the path to your database file
DB_PATH = "f:/Hotel management sytem/hotel_restaurant.db"

def clear_all_data_except_users():
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Enable foreign key constraints for proper deletion order
        cur.execute("PRAGMA foreign_keys = ON")

        # List of tables to clear, in an order that respects foreign key constraints
        # All tables except 'Users'
        tables_to_clear = [
            "Payments",
            "OrderDetails",
            "Orders",
            "Reservations",
            "Customers",
            "Rooms",
            "MenuItems",
            "Inventory",
            "Suppliers",
            "Tables" # Now including Tables
        ]

        print("Clearing data from the following tables:")
        for table_name in tables_to_clear:
            print(f"- {table_name}")
            cur.execute(f"DELETE FROM {table_name}")
            print(f"  Deleted {cur.rowcount} rows from {table_name}")

        conn.commit()
        print("\nAll specified data cleared successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        clear_all_data_except_users()
    else:
        print(f"Database file not found at {DB_PATH}. Please ensure the database is initialized.")
