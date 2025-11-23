# Quick Test Guide - Camera Recognition

## ✅ Backend is Running!

The backend server is now running with improved face recognition.

## 🚀 Quick Test (3 Steps)

### Step 1: Open Test Page
```
1. Open: frontend/test-recognition.html in your browser
2. Or double-click the file to open it
```

### Step 2: Start Camera
```
1. Click "Start Camera" button
2. Allow camera permission if prompted
3. Position your face in the frame
```

### Step 3: Test Recognition
```
1. Click "Capture & Recognize"
2. Wait 2-3 seconds
3. Check results below video
```

## 📋 What to Expect

### If You Have Photos Uploaded:
- ✅ Your name and student ID will appear
- ✅ Green checkmark with your details
- ✅ Attendance will be marked automatically

### If No Photos Uploaded:
- ⚠️ "No students recognized"
- 📸 Upload photos first:
  1. Go to http://localhost:3000 (frontend)
  2. Login as teacher/admin
  3. Go to Students page
  4. Click on your student record
  5. Upload 3-5 clear photos

### If No Face Detected:
- ⚠️ "No faces detected"
- 💡 Tips:
  - Improve lighting
  - Move closer to camera (2-3 feet)
  - Face the camera directly
  - Remove obstructions

## 🔍 Diagnostic Tools

### Check Database:
```bash
cd backend
python test_recognition.py
```
Shows: Students and photos in database

### Test Camera:
```bash
cd backend
python diagnose_camera.py
```
Shows: Camera status, face detection, saves test images

### Test Recognition Endpoint:
```bash
cd backend
python test_camera_recognition.py
```
Shows: Recognition results with uploaded photo

## 📊 Understanding Results

### Distance Values:
- `< 0.2` = Excellent match (90%+ confidence)
- `0.2 - 0.4` = Good match (70-90% confidence)
- `0.4 - 0.6` = Acceptable match (50-70% confidence)
- `> 0.6` = No match (rejected)

### Current Threshold: 0.6
- Adjust in `backend/main.py` if needed
- Lower = stricter, Higher = more lenient

## 🎯 Tips for Best Results

### Photo Upload:
1. Upload 3-5 photos per student
2. Different angles (front, left, right)
3. Clear, well-lit photos
4. High resolution (640x480 minimum)
5. Similar to camera conditions

### Camera Usage:
1. Good lighting (natural light best)
2. Face camera directly
3. Stay 2-3 feet away
4. Keep still during capture
5. Remove glasses if not in photos

### Environment:
1. Consistent lighting
2. Plain background helps
3. Avoid backlighting
4. Minimize shadows
5. Stable camera position

## 🐛 Common Issues

### Issue: "Camera permission denied"
**Solution**: Allow camera in browser settings

### Issue: "No faces detected"
**Solution**: Check lighting, position, run diagnose_camera.py

### Issue: "Face detected but not recognized"
**Solution**: Upload photos, check photo quality

### Issue: "Wrong person recognized"
**Solution**: Upload more photos, check for duplicates

### Issue: "Recognition is slow"
**Solution**: First run downloads models, subsequent runs faster

## 📱 Using the Main Application

Once testing works:

1. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

2. **Login**: http://localhost:3000
   - Teacher/Admin account
   - Or student account

3. **Go to Dashboard**:
   - Click "Start Monitoring"
   - Camera will recognize faces every 3 seconds
   - Attendance marked automatically

4. **View Results**:
   - Detected students shown in real-time
   - Check attendance records
   - View suspicious activities

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Camera starts without errors
- ✅ Face is detected (bounding box shown)
- ✅ Your name appears in results
- ✅ Student ID is correct
- ✅ Attendance is marked in database

## 📞 Still Not Working?

1. Check backend logs (terminal running main.py)
2. Check browser console (F12)
3. Run all diagnostic tools
4. Verify photos are uploaded
5. Check MongoDB is running
6. Ensure port 8000 is not blocked

## 🔧 Advanced Configuration

### Change Recognition Threshold:
Edit `backend/main.py`, line ~750:
```python
RECOGNITION_THRESHOLD = 0.6  # Adjust this value
```

### Change Recognition Frequency:
Edit `frontend/src/components/CameraFeed.tsx`, line ~50:
```typescript
intervalRef.current = setInterval(() => {
    captureAndRecognize();
}, 3000);  // Change 3000 to desired milliseconds
```

### Change Camera Resolution:
Edit `frontend/src/components/CameraFeed.tsx`, line ~35:
```typescript
video: {
    width: { ideal: 1280 },  // Change resolution
    height: { ideal: 720 },
    facingMode: "user"
}
```

---

**Ready to test? Open `frontend/test-recognition.html` now!** 🚀
