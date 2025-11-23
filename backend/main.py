"""
FastAPI Backend for Smart Classroom Attendance System
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
from bson import ObjectId
import cv2
import numpy as np
from deepface import DeepFace
import os
import json
import asyncio
import base64
from collections import deque
import shutil

# Import database and auth
from database_mongo import AttendanceDatabase
from auth import (
    UserManager, UserCreate, UserLogin, Token, User,
    create_access_token, get_current_user, get_current_user_with_manager,
    require_teacher, require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from liveness_detection import EnhancedStudentTracker, LivenessDetector

# Initialize FastAPI app
app = FastAPI(
    title="Smart Classroom Attendance API",
    description="AI-powered attendance system with anti-spoofing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and auth
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db = AttendanceDatabase(connection_string=MONGODB_URI)
user_manager = UserManager(db)

# Global variables for camera monitoring
camera_active = False
camera = None
active_websockets = []

# Student trackers with liveness detection
student_trackers = {}

# Global liveness detector
liveness_detector = LivenessDetector()

# ==================== PYDANTIC MODELS ====================

class StudentCreate(BaseModel):
    student_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class AttendanceEntry(BaseModel):
    student_id: str
    entry_time: Optional[datetime] = None

class AttendanceExit(BaseModel):
    student_id: str
    exit_time: Optional[datetime] = None

class SuspicionUpdate(BaseModel):
    student_id: str
    score: float
    date: Optional[date] = None

class ActivityResolve(BaseModel):
    activity_id: str

# ==================== STUDENT ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "message": "Smart Classroom Attendance API",
        "version": "1.0.0",
        "status": "running"
    }

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register", response_model=dict)
async def register(user: UserCreate):
    """Register a new user (admin only in production)"""
    try:
        new_user = user_manager.create_user(user)
        return {
            "success": True,
            "message": "User created successfully",
            "user": new_user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user (admin/teacher/student) and return JWT token"""
    try:
        # Try admin/teacher login first
        user = user_manager.authenticate_user(user_credentials.email, user_credentials.password)
        
        # If not found, try student login
        if not user:
            user = user_manager.authenticate_student(user_credentials.email, user_credentials.password, db)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"], "role": user.get("role", "student")},
            expires_delta=access_token_expires
        )
        
        # Remove sensitive data
        user_data = {
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "student"),
            "is_active": user.get("is_active", True)
        }
        
        # Add student_id if student
        if user.get("student_id"):
            user_data["student_id"] = user["student_id"]
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(get_current_user_with_manager(user_manager))):
    """Get current user information"""
    return {
        "success": True,
        "user": current_user
    }

