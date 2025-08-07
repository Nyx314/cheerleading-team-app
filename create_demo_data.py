import sqlite3
import hashlib
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_data():
    # Create database directory
    os.makedirs('database', exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect('database/app.db')
    
    # Create users table first
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users (id)
        )
    ''')
    
    # Clear existing users
    conn.execute('DELETE FROM users')
    
    # Add demo users
    users = [
        ('coach', hash_password('password123'), 'coach', 'Sarah', 'Johnson', 'coach@school.edu', '555-0101', None),
        ('student1', hash_password('password123'), 'student', 'Emma', 'Smith', 'emma@student.edu', '555-0201', None),
        ('parent1', hash_password('password123'), 'parent', 'John', 'Smith', 'john@email.com', '555-0301', None),
        ('director', hash_password('password123'), 'athletic_director', 'Robert', 'Davis', 'director@school.edu', '555-0103', None),
    ]
    
    for username, password, role, first_name, last_name, email, phone, parent_id in users:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, role, first_name, last_name, email, phone, parent_id))
    
    conn.commit()
    conn.close()
    print("Demo users created successfully!")

if __name__ == '__main__':
    create_demo_data()
