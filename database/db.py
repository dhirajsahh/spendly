import sqlite3
from werkzeug.security import generate_password_hash

def get_db():
    """Open connection to spendly.db with row_factory and foreign keys enabled."""
    conn = sqlite3.connect('spendly.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    try:
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        # Create expenses table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def seed_db():
    """Seed the database with demo data if empty."""
    conn = get_db()
    try:
        # Check if users table already has data
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        if count > 0:
            return  # Already seeded

        # Hash the demo password
        password_hash = generate_password_hash('demo123')

        # Insert demo user
        cursor = conn.execute(
            '''INSERT INTO users (name, email, password_hash)
               VALUES (?, ?, ?)''',
            ('Demo User', 'demo@spendly.com', password_hash)
        )
        user_id = cursor.lastrowid

        # Sample expenses data: 8 expenses across categories
        # Categories list from spec
        categories = ['Food', 'Transport', 'Bills', 'Health', 'Entertainment', 'Shopping', 'Other']
        # We'll create 8 expenses: one for each category plus an extra for Food
        expenses_data = [
            # Food (two entries)
            {'amount': 12.50, 'category': 'Food', 'date': '2026-06-01', 'description': 'Groceries at supermarket'},
            {'amount': 8.75, 'category': 'Food', 'date': '2026-06-03', 'description': 'Lunch at cafe'},
            # Transport
            {'amount': 25.00, 'category': 'Transport', 'date': '2026-06-02', 'description': 'Taxi ride to airport'},
            # Bills
            {'amount': 85.30, 'category': 'Bills', 'date': '2026-06-05', 'description': 'Electricity bill'},
            # Health
            {'amount': 45.00, 'category': 'Health', 'date': '2026-06-04', 'description': 'Pharmacy prescription'},
            # Entertainment
            {'amount': 20.00, 'category': 'Entertainment', 'date': '2026-06-06', 'description': 'Movie tickets'},
            # Shopping
            {'amount': 60.00, 'category': 'Shopping', 'date': '2026-06-07', 'description': 'New clothing'},
            # Other
            {'amount': 15.99, 'category': 'Other', 'date': '2026-06-08', 'description': 'Household supplies'},
        ]

        # Insert each expense
        for expense in expenses_data:
            conn.execute(
                '''INSERT INTO expenses (user_id, amount, category, date, description)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, expense['amount'], expense['category'], expense['date'], expense['description'])
            )

        conn.commit()
    finally:
        conn.close()