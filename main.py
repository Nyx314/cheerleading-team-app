from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'your-secret-key-change-in-production'
CORS(app, supports_credentials=True)

DATABASE = 'database/app.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = get_db()
    
    # Users table
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
    
    # Events table
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
    
    # Attendance table
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
    
    # Academic requirements table
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
    
    conn.commit()
    conn.close()

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    
    if user and user['password'] == hash_password(password):
        session['user_id'] = user['id']
        session['role'] = user['role']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    user = conn.execute(
        'SELECT id, username, role, first_name, last_name, email FROM users WHERE id = ?',
        (session['user_id'],)
    ).fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email']
        })
    
    return jsonify({'error': 'User not found'}), 404

# Events routes
@app.route('/api/events', methods=['GET'])
def get_events():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    events = conn.execute('''
        SELECT e.*, u.first_name, u.last_name 
        FROM events e
        LEFT JOIN users u ON e.created_by = u.id
        ORDER BY e.date ASC, e.start_time ASC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(event) for event in events])

@app.route('/api/events', methods=['POST'])
def create_event():
    if 'user_id' not in session or session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    required_fields = ['title', 'event_type', 'date', 'start_time']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO events (title, description, event_type, date, start_time, end_time, location, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['title'], data.get('description', ''), data['event_type'],
        data['date'], data['start_time'], data.get('end_time'),
        data.get('location', ''), session['user_id']
    ))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'event_id': event_id}), 201

@app.route('/api/events/today', methods=['GET'])
def get_today_events():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    events = conn.execute('''
        SELECT * FROM events 
        WHERE date = ?
        ORDER BY start_time ASC
    ''', (today,)).fetchall()
    conn.close()
    
    return jsonify([dict(event) for event in events])

# Attendance routes
@app.route('/api/attendance/sign-in', methods=['POST'])
def sign_in():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    event_id = data.get('event_id')
    
    if not event_id:
        return jsonify({'error': 'Event ID required'}), 400
    
    conn = get_db()
    
    # Check if already signed in
    existing = conn.execute('''
        SELECT * FROM attendance 
        WHERE user_id = ? AND event_id = ? AND sign_out_time IS NULL
    ''', (session['user_id'], event_id)).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'error': 'Already signed in'}), 400
    
    # Sign in
    conn.execute('''
        INSERT INTO attendance (user_id, event_id, sign_in_time, status)
        VALUES (?, ?, ?, 'signed_in')
    ''', (session['user_id'], event_id, datetime.now()))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/attendance/sign-out', methods=['POST'])
def sign_out():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    event_id = data.get('event_id')
    
    conn = get_db()
    conn.execute('''
        UPDATE attendance 
        SET sign_out_time = ?, status = 'completed'
        WHERE user_id = ? AND event_id = ? AND sign_out_time IS NULL
    ''', (datetime.now(), session['user_id'], event_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/attendance/students/<int:student_id>/attendance', methods=['GET'])
def get_student_attendance(student_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check permissions
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        # Students can only view their own attendance
        # Parents can view their child's attendance
        if session['role'] == 'student' and session['user_id'] != student_id:
            return jsonify({'error': 'Unauthorized'}), 403
        elif session['role'] == 'parent':
            conn = get_db()
            student = conn.execute(
                'SELECT parent_id FROM users WHERE id = ?', (student_id,)
            ).fetchone()
            if not student or student['parent_id'] != session['user_id']:
                conn.close()
                return jsonify({'error': 'Unauthorized'}), 403
            conn.close()
    
    conn = get_db()
    attendance = conn.execute('''
        SELECT a.*, e.title, e.date, e.start_time, e.event_type
        FROM attendance a
        JOIN events e ON a.event_id = e.id
        WHERE a.user_id = ?
        ORDER BY e.date DESC, e.start_time DESC
    ''', (student_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(record) for record in attendance])

# Academic requirements routes
@app.route('/api/academics/requirements', methods=['GET'])
def get_academic_requirements():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    
    if session['role'] == 'student':
        requirements = conn.execute('''
            SELECT ar.*, u.first_name, u.last_name
            FROM academic_requirements ar
            LEFT JOIN users u ON ar.created_by = u.id
            WHERE ar.student_id = ?
            ORDER BY ar.due_date ASC
        ''', (session['user_id'],)).fetchall()
    elif session['role'] == 'parent':
        # Get requirements for parent's children
        requirements = conn.execute('''
            SELECT ar.*, u.first_name, u.last_name, s.first_name as student_first, s.last_name as student_last
            FROM academic_requirements ar
            LEFT JOIN users u ON ar.created_by = u.id
            JOIN users s ON ar.student_id = s.id
            WHERE s.parent_id = ?
            ORDER BY ar.due_date ASC
        ''', (session['user_id'],)).fetchall()
    else:
        # Coaches and directors see all requirements
        requirements = conn.execute('''
            SELECT ar.*, u.first_name, u.last_name, s.first_name as student_first, s.last_name as student_last
            FROM academic_requirements ar
            LEFT JOIN users u ON ar.created_by = u.id
            JOIN users s ON ar.student_id = s.id
            ORDER BY ar.due_date ASC
        ''').fetchall()
    
    conn.close()
    return jsonify([dict(req) for req in requirements])

@app.route('/api/academics/requirements', methods=['POST'])
def create_academic_requirement():
    if 'user_id' not in session or session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    required_fields = ['student_id', 'subject', 'grade_required', 'semester']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO academic_requirements 
        (student_id, subject, grade_required, current_grade, semester, due_date, notes, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['student_id'], data['subject'], data['grade_required'],
        data.get('current_grade'), data['semester'], data.get('due_date'),
        data.get('notes', ''), session['user_id']
    ))
    conn.commit()
    req_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'success': True, 'requirement_id': req_id}), 201

@app.route('/api/academics/alerts', methods=['GET'])
def get_academic_alerts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    
    # Get requirements where current grade is below required grade
    alerts = conn.execute('''
        SELECT ar.*, s.first_name, s.last_name, s.username
        FROM academic_requirements ar
        JOIN users s ON ar.student_id = s.id
        WHERE ar.current_grade IS NOT NULL 
        AND ar.current_grade < ar.grade_required
        AND ar.status != 'completed'
        ORDER BY ar.due_date ASC
    ''').fetchall()
    
    conn.close()
    return jsonify([dict(alert) for alert in alerts])

# User management routes
@app.route('/api/users/students', methods=['GET'])
def get_students():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    students = conn.execute('''
        SELECT id, username, first_name, last_name, email, phone, grade
        FROM users 
        WHERE role = 'student'
        ORDER BY grade, last_name, first_name
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(student) for student in students])

