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
            grade INTEGER,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES users (id)
        )
    ''')
    
    # Events table - UPDATED with is_mandatory field
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
            is_mandatory BOOLEAN DEFAULT 0,
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
    
    # Academic requirements table - SIMPLIFIED
    conn.execute('''
        CREATE TABLE IF NOT EXISTS academic_requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            grade_required REAL NOT NULL,
            semester TEXT,
            year INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Student grades table - NEW
    conn.execute('''
        CREATE TABLE IF NOT EXISTS student_grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            requirement_id INTEGER NOT NULL,
            current_grade REAL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (requirement_id) REFERENCES academic_requirements (id),
            UNIQUE(student_id, requirement_id)
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

# Events routes - GET all events
@app.route('/api/events', methods=['GET'])
def get_events():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    events = conn.execute('''
        SELECT e.*, u.first_name, u.last_name 
        FROM events e
        LEFT JOIN users u ON e.created_by = u.id
        ORDER BY e.date DESC, e.start_time DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(event) for event in events])

# Events routes - CREATE event (UPDATED)
@app.route('/api/events', methods=['POST'])
def create_event():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    required_fields = ['title', 'event_type', 'date', 'start_time']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    conn = get_db()
    cursor = conn.execute('''
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
    conn.commit()
    event_id = cursor.lastrowid
    
    # Get the created event
    event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
    conn.close()
    
    return jsonify(dict(event)), 201

# UPDATE event
@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    conn = get_db()
    
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
        conn.execute(
            f"UPDATE events SET {', '.join(update_fields)} WHERE id = ?",
            values
        )
        conn.commit()
        
        event = conn.execute('SELECT * FROM events WHERE id = ?', (event_id,)).fetchone()
        conn.close()
        
        return jsonify(dict(event))
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

# DELETE event
@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    
    try:
        # Delete related attendance records first
        conn.execute('DELETE FROM attendance WHERE event_id = ?', (event_id,))
        # Delete the event
        conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Event deleted successfully'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

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

# Academic requirements routes - GET
@app.route('/api/academics/requirements', methods=['GET'])
def get_requirements():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    requirements = conn.execute(
        'SELECT * FROM academic_requirements ORDER BY subject'
    ).fetchall()
    conn.close()
    
    return jsonify([dict(req) for req in requirements])

# Academic requirements routes - CREATE
@app.route('/api/academics/requirements', methods=['POST'])
def create_requirement():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('subject') or not data.get('grade_required'):
        return jsonify({'error': 'Subject and grade_required are required'}), 400
    
    conn = get_db()
    
    try:
        cursor = conn.cursor()
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
        conn.commit()
        
        requirement = conn.execute(
            'SELECT * FROM academic_requirements WHERE id = ?', 
            (req_id,)
        ).fetchone()
        conn.close()
        
        return jsonify(dict(requirement)), 201
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

# Academic requirements routes - DELETE
@app.route('/api/academics/requirements/<int:req_id>', methods=['DELETE'])
def delete_requirement(req_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    
    try:
        # Delete related student grades first
        conn.execute('DELETE FROM student_grades WHERE requirement_id = ?', (req_id,))
        # Delete the requirement
        conn.execute('DELETE FROM academic_requirements WHERE id = ?', (req_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Requirement deleted successfully'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

# Academic alerts
@app.route('/api/academics/alerts', methods=['GET'])
def get_academic_alerts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    
    # Get students with grades below requirements
    alerts = conn.execute('''
        SELECT 
            u.first_name, 
            u.last_name,
            ar.subject,
            ar.grade_required,
            sg.current_grade
        FROM student_grades sg
        JOIN users u ON sg.student_id = u.id
        JOIN academic_requirements ar ON sg.requirement_id = ar.id
        WHERE sg.current_grade < ar.grade_required
        AND u.role = 'student'
        ORDER BY u.last_name, u.first_name
    ''').fetchall()
    
    conn.close()
    return jsonify([dict(alert) for alert in alerts])

# User management routes - Get students
@app.route('/api/users/students', methods=['GET'])
def get_students():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    students = conn.execute('''
        SELECT id, username, first_name, last_name, email, phone, grade
        FROM users 
        WHERE role = 'student'
        ORDER BY last_name, first_name
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(student) for student in students])

# Update student grades
@app.route('/api/students/<int:student_id>/grades', methods=['POST'])
def update_student_grade(student_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if session['role'] not in ['coach', 'assistant_coach', 'athletic_director']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data.get('requirement_id') or data.get('grade') is None:
        return jsonify({'error': 'requirement_id and grade are required'}), 400
    
    conn = get_db()
    
    try:
        # Check if grade entry exists
        existing = conn.execute('''
            SELECT id FROM student_grades 
            WHERE student_id = ? AND requirement_id = ?
        ''', (student_id, data['requirement_id'])).fetchone()
        
        if existing:
            # Update existing grade
            conn.execute('''
                UPDATE student_grades 
                SET current_grade = ?, last_updated = ?
                WHERE student_id = ? AND requirement_id = ?
            ''', (data['grade'], datetime.now(), student_id, data['requirement_id']))
        else:
            # Insert new grade
            conn.execute('''
                INSERT INTO student_grades (student_id, requirement_id, current_grade, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (student_id, data['requirement_id'], data['grade'], datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Grade updated successfully'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

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
         app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
         init_db()
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
    
