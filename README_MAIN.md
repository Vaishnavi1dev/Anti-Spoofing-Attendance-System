# 🎓 Smart Classroom Attendance System

> AI-powered attendance system with real-time face recognition and anti-spoofing detection

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

## 🌟 Features

### 🎯 Core Functionality
- **Automated Attendance**: Multi-face detection and recognition in real-time
- **Anti-Spoofing**: Detects static photos/videos attempting to fake attendance
- **Multi-Photo Support**: Store multiple photos per student (different angles, with/without glasses)
- **Real-time Monitoring**: Live camera feed with WebSocket streaming
- **Smart Alerts**: Automatic notifications for suspicious behavior

### 📊 Management & Analytics
- **Student Management**: Add, edit, delete students with multiple photos
- **Attendance Dashboard**: Real-time and historical attendance tracking
- **Statistics & Reports**: Comprehensive analytics and CSV export
- **Suspicious Activity Log**: Track and resolve spoofing attempts

### 🔐 Security
- **Movement Detection**: Monitors natural head movements
- **Liveness Scoring**: Calculates suspicion scores based on behavior
- **Challenge System**: Issues verification challenges to suspicious students
- **Activity Logging**: Complete audit trail of all suspicious activities

## 🏗️ Architecture

```
Frontend (React + TypeScript) ←→ Backend API (FastAPI) ←→ Database (MongoDB)
                                         ↓
                                 Face Recognition (DeepFace)
                                    ↓
                            Camera Feed (OpenCV)
```

## 📁 Project Structure

```
smart-classroom-attendance/
├── backend/                    # FastAPI REST API
│   ├── main.py                # Main application
│   ├── requirements.txt       # Dependencies
│   └── README.md             # Backend docs
│
├── database_mongo.py          # MongoDB database module
├── setup_database_mongo.py    # Database setup script
│
├── photos/                    # Student photos storage
│   └── students/
│
├── frontend/                  # React frontend application
├── QUICK_START.md            # Quick setup guide
├── PROJECT_STRUCTURE.md      # Detailed documentation
└── README_MAIN.md            # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB (local or Atlas)
- Webcam
- Node.js 16+ (for frontend)

### 1. Install MongoDB

**Local:**
```bash
# Windows: Download from mongodb.com
# Mac: brew install mongodb-community
# Linux: sudo apt-get install mongodb
```

**Cloud (MongoDB Atlas):**
- Sign up at https://www.mongodb.com/cloud/atlas
- Create free cluster
- Get connection string

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 3. Add Students

```bash
python setup_database_mongo.py
# Follow interactive prompts to add students and photos
```

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open browser at `http://localhost:8080`

Frontend: `http://localhost:5173`

## 📚 Documentation

- **Quick Start**: [`QUICK_START.md`](QUICK_START.md) - Get running in 10 minutes
- **Full Documentation**: [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) - Complete guide
- **Backend API**: [`backend/README.md`](backend/README.md) - API documentation
- **Frontend**: React application in `frontend/` directory

## 🔌 API Overview

### REST Endpoints

```
Students:     GET/POST/PUT/DELETE  /api/students
Photos:       POST/GET/DELETE      /api/students/{id}/photos
Attendance:   GET/POST/PUT         /api/attendance/*
Suspicious:   GET/POST             /api/suspicious
Statistics:   GET                  /api/stats
Camera:       POST/GET             /api/camera/*
```

### WebSocket

```javascript
// Real-time camera feed
const ws = new WebSocket('ws://localhost:8000/ws/camera');
ws.onmessage = (event) => {
  const { frame, students, timestamp } = JSON.parse(event.data);
  // frame: Base64 encoded image
  // students: Array of detected students with bounding boxes
};
```

## 💡 How It Works

### Face Recognition Flow

1. **Camera captures frame** → OpenCV processes image
2. **Face detection** → Haar Cascade detects faces
3. **Face recognition** → DeepFace matches against database
4. **Liveness check** → Monitors movement patterns
5. **Attendance logging** → Records entry/exit times
6. **Alert generation** → Flags suspicious behavior

### Anti-Spoofing Detection

```
Movement Tracking → Variance Calculation → Suspicion Score
                                              ↓
                                    Score > Threshold?
                                              ↓
                                    Issue Challenge
                                              ↓
                                    Monitor Response
                                              ↓
                                    Verify or Flag
```

## 🎯 Use Cases

- **Schools & Colleges**: Automated classroom attendance
- **Training Centers**: Track participant presence
- **Exam Halls**: Monitor test-takers
- **Corporate**: Meeting room attendance
- **Events**: Track attendee presence

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenCV**: Computer vision and face detection
- **DeepFace**: Face recognition (VGG-Face model)
- **PyMongo**: MongoDB driver
- **WebSockets**: Real-time communication

### Database
- **MongoDB**: NoSQL database for flexible schema
- **Collections**: students, student_photos, attendance, suspicious_activity

### Frontend (React + TypeScript)
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Shadcn/UI**: Component library

## 📊 Database Schema

### Students
```json
{
  "student_id": "STU001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Student Photos
```json
{
  "student_id": "STU001",
  "photo_path": "/photos/students/STU001/front.jpg",
  "photo_type": "front",
  "description": "Front facing photo",
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Attendance
```json
{
  "student_id": "STU001",
  "date": "2024-01-20",
  "entry_time": "2024-01-20T09:00:00Z",
  "exit_time": "2024-01-20T11:30:00Z",
  "status": "present",
  "suspicion_score": 0.2
}
```

## 🔐 Security Best Practices

- [ ] Use environment variables for sensitive data
- [ ] Implement authentication (JWT)
- [ ] Enable MongoDB authentication
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Validate all inputs
- [ ] Regular security audits

## 🐛 Troubleshooting

### MongoDB Connection Failed
```bash
# Check if MongoDB is running
mongo --version
# Start MongoDB service
```

### Camera Not Working
```bash
# Try different camera index
# In backend/main.py: cv2.VideoCapture(1)
```

### Face Not Recognized
- Add multiple photos per student
- Ensure good lighting
- Use clear, front-facing photos

## 🚀 Deployment

### Backend (Docker)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Vercel/Netlify)
```bash
npm run build
# Deploy dist/ folder
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is for educational purposes.

## 👥 Authors

Built for hackathon/educational purposes

## 🙏 Acknowledgments

- **DeepFace**: Face recognition library
- **FastAPI**: Modern Python web framework
- **MongoDB**: Flexible NoSQL database
- **OpenCV**: Computer vision library
- **Vite**: Fast frontend build tool

## 📞 Support

- **Documentation**: See `QUICK_START.md` and `PROJECT_STRUCTURE.md`
- **API Docs**: `http://localhost:8000/docs`
- **Issues**: Check troubleshooting section

---

**⭐ Star this repo if you find it useful!**

Made with ❤️ for smart classrooms
