import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
import os
import time
import pandas as pd
from datetime import datetime
from collections import defaultdict, deque
import json
from database_mongo import AttendanceDatabase

# Page config
st.set_page_config(
    page_title="Smart Classroom Attendance",
    page_icon="🎓",
    layout="wide"
)

# Initialize MongoDB database
@st.cache_resource
def get_database():
    # Change this to your MongoDB connection string
    # For local: "mongodb://localhost:27017/"
    # For Atlas: "mongodb+srv://username:password@cluster.mongodb.net/"
    connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    return AttendanceDatabase(connection_string=connection_string)

db = get_database()

# Initialize session state
if 'suspicious_students' not in st.session_state:
    st.session_state.suspicious_students = set()
if 'active_challenges' not in st.session_state:
    st.session_state.active_challenges = {}
if 'student_trackers' not in st.session_state:
    st.session_state.student_trackers = {}
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()

# Create necessary folders
os.makedirs("photos", exist_ok=True)
os.makedirs("photos/students", exist_ok=True)
os.makedirs("logs", exist_ok=True)

class StudentTracker:
    """Track individual student's liveness metrics"""
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.blink_history = deque(maxlen=30)
        self.movement_history = deque(maxlen=30)
        self.last_seen = time.time()
        self.entry_time = datetime.now()
        self.exit_time = None
        self.suspicion_score = 0
        self.challenge_issued = False
        self.challenge_time = None
        self.last_position = None
        self.entry_logged = False
        
    def update_metrics(self, bbox, landmarks=None):
        """Update liveness metrics"""
        self.last_seen = time.time()
        
        # Track position movement
        current_center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        if self.last_position is not None:
            movement = np.sqrt(
                (current_center[0] - self.last_position[0])**2 + 
                (current_center[1] - self.last_position[1])**2
            )
            self.movement_history.append(movement)
        self.last_position = current_center
        
        # Calculate suspicion score
        if len(self.movement_history) >= 20:
            avg_movement = np.mean(list(self.movement_history))
            movement_variance = np.var(list(self.movement_history))
            
            # Too static = suspicious
            if avg_movement < 2 and movement_variance < 1:
                self.suspicion_score += 1
            else:
                self.suspicion_score = max(0, self.suspicion_score - 0.5)
    
    def is_suspicious(self):
        """Check if student behavior is suspicious"""
        return self.suspicion_score > 10
    
    def get_status(self):
        """Get current status"""
        if self.challenge_issued and not self.challenge_passed():
            return "⚠️ CHALLENGE PENDING"
        elif self.is_suspicious():
            return "🚨 SUSPICIOUS"
        else:
            return "✅ VERIFIED"
    
    def challenge_passed(self):
        """Check if challenge was passed"""
        if self.challenge_time and (time.time() - self.challenge_time) < 10:
            # Check if movement increased after challenge
            recent_movement = list(self.movement_history)[-5:] if len(self.movement_history) >= 5 else []
            if recent_movement and np.mean(recent_movement) > 5:
                self.challenge_issued = False
                self.suspicion_score = 0
                return True
        return False

def detect_faces(frame):
    """Detect faces using OpenCV"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

def recognize_face(frame, bbox):
    """Recognize face in bounding box using database photos"""
    try:
        x, y, w, h = bbox
        face_img = frame[y:y+h, x:x+w]
        
        # Save temp image
        temp_path = f"temp_face_{time.time()}.jpg"
        cv2.imwrite(temp_path, face_img)
        
        # Get all student photos from database
        all_photos = db.get_all_student_photos()
        
        if not all_photos:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None, None, None
        
        # Create temporary db folder for DeepFace
        temp_db = "temp_db"
        os.makedirs(temp_db, exist_ok=True)
        
        # Copy photos to temp db (DeepFace needs a folder structure)
        for photo in all_photos:
            if os.path.exists(photo['photo_path']):
                import shutil
                dest = os.path.join(temp_db, os.path.basename(photo['photo_path']))
                shutil.copy2(photo['photo_path'], dest)
        
        # Try to find match
        result = DeepFace.find(
            img_path=temp_path,
            db_path=temp_db,
            model_name="VGG-Face",
            enforce_detection=False,
            silent=True
        )
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        import shutil
        if os.path.exists(temp_db):
            shutil.rmtree(temp_db)
        
        if len(result) > 0 and len(result[0]) > 0:
            matched_path = result[0]['identity'].iloc[0]
            matched_filename = os.path.basename(matched_path)
            
            # Extract student_id from filename (format: studentid_phototype_*.jpg)
            student_id = matched_filename.split('_')[0]
            
            # Get student info from database
            student = db.get_student(student_id)
            if student:
                confidence = result[0]['distance'].iloc[0] if 'distance' in result[0].columns else 0
                return student_id, student['name'], confidence
        
        return None, None, None
    except Exception as e:
        return None, None, None

def save_attendance_log():
    """Save current session attendance to CSV"""
    attendance_data = db.get_today_attendance()
    
    if attendance_data:
        df = pd.DataFrame(attendance_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"logs/attendance_{timestamp}.csv"
        df.to_csv(filename, index=False)
        return filename
    return None

# UI Layout
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>
        🎓 Smart Classroom Attendance System
    </h1>
    <p style='text-align: center; color: #666; font-size: 18px;'>
        AI-Powered Attendance with Anti-Spoofing Detection
    </p>
""", unsafe_allow_html=True)

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📹 Live Monitoring", "👥 Attendance Dashboard", "⚙️ Settings"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📹 Classroom Camera Feed")
        camera_placeholder = st.empty()
        
    with col2:
        st.markdown("### 🚨 Alerts & Challenges")
        alerts_placeholder = st.empty()
        
        st.markdown("### 📊 Quick Stats")
        stats_placeholder = st.empty()
    
    # Control buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        start_button = st.button("▶️ Start Monitoring", use_container_width=True)
    with btn_col2:
        stop_button = st.button("⏹️ Stop", use_container_width=True)
    with btn_col3:
        save_button = st.button("💾 Save Attendance", use_container_width=True)

