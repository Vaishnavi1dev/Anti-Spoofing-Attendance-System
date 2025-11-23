# Unknown Person Detection & Suspicious Activity Logging

## Overview

Implemented automatic detection and logging of unknown persons (people without photos in the system) as suspicious activities.

## How It Works

### Detection Process

1. **Face Detection**: Camera detects a face in the frame
2. **Recognition Attempt**: System tries to match face against student database
3. **Two Outcomes**:
   - **Match Found**: Student recognized → Attendance marked
   - **No Match**: Unknown person → Logged as suspicious

### Unknown Person Handling

When an unknown person is detected:

1. **Face Image Saved**:
   - Captured face saved to `unknown_faces/` directory
   - Filename: `unknown_{timestamp}.jpg`
   - Used for later review and identification

2. **Suspicious Activity Logged**:
   - Student ID: "UNKNOWN"
   - Activity Type: "unknown_person"
   - Description: Timestamp and image path
   - Stored in MongoDB `suspicious_activities` collection

3. **Visual Alert**:
   - Orange/yellow bounding box on camera feed
   - Label: "UNKNOWN"
   - Listed separately in detection panel

4. **Throttling**:
   - Temporary tracker created to avoid spam
   - Same unknown person not logged repeatedly
   - Resets when they leave frame

## Visual Indicators

### Camera Feed Display

**Recognized Students**:
- ✅ Green bounding box
- Student name displayed
- Listed under "Recognized Students"

**Unknown Persons**:
- ⚠️ Orange/yellow bounding box
- "UNKNOWN" label
- Listed under "Unknown Persons Detected"
- Pulsing indicator
- "Logged as suspicious" note

### Color Coding

- **Green** (0, 255, 0): Known student, normal behavior
- **Red** (0, 0, 255): Known student, suspicious behavior (static)
- **Orange** (0, 165, 255): Unknown person

## API Response Format

### Recognition Endpoint Response

```json
{
  "success": true,
  "detected_students": [
    {
      "student_id": "245524733014",
      "name": "Sahithi",
      "bbox": [683, 356, 366, 366],
      "status": "recognized"
    }
  ],
  "unknown_faces": [
    {
      "bbox": [100, 200, 300, 300],
      "status": "unknown",
      "image_path": "unknown_faces/unknown_1763812345.678.jpg"
    }
  ],
  "face_count": 2,
  "unknown_count": 1
}
```

### WebSocket Response

```json
{
  "frame": "base64_encoded_image",
  "students": [
    {
      "student_id": "245524733014",
      "name": "Sahithi",
      "bbox": [683, 356, 366, 366],
      "suspicious": false,
      "suspicion_score": 0,
      "status": "recognized"
    }
  ],
  "unknown_faces": [
    {
      "bbox": [100, 200, 300, 300],
      "status": "unknown",
      "timestamp": "2024-01-20T10:30:45.123456"
    }
  ],
  "unknown_count": 1,
  "timestamp": "2024-01-20T10:30:45.123456"
}
```

## Suspicious Activity Database Entry

```javascript
{
  _id: ObjectId("..."),
  student_id: "UNKNOWN",
  activity_type: "unknown_person",
  description: "Unrecognized person detected at 10:30:45. Image: unknown_faces/unknown_1763812345.678.jpg",
  timestamp: ISODate("2024-01-20T10:30:45.123Z"),
  resolved: false
}
```

## Use Cases

### 1. Security Monitoring
- Detect unauthorized persons in classroom
- Alert staff to unknown individuals
- Review captured images later

### 2. Student Registration
- Identify students without photos
- Prompt to add them to system
- Improve recognition coverage

### 3. Visitor Tracking
- Log non-student visitors
- Maintain security records
- Audit trail for access

### 4. System Improvement
- Identify recognition failures
- Find students needing better photos
- Improve threshold settings

## Viewing Unknown Persons

### Dashboard View
1. Go to Dashboard
2. Start monitoring
3. Unknown persons shown in orange
4. Listed separately from students

### Suspicious Activities Page
1. Navigate to "Suspicious" page
2. Filter by type: "unknown_person"
3. View all unknown person detections
4. See captured images
5. Resolve after identification

### Saved Images
- Location: `backend/unknown_faces/`
- Format: `unknown_{timestamp}.jpg`
- Review manually for identification
- Add to system if they're students

## Configuration

### Throttling
Prevent spam logging of same unknown person:

