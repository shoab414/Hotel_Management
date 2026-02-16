import sqlite3
import os
import hashlib
import secrets
import datetime

class DatabaseManager:
    def __init__(self, path):
        self.path = path
        self.conn = None

    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Admin','Manager','Staff')),
                created_at TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Customers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Rooms(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL CHECK(category IN ('Standard','Deluxe','Suite')),
                status TEXT NOT NULL CHECK(status IN ('Available','Occupied','Cleaning')),
                rate REAL NOT NULL
            )
        """)
        cur.execute("""
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Tables(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER UNIQUE NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Available','Occupied','Cleaning'))
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS MenuItems(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)
        cur.execute("""
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
        cur.execute("""
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
        cur.execute("""
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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Suppliers(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)
        cur.execute("""
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
        cur.execute("""
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
        conn.commit()
        self._apply_migrations()
        self._seed_if_empty()

    def _apply_migrations(self):
        """Apply schema migrations to existing databases"""
        conn = self.conn
        cur = conn.cursor()
        
        # Check if price column exists in Inventory table, if not add it
        cur.execute("PRAGMA table_info(Inventory)")
        columns = [row[1] for row in cur.fetchall()]
        
        if "price" not in columns:
            cur.execute("ALTER TABLE Inventory ADD COLUMN price REAL NOT NULL DEFAULT 0")
            conn.commit()
        
        if "total_price" not in columns:
            cur.execute("ALTER TABLE Inventory ADD COLUMN total_price REAL NOT NULL DEFAULT 0")
            conn.commit()
        
        # Check if InventoryConsumption table exists
        cur.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='InventoryConsumption'
        """)
        if not cur.fetchone():
            # Create the InventoryConsumption table if it doesn't exist
            cur.execute("""
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
            conn.commit()

    def _seed_if_empty(self):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM Users")
        if cur.fetchone()["c"] == 0:
            self.create_user("admin", "admin123", "Admin")
            self.create_user("manager", "manager123", "Manager")
            self.create_user("staff", "staff123", "Staff")
        conn.commit()



    def create_user(self, username, password, role):
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 200000).hex()
        created_at = datetime.datetime.now().isoformat()
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO Users(username,password_hash,salt,role,created_at) VALUES(?,?,?,?,?)",
                    (username, pwd_hash, salt, role, created_at))
        conn.commit()

    def verify_user(self, username, password):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            return None
        salt = bytes.fromhex(row["salt"])
        pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000).hex()
        if pwd_hash == row["password_hash"]:
            return dict(row)
        return None
