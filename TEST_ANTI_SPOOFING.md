# Testing Anti-Spoofing Detection

## Changes Made

### Stricter Thresholds

**Texture Analysis**:
- Old: variance < 50 = fail
- New: variance < 80 = fail (stricter)

**Reflection Detection**:
- Old: bright_ratio > 0.15 = fail
- New: bright_ratio > 0.08 OR moderate_ratio > 0.25 = fail (much stricter)

**Depth Cues**:
- Old: edge_variance < 100 = fail
- New: edge_variance < 200 = fail (stricter)

**Overall Decision**:
- Old: Need 3/5 checks passing, avg > 0.6
- New: Need 5/6 checks passing, avg > 0.75, AND 3+ high scores (>0.8)

### New Detection Method

**Screen Pattern Detection** (6th method):
- Uses FFT (Fast Fourier Transform) to detect pixel grid patterns
- Phone/monitor screens have characteristic high-frequency patterns
- Real faces don't have these regular patterns

## How to Test

### Method 1: Test with Image File

```bash
cd backend
python test_liveness.py path/to/image.jpg
```

Example:
```bash
# Test with real photo
python test_liveness.py photos/students/245524733014/245524733014_front_1763808955.181779.jpg

# Test with phone screen capture (if you have one)
python test_liveness.py unknown_faces/unknown_1763812018.320704.jpg
```

### Method 2: Test with Camera

1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Open Test Page**:
   - Open `frontend/test-recognition.html` in browser
   - Or use Dashboard camera

3. **Test Scenarios**:
   
   **A. Real Person (Should PASS)**:
   - Face camera directly
   - Good lighting
   - Natural position
   - Expected: Green box, attendance marked
   
   **B. Phone Display (Should FAIL)**:
   - Show photo on phone screen
   - Hold phone to camera
   - Expected: Red box, "SPOOF!" label, NO attendance
   
   **C. Printed Photo (Should FAIL)**:
   - Print a photo
   - Hold to camera
   - Expected: Red box, "SPOOF!" label, NO attendance

### Method 3: Check Backend Logs

Watch the backend terminal for detailed output:

```
Liveness check for Sahithi: is_live=False, score=0.45
  Texture variance: 45.23
  Bright spots: 0.1234, Moderate: 0.3456
  High-freq energy: 18.45
  Edge variance: 123.45
  Liveness decision: passing=2/6, high_score=0/6, avg=0.45, is_live=False
⚠️ SPOOFING DETECTED: phone_screen_display for Sahithi
```

## Expected Results

### Real Person
```
✅ Texture: PASS (variance > 80)
✅ Color: PASS (entropy > 4.0)
✅ Reflection: PASS (bright < 0.08)
✅ Depth: PASS (edge_var > 200)
✅ Movement: PASS (natural movement)
✅ Screen Pattern: PASS (no pixel grid)

Result: 6/6 passing, avg > 0.75
Status: LIVE ✅
Action: Attendance marked
```

### Phone Display
```
❌ Texture: FAIL (variance < 80) - too smooth
❌ Reflection: FAIL (bright > 0.08) - screen glow
❌ Screen Pattern: FAIL (high-freq > 15) - pixel grid detected
✓ Color: PASS (might pass)
✓ Depth: BORDERLINE
✓ Movement: BORDERLINE

Result: 2-3/6 passing, avg < 0.75
Status: SPOOF ❌
Type: phone_screen_display
Action: NO attendance, logged as suspicious
```

### Printed Photo
```
❌ Texture: FAIL (variance < 80) - too smooth
❌ Depth: FAIL (edge_var < 200) - flat surface
✓ Color: BORDERLINE
✓ Reflection: PASS (no screen)
✓ Screen Pattern: PASS (no pixels)
✓ Movement: BORDERLINE

Result: 3/6 passing, avg < 0.75
Status: SPOOF ❌
Type: printed_photo
Action: NO attendance, logged as suspicious
```

## Troubleshooting

### Phone Display Still Passing

If phone display is still being detected as live:

1. **Check Backend Logs**:
   - Look for liveness scores
   - Check which tests are passing/failing
   - Note the specific values

2. **Make Even Stricter**:
   Edit `backend/liveness_detection.py`:
   ```python
   # Line ~30: Texture threshold
   if variance < 100:  # Increase from 80
   
   # Line ~90: Reflection threshold
   if bright_ratio > 0.05 or moderate_ratio > 0.20:  # Lower from 0.08/0.25
   
   # Line ~180: Overall decision
   is_live = passing_checks >= 6 and avg_score > 0.80  # Require ALL checks
   ```

3. **Restart Backend**:
   ```bash
   # Stop current process
   # Start again
   cd backend
   python main.py
   ```

### Real Person Being Rejected

If real people are being flagged as spoofs:

1. **Check Lighting**:
   - Ensure good, even lighting
   - Avoid harsh shadows
   - Natural light works best

2. **Check Camera Quality**:
   - Higher resolution helps
   - Clean camera lens
   - Stable camera position

3. **Relax Thresholds Slightly**:
   ```python
   # Texture
   if variance < 70:  # Lower from 80
   
   # Overall decision
   is_live = passing_checks >= 4 and avg_score > 0.70  # Relax from 5/0.75
   ```

## Monitoring

### Check Suspicious Activities

1. Go to Dashboard → Suspicious Activities
2. Look for "spoofing_attempt" entries
3. Review details and images
4. Verify detection is working

### Review Logs

```bash
# In backend terminal, watch for:
- "Liveness check for [name]: is_live=False"
- "SPOOFING DETECTED: [type]"
- Individual check results
```

## Fine-Tuning

### Adjust for Your Environment

Different environments may need different thresholds:

**Bright Environment** (lots of natural light):
- May need to relax reflection thresholds
- Texture detection works better

**Dim Environment**:
- May need to relax texture thresholds
- Reflection detection more sensitive

**High-Quality Camera**:
- Can use stricter thresholds
- Better texture and depth detection

**Low-Quality Camera**:
- Need more lenient thresholds
- Focus on reflection and screen pattern

## Current Settings (Very Strict)

```python
# Texture
variance < 80: FAIL

# Reflection
bright_ratio > 0.08 OR moderate_ratio > 0.25: FAIL

# Depth
edge_variance < 200: FAIL

# Screen Pattern (NEW)
high_freq_energy > 15: FAIL

# Overall
Need 5/6 checks passing
AND avg_score > 0.75
AND 3+ checks with score > 0.8
```

These settings are designed to catch phone displays while still allowing real people through.

## Next Steps

1. **Test with phone display** - Should now be detected as spoof
2. **Test with real person** - Should still pass
3. **Check backend logs** - Verify detection details
4. **Adjust if needed** - Fine-tune thresholds
5. **Monitor over time** - Track false positives/negatives

The system is now MUCH more strict and should catch phone display spoofing!
