# Smart Classroom Attendance - Backend API

FastAPI backend for the Smart Classroom Attendance System with MongoDB integration.

## 🚀 Quick Start

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update MongoDB connection string in `.env`:
```env
MONGODB_URI=mongodb://localhost:27017/
```

### Run the Server

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python main.py
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📚 API Endpoints

### Students

- `GET /api/students` - Get all students
- `GET /api/students/{student_id}` - Get student details
- `POST /api/students` - Create new student
- `PUT /api/students/{student_id}` - Update student
- `DELETE /api/students/{student_id}` - Delete student

### Photos

- `POST /api/students/{student_id}/photos` - Upload photo
- `GET /api/students/{student_id}/photos` - Get student photos
- `DELETE /api/photos/{photo_id}` - Delete photo

### Attendance

- `GET /api/attendance/today` - Get today's attendance
- `GET /api/attendance/date/{date}` - Get attendance by date
- `GET /api/attendance/range?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Get attendance range
- `GET /api/attendance/student/{student_id}` - Get student attendance history
- `POST /api/attendance/entry` - Mark entry
- `POST /api/attendance/exit` - Mark exit
- `PUT /api/attendance/suspicion` - Update suspicion score

### Suspicious Activity

- `GET /api/suspicious?resolved=false` - Get suspicious activities
- `POST /api/suspicious/resolve` - Resolve activity

### Statistics

- `GET /api/stats` - Get overall statistics
- `GET /api/stats/student/{student_id}` - Get student statistics

### Camera/Monitoring

- `GET /api/camera/status` - Get camera status
- `POST /api/camera/start` - Start monitoring
- `POST /api/camera/stop` - Stop monitoring
- `WS /ws/camera` - WebSocket for real-time feed

## 🔌 WebSocket Connection

Connect to `/ws/camera` for real-time camera feed:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/camera');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // data.frame - Base64 encoded image
  // data.students - Array of detected students
  // data.timestamp - Current timestamp
};
```

## 📝 Request Examples

### Create Student

```bash
curl -X POST "http://localhost:8000/api/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }'
```

### Upload Photo

```bash
curl -X POST "http://localhost:8000/api/students/STU001/photos" \
  -F "file=@photo.jpg" \
  -F "photo_type=front" \
  -F "description=Front facing photo"
```

### Get Today's Attendance

```bash
curl "http://localhost:8000/api/attendance/today"
```

## 🔧 Development

### Project Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

### Testing

Access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐛 Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running
- Check connection string in `.env`
- For Atlas, whitelist your IP address

**Camera Not Working:**
- Check camera permissions
- Ensure no other application is using the camera
- Try different camera index in `cv2.VideoCapture(0)`

**CORS Issues:**
- Update `allow_origins` in CORS middleware
- Add your frontend URL to allowed origins

## 📦 Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔐 Security Notes

- In production, update CORS origins to specific domains
- Use environment variables for sensitive data
- Implement authentication/authorization
- Use HTTPS in production
- Validate and sanitize all inputs
