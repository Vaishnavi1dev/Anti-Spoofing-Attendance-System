# 🚀 Quick Start Guide - Smart Classroom Attendance System

Get up and running in 10 minutes!

## ⚡ Prerequisites

- Python 3.9+
- MongoDB (local or Atlas account)
- Node.js 16+ (for frontend)
- Webcam

## 📋 Step-by-Step Setup

### Step 1: Install MongoDB (Choose One)

**Option A: Local MongoDB (Recommended for Development)**
```bash
# Windows
# Download from: https://www.mongodb.com/try/download/community
# Install and it runs automatically as a service

# Mac
brew install mongodb-community
brew services start mongodb-community

# Linux (Ubuntu/Debian)
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Option B: MongoDB Atlas (Cloud - Free Tier)**
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create free account
3. Create a cluster (takes 3-5 minutes)
4. Click "Connect" → "Connect your application"
5. Copy the connection string

### Step 2: Setup Backend

```bash
# Clone or navigate to project directory
cd smart-classroom-attendance

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file (use notepad, vim, or any editor)
# For local MongoDB:
MONGODB_URI=mongodb://localhost:27017/

# For MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/

# Start the backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend is now running at: `http://localhost:8000`
📚 API Docs available at: `http://localhost:8000/docs`

### Step 3: Add Students to Database

Open a **new terminal** (keep backend running):

```bash
# Navigate to project root
cd smart-classroom-attendance

# Run setup script
python setup_database_mongo.py
```

**Interactive Menu:**
```
1. Add Student
   - Enter Student ID (e.g., STU001)
   - Enter Name (e.g., John Doe)
   - Enter Email (optional)
   - Enter Phone (optional)
   
2. Add Photos for Student
   - Enter photo file path
   - Select photo type: front, left, right, with_glasses, without_glasses
   - Repeat for multiple photos
   - Type 'done' when finished

3. Repeat for more students
```

**Example:**
```
Student ID: STU001
Name: John Doe
Email: john@example.com
Phone: +1234567890

Photo path: C:\Users\YourName\Pictures\john_front.jpg
Photo type: front

Photo path: C:\Users\YourName\Pictures\john_left.jpg
Photo type: left

Photo path: done
```

### Step 4: Test Backend API

Open browser and go to: `http://localhost:8000/docs`

Try these endpoints:
1. **GET /api/students** - See your registered students
2. **GET /api/attendance/today** - Check today's attendance
3. **POST /api/camera/start** - Start camera monitoring

### Step 5: Run Frontend Application

1. **Navigate to frontend**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start development server**:
```bash
npm run dev
```

4. **Open in browser**: `http://localhost:8080`

✅ Frontend is now running at: `http://localhost:5173` (or similar)

### Step 6: Start Monitoring!

1. Open frontend in browser: `http://localhost:5173`
2. Click "Start Monitoring" button
3. Allow camera permissions
4. Watch as the system detects and recognizes students!

## 🎯 Quick Test

### Test Face Recognition

1. **Start backend**: `uvicorn main:app --reload` (in backend folder)
2. **Start camera**: 
   ```bash
   curl -X POST http://localhost:8000/api/camera/start
   ```
3. **Open WebSocket test**: Go to `http://localhost:8000/docs`
4. **Try WebSocket endpoint**: `/ws/camera`
5. **Sit in front of camera**: System should detect and recognize you!

### Test API Endpoints

```bash
# Get all students
curl http://localhost:8000/api/students

# Get today's attendance
curl http://localhost:8000/api/attendance/today

# Get statistics
curl http://localhost:8000/api/stats
```

## 📊 Verify Everything is Working

### ✅ Checklist

- [ ] MongoDB is running (check with `mongo` command or MongoDB Compass)
- [ ] Backend is running at `http://localhost:8000`
- [ ] API docs accessible at `http://localhost:8000/docs`
- [ ] At least one student added with photos
- [ ] Camera starts successfully
- [ ] Frontend is running (if generated)

### 🔍 Check MongoDB Data

```bash
# Open MongoDB shell
mongo

# Switch to database
use classroom_attendance

# Check students
db.students.find().pretty()

# Check photos
db.student_photos.find().pretty()

# Exit
exit
```

## 🐛 Common Issues & Solutions

### Issue: "Failed to connect to MongoDB"

**Solution:**
```bash
# Check if MongoDB is running
# Windows: Open Services, look for "MongoDB Server"
# Mac: brew services list
# Linux: sudo systemctl status mongod

# If not running, start it
# Windows: Start the service
# Mac: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

### Issue: "Camera not found"

**Solution:**
```bash
# Check camera permissions
# Try different camera index in backend/main.py
# Change: camera = cv2.VideoCapture(0)
# To: camera = cv2.VideoCapture(1)
```

### Issue: "Face not recognized"

**Solution:**
- Ensure photos are clear and front-facing
- Add multiple photos per student (different angles)
- Check lighting conditions
- Verify photos are uploaded: `python setup_database_mongo.py` → Option 2

### Issue: "CORS error in frontend"

**Solution:**
In `backend/main.py`, update CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎓 Next Steps

1. **Add more students**: Run `python setup_database_mongo.py`
2. **Customize settings**: Edit `backend/.env`
3. **Test anti-spoofing**: Try holding up a photo (should be detected as suspicious)
4. **View reports**: Check attendance dashboard
5. **Export data**: Use CSV export feature

## 📚 Additional Resources

- **Full Documentation**: See `PROJECT_STRUCTURE.md`
- **API Reference**: `http://localhost:8000/docs`
- **Backend Details**: `backend/README.md`
- **Database Schema**: See `PROJECT_STRUCTURE.md`

## 💡 Tips

- **Multiple Photos**: Add 3-5 photos per student for better recognition
- **Photo Types**: Include front, left, right, with/without glasses
- **Lighting**: Ensure good lighting for camera
- **Camera Position**: Position camera to capture all students
- **Testing**: Test with one student first before adding many

## 🎉 You're Ready!

Your Smart Classroom Attendance System is now running!

- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:8080`

Happy monitoring! 🚀
