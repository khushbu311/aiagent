import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import json

class OrderDatabase:
    def __init__(self, db_path: str = "orders.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                items TEXT NOT NULL,  -- JSON string of ordered items
                total_amount REAL NOT NULL,
                order_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Create menu table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                available BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Populate menu if empty
        self.populate_menu()
    
    def populate_menu(self):
        """Populate menu with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if menu is already populated
        cursor.execute("SELECT COUNT(*) FROM menu")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        menu_items = [
            ("Margherita Pizza", "Pizza", 12.99, "Classic pizza with tomato sauce, mozzarella, and basil"),
            ("Pepperoni Pizza", "Pizza", 15.99, "Pizza topped with pepperoni and mozzarella cheese"),
            ("Caesar Salad", "Salad", 8.99, "Romaine lettuce with Caesar dressing and croutons"),
            ("Chicken Burger", "Burger", 13.99, "Grilled chicken breast with lettuce and tomato"),
            ("Beef Burger", "Burger", 16.99, "Juicy beef patty with cheese, lettuce, and tomato"),
            ("Pasta Carbonara", "Pasta", 14.99, "Creamy pasta with bacon and parmesan cheese"),
            ("Coca Cola", "Beverage", 2.99, "Refreshing cola drink"),
            ("Orange Juice", "Beverage", 3.99, "Fresh squeezed orange juice"),
            ("Chocolate Cake", "Dessert", 6.99, "Rich chocolate cake with frosting"),
            ("Ice Cream", "Dessert", 4.99, "Vanilla ice cream with chocolate chips")
        ]
        
        cursor.executemany(
            "INSERT INTO menu (name, category, price, description) VALUES (?, ?, ?, ?)",
            menu_items
        )
        
        conn.commit()
        conn.close()
    
    def get_menu(self) -> List[Dict[str, Any]]:
        """Retrieve all menu items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, price, description, available 
            FROM menu WHERE available = 1
            ORDER BY category, name
        """)
        
        columns = ['id', 'name', 'category', 'price', 'description', 'available']
        menu_items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return menu_items
    
    def create_order(self, customer_name: str, items: List[Dict], total_amount: float) -> int:
        """Create a new order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        items_json = json.dumps(items)
        
        cursor.execute("""
            INSERT INTO orders (customer_name, items, total_amount)
            VALUES (?, ?, ?)
        """, (customer_name, items_json, total_amount))
        
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return order_id
    
    def get_order_analytics(self) -> Dict[str, Any]:
        """Get analytics data for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total orders
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        # Total revenue
        cursor.execute("SELECT SUM(total_amount) FROM orders")
        total_revenue = cursor.fetchone()[0] or 0
        
        # Most popular items
        cursor.execute("""
            SELECT items FROM orders
        """)
        
        all_items = {}
        for row in cursor.fetchall():
            items = json.loads(row[0])
            for item in items:
                item_name = item['name']
                quantity = item['quantity']
                if item_name in all_items:
                    all_items[item_name] += quantity
                else:
                    all_items[item_name] = quantity
        
        # Sort by popularity
        popular_items = sorted(all_items.items(), key=lambda x: x[1], reverse=True)[:5]
        
        conn.close()
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'popular_items': popular_items
        }