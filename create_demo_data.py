import sqlite3
import hashlib
from datetime import datetime, timedelta
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_demo_data():
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/app.db')
    
    # Create tables first
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
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT NOT NULL,
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME,
            location TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            sign_in_time TIMESTAMP,
            sign_out_time TIMESTAMP,
            status TEXT DEFAULT 'signed_in',
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS academic_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            grade_required REAL NOT NULL,
            current_grade REAL,
            semester TEXT NOT NULL,
            due_date DATE,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Clear existing data safely
    conn.execute('DELETE FROM attendance WHERE 1=1')
    conn.execute('DELETE FROM academic_requirements WHERE 1=1')
    conn.execute('DELETE FROM events WHERE 1=1')
    conn.execute('DELETE FROM users WHERE 1=1')
    
    # Create demo users
    users = [
        # Coaches and Staff
        ('coach', hash_password('password123'), 'coach', 'Sarah', 'Johnson', 'coach@school.edu', '555-0101', None),
        ('assistant', hash_password('password123'), 'assistant_coach', 'Mike', 'Williams', 'assistant@school.edu', '555-0102', None),
        ('director', hash_password('password123'), 'athletic_director', 'Robert', 'Davis', 'director@school.edu', '555-0103', None),
        
        # Students
        ('student1', hash_password('password123'), 'student', 'Emma', 'Smith', 'emma.smith@student.edu', '555-0201', None),
        ('student2', hash_password('password123'), 'student', 'Sophia', 'Garcia', 'sophia.garcia@student.edu', '555-0202', None),
        ('student3', hash_password('password123'), 'student', 'Olivia', 'Johnson', 'olivia.johnson@student.edu', '555-0203', None),
        ('student4', hash_password('password123'), 'student', 'Ava', 'Brown', 'ava.brown@student.edu', '555-0204', None),
        ('student5', hash_password('password123'), 'student', 'Isabella', 'Davis', 'isabella.davis@student.edu', '555-0205', None),
    ]
    
    for user in users:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', user)
    
    # Get user IDs for parents
    emma_id = conn.execute('SELECT id FROM users WHERE username = "student1"').fetchone()[0]
    sophia_id = conn.execute('SELECT id FROM users WHERE username = "student2"').fetchone()[0]
    olivia_id = conn.execute('SELECT id FROM users WHERE username = "student3"').fetchone()[0]
    
    # Create parents
    parents = [
        ('parent1', hash_password('password123'), 'parent', 'John', 'Smith', 'john.smith@email.com', '555-0301', emma_id),
        ('parent2', hash_password('password123'), 'parent', 'Maria', 'Garcia', 'maria.garcia@email.com', '555-0302', sophia_id),
        ('parent3', hash_password('password123'), 'parent', 'David', 'Johnson', 'david.johnson@email.com', '555-0303', olivia_id),
    ]
    
    for parent in parents:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', parent)
    
    # Create demo events
    coach_id = conn.execute('SELECT id FROM users WHERE username = "coach"').fetchone()[0]
    
    today = datetime.now()
    events = [
        # Today's events
        ('Morning Practice', 'Regular team practice session', 'practice', today.strftime('%Y-%m-%d'), '07:00', '09:00', 'Main Gym', coach_id),
        ('Afternoon Training', 'Conditioning and skills training', 'practice', today.strftime('%Y-%m-%d'), '15:30', '17:30', 'Main Gym', coach_id),
        
        # This week's events
        ('Team Meeting', 'Weekly team meeting and announcements', 'meeting', (today + timedelta(days=1)).strftime('%Y-%m-%d'), '16:00', '17:00', 'Conference Room', coach_id),
        ('Competition Practice', 'Practice for upcoming competition', 'practice', (today + timedelta(days=2)).strftime('%Y-%m-%d'), '15:00', '18:00', 'Main Gym', coach_id),
        
        # Upcoming events
        ('Regional Competition', 'Regional cheerleading competition', 'competition', (today + timedelta(days=7)).strftime('%Y-%m-%d'), '09:00', '17:00', 'Regional Sports Center', coach_id),
        ('Community Performance', 'Performance at community event', 'performance', (today + timedelta(days=14)).strftime('%Y-%m-%d'), '14:00', '16:00', 'Community Center', coach_id),
        ('Fundraiser Event', 'Team fundraising activity', 'fundraiser', (today + timedelta(days=21)).strftime('%Y-%m-%d'), '10:00', '15:00', 'School Parking Lot', coach_id),
    ]
    
    for event in events:
        conn.execute('''
            INSERT INTO events (title, description, event_type, date, start_time, end_time, location, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', event)
    
    # Create academic requirements
    academic_requirements = [
        # Emma Smith (Good standing)
        (emma_id, 'Mathematics', 85.0, 92.0, 'Fall 2024', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'completed', 'Excellent performance', coach_id),
        (emma_id, 'English', 80.0, 88.0, 'Fall 2024', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'completed', 'Good work', coach_id),
        (emma_id, 'Science', 75.0, 82.0, 'Fall 2024', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'completed', 'Steady improvement', coach_id),
        
        # Sophia Garcia (Has academic alerts)
        (sophia_id, 'Mathematics', 80.0, 72.0, 'Fall 2024', (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'at_risk', 'Needs improvement', coach_id),
        (sophia_id, 'English', 75.0, 68.0, 'Fall 2024', (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'at_risk', 'Requires tutoring', coach_id),
        (sophia_id, 'History', 70.0, 74.0, 'Fall 2024', (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'on_track', 'Improving', coach_id),
        
        # Olivia Johnson (Pending requirements)
        (olivia_id, 'Mathematics', 85.0, None, 'Fall 2024', (today + timedelta(days=20)).strftime('%Y-%m-%d'), 'pending', 'Grade pending', coach_id),
        (olivia_id, 'English', 80.0, None, 'Fall 2024', (today + timedelta(days=20)).strftime('%Y-%m-%d'), 'pending', 'Grade pending', coach_id),
        (olivia_id, 'Science', 75.0, 78.0, 'Fall 2024', (today + timedelta(days=20)).strftime('%Y-%m-%d'), 'on_track', 'Good progress', coach_id),
    ]
    
    for req in academic_requirements:
        conn.execute('''
            INSERT INTO academic_requirements 
            (student_id, subject, grade_required, current_grade, semester, due_date, status, notes, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', req)
    
    # Create some attendance records
    event_ids = [row[0] for row in conn.execute('SELECT id FROM events').fetchall()]
    student_ids = [emma_id, sophia_id, olivia_id]
    
    # Create attendance for today's first event
    if event_ids:
        for student_id in student_ids:
            conn.execute('''
                INSERT INTO attendance (user_id, event_id, sign_in_time, status)
                VALUES (?, ?, ?, 'signed_in')
            ''', (student_id, event_ids[0], today.replace(hour=7, minute=5)))
    
    conn.commit()
    conn.close()
    print("Demo data created successfully!")

if __name__ == '__main__':
    create_demo_data()