with tab2:
    st.markdown("### 📋 Current Attendance")
    attendance_table_placeholder = st.empty()
    
    st.markdown("### 🚨 Suspicious Activity Log")
    suspicious_table_placeholder = st.empty()

with tab3:
    st.markdown("### ⚙️ System Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        suspicion_threshold = st.slider("Suspicion Threshold", 5, 20, 10)
        recognition_interval = st.slider("Recognition Interval (frames)", 10, 60, 30)
    
    with col2:
        challenge_timeout = st.slider("Challenge Timeout (seconds)", 5, 30, 10)
        absence_timeout = st.slider("Mark Absent After (seconds)", 5, 30, 10)
    
    st.markdown("### 📁 Student Database")
    students = db.get_all_students()
    st.write(f"**Registered Students:** {len(students)}")
    
    if students:
        student_df = pd.DataFrame(students)
        st.dataframe(student_df[['student_id', 'name', 'email']], use_container_width=True)
        
        st.info("💡 To add students and photos, run: `python setup_database.py`")

# Main monitoring loop
if start_button:
    cap = cv2.VideoCapture(0)
    frame_count = 0
    
    try:
        while not stop_button:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to access camera")
                break
            
            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()
            frame_count += 1
            
            # Detect faces
            faces = detect_faces(frame)
            
            current_students = set()
            
            # Process each detected face
            for (x, y, w, h) in faces:
                bbox = (x, y, w, h)
                
                # Recognize face periodically
                name = None
                if frame_count % recognition_interval == 0:
                    name, confidence = recognize_face(frame, bbox)
                else:
                    # Try to match with existing trackers by position
                    center = ((x + w/2), (y + h/2))
                    for tracked_name, tracker in st.session_state.student_trackers.items():
                        if tracker.last_position:
                            dist = np.sqrt(
                                (center[0] - tracker.last_position[0])**2 + 
                                (center[1] - tracker.last_position[1])**2
                            )
                            if dist < 100:  # Same person
                                name = tracked_name
                                break
                
                if name:
                    current_students.add(name)
                    
                    # Create or update tracker
                    if name not in st.session_state.student_trackers:
                        st.session_state.student_trackers[name] = StudentTracker(name)
                    
                    tracker = st.session_state.student_trackers[name]
                    tracker.update_metrics(bbox)
                    
                    # Check for suspicious behavior
                    if tracker.is_suspicious() and not tracker.challenge_issued:
                        tracker.challenge_issued = True
                        tracker.challenge_time = time.time()
                        st.session_state.suspicious_students.add(name)
                    
                    # Draw bounding box
                    color = (0, 255, 0)  # Green
                    if tracker.challenge_issued:
                        color = (0, 165, 255)  # Orange
                    elif tracker.is_suspicious():
                        color = (0, 0, 255)  # Red
                    
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Draw label
                    label = f"{name} - {tracker.get_status()}"
                    cv2.putText(display_frame, label, (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                else:
                    # Unknown face
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (128, 128, 128), 2)
                    cv2.putText(display_frame, "Unknown", (x, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
            
            # Mark absent students
            for name, tracker in list(st.session_state.student_trackers.items()):
                if name not in current_students:
                    if time.time() - tracker.last_seen > absence_timeout:
                        if not tracker.exit_time:
                            tracker.exit_time = datetime.now()
            
            # Display camera feed
            camera_placeholder.image(display_frame, channels="BGR", use_container_width=True)
            
            # Display alerts
            with alerts_placeholder.container():
                if st.session_state.suspicious_students:
                    st.error("🚨 **SUSPICIOUS ACTIVITY DETECTED**")
                    for student in st.session_state.suspicious_students:
                        if student in st.session_state.student_trackers:
                            tracker = st.session_state.student_trackers[student]
                            if tracker.challenge_issued and not tracker.challenge_passed():
                                st.warning(f"**{student}**: Please turn your head left and right to verify presence")
                else:
                    st.success("✅ All students verified")
            
            # Display stats
            with stats_placeholder.container():
                present = sum(1 for t in st.session_state.student_trackers.values() if not t.exit_time)
                total = len(load_face_database())
                st.metric("Present", f"{present}/{total}")
                st.metric("Suspicious", len(st.session_state.suspicious_students))
            
            # Update attendance table
            if st.session_state.student_trackers:
                attendance_data = []
                for name, tracker in st.session_state.student_trackers.items():
                    attendance_data.append({
                        'Name': name,
                        'Status': '🟢 Present' if not tracker.exit_time else '🔴 Left',
                        'Entry': tracker.entry_time.strftime('%H:%M:%S'),
                        'Behavior': tracker.get_status()
                    })
                attendance_table_placeholder.dataframe(pd.DataFrame(attendance_data), use_container_width=True)
            
            time.sleep(0.03)
    
    finally:
        cap.release()

if save_button:
    filename = save_attendance_log()
    if filename:
        st.success(f"✅ Attendance saved to {filename}")
        with open(filename, 'r') as f:
            st.download_button(
                label="📥 Download Attendance Report",
                data=f.read(),
                file_name=os.path.basename(filename),
                mime='text/csv'
            )
    else:
        st.warning("No attendance data to save")
