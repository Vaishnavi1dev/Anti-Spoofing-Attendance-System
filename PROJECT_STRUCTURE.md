# 🎓 Smart Classroom Attendance System - Complete Project Structure

## 📁 Project Overview

This project consists of three main components:

1. **Backend API** (FastAPI + MongoDB) - Handles all business logic and database operations
2. **Frontend** (React + TypeScript) - Modern web interface for teachers and administrators
3. **Database** (MongoDB) - Stores student data, photos, attendance records, and suspicious activities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                  (React + TypeScript)                        │
│  - Live Monitoring Dashboard                                 │
│  - Student Management                                        │
│  - Attendance Reports                                        │
│  - Analytics & Statistics                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ REST API + WebSocket
                 │
┌────────────────▼────────────────────────────────────────────┐
│                      BACKEND API                             │
│                      (FastAPI)                               │
│  - Face Detection & Recognition                              │
│  - Anti-Spoofing Detection                                   │
│  - Real-time Monitoring                                      │
│  - API Endpoints                                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ PyMongo
                 │
┌────────────────▼────────────────────────────────────────────┐
│                       DATABASE                               │
│                       (MongoDB)                              │
│  Collections:                                                │
│  - students                                                  │
│  - student_photos                                            │
│  - attendance                                                │
│  - suspicious_activity                                       │
└─────────────────────────────────────────────────────────────┘
```

## 📂 Directory Structure

```
smart-classroom-attendance/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Main FastAPI application
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   └── README.md                     # Backend documentation
│
├── frontend/                         # React + TypeScript Frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── database_mongo.py                 # MongoDB database module
├── setup_database_mongo.py           # Database setup script
│
├── photos/                           # Student photos storage
│   └── students/
│       ├── STU001/
│       │   ├── STU001_front.jpg
│       │   ├── STU001_left.jpg
│       │   └── STU001_with_glasses.jpg
│       └── STU002/
│
├── PROJECT_STRUCTURE.md              # This file
└── README.md                         # Main project README
```

## 🚀 Setup Instructions

### 1. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB Community Edition
# Windows: Download from https://www.mongodb.com/try/download/community
# Mac: brew install mongodb-community
# Linux: Follow official docs

# Start MongoDB
# Windows: Runs as service automatically
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

**Option B: MongoDB Atlas (Cloud)**
```bash
# 1. Create account at https://www.mongodb.com/cloud/atlas/register
# 2. Create a free cluster
# 3. Get connection string
# 4. Whitelist your IP address
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your MongoDB connection string
# MONGODB_URI=mongodb://localhost:27017/
# or
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Run the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### 3. Database Setup (Add Students)

```bash
# Run the setup script
python setup_database_mongo.py

# Follow the interactive prompts to:
# 1. Add students
# 2. Upload multiple photos per student
# 3. View registered students
```

### 4. Frontend Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open browser at http://localhost:8080

cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173` (or similar)

## 🔌 API Integration

### REST API Examples

**Get All Students:**
```bash
curl http://localhost:8000/api/students
```

**Create Student:**
```bash
curl -X POST http://localhost:8000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU001",
    "name": "John Doe",
    "email": "john@example.com"
  }'
```

**Upload Photo:**
```bash
curl -X POST http://localhost:8000/api/students/STU001/photos \
  -F "file=@photo.jpg" \
  -F "photo_type=front" \
  -F "description=Front facing photo"
```

**Get Today's Attendance:**
```bash
curl http://localhost:8000/api/attendance/today
```

### WebSocket Connection (Real-time Camera Feed)

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/camera');

// Receive real-time data
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // data.frame - Base64 encoded camera frame
  // data.students - Array of detected students with bounding boxes
  // data.timestamp - Current timestamp
  
  // Display frame
  const img = document.getElementById('camera-feed');
  img.src = `data:image/jpeg;base64,${data.frame}`;
  
  // Update student list
  console.log('Detected students:', data.students);
};
```