@app.get("/api/auth/users")
async def get_all_users(current_user: dict = Depends(require_admin(user_manager))):
    """Get all users (admin only)"""
    try:
        users = user_manager.get_all_users()
        return {"success": True, "data": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/auth/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_admin(user_manager))):
    """Delete a user (admin only)"""
    try:
        # Get user by ID first
        user = user_manager.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Don't allow deleting yourself
        if user["email"] == current_user["email"]:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Delete the user
        success = user_manager.delete_user(user["email"])
        
        if success:
            return {"success": True, "message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STUDENT-SPECIFIC ENDPOINTS ====================

@app.get("/api/student/me")
async def get_student_profile(current_user: dict = Depends(get_current_user_with_manager(user_manager))):
    """Get current student's profile (student only)"""
    try:
        if current_user["role"] != "student":
            raise HTTPException(status_code=403, detail="Students only")
        
        student_id = current_user.get("student_id")
        if not student_id:
            raise HTTPException(status_code=404, detail="Student ID not found")
        
        student = db.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get photos
        photos = db.get_student_photos(student_id)
        student['photos'] = photos
        
        # Get stats
        stats = db.get_student_stats(student_id)
        student['stats'] = stats
        
        # Remove password
        student.pop('password', None)
        
        return {"success": True, "data": student}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/attendance")
async def get_student_attendance(current_user: dict = Depends(get_current_user_with_manager(user_manager))):
    """Get current student's attendance history (student only)"""
    try:
        if current_user["role"] != "student":
            raise HTTPException(status_code=403, detail="Students only")
        
        student_id = current_user.get("student_id")
        if not student_id:
            raise HTTPException(status_code=404, detail="Student ID not found")
        
        history = db.get_student_attendance_history(student_id, limit=30)
        return {"success": True, "data": history}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/student/suspicious-activities")
async def get_student_suspicious_activities(current_user: dict = Depends(get_current_user_with_manager(user_manager))):
    """Get current student's suspicious activities (student only)"""
    try:
        if current_user["role"] != "student":
            raise HTTPException(status_code=403, detail="Students only")
        
        student_id = current_user.get("student_id")
        if not student_id:
            raise HTTPException(status_code=404, detail="Student ID not found")
        
        activities = db.get_student_suspicious_activities(student_id)
        return {"success": True, "data": activities}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students")
async def get_all_students(current_user: dict = Depends(get_current_user_with_manager(user_manager))):
    """Get all registered students (requires authentication)"""
    try:
        students = db.get_all_students()
        return {"success": True, "data": students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students/{student_id}")
async def get_student(student_id: str):
    """Get specific student details"""
    try:
        student = db.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get photos
        photos = db.get_student_photos(student_id)
        student['photos'] = photos
        
        # Get stats
        stats = db.get_student_stats(student_id)
        student['stats'] = stats
        
        return {"success": True, "data": student}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/students")
async def create_student(student: StudentCreate, current_user: dict = Depends(require_teacher(user_manager))):
    """Create a new student (requires teacher role)"""
    try:
        success = db.add_student(
            student.student_id,
            student.name,
            student.email,
            student.phone
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Student already exists")
        
        return {"success": True, "message": "Student created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/students/{student_id}")
async def update_student(student_id: str, student: StudentUpdate):
    """Update student details"""
    try:
        success = db.update_student(
            student_id,
            student.name,
            student.email,
            student.phone
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {"success": True, "message": "Student updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: str):
    """Delete a student"""
    try:
        success = db.delete_student(student_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return {"success": True, "message": "Student deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PHOTO ENDPOINTS ====================

@app.post("/api/students/{student_id}/photos")
async def upload_student_photo(
    student_id: str,
    file: UploadFile = File(...),
    photo_type: str = Form(...),
    description: Optional[str] = Form(None)
):
    """Upload a photo for a student"""
    try:
        # Check if student exists
        student = db.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Create student directory
        student_dir = os.path.join("photos", "students", student_id)
        os.makedirs(student_dir, exist_ok=True)
        
        # Save file
        ext = os.path.splitext(file.filename)[1]
        filename = f"{student_id}_{photo_type}_{datetime.now().timestamp()}{ext}"
        file_path = os.path.join(student_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to database
        photo_id = db.add_student_photo(student_id, file_path, photo_type, description)
        
        return {
            "success": True,
            "message": "Photo uploaded successfully",
            "photo_id": photo_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/students/{student_id}/photos")
async def get_student_photos(student_id: str):
    """Get all photos for a student"""
    try:
        photos = db.get_student_photos(student_id)
        return {"success": True, "data": photos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/photos/{photo_id}")
async def delete_photo(photo_id: str):
    """Delete a photo"""
    try:
        success = db.delete_photo(photo_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        return {"success": True, "message": "Photo deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ATTENDANCE ENDPOINTS ====================

@app.get("/api/attendance/today")
async def get_today_attendance():
    """Get today's attendance"""
    try:
        attendance = db.get_today_attendance()
        return {"success": True, "data": attendance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/date/{date}")
async def get_attendance_by_date(date: str):
    """Get attendance for a specific date (YYYY-MM-DD)"""
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        attendance = db.get_attendance_by_date(date_obj)
        return {"success": True, "data": attendance}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/range")
async def get_attendance_by_range(start_date: str, end_date: str):
    """Get attendance for a date range"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        attendance = db.get_attendance_by_date_range(start, end)
        return {"success": True, "data": attendance}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/attendance/student/{student_id}")
async def get_student_attendance(student_id: str, limit: int = 30):
    """Get attendance history for a student"""
    try:
        history = db.get_student_attendance_history(student_id, limit)
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/attendance/entry")
async def mark_entry(entry: AttendanceEntry):
    """Mark student entry"""
    try:
        db.mark_entry(entry.student_id, entry.entry_time)
        return {"success": True, "message": "Entry marked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/attendance/exit")
async def mark_exit(exit: AttendanceExit):
    """Mark student exit"""
    try:
        db.mark_exit(exit.student_id, exit.exit_time)
        return {"success": True, "message": "Exit marked successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/attendance/suspicion")
async def update_suspicion(suspicion: SuspicionUpdate):
    """Update suspicion score"""
    try:
        db.update_suspicion_score(suspicion.student_id, suspicion.score, suspicion.date)
        return {"success": True, "message": "Suspicion score updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SUSPICIOUS ACTIVITY ENDPOINTS ====================

@app.get("/api/suspicious")
async def get_suspicious_activities(resolved: bool = False, limit: int = 50):
    """Get suspicious activities"""
    try:
        activities = db.get_suspicious_activities(resolved, limit)
        return {"success": True, "data": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/suspicious/resolve")
async def resolve_activity(resolve: ActivityResolve):
    """Resolve a suspicious activity"""
    try:
        success = db.resolve_suspicious_activity(resolve.activity_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        return {"success": True, "message": "Activity resolved"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STATISTICS ENDPOINTS ====================

@app.get("/api/stats")
async def get_statistics(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get attendance statistics"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        
        stats = db.get_attendance_stats(start, end)
        return {"success": True, "data": stats}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/student/{student_id}")
async def get_student_statistics(student_id: str):
    """Get statistics for a specific student"""
    try:
        stats = db.get_student_stats(student_id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CAMERA/MONITORING ENDPOINTS ====================

@app.get("/api/camera/status")
async def get_camera_status():
    """Get camera monitoring status"""
    return {
        "success": True,
        "data": {
            "active": camera_active,
            "connected_clients": len(active_websockets)
        }
    }

@app.post("/api/camera/start")
async def start_camera():
    """Start camera monitoring"""
    global camera_active, camera
    
    if camera_active:
        return {"success": True, "message": "Camera already active"}
    
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            raise HTTPException(status_code=500, detail="Failed to open camera")
        
        camera_active = True
        return {"success": True, "message": "Camera started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/camera/stop")
async def stop_camera():
    """Stop camera monitoring"""
    global camera_active, camera
    
    if not camera_active:
        return {"success": True, "message": "Camera already stopped"}
    
    camera_active = False
    if camera:
        camera.release()
        camera = None
    
    return {"success": True, "message": "Camera stopped"}

@app.post("/api/camera/recognize")
async def recognize_from_frame(file: UploadFile = File(...)):
    """Recognize faces from uploaded frame"""
    try:
        # Read uploaded image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect faces
        faces = detect_faces(frame)
        print(f"Detected {len(faces)} face(s) in frame")
        detected_students = []
        unknown_faces = []
        
        for (x, y, w, h) in faces:
            # Extract face image for liveness detection
            face_img = frame[int(y):int(y+h), int(x):int(x+w)]
            
            # Recognize face
            student_id, name = recognize_face(frame, (int(x), int(y), int(w), int(h)))
            
            if student_id:
                # Perform liveness detection
                is_live, liveness_score, liveness_checks = liveness_detector.detect_liveness(face_img)
                
                print(f"Liveness check for {name}: is_live={is_live}, score={liveness_score:.2f}")
                
                if not is_live:
                    # Spoofing detected!
                    spoofing_type = liveness_detector.get_spoofing_type(liveness_checks)
                    print(f"⚠️ SPOOFING DETECTED: {spoofing_type} for {name}")
                    
                    # Log as suspicious activity
                    db.log_suspicious_activity(
                        student_id=student_id,
                        activity_type="spoofing_attempt",
                        description=f"Liveness check failed (score: {liveness_score:.2f}). Suspected {spoofing_type}. Details: {liveness_checks}"
                    )
                    
                    detected_students.append({
                        "student_id": student_id,
                        "name": name,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "status": "spoofing_detected",
                        "liveness_score": float(liveness_score),
                        "spoofing_type": spoofing_type,
                        "warning": "Attendance NOT marked - spoofing detected"
                    })
                else:
                    # Real person - Mark attendance
                    db.mark_entry(student_id)
                    
                    detected_students.append({
                        "student_id": student_id,
                        "name": name,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "status": "recognized",
                        "liveness_score": float(liveness_score)
                    })
            else:
                # Unknown person - Log as suspicious
                print(f"⚠️  Unknown person detected at position ({x}, {y})")
                
                # Save unknown face image for review
                face_img = frame[int(y):int(y+h), int(x):int(x+w)]
                unknown_dir = "unknown_faces"
                os.makedirs(unknown_dir, exist_ok=True)
                
                timestamp = datetime.now().timestamp()
                unknown_path = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")
                cv2.imwrite(unknown_path, face_img)
                
                # Log suspicious activity
                db.log_suspicious_activity(
                    student_id="UNKNOWN",
                    activity_type="unknown_person",
                    description=f"Unrecognized person detected. Image saved: {unknown_path}"
                )
                
                unknown_faces.append({
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "status": "unknown",
                    "image_path": unknown_path
                })
        
        return {
            "success": True,
            "detected_students": detected_students,
            "unknown_faces": unknown_faces,
            "face_count": len(faces),
            "unknown_count": len(unknown_faces)
        }
    except Exception as e:
        print(f"Recognition error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/camera")
async def websocket_camera(websocket: WebSocket):
    """WebSocket endpoint for real-time camera feed"""
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        while camera_active and camera:
            ret, frame = camera.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Detect and recognize faces
            faces = detect_faces(frame)
            detected_students = []
            unknown_faces = []
            
            for (x, y, w, h) in faces:
                # Extract face image for liveness detection
                face_img = frame[y:y+h, x:x+w]
                
                # Recognize face
                student_id, name = recognize_face(frame, (x, y, w, h))
                
                if student_id:
                    # Known student - Track and monitor with liveness
                    if student_id not in student_trackers:
                        student_trackers[student_id] = EnhancedStudentTracker(student_id, name)
                    
                    tracker = student_trackers[student_id]
                    tracker.update_metrics((x, y, x+w, y+h), face_img)
                    
                    # Check for suspicious behavior or spoofing
                    if tracker.is_suspicious():
                        if tracker.spoofing_detected:
                            db.log_suspicious_activity(
                                student_id,
                                "spoofing_attempt",
                                f"Liveness check failed. Suspected {tracker.spoofing_type}. Score: {tracker.liveness_score:.2f}"
                            )
                        else:
                            db.log_suspicious_activity(
                                student_id,
                                "static_behavior",
                                "No movement detected for extended period"
                            )
                    
                    # Mark attendance only if live
                    if tracker.is_live and not tracker.entry_logged:
                        db.mark_entry(student_id)
                        tracker.entry_logged = True
                    
                    detected_students.append({
                        "student_id": student_id,
                        "name": name,
                        "bbox": [x, y, w, h],
                        "suspicious": tracker.is_suspicious(),
                        "suspicion_score": tracker.suspicion_score,
                        "status": "spoofing" if tracker.spoofing_detected else "recognized",
                        "liveness_score": tracker.liveness_score,
                        "is_live": tracker.is_live,
                        "spoofing_type": tracker.spoofing_type
                    })
                    
                    # Draw on frame - Red for spoofing, Orange for suspicious, Green for normal
                    if tracker.spoofing_detected:
                        color = (0, 0, 255)  # Red for spoofing
                        label = f"{name} - SPOOF!"
                    elif tracker.is_suspicious():
                        color = (0, 165, 255)  # Orange for suspicious
                        label = f"{name} - SUSPICIOUS"
                    else:
                        color = (0, 255, 0)  # Green for normal
                        label = name
                    
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                else:
                    # Unknown person - Flag as suspicious
                    unknown_id = f"UNKNOWN_{datetime.now().timestamp()}"
                    
                    # Log suspicious activity (throttled to avoid spam)
                    if unknown_id not in student_trackers:
                        # Save unknown face image
                        face_img = frame[y:y+h, x:x+w]
                        unknown_dir = "unknown_faces"
                        os.makedirs(unknown_dir, exist_ok=True)
                        
                        timestamp = datetime.now().timestamp()
                        unknown_path = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")
                        cv2.imwrite(unknown_path, face_img)
                        
                        db.log_suspicious_activity(
                            student_id="UNKNOWN",
                            activity_type="unknown_person",
                            description=f"Unrecognized person detected at {datetime.now().strftime('%H:%M:%S')}. Image: {unknown_path}"
                        )
                        
                        # Create temporary tracker to avoid repeated logging
                        student_trackers[unknown_id] = StudentTracker(unknown_id, "Unknown Person")
                    
                    unknown_faces.append({
                        "bbox": [x, y, w, h],
                        "status": "unknown",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Draw on frame - Orange/Yellow for unknown
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 165, 255), 2)
                    cv2.putText(frame, "UNKNOWN", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            
            # Encode frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send data
            await websocket.send_json({
                "frame": frame_base64,
                "students": detected_students,
                "unknown_faces": unknown_faces,
                "unknown_count": len(unknown_faces),
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(0.033)  # ~30 FPS
    
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        active_websockets.remove(websocket)

# ==================== HELPER FUNCTIONS ====================

def detect_faces(frame):
    """Detect faces using OpenCV"""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return faces

def recognize_face(frame, bbox):
    """Recognize face in bounding box"""
    temp_path = None
    temp_db = None
    
    try:
        x, y, w, h = bbox
        face_img = frame[y:y+h, x:x+w]
        
        # Save temp face image
        temp_path = f"temp_face_{datetime.now().timestamp()}.jpg"
        cv2.imwrite(temp_path, face_img)
        print(f"Saved temp face image: {temp_path}")
        
        # Get all student photos
        all_photos = db.get_all_student_photos()
        print(f"Found {len(all_photos)} photos in database")
        
        if not all_photos:
            print("No photos in database to match against")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None, None
        
        # Create temp database with student photos
        temp_db = f"temp_db_{datetime.now().timestamp()}"
        os.makedirs(temp_db, exist_ok=True)
        
        photo_count = 0
        for photo in all_photos:
            if os.path.exists(photo['photo_path']):
                # Use student_id in filename for easier matching
                dest = os.path.join(temp_db, f"{photo['student_id']}_{os.path.basename(photo['photo_path'])}")
                shutil.copy2(photo['photo_path'], dest)
                photo_count += 1
        
        print(f"Copied {photo_count} photos to temp database")
        
        if photo_count == 0:
            print("No valid photo files found")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_db):
                shutil.rmtree(temp_db)
            return None, None
        
        # Perform face recognition
        print("Running DeepFace.find...")
        result = DeepFace.find(
            img_path=temp_path,
            db_path=temp_db,
            model_name="VGG-Face",
            enforce_detection=False,
            silent=True,
            distance_metric="cosine"
        )
        
        print(f"DeepFace result: {len(result)} dataframes")
        
        # Cleanup temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_db):
            shutil.rmtree(temp_db)
        
        # Process results
        if len(result) > 0 and len(result[0]) > 0:
            # Show top 3 matches for debugging
            print(f"\n=== Top Matches ===")
            for i in range(min(3, len(result[0]))):
                match = result[0].iloc[i]
                match_path = match['identity']
                match_distance = match.get('VGG-Face_cosine', 1.0)
                match_student_id = os.path.basename(match_path).split('_')[0]
                print(f"{i+1}. Student {match_student_id}: distance={match_distance:.4f}, confidence={((1-match_distance)*100):.1f}%")
            print("==================\n")
            
            # Get the best match (first row)
            best_match = result[0].iloc[0]
            matched_path = best_match['identity']
            distance = best_match.get('VGG-Face_cosine', 1.0)
            
            print(f"Best match: {matched_path}, distance: {distance}")
            
            # Check if distance is within acceptable threshold
            # Lower distance = better match. Strict threshold to prevent false positives
            # 0.3 = Very strict (90%+ confidence required)
            # 0.4 = Strict (80%+ confidence)
            # 0.5 = Moderate (70%+ confidence)
            RECOGNITION_THRESHOLD = 0.3
            
            if distance > RECOGNITION_THRESHOLD:
                print(f"Distance {distance} exceeds threshold {RECOGNITION_THRESHOLD}, no match")
                print(f"Confidence would be: {(1-distance)*100:.1f}% - REJECTED (need {(1-RECOGNITION_THRESHOLD)*100:.1f}%+)")
                return None, None
            
            # Extract student ID from filename
            filename = os.path.basename(matched_path)
            student_id = filename.split('_')[0]
            
            print(f"Extracted student ID: {student_id}")
            
            # Get student details
            student = db.get_student(student_id)
            if student:
                print(f"Student found: {student['name']} (confidence: {1-distance:.2%})")
                return student_id, student['name']
            else:
                print(f"Student not found in database: {student_id}")
        else:
            print("No match found in DeepFace results")
        
        return None, None
        
    except Exception as e:
        print(f"Recognition error: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        if temp_db and os.path.exists(temp_db):
            shutil.rmtree(temp_db)
        
        return None, None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
