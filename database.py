import sqlite3
import os
from datetime import datetime
import json

class AttendanceDatabase:
    def __init__(self, db_path="attendance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student photos table (multiple photos per student)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_photos (
                photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                photo_path TEXT NOT NULL,
                photo_type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        # Attendance records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date DATE NOT NULL,
                entry_time TIMESTAMP,
                exit_time TIMESTAMP,
                status TEXT DEFAULT 'present',
                suspicion_score REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE(student_id, date)
            )
        ''')
        
        # Suspicious activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suspicious_activity (
                activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activity_type TEXT,
                description TEXT,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== STUDENT MANAGEMENT ====================
    
    def add_student(self, student_id, name, email=None, phone=None):
        """Add a new student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO students (student_id, name, email, phone)
                VALUES (?, ?, ?, ?)
            ''', (student_id, name, email, phone))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_student(self, student_id):
        """Get student details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'student_id': result[0],
                'name': result[1],
                'email': result[2],
                'phone': result[3],
                'created_at': result[4]
            }
        return None
    
    def get_all_students(self):
        """Get all students"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM students ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        students = []
        for row in results:
            students.append({
                'student_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'created_at': row[4]
            })
        return students
    
    def update_student(self, student_id, name=None, email=None, phone=None):
        """Update student details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if phone:
            updates.append("phone = ?")
            params.append(phone)
        
        if updates:
            params.append(student_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
    
    def delete_student(self, student_id):
        """Delete a student and all related data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM student_photos WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM suspicious_activity WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        
        conn.commit()
        conn.close()
    
    # ==================== PHOTO MANAGEMENT ====================
    
    def add_student_photo(self, student_id, photo_path, photo_type=None, description=None):
        """Add a photo for a student
        
        photo_type examples: 'front', 'left', 'right', 'with_glasses', 'without_glasses'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO student_photos (student_id, photo_path, photo_type, description)
            VALUES (?, ?, ?, ?)
        ''', (student_id, photo_path, photo_type, description))
        
        conn.commit()
        conn.close()
    
    def get_student_photos(self, student_id):
        """Get all photos for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT photo_id, photo_path, photo_type, description, created_at
            FROM student_photos
            WHERE student_id = ?
            ORDER BY created_at
        ''', (student_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        photos = []
        for row in results:
            photos.append({
                'photo_id': row[0],
                'photo_path': row[1],
                'photo_type': row[2],
                'description': row[3],
                'created_at': row[4]
            })
        return photos
    
    def get_all_student_photos(self):
        """Get all photos for all students (for face recognition)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sp.photo_path, sp.student_id, s.name, sp.photo_type
            FROM student_photos sp
            JOIN students s ON sp.student_id = s.student_id
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        photos = []
        for row in results:
            photos.append({
                'photo_path': row[0],
                'student_id': row[1],
                'name': row[2],
                'photo_type': row[3]
            })
        return photos
    
    def delete_photo(self, photo_id):
        """Delete a specific photo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get photo path first
        cursor.execute('SELECT photo_path FROM student_photos WHERE photo_id = ?', (photo_id,))
        result = cursor.fetchone()
        
        if result:
            photo_path = result[0]
            # Delete from database
            cursor.execute('DELETE FROM student_photos WHERE photo_id = ?', (photo_id,))
            conn.commit()
            
            # Delete file if exists
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        conn.close()
    
    # ==================== ATTENDANCE MANAGEMENT ====================
    
    def mark_entry(self, student_id, entry_time=None):
        """Mark student entry"""
        if entry_time is None:
            entry_time = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date = entry_time.date()
        
        try:
            cursor.execute('''
                INSERT INTO attendance (student_id, date, entry_time, status)
                VALUES (?, ?, ?, 'present')
            ''', (student_id, date, entry_time))
        except sqlite3.IntegrityError:
            # Already exists, update entry time
            cursor.execute('''
                UPDATE attendance
                SET entry_time = ?, status = 'present'
                WHERE student_id = ? AND date = ?
            ''', (entry_time, student_id, date))
        
        conn.commit()
        conn.close()
    
    def mark_exit(self, student_id, exit_time=None):
        """Mark student exit"""
        if exit_time is None:
            exit_time = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date = exit_time.date()
        
        cursor.execute('''
            UPDATE attendance
            SET exit_time = ?
            WHERE student_id = ? AND date = ?
        ''', (exit_time, student_id, date))
        
        conn.commit()
        conn.close()
    
    def update_suspicion_score(self, student_id, score, date=None):
        """Update suspicion score for a student"""
        if date is None:
            date = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE attendance
            SET suspicion_score = ?
            WHERE student_id = ? AND date = ?
        ''', (score, student_id, date))
        
        conn.commit()
        conn.close()
    
    def get_today_attendance(self):
        """Get today's attendance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute('''
            SELECT a.student_id, s.name, a.entry_time, a.exit_time, 
                   a.status, a.suspicion_score, a.notes
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ?
            ORDER BY a.entry_time
        ''', (today,))
        
        results = cursor.fetchall()
        conn.close()
        
        attendance = []
        for row in results:
            attendance.append({
                'student_id': row[0],
                'name': row[1],
                'entry_time': row[2],
                'exit_time': row[3],
                'status': row[4],
                'suspicion_score': row[5],
                'notes': row[6]
            })
        return attendance
    
    def get_attendance_by_date(self, date):
        """Get attendance for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.student_id, s.name, a.entry_time, a.exit_time, 
                   a.status, a.suspicion_score, a.notes
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = ?
            ORDER BY a.entry_time
        ''', (date,))
        
        results = cursor.fetchall()
        conn.close()
        
        attendance = []
        for row in results:
            attendance.append({
                'student_id': row[0],
                'name': row[1],
                'entry_time': row[2],
                'exit_time': row[3],
                'status': row[4],
                'suspicion_score': row[5],
                'notes': row[6]
            })
        return attendance
    
    def get_student_attendance_history(self, student_id, limit=30):
        """Get attendance history for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, entry_time, exit_time, status, suspicion_score, notes
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
            LIMIT ?
        ''', (student_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            history.append({
                'date': row[0],
                'entry_time': row[1],
                'exit_time': row[2],
                'status': row[3],
                'suspicion_score': row[4],
                'notes': row[5]
            })
        return history
    
    # ==================== SUSPICIOUS ACTIVITY ====================
    
    def log_suspicious_activity(self, student_id, activity_type, description):
        """Log suspicious activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO suspicious_activity (student_id, activity_type, description)
            VALUES (?, ?, ?)
        ''', (student_id, activity_type, description))
        
        conn.commit()
        conn.close()
    
    def get_suspicious_activities(self, resolved=False, limit=50):
        """Get suspicious activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sa.activity_id, sa.student_id, s.name, sa.timestamp,
                   sa.activity_type, sa.description, sa.resolved
            FROM suspicious_activity sa
            JOIN students s ON sa.student_id = s.student_id
            WHERE sa.resolved = ?
            ORDER BY sa.timestamp DESC
            LIMIT ?
        ''', (1 if resolved else 0, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        activities = []
        for row in results:
            activities.append({
                'activity_id': row[0],
                'student_id': row[1],
                'name': row[2],
                'timestamp': row[3],
                'activity_type': row[4],
                'description': row[5],
                'resolved': row[6]
            })
        return activities
    
    def resolve_suspicious_activity(self, activity_id):
        """Mark suspicious activity as resolved"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE suspicious_activity
            SET resolved = 1
            WHERE activity_id = ?
        ''', (activity_id,))
        
        conn.commit()
        conn.close()
    
    # ==================== STATISTICS ====================
    
    def get_attendance_stats(self, start_date=None, end_date=None):
        """Get attendance statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT student_id) as total_students,
                    COUNT(*) as total_records,
                    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                    AVG(suspicion_score) as avg_suspicion
                FROM attendance
                WHERE date BETWEEN ? AND ?
            ''', (start_date, end_date))
        else:
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT student_id) as total_students,
                    COUNT(*) as total_records,
                    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                    AVG(suspicion_score) as avg_suspicion
                FROM attendance
            ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_students': result[0] or 0,
            'total_records': result[1] or 0,
            'present_count': result[2] or 0,
            'avg_suspicion': result[3] or 0
        }
