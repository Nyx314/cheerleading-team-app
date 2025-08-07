# 🏆 Cheerleading Team Management System

A comprehensive web application for managing cheerleading teams, including student attendance tracking, academic requirements monitoring, and event scheduling.

## ✨ Features

### 👩‍🎓 For Students
- **Sign In/Out** for practices and events
- **View Academic Requirements** and current grades
- **Track Personal Attendance** history
- **Access Team Schedule** and upcoming events

### 👨‍🏫 For Coaches & Staff
- **Monitor Academic Alerts** for all students
- **Create and Manage Events** (practices, competitions, performances)
- **Add Academic Requirements** and track student progress
- **View Team Attendance** and performance analytics

### 👨‍👩‍👧‍👦 For Parents
- **View Child's Academic Status** and requirements
- **Access Team Schedule** and important dates
- **Monitor Attendance History** for their child

### 🏢 For Athletic Directors
- **Comprehensive Dashboard** with team overview
- **Generate Reports** on academic performance
- **Manage Multiple Teams** and coaches
- **Monitor Overall Statistics**

## 🚀 Live Demo

**Try the live application:** [Your App URL Here]

### Demo Accounts
| Username | Password | Role |
|----------|----------|------|
| `coach` | `password123` | Coach |
| `student1` | `password123` | Student (Emma - Good standing) |
| `student2` | `password123` | Student (Sophia - Has academic alerts) |
| `parent1` | `password123` | Parent (John Smith) |
| `director` | `password123` | Athletic Director |

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** React with Tailwind CSS
- **Database:** SQLite
- **Authentication:** Session-based with password hashing
- **Deployment:** Render.com / Railway.app

## 📁 Project Structure
## 🔧 Local Development Setup

### Prerequisites
- Python 3.8+
- Git

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/cheerleading-team-app.git
   cd cheerleading-team-app

   # Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python create_demo_data.py

python main.py
