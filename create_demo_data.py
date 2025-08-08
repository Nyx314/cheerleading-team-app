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
    
    # Create users table with grade field
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
            grade TEXT,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users (id)
        )
    ''')
    
    # Clear existing users
    conn.execute('DELETE FROM users')
    
    # Add demo users organized by grade
    users = [
        # Coaches (no grade needed)
        ('coach', hash_password('password123'), 'coach', 'Y', 'Llevada', 'coach@aviators.edu', '555-0101', None, None),
        ('assistant', hash_password('password123'), 'coach', 'Kat', 'Atherly', 'assistant@aviators.edu', '555-0102', None, None),
        
        # 9th Grade Cheerleaders
        ('student1', hash_password('password123'), 'student', 'Emma', 'Smith', 'emma@aviators.edu', '555-0201', '9th', None),
        ('student5', hash_password('password123'), 'student', 'Isabella', 'Davis', 'isabella@aviators.edu', '555-0205', '9th', None),
        
        # 10th Grade Cheerleaders  
        ('student2', hash_password('password123'), 'student', 'Sophia', 'Garcia', 'sophia@aviators.edu', '555-0202', '10th', None),
        ('student6', hash_password('password123'), 'student', 'Mia', 'Wilson', 'mia@aviators.edu', '555-0206', '10th', None),
        
        # 11th Grade Cheerleaders
        ('student3', hash_password('password123'), 'student', 'Olivia', 'Johnson', 'olivia@aviators.edu', '555-0203', '11th', None),
        ('student7', hash_password('password123'), 'student', 'Charlotte', 'Moore', 'charlotte@aviators.edu', '555-0207', '11th', None),
        
        # 12th Grade Cheerleaders
        ('student4', hash_password('password123'), 'student', 'Ava', 'Brown', 'ava@aviators.edu', '555-0204', '12th', None),
        ('student8', hash_password('password123'), 'student', 'Amelia', 'Taylor', 'amelia@aviators.edu', '555-0208', '12th', None),
    ]
    
    for username, password, role, first_name, last_name, email, phone, grade, parent_id in users:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, grade, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, role, first_name, last_name, email, phone, grade, parent_id))
    
    # Add parents for some students
    emma_id = conn.execute('SELECT id FROM users WHERE username = "student1"').fetchone()[0]
    sophia_id = conn.execute('SELECT id FROM users WHERE username = "student2"').fetchone()[0]
    olivia_id = conn.execute('SELECT id FROM users WHERE username = "student3"').fetchone()[0]
    
    parents = [
        ('parent1', hash_password('password123'), 'parent', 'John', 'Smith', 'john.smith@email.com', '555-0301', None, emma_id),
        ('parent2', hash_password('password123'), 'parent', 'Maria', 'Garcia', 'maria.garcia@email.com', '555-0302', None, sophia_id),
        ('parent3', hash_password('password123'), 'parent', 'David', 'Johnson', 'david.johnson@email.com', '555-0303', None, olivia_id),
    ]
    
    for username, password, role, first_name, last_name, email, phone, grade, parent_id in parents:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, grade, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, role, first_name, last_name, email, phone, grade, parent_id))
    
    conn.commit()
    conn.close()
    print("Aviators demo users created successfully!")

if __name__ == '__main__':
    create_demo_data()