```python
# In backend/main.py
unknown_id = f"UNKNOWN_{datetime.now().timestamp()}"

if unknown_id not in student_trackers:
    # Log suspicious activity
    # Create temporary tracker
    student_trackers[unknown_id] = StudentTracker(unknown_id, "Unknown Person")
```

### Image Storage
```python
# Directory for unknown faces
unknown_dir = "unknown_faces"
os.makedirs(unknown_dir, exist_ok=True)

# Save with timestamp
timestamp = datetime.now().timestamp()
unknown_path = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")
cv2.imwrite(unknown_path, face_img)
```

## Testing

### Test Unknown Person Detection

1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Open Test Page**:
   - Open `frontend/test-recognition.html`
   - Or use Dashboard camera

3. **Test Scenarios**:
   - **Known Student**: Should show green box, name
   - **Unknown Person**: Should show orange box, "UNKNOWN"
   - **Mixed**: Both types displayed separately

4. **Verify Logging**:
   - Check `backend/unknown_faces/` for images
   - Check MongoDB `suspicious_activities` collection
   - View in Suspicious Activities page

### Expected Behavior

**Scenario 1: Student with Photos**
```
✅ Face detected
✅ Recognized as "Sahithi"
✅ Green bounding box
✅ Attendance marked
✅ No suspicious activity
```

**Scenario 2: Person without Photos**
```
✅ Face detected
⚠️ Not recognized
⚠️ Orange bounding box
⚠️ Labeled "UNKNOWN"
⚠️ Image saved to unknown_faces/
⚠️ Logged as suspicious activity
❌ No attendance marked
```

**Scenario 3: Multiple People**
```
✅ 2 faces detected
✅ 1 recognized (green)
⚠️ 1 unknown (orange)
✅ Both displayed separately
⚠️ Unknown logged as suspicious
```

## Security Considerations

### Privacy
- Unknown face images stored locally
- Not shared externally
- Can be deleted after review
- Consider data retention policy

### Access Control
- Only admin/teacher can view suspicious activities
- Students cannot see unknown person logs
- Images not accessible via web

### Data Retention
- Periodically review and clean up old images
- Resolve suspicious activities after identification
- Archive or delete as per policy

## Troubleshooting

### Unknown Person Not Detected
**Issue**: Person appears but not flagged as unknown

**Possible Causes**:
- Face not detected by OpenCV
- Recognition threshold too high
- Person partially matches someone

**Solutions**:
- Check face detection (run diagnose_camera.py)
- Lower recognition threshold
- Improve lighting

### Too Many False Unknowns
**Issue**: Known students flagged as unknown

**Possible Causes**:
- Recognition threshold too strict
- Poor photo quality
- Lighting differences

**Solutions**:
- Raise threshold slightly (0.3 → 0.35)
- Upload more/better photos
- Improve camera conditions

### Images Not Saving
**Issue**: No images in unknown_faces/ directory

**Possible Causes**:
- Permission issues
- Disk space
- Path problems

**Solutions**:
- Check directory permissions
- Verify disk space
- Check backend logs for errors

### Spam Logging
**Issue**: Same person logged multiple times

**Possible Causes**:
- Throttling not working
- Person leaving and re-entering frame

**Solutions**:
- Check tracker implementation
- Increase tracker timeout
- Review logs for patterns

## Integration with Existing Features

### Attendance System
- Unknown persons do NOT get attendance marked
- Only recognized students get attendance
- Clear separation in records

### Suspicious Activities
- Unknown persons automatically logged
- Viewable in Suspicious Activities page
- Can be resolved after identification

### Dashboard
- Real-time display of unknown persons
- Visual distinction from students
- Count shown separately

## Future Enhancements

### Planned Features
- [ ] Face matching against unknown images
- [ ] Bulk identification of unknowns
- [ ] Email alerts for unknown persons
- [ ] Visitor registration system
- [ ] Temporary access codes
- [ ] Integration with access control
- [ ] Analytics on unknown detections
- [ ] Pattern recognition for repeat unknowns

### Possible Improvements
- [ ] Confidence score for unknowns
- [ ] Multiple angle capture
- [ ] Video recording of unknowns
- [ ] Automatic notification system
- [ ] Integration with security cameras
- [ ] Face clustering for same unknown person
- [ ] Quick-add to system from unknown image

## Summary

Unknown person detection provides:
- ✅ Automatic identification of non-students
- ✅ Security monitoring and alerts
- ✅ Image capture for review
- ✅ Suspicious activity logging
- ✅ Visual distinction on camera feed
- ✅ Integration with existing systems

This ensures only authorized students are recognized while flagging potential security concerns.
