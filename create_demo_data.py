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
        
        // ADD THIS TO YOUR static/index.html - REPLACE the renderCoachDashboard function

function renderCoachDashboard() {
    const alertsHtml = currentAlerts.length === 0 
        ? '<div class="empty-state">No academic alerts at this time</div>'
        : currentAlerts.map(alert => `
            <div class="alert-item">
                <div class="alert-title">${alert.first_name} ${alert.last_name} - ${alert.subject}</div>
                <div class="alert-text">Current: ${alert.current_grade}% (Required: ${alert.grade_required}%)</div>
            </div>
        `).join('');
    
    return `
        <div class="main-content">
            <div class="card">
                <h2 class="card-title">Coach Dashboard 📊</h2>
                <p class="card-subtitle">Manage your team and track performance</p>
                
                <div class="stats-grid">
                    <div class="stat-card red">
                        <div class="stat-title">Academic Alerts</div>
                        <div class="stat-value">${currentAlerts.length}</div>
                    </div>
                    <div class="stat-card blue">
                        <div class="stat-title">Total Events</div>
                        <div class="stat-value">${currentEvents.length}</div>
                    </div>
                    <div class="stat-card green">
                        <div class="stat-title">Active Students</div>
                        <div class="stat-value">15</div>
                    </div>
                    <div class="stat-card purple">
                        <div class="stat-title">This Season</div>
                        <div class="stat-value">2024</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <button class="btn-action" onclick="showCreateEvent()">
                        ➕ Create New Event
                    </button>
                    <button class="btn-secondary" onclick="showAttendanceTracker()">
                        📋 View Attendance
                    </button>
                    <button class="btn-action" onclick="showStudentList()">
                        👥 Manage Students
                    </button>
                </div>
            </div>

            <!-- CREATE EVENT FORM -->
            <div id="createEventCard" class="card" style="display: none;">
                <h3 class="section-title">➕ Create New Event</h3>
                <form id="createEventForm">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
                        <div>
                            <label class="form-label">Event Title</label>
                            <input type="text" id="eventTitle" class="form-input" required placeholder="Monday Practice">
                        </div>
                        <div>
                            <label class="form-label">Event Type</label>
                            <select id="eventType" class="form-input" required>
                                <option value="practice">Practice</option>
                                <option value="competition">Competition</option>
                                <option value="performance">Performance</option>
                                <option value="meeting">Team Meeting</option>
                                <option value="fundraiser">Fundraiser</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 16px;">
                        <div>
                            <label class="form-label">Date</label>
                            <input type="date" id="eventDate" class="form-input" required>
                        </div>
                        <div>
                            <label class="form-label">Start Time</label>
                            <input type="time" id="startTime" class="form-input" required>
                        </div>
                        <div>
                            <label class="form-label">End Time</label>
                            <input type="time" id="endTime" class="form-input">
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <label class="form-label">Location</label>
                        <input type="text" id="eventLocation" class="form-input" placeholder="Main Gym">
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <label class="form-label">Description (Optional)</label>
                        <textarea id="eventDescription" class="form-input" rows="3" placeholder="Practice details..."></textarea>
                    </div>
                    
                    <div style="display: flex; gap: 12px;">
                        <button type="button" onclick="hideCreateEvent()" class="btn-secondary">Cancel</button>
                        <button type="submit" class="btn-primary">Create Event</button>
                    </div>
                </form>
            </div>

            <!-- ATTENDANCE TRACKER -->
            <div id="attendanceCard" class="card" style="display: none;">
                <h3 class="section-title">📋 Attendance Tracker</h3>
                <div id="attendanceContent">
                    <p>Loading attendance data...</p>
                </div>
            </div>

            <!-- STUDENT LIST -->
            <div id="studentListCard" class="card" style="display: none;">
                <h3 class="section-title">👥 Team Roster</h3>
                <div id="studentListContent">
                    <p>Loading student list...</p>
                </div>
            </div>
            
            ${currentAlerts.length > 0 ? `
            <div class="card">
                <h3 class="section-title">⚠️ Academic Alerts</h3>
                ${alertsHtml}
            </div>
            ` : ''}
            
            <div class="card">
                <h3 class="section-title">Recent Events</h3>
                <div class="events-list">
                    ${currentEvents.slice(0, 5).map(event => `
                        <div class="event-item">
                            <div class="event-info">
                                <h4>${event.title}</h4>
                                <div class="event-time">${event.date} | ${event.start_time}</div>
                                <div class="event-location">${event.location || 'TBD'}</div>
                            </div>
                            <div style="display: flex; gap: 8px;">
                                <div style="padding: 8px 12px; background: #ebf8ff; color: #3182ce; border-radius: 4px; font-size: 12px; font-weight: 600;">
                                    ${event.event_type.toUpperCase()}
                                </div>
                                <button class="btn-signin" onclick="viewEventAttendance(${event.id})">
                                    View Attendance
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// ADD THESE NEW FUNCTIONS TO YOUR JAVASCRIPT:

function showCreateEvent() {
    document.getElementById('createEventCard').style.display = 'block';
    document.getElementById('attendanceCard').style.display = 'none';
    document.getElementById('studentListCard').style.display = 'none';
    
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('eventDate').value = today;
    
    // Add form submission handler
    document.getElementById('createEventForm').onsubmit = handleCreateEvent;
}

function hideCreateEvent() {
    document.getElementById('createEventCard').style.display = 'none';
}

function showAttendanceTracker() {
    document.getElementById('createEventCard').style.display = 'none';
    document.getElementById('attendanceCard').style.display = 'block';
    document.getElementById('studentListCard').style.display = 'none';
    loadAttendanceData();
}

function showStudentList() {
    document.getElementById('createEventCard').style.display = 'none';
    document.getElementById('attendanceCard').style.display = 'none';
    document.getElementById('studentListCard').style.display = 'block';
    loadStudentList();
}

async function handleCreateEvent(event) {
    event.preventDefault();
    
    const eventData = {
        title: document.getElementById('eventTitle').value,
        event_type: document.getElementById('eventType').value,
        date: document.getElementById('eventDate').value,
        start_time: document.getElementById('startTime').value,
        end_time: document.getElementById('endTime').value,
        location: document.getElementById('eventLocation').value,
        description: document.getElementById('eventDescription').value
    };
    
    try {
        await apiRequest('/api/events', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
        
        alert('✅ Event created successfully!');
        document.getElementById('createEventForm').reset();
        hideCreateEvent();
        await loadDashboardData();
        render();
    } catch (error) {
        alert('❌ Error creating event: ' + error.message);
    }
}

async function loadAttendanceData() {
    try {
        const events = await getAllEvents();
        const attendanceHtml = events.slice(0, 10).map(event => `
            <div class="event-item">
                <div class="event-info">
                    <h4>${event.title}</h4>
                    <div class="event-time">${event.date} | ${event.start_time}</div>
                    <div class="event-location">${event.location || 'TBD'}</div>
                </div>
                <button class="btn-signin" onclick="viewEventAttendance(${event.id})">
                    View Attendance (${event.attendance_count || 0})
                </button>
            </div>
        `).join('');
        
        document.getElementById('attendanceContent').innerHTML = attendanceHtml;
    } catch (error) {
        document.getElementById('attendanceContent').innerHTML = 
            '<div class="empty-state">Error loading attendance data</div>';
    }
}

async function loadStudentList() {
    try {
        const response = await apiRequest('/api/users/students');
        const studentsHtml = response.map(student => `
            <div class="event-item">
                <div class="event-info">
                    <h4>${student.first_name} ${student.last_name}</h4>
                    <div class="event-time">Username: ${student.username}</div>
                    <div class="event-location">${student.email || 'No email'}</div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button class="btn-signin" onclick="viewStudentAttendance(${student.id})">
                        View Attendance
                    </button>
                </div>
            </div>
        `).join('');
        
        document.getElementById('studentListContent').innerHTML = studentsHtml;
    } catch (error) {
        document.getElementById('studentListContent').innerHTML = 
            '<div class="empty-state">Error loading student list</div>';
    }
}

async function viewEventAttendance(eventId) {
    try {
        const response = await apiRequest(`/api/events/${eventId}/attendance`);
        const attendees = response.map(att => 
            `${att.first_name} ${att.last_name} - Signed in: ${att.sign_in_time}`
        ).join('\n');
        
        alert(`Event Attendance:\n\n${attendees || 'No one signed in yet'}`);
    } catch (error) {
        alert('Error loading event attendance: ' + error.message);
    }
}

async function viewStudentAttendance(studentId) {
    try {
        const response = await apiRequest(`/api/attendance/students/${studentId}/attendance`);
        const attendance = response.slice(0, 10).map(att => 
            `${att.title} (${att.date}) - ${att.status}`
        ).join('\n');
        
        alert(`Student Attendance:\n\n${attendance || 'No attendance records'}`);
    } catch (error) {
        alert('Error loading student attendance: ' + error.message);
    }
}
    
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
