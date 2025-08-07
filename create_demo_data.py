import sqlite3
import hashlib
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create database directory
os.makedirs('database', exist_ok=True)

# Connect to database
conn = sqlite3.connect('database/app.db')

# Add demo users
users = [
    ('coach', hash_password('password123'), 'coach', 'Sarah', 'Johnson', 'coach@school.edu', '555-0101'),
    ('student1', hash_password('password123'), 'student', 'Emma', 'Smith', 'emma@student.edu', '555-0201'),
    ('parent1', hash_password('password123'), 'parent', 'John', 'Smith', 'john@email.com', '555-0301'),
    ('director', hash_password('password123'), 'athletic_director', 'Robert', 'Davis', 'director@school.edu', '555-0103'),
]

for username, password, role, first_name, last_name, email, phone in users:
    try:
        conn.execute('''
            INSERT OR REPLACE INTO users (username, password, role, first_name, last_name, email, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, role, first_name, last_name, email, phone))
    except:
        pass

conn.commit()
conn.close()
print("Demo users created!")
