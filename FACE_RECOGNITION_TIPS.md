# Face Recognition Troubleshooting Guide

## Why the camera might not be detecting you:

### 1. **Photo Quality Issues**
- **Upload multiple photos**: The system works better with 3-5 photos of the same person
- **Photo types to upload**:
  - Front-facing (looking directly at camera)
  - Left profile
  - Right profile
  - With glasses (if you wear them)
  - Different lighting conditions

### 2. **Camera Conditions**
- **Lighting**: Make sure you have good, even lighting on your face
  - Avoid backlighting (light behind you)
  - Avoid harsh shadows
  - Natural daylight works best
  
- **Distance**: Position yourself 2-3 feet from the camera
  - Not too close (face fills entire frame)
  - Not too far (face is too small)

- **Angle**: Face the camera directly
  - Look straight at the camera
  - Keep your head level (not tilted)

### 3. **Image Quality**
- **Resolution**: The uploaded photos should be clear and high-resolution
- **Focus**: Photos should be in focus, not blurry
- **Face size**: Your face should be clearly visible in the photo

### 4. **Recognition Settings**
The system uses:
- **Model**: VGG-Face (deep learning model)
- **Detection**: OpenCV Haar Cascade
- **Threshold**: Cosine distance < 0.4 (lower = more similar)

### 5. **Testing Steps**

1. **Test the recognition endpoint**:
   ```bash
   cd backend
   python test_camera_recognition.py
   ```

2. **Use the test page**:
   - Open `frontend/test-recognition.html` in your browser
   - Click "Start Camera"
   - Position your face
   - Click "Capture & Recognize"
   - Check the results

3. **Check the backend logs**:
   - Look for "Match found" messages
   - Check the distance value (should be < 0.4)
   - Verify student ID extraction

### 6. **Common Issues**

**Issue**: "No faces recognized"
- **Solution**: Upload more photos, improve lighting, get closer to camera

**Issue**: "Wrong person detected"
- **Solution**: Upload more varied photos of yourself, ensure photos are labeled correctly

**Issue**: "Face detected but not recognized"
- **Solution**: The face is detected but doesn't match any photos in database
  - Check if photos are uploaded for your student ID
  - Verify photos are in the correct folder
  - Try uploading clearer photos

### 7. **Optimal Photo Upload**

When uploading photos:
1. Take photos in the same environment where you'll use the camera
2. Use the same camera if possible
3. Wear similar clothing/accessories
4. Upload at least 3 different photos
5. Include variations (with/without glasses, different expressions)

### 8. **Database Check**

Run this to verify your photos are in the system:
```bash
cd backend
python test_recognition.py
```

This will show:
- Total photos in database
- Student IDs with photos
- File paths and sizes

### 9. **Recognition Process**

The system:
1. Captures frame from camera (every 3 seconds)
2. Detects faces using OpenCV
3. Extracts face region
4. Compares against all student photos using DeepFace
5. Returns best match if distance < threshold
6. Marks attendance automatically

### 10. **Performance Tips**

- **First recognition is slow**: DeepFace downloads models on first run (~580MB)
- **Subsequent recognitions are faster**: Models are cached
- **More photos = slower**: Each photo is compared, so keep it reasonable (3-5 per student)
- **Image size matters**: Larger images take longer to process

## Quick Fix Checklist

- [ ] Photos uploaded for your student ID
- [ ] Good lighting on your face
- [ ] Face clearly visible in camera
- [ ] Looking directly at camera
- [ ] 2-3 feet from camera
- [ ] Backend server running
- [ ] No errors in backend logs
- [ ] Browser has camera permission