# Serve React app
@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
    # =========== ADD THESE NEW ROUTES FOR EVENT MANAGEMENT ===========

@app.route('/api/events', methods=['POST'])
def create_event():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check if user is coach or athletic director
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    # Validate required fields
    required_fields = ['title', 'event_type', 'date', 'start_time']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO events (title, description, event_type, date, start_time, 
                              end_time, location, is_mandatory, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('description', ''),
            data['event_type'],
            data['date'],
            data['start_time'],
            data.get('end_time'),
            data.get('location', ''),
            data.get('is_mandatory', False),
            session['user_id']
        ))
        
        event_id = cursor.lastrowid
        db.commit()
        
        # Fetch the created event
        event = db.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        db.close()
        
        return jsonify(dict(event)), 201
        
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    db = get_db()
    
    # Build update query dynamically
    update_fields = []
    values = []
    
    allowed_fields = ['title', 'description', 'event_type', 'date', 'start_time', 
                     'end_time', 'location', 'is_mandatory']
    
    for field in allowed_fields:
        if field in data:
            update_fields.append(f'{field} = ?')
            values.append(data[field])
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    values.append(event_id)
    
    try:
        db.execute(
            f"UPDATE events SET {', '.join(update_fields)} WHERE id = ?",
            values
        )
        db.commit()
        
        event = db.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        db.close()
        
        return jsonify(dict(event))
        
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    
    try:
        # Delete related attendance records first
        db.execute('DELETE FROM attendance WHERE event_id = ?', (event_id,))
        # Delete the event
        db.execute('DELETE FROM events WHERE id = ?', (event_id,))
        db.commit()
        db.close()
        
        return jsonify({'message': 'Event deleted successfully'})
        
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400

# =========== ADD THESE NEW ROUTES FOR ACADEMIC MANAGEMENT ===========

@app.route('/api/academics/requirements', methods=['GET'])
def get_requirements():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    requirements = db.execute(
        'SELECT * FROM academic_requirements ORDER BY subject'
    ).fetchall()
    db.close()
    
    return jsonify([dict(req) for req in requirements])

@app.route('/api/academics/requirements', methods=['POST'])
def create_requirement():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    # Validate required fields
    if not data.get('subject') or not data.get('grade_required'):
        return jsonify({'error': 'Subject and grade_required are required'}), 400
    
    db = get_db()
    
    try:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO academic_requirements (subject, grade_required, semester, year)
            VALUES (?, ?, ?, ?)
        ''', (
            data['subject'],
            data['grade_required'],
            data.get('semester', 'Fall'),
            data.get('year', datetime.now().year)
        ))
        
        req_id = cursor.lastrowid
        db.commit()
        
        requirement = db.execute(
            'SELECT * FROM academic_requirements WHERE id = ?', 
            (req_id,)
        ).fetchone()
        db.close()
        
        return jsonify(dict(requirement)), 201
        
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/academics/requirements/<int:req_id>', methods=['DELETE'])
def delete_requirement(req_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    
    try:
        # Delete related student grades first
        db.execute('DELETE FROM student_grades WHERE requirement_id = ?', (req_id,))
        # Delete the requirement
        db.execute('DELETE FROM academic_requirements WHERE id = ?', (req_id,))
        db.commit()
        db.close()
        
        return jsonify({'message': 'Requirement deleted successfully'})
        
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/students', methods=['GET'])
def get_students():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = get_db()
    students = db.execute('''
        SELECT s.*, u.first_name, u.last_name, u.email
        FROM students s
        JOIN users u ON s.user_id = u.id
        ORDER BY u.last_name, u.first_name
    ''').fetchall()
    db.close()
    
    return jsonify([dict(student) for student in students])

@app.route('/api/students/<int:student_id>/grades', methods=['POST'])
def update_student_grade(student_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    if not data.get('requirement_id') or data.get('grade') is None:
        return jsonify({'error': 'requirement_id and grade are required'}), 400
    
    db = get_db()
    
    try:
        # Check if grade entry exists
        existing = db.execute('''
            SELECT id FROM student_grades 
            WHERE student_id = ? AND requirement_id = ?
        ''', (student_id, data['requirement_id'])).fetchone()
        
        if existing:
            # Update existing grade
            db.execute('''
                UPDATE student_grades 
                SET current_grade = ?, last_updated = ?
                WHERE student_id = ? AND requirement_id = ?
            ''', (data['grade'], datetime.now(), student_id, data['requirement_id']))
        else:
            # Insert new grade
            db.execute('''
                INSERT INTO student_grades (student_id, requirement_id, current_grade, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (student_id, data['requirement_id'], data['grade'], datetime.now()))
        
        db.commit()
        db.close()
        
        return jsonify({'message': 'Grade updated successfully'})
        
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 400