## 📊 Database Schema

### Students Collection
```json
{
  "_id": ObjectId,
  "student_id": "STU001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "created_at": ISODate
}
```

### Student Photos Collection
```json
{
  "_id": ObjectId,
  "student_id": "STU001",
  "photo_path": "/photos/students/STU001/front.jpg",
  "photo_type": "front",
  "description": "Front facing photo",
  "created_at": ISODate
}
```

### Attendance Collection
```json
{
  "_id": ObjectId,
  "student_id": "STU001",
  "date": ISODate,
  "entry_time": ISODate,
  "exit_time": ISODate,
  "status": "present",
  "suspicion_score": 0.5,
  "notes": null
}
```

### Suspicious Activity Collection
```json
{
  "_id": ObjectId,
  "student_id": "STU001",
  "timestamp": ISODate,
  "activity_type": "static_behavior",
  "description": "No movement detected for 30 seconds",
  "resolved": false
}
```

## 🎯 Features

### ✅ Implemented

- **Student Management**
  - Add/Edit/Delete students
  - Multiple photos per student (front, left, right, with/without glasses)
  - Student profile with statistics

- **Face Recognition**
  - Multi-face detection
  - Recognition using DeepFace (VGG-Face model)
  - Support for multiple photos per student

- **Attendance Tracking**
  - Automatic entry/exit logging
  - Real-time attendance dashboard
  - Historical attendance records
  - Date range queries

- **Anti-Spoofing**
  - Movement detection
  - Suspicion score calculation
  - Automatic alerts for suspicious behavior
  - Activity logging

- **Statistics & Reports**
  - Overall attendance statistics
  - Per-student statistics
  - Attendance rate calculation
  - CSV export

- **Real-time Monitoring**
  - WebSocket-based live camera feed
  - Real-time face detection overlay
  - Live attendance updates

### 🔮 Future Enhancements

- Multi-camera support
- Attention tracking (looking at board vs away)
- Behavior analytics
- Integration with LMS systems
- Mobile app for teachers
- Email/SMS notifications
- Advanced deepfake detection
- Facial expression analysis

## 🔐 Security Considerations

### Production Checklist

- [ ] Update CORS origins to specific frontend URL
- [ ] Implement authentication (JWT tokens)
- [ ] Add rate limiting
- [ ] Use HTTPS in production
- [ ] Secure MongoDB with authentication
- [ ] Validate and sanitize all inputs
- [ ] Implement role-based access control (RBAC)
- [ ] Add API key authentication
- [ ] Enable MongoDB encryption at rest
- [ ] Regular security audits

## 🐛 Troubleshooting

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
# Windows: services.msc -> MongoDB Server
# Mac: brew services list
# Linux: sudo systemctl status mongod

# Test connection
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('Connected!')"
```

### Camera Not Working
```bash
# Check camera permissions
# Try different camera index
# In backend/main.py, change: camera = cv2.VideoCapture(0)
# to: camera = cv2.VideoCapture(1) or camera = cv2.VideoCapture(2)
```

### Face Recognition Not Working
```bash
# Ensure photos are properly uploaded
# Check photo quality (clear, front-facing)
# Verify photos exist in database
python setup_database_mongo.py
# Select option 2 to list students and verify photo count
```

## 📝 Development Workflow

1. **Add Students**: Use `setup_database_mongo.py` to add students with photos
2. **Start Backend**: Run `uvicorn main:app --reload` in backend directory
3. **Start Frontend**: Run `npm run dev` in frontend directory
4. **Test API**: Visit `http://localhost:8000/docs` for interactive API testing
5. **Monitor**: Use frontend dashboard to monitor attendance

## 📚 Documentation

- **Backend API**: `http://localhost:8000/docs` (Swagger UI)
- **Backend README**: `backend/README.md`
- **Database Module**: See docstrings in `database_mongo.py`
- **Frontend**: React application in `frontend/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check MongoDB connection
4. Verify camera permissions
