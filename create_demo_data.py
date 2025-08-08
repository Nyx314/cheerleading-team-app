import sqlite3
import hashlib
from datetime import datetime, timedelta
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_aviators_data():
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/app.db')
    
    # Clear existing data
    conn.execute('DELETE FROM attendance')
    conn.execute('DELETE FROM academic_requirements')
    conn.execute('DELETE FROM events')
    conn.execute('DELETE FROM users')
    
    # AVIATORS COACHING STAFF
    coaches_staff = [
        # Format: (username, password, role, first_name, last_name, email, phone, grade, parent_id)
        ('coach.llevada', hash_password('Aviators2025!'), 'coach', 'Y', 'Llevada', 'y.llevada@aviators.edu', '786-267-2707', None, None),
        ('coach.atherly', hash_password('Aviators2025!'), 'coach', 'Kat', 'Atherly', 'k.atherly@aviators.edu', '555-0102', None, None),
    ]
    
    for user in coaches_staff:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, grade, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', user)
    
    # AVIATORS CHEERLEADING TEAM BY GRADE
    # Replace these with your actual team members - organized by grade
    
    # 9TH GRADE CHEERLEADERS
    ninth_graders = [
        # Format: (username, password, role, first_name, last_name, email, phone, grade, parent_id)
        ('emma.smith', hash_password('Aviators2025!'), 'student', 'Emma', 'Smith', 'emma.smith@student.aviators.edu', '555-1001', '9th', None),
        ('sophia.johnson', hash_password('Aviators2025!'), 'student', 'Sophia', 'Johnson', 'sophia.johnson@student.aviators.edu', '555-1002', '9th', None),
        ('olivia.williams', hash_password('Aviators2025!'), 'student', 'Olivia', 'Williams', 'olivia.williams@student.aviators.edu', '555-1003', '9th', None),
        # ADD MORE 9TH GRADERS HERE:
        # ('firstname.lastname', hash_password('Aviators2025!'), 'student', 'FirstName', 'LastName', 'firstname.lastname@student.aviators.edu', '555-1004', '9th', None),
    ]
    
    # 10TH GRADE CHEERLEADERS
    tenth_graders = [
        ('ava.brown', hash_password('Aviators2025!'), 'student', 'Ava', 'Brown', 'ava.brown@student.aviators.edu', '555-1101', '10th', None),
        ('isabella.davis', hash_password('Aviators2025!'), 'student', 'Isabella', 'Davis', 'isabella.davis@student.aviators.edu', '555-1102', '10th', None),
        ('mia.miller', hash_password('Aviators2025!'), 'student', 'Mia', 'Miller', 'mia.miller@student.aviators.edu', '555-1103', '10th', None),
        # ADD MORE 10TH GRADERS HERE:
        # ('firstname.lastname', hash_password('Aviators2025!'), 'student', 'FirstName', 'LastName', 'firstname.lastname@student.aviators.edu', '555-1104', '10th', None),
    ]
    
    # 11TH GRADE CHEERLEADERS
    eleventh_graders = [
        ('charlotte.wilson', hash_password('Aviators2025!'), 'student', 'Charlotte', 'Wilson', 'charlotte.wilson@student.aviators.edu', '555-1201', '11th', None),
        ('amelia.moore', hash_password('Aviators2025!'), 'student', 'Amelia', 'Moore', 'amelia.moore@student.aviators.edu', '555-1202', '11th', None),
        ('harper.taylor', hash_password('Aviators2025!'), 'student', 'Harper', 'Taylor', 'harper.taylor@student.aviators.edu', '555-1203', '11th', None),
        # ADD MORE 11TH GRADERS HERE:
        # ('firstname.lastname', hash_password('Aviators2025!'), 'student', 'FirstName', 'LastName', 'firstname.lastname@student.aviators.edu', '555-1204', '11th', None),
    ]
    
    # 12TH GRADE CHEERLEADERS (SENIORS)
    seniors = [
        ('evelyn.anderson', hash_password('Aviators2025!'), 'student', 'Evelyn', 'Anderson', 'evelyn.anderson@student.aviators.edu', '555-1301', '12th', None),
        ('abigail.thomas', hash_password('Aviators2025!'), 'student', 'Abigail', 'Thomas', 'abigail.thomas@student.aviators.edu', '555-1302', '12th', None),
        ('emily.jackson', hash_password('Aviators2025!'), 'student', 'Emily', 'Jackson', 'emily.jackson@student.aviators.edu', '555-1303', '12th', None),
        # ADD MORE SENIORS HERE:
        # ('firstname.lastname', hash_password('Aviators2025!'), 'student', 'FirstName', 'LastName', 'firstname.lastname@student.aviators.edu', '555-1304', '12th', None),
    ]
    
    # Insert all students
    all_students = ninth_graders + tenth_graders + eleventh_graders + seniors
    for student in all_students:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, grade, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', student)
    
    # GET COACH ID FOR EVENTS
    coach_id = conn.execute('SELECT id FROM users WHERE role = "coach" LIMIT 1').fetchone()[0]
    
    # CREATE AVIATORS PRACTICE SCHEDULE AND EVENTS
    today = datetime.now()
    events = [
        # THIS WEEK'S PRACTICES
        ('Monday Practice', 'Regular team practice - stunts and tumbling', 'practice', 
         (today + timedelta(days=1)).strftime('%Y-%m-%d'), '15:30', '17:30', 'Main Gym', coach_id),
        
        ('Wednesday Practice', 'Game routine practice', 'practice', 
         (today + timedelta(days=3)).strftime('%Y-%m-%d'), '15:30', '17:30', 'Main Gym', coach_id),
        
        ('Friday Practice', 'Competition prep', 'practice', 
         (today + timedelta(days=5)).strftime('%Y-%m-%d'), '15:30', '17:30', 'Main Gym', coach_id),
        
        # UPCOMING EVENTS
        ('Team Meeting', 'Monthly team meeting and announcements', 'meeting', 
         (today + timedelta(days=7)).strftime('%Y-%m-%d'), '16:00', '17:00', 'Conference Room', coach_id),
        
        ('Home Football Game', 'Halftime performance vs Eagles', 'performance', 
         (today + timedelta(days=10)).strftime('%Y-%m-%d'), '18:00', '21:00', 'Aviators Stadium', coach_id),
        
        ('Regional Competition', 'Regional cheerleading competition', 'competition', 
         (today + timedelta(days=21)).strftime('%Y-%m-%d'), '08:00', '18:00', 'Regional Sports Center', coach_id),
        
        ('Homecoming Performance', 'Homecoming halftime show', 'performance', 
         (today + timedelta(days=28)).strftime('%Y-%m-%d'), '19:00', '22:00', 'Aviators Stadium', coach_id),
        
        ('Car Wash Fundraiser', 'Team fundraising event', 'fundraiser', 
         (today + timedelta(days=35)).strftime('%Y-%m-%d'), '09:00', '15:00', 'School Parking Lot', coach_id),
    ]
    
    for event in events:
        conn.execute('''
            INSERT INTO events (title, description, event_type, date, start_time, end_time, location, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', event)
    
    # ADD SAMPLE PARENTS (OPTIONAL)
    # Get some student IDs for parent relationships
    sample_students = conn.execute('SELECT id, first_name, last_name FROM users WHERE role = "student" LIMIT 3').fetchall()
    
    sample_parents = [
        ('parent.smith', hash_password('Aviators2025!'), 'parent', 'Robert', 'Smith', 'robert.smith@email.com', '555-2001', None, sample_students[0][0]),
        ('parent.johnson', hash_password('Aviators2025!'), 'parent', 'Maria', 'Johnson', 'maria.johnson@email.com', '555-2002', None, sample_students[1][0]),
        ('parent.williams', hash_password('Aviators2025!'), 'parent', 'David', 'Williams', 'david.williams@email.com', '555-2003', None, sample_students[2][0]),
    ]
    
    for parent in sample_parents:
        conn.execute('''
            INSERT INTO users (username, password, role, first_name, last_name, email, phone, grade, parent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', parent)
    
    # CREATE SAMPLE ACADEMIC REQUIREMENTS
    student_ids = [row[0] for row in conn.execute('SELECT id FROM users WHERE role = "student" LIMIT 5').fetchall()]
    
    for student_id in student_ids:
        requirements = [
            (student_id, 'Mathematics', 80.0, None, 'Fall 2025', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'pending', 'Grade pending', coach_id),
            (student_id, 'English', 75.0, None, 'Fall 2025', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'pending', 'Grade pending', coach_id),
            (student_id, 'History', 75.0, None, 'Fall 2025', (today + timedelta(days=30)).strftime('%Y-%m-%d'), 'pending', 'Grade pending', coach_id),
        ]
        
        for req in requirements:
            conn.execute('''
                INSERT INTO academic_requirements 
                (student_id, subject, grade_required, current_grade, semester, due_date, status, notes, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', req)
    
    conn.commit()
    conn.close()
    print("✅ Aviators Cheerleading Team data created successfully!")
    print("\n🏆 AVIATORS LOGIN CREDENTIALS:")
    print("="*50)
    print("COACHES:")
    print("Coach Y. Llevada: coach.llevada / Aviators2025!")
    print("Coach Kat Atherly: coach.atherly / Aviators2025!")
    print("\nSTUDENTS:")
    print("All students: firstname.lastname / Aviators2025!")
    print("Example: emma.smith / Aviators2025!")
    print("\nPARENTS:")
    print("Parents: parent.lastname / Aviators2025!")
    print("Example: parent.smith / Aviators2025!")
    print("="*50)

if __name__ == '__main__':
    create_aviators_data()
