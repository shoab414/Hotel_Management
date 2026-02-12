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
                FOREIGN KEY(supplier_id) REFERENCES Suppliers(id)
            )
        """)
        conn.commit()
        self._seed_if_empty()

    def _seed_if_empty(self):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM Users")
        if cur.fetchone()["c"] == 0:
            self.create_user("admin", "admin123", "Admin")
            self.create_user("manager", "manager123", "Manager")
            self.create_user("staff", "staff123", "Staff")
        cur.execute("SELECT COUNT(*) AS c FROM Rooms")
        if cur.fetchone()["c"] == 0:
            rooms = [
                ("101", "Standard", "Available", 2500.0),
                ("102", "Deluxe", "Available", 4000.0),
                ("201", "Suite", "Cleaning", 7000.0),
                ("202", "Deluxe", "Occupied", 4200.0)
            ]
            cur.executemany("INSERT INTO Rooms(number,category,status,rate) VALUES(?,?,?,?)", rooms)
        cur.execute("SELECT COUNT(*) AS c FROM Tables")
        if cur.fetchone()["c"] == 0:
            tables = [(i, "Available") for i in range(1, 11)]
            cur.executemany("INSERT INTO Tables(number,status) VALUES(?,?)", tables)
        cur.execute("SELECT COUNT(*) AS c FROM MenuItems")
        if cur.fetchone()["c"] == 0:
            items = [
                ("Paneer Tikka", "Starter", 220.0, 1),
                ("Veg Biryani", "Main", 280.0, 1),
                ("Chicken Curry", "Main", 320.0, 1),
                ("Gulab Jamun", "Dessert", 120.0, 1),
                ("Masala Dosa", "Main", 200.0, 1)
            ]
            cur.executemany("INSERT INTO MenuItems(name,category,price,active) VALUES(?,?,?,?)", items)
        cur.execute("SELECT COUNT(*) AS c FROM Suppliers")
        if cur.fetchone()["c"] == 0:
            suppliers = [
                ("FreshFoods Ltd", "9990001111", "fresh@example.com"),
                ("Daily Dairy", "9990002222", "dairy@example.com")
            ]
            cur.executemany("INSERT INTO Suppliers(name,phone,email) VALUES(?,?,?)", suppliers)
        cur.execute("SELECT COUNT(*) AS c FROM Inventory")
        if cur.fetchone()["c"] == 0:
            inventory = [
                ("Rice", 50, "kg", 10, 1),
                ("Paneer", 20, "kg", 5, 2),
                ("Spices Mix", 8, "kg", 5, 1),
                ("Cooking Oil", 15, "L", 5, 1)
            ]
            cur.executemany("INSERT INTO Inventory(name,qty,unit,threshold,supplier_id) VALUES(?,?,?,?,?)", inventory)
        cur.execute("SELECT COUNT(*) AS c FROM Customers")
        if cur.fetchone()["c"] == 0:
            customers = [
                ("Rahul Sharma", "9001112223", "rahul@example.com"),
                ("Aisha Khan", "9003334445", "aisha@example.com")
            ]
            cur.executemany("INSERT INTO Customers(name,phone,email) VALUES(?,?,?)", customers)
        conn.commit()
        self._seed_sales_samples()

    def _seed_sales_samples(self):
        conn = self.conn
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM Orders")
        if cur.fetchone()["c"] == 0:
            now = datetime.datetime.now()
            for d in range(0, 30):
                day = now - datetime.timedelta(days=d)
                cur.execute("INSERT INTO Orders(table_id,customer_id,status,created_at) VALUES(?,?,?,?)",
                            (1, 1, "Paid", day.isoformat()))
                order_id = cur.lastrowid
                cur.execute("SELECT id, price FROM MenuItems LIMIT 3")
                for row in cur.fetchall():
                    cur.execute("INSERT INTO OrderDetails(order_id,item_id,qty,price,kitchen_status) VALUES(?,?,?,?,?)",
                                (order_id, row["id"], 1 + (d % 2), row["price"], "Served"))
                cur.execute("SELECT SUM(qty*price) AS amt FROM OrderDetails WHERE order_id=?", (order_id,))
                amt = cur.fetchone()["amt"] or 0
                gst = round(amt * 0.18, 2)
                cur.execute("INSERT INTO Payments(order_id,amount,gst,method,paid_at) VALUES(?,?,?,?,?)",
                            (order_id, amt, gst, "Cash", day.isoformat()))
        cur.execute("SELECT COUNT(*) AS c FROM Reservations")
        if cur.fetchone()["c"] == 0:
            today = datetime.date.today()
            cur.execute("INSERT INTO Reservations(customer_id,room_id,check_in,check_out,status) VALUES(?,?,?,?,?)",
                        (1, 1, today.isoformat(), (today + datetime.timedelta(days=1)).isoformat(), "CheckedIn"))
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
