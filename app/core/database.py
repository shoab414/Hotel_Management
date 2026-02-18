"""
Database management module for the hotel management system.

This module provides DatabaseManager class for managing SQLite database
operations including user authentication, schema initialization, and
database migrations.
"""
import sqlite3
import os
import hashlib
import secrets
import datetime
from typing import Optional, Dict, List, Any


class DatabaseManager:
    """Manages SQLite database connections and operations.
    
    Handles database initialization, schema creation, user management,
    and various CRUD operations for all entities in the system."""
    
    def __init__(self, path: str) -> None:
        """Initialize database manager with database file path.
        
        Args:
            path: File path to the SQLite database file.
        """
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Establish connection to the database.
        
        Returns:
            SQLite connection object with row_factory set to sqlite3.Row
            for dictionary-like row access.
        """
        if not self.conn:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self) -> None:
        """Close the database connection if open."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize(self) -> None:
        """Initialize the database schema and seed initial data.
        
        Creates all required tables if they don't exist, applies any pending
        migrations, and seeds default data if database is empty.
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create all tables
        self._create_users_table(cursor)
        self._create_customers_table(cursor)
        self._create_rooms_table(cursor)
        self._create_reservations_table(cursor)
        self._create_tables_table(cursor)
        self._create_menu_items_table(cursor)
        self._create_orders_table(cursor)
        self._create_order_details_table(cursor)
        self._create_payments_table(cursor)
        self._create_suppliers_table(cursor)
        self._create_inventory_table(cursor)
        self._create_inventory_consumption_table(cursor)
        
        connection.commit()
        self._apply_migrations()
        self._seed_if_empty()

    def _create_users_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Users table for user authentication."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Admin','Manager','Staff')),
                created_at TEXT NOT NULL
            )
        """)

    def _create_customers_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Customers table for customer records."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)

    def _create_rooms_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Rooms table for hotel room management."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Rooms(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('Standard','Deluxe','Suite')),
                status TEXT NOT NULL CHECK(status IN ('Available','Occupied','Cleaning')),
                rate REAL NOT NULL
            )
        """)

    def _create_reservations_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Reservations table for room bookings."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reservations(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT,
                status TEXT NOT NULL CHECK(status IN ('Reserved','CheckedIn','CheckedOut','Cancelled')),
                FOREIGN KEY(customer_id) REFERENCES Customers(id) ON DELETE CASCADE,
                FOREIGN KEY(room_id) REFERENCES Rooms(id) ON DELETE CASCADE
            )
        """)

    def _create_tables_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Tables table for restaurant table management."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tables(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER UNIQUE NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Available','Occupied','Cleaning'))
            )
        """)

    def _create_menu_items_table(self, cursor: sqlite3.Cursor) -> None:
        """Create MenuItems table for restaurant menu."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS MenuItems(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)

    def _create_orders_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Orders table for restaurant orders."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Orders(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_id INTEGER,
                customer_id INTEGER,
                status TEXT NOT NULL CHECK(status IN ('Open','InKitchen','Served','Paid','Cancelled')),
                created_at TEXT NOT NULL,
                FOREIGN KEY(table_id) REFERENCES Tables(id),
                FOREIGN KEY(customer_id) REFERENCES Customers(id)
            )
        """)

    def _create_order_details_table(self, cursor: sqlite3.Cursor) -> None:
        """Create OrderDetails table for order line items."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS OrderDetails(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                price REAL NOT NULL,
                kitchen_status TEXT NOT NULL CHECK(kitchen_status IN ('Pending','Cooking','Ready','Served')),
                FOREIGN KEY(order_id) REFERENCES Orders(id) ON DELETE CASCADE,
                FOREIGN KEY(item_id) REFERENCES MenuItems(id)
            )
        """)

    def _create_payments_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Payments table for transaction records."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Payments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                reservation_id INTEGER,
                amount REAL NOT NULL,
                gst REAL NOT NULL,
                method TEXT NOT NULL CHECK(method IN ('Cash','Card','UPI')),
                paid_at TEXT NOT NULL,
                FOREIGN KEY(order_id) REFERENCES Orders(id) ON DELETE CASCADE,
                FOREIGN KEY(reservation_id) REFERENCES Reservations(id) ON DELETE CASCADE
            )
        """)

    def _create_suppliers_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Suppliers table for supplier management."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Suppliers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)

    def _create_inventory_table(self, cursor: sqlite3.Cursor) -> None:
        """Create Inventory table for stock management."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Inventory(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                qty REAL NOT NULL,
                unit TEXT NOT NULL,
                threshold REAL NOT NULL DEFAULT 5,
                supplier_id INTEGER,
                price REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(supplier_id) REFERENCES Suppliers(id)
            )
        """)

    def _create_inventory_consumption_table(self, cursor: sqlite3.Cursor) -> None:
        """Create InventoryConsumption table for consumption tracking."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS InventoryConsumption(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                qty_consumed REAL NOT NULL,
                consumption_date TEXT NOT NULL,
                price REAL NOT NULL,
                total_value REAL NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(inventory_id) REFERENCES Inventory(id) ON DELETE CASCADE
            )
        """)

    def _apply_migrations(self) -> None:
        """Apply schema migrations to existing databases.
        
        Checks for missing columns and tables, adding them as needed to
        support backward compatibility with older database versions.
        """
        connection = self.conn
        cursor = connection.cursor()
        
        # Check if price column exists in Inventory table
        cursor.execute("PRAGMA table_info(Inventory)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "price" not in columns:
            cursor.execute("ALTER TABLE Inventory ADD COLUMN price REAL NOT NULL DEFAULT 0")
            connection.commit()
        
        if "total_price" not in columns:
            cursor.execute("ALTER TABLE Inventory ADD COLUMN total_price REAL NOT NULL DEFAULT 0")
            connection.commit()
        
        # Check if InventoryConsumption table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='InventoryConsumption'
        """)
        if not cursor.fetchone():
            # Create InventoryConsumption table if it doesn't exist
            cursor.execute("""
                CREATE TABLE InventoryConsumption(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inventory_id INTEGER NOT NULL,
                    qty_consumed REAL NOT NULL,
                    consumption_date TEXT NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(inventory_id) REFERENCES Inventory(id) ON DELETE CASCADE
                )
            """)
            connection.commit()

    def _seed_if_empty(self) -> None:
        """Seed database with default users if database is empty.
        
        Creates default admin, manager, and staff user accounts with
        standard credentials for initial setup.
        """
        connection = self.conn
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) AS c FROM Users")
        if cursor.fetchone()["c"] == 0:
            self.create_user("admin", "admin123", "Admin")
            self.create_user("manager", "manager123", "Manager")
            self.create_user("staff", "staff123", "Staff")
        connection.commit()

    def create_user(self, username: str, password: str, role: str) -> None:
        """Create a new user account with hashed password.
        
        Uses PBKDF2-SHA256 hashing with a random salt for password security.
        
        Args:
            username: Unique username for the account.
            password: Plain text password to be hashed.
            role: User role ('Admin', 'Manager', or 'Staff').
        """
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", 
            password.encode("utf-8"), 
            bytes.fromhex(salt), 
            200000
        ).hex()
        created_at = datetime.datetime.now().isoformat()
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Users(username,password_hash,salt,role,created_at) VALUES(?,?,?,?,?)",
            (username, pwd_hash, salt, role, created_at)
        )
        connection.commit()

    def verify_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials and return user record if valid.
        
        Validates username and password against stored hash using the
        user's stored salt.
        
        Args:
            username: Username to verify.
            password: Plain text password to verify.
            
        Returns:
            Dictionary with user record if credentials are valid, None otherwise.
        """
        connection = self.connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
        row = cursor.fetchone()
        if not row:
            return None
        
        salt = bytes.fromhex(row["salt"])
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256", 
            password.encode("utf-8"), 
            salt, 
            200000
        ).hex()
        
        if pwd_hash == row["password_hash"]:
            return dict(row)
        return None
