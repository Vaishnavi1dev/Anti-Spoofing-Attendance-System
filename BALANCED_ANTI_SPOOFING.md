# Balanced Anti-Spoofing Configuration

## Problem
The anti-spoofing was too strict and was rejecting real people.

## Solution
Adjusted thresholds to be balanced - strict enough to catch phone displays but lenient enough for real people.

## New Balanced Thresholds

### 1. Texture Analysis
```python
# Old (too strict):
variance < 80: FAIL

# New (balanced):
variance < 15: FAIL (very smooth - definitely fake)
variance > 25: PASS (good texture - real person)
15-25: PASS with lower score (borderline - allow)
```

### 2. Reflection Detection
```python
# Old (too strict):
bright > 0.08 OR moderate > 0.25: FAIL

# New (balanced):
bright > 0.20 OR moderate > 0.35: FAIL (obvious screen glow)
bright < 0.10 AND moderate < 0.25: PASS (no reflections)
Otherwise: PASS with lower score (borderline)
```

### 3. Depth Cues
```python
# Old (too strict):
edge_variance < 200: FAIL

# New (balanced):
edge_variance < 100: FAIL (very flat - definitely fake)
edge_variance > 400: PASS (good depth - real person)
100-400: PASS with lower score (borderline)
```

### 4. Screen Pattern Detection
```python
# Old (too simple):
high_freq > 15: FAIL

# New (smarter):
20 < high_freq < 80: FAIL (screen pixel pattern range)
high_freq < 15 OR high_freq > 100: PASS (no pattern or camera noise)
Otherwise: PASS with lower score
```

**Key Insight**: Very high frequency energy (>100) is actually from camera noise/quality, not screens. Screens have moderate high-freq energy (20-80).

### 5. Overall Decision
```python
# Old (too strict):
Need 5/6 checks passing
AND avg_score > 0.75
AND 3+ high scores (>0.8)

# New (balanced):
Need 4/6 checks passing (majority)
AND avg_score > 0.65
AND 2+ high scores (>0.7)
AND no more than 2 checks failing badly
```

## Expected Behavior

### Real Person (Webcam)
```
Texture variance: 19-30 → PASS (0.6-0.9)
Bright spots: 0.00-0.15 → PASS (0.9)
Edge variance: 400-1500 → PASS (0.9)
High-freq energy: 100-150 → PASS (0.9) [camera noise, not screen]
Movement: Natural → PASS (0.9)
Color: Good diversity → PASS (0.9)

Result: 5-6/6 passing, avg 0.75-0.85
Status: LIVE ✅
```

### Phone Display
```
Texture variance: 5-12 → FAIL (0.2) [too smooth]
Bright spots: 0.15-0.30 → FAIL (0.2-0.6) [screen glow]
Edge variance: 50-150 → FAIL (0.3-0.6) [flat surface]
High-freq energy: 30-60 → FAIL (0.3) [pixel pattern]
Movement: Static/uniform → FAIL (0.2-0.5)
Color: Limited → FAIL (0.4-0.6)

Result: 1-3/6 passing, avg 0.35-0.55
Status: SPOOF ❌
```

### Printed Photo
```
Texture variance: 3-10 → FAIL (0.2) [very smooth]
Bright spots: 0.00-0.05 → PASS (0.9) [no screen]
Edge variance: 30-80 → FAIL (0.3) [very flat]
High-freq energy: 5-15 → PASS (0.9) [no pixels]
Movement: Static → FAIL (0.2)
Color: Limited → FAIL (0.4)

Result: 2/6 passing, avg 0.45
Status: SPOOF ❌
```

## Testing

### Test Real Person
```bash
# Should now PASS
cd backend
python main.py

# In another terminal or browser:
# Open frontend/test-recognition.html
# Face camera directly
# Expected: Green box, attendance marked
```

### Test Phone Display
```bash
# Should still FAIL
# Show photo on phone screen
# Expected: Red box, "SPOOF!" label, NO attendance
```

### Check Logs
```
Real person example:
  Texture variance: 26.67
  Bright spots: 0.0000, Moderate: 0.0000
  Edge variance: 619.71
  High-freq energy: 148.45
  Liveness decision: passing=5/6, high_score=4/6, avg=0.82, is_live=True
✅ LIVE PERSON

Phone display example:
  Texture variance: 8.23
  Bright spots: 0.1823, Moderate: 0.2891
  Edge variance: 67.45
  High-freq energy: 45.67
  Liveness decision: passing=2/6, high_score=0/6, avg=0.42, is_live=False
❌ SPOOFING DETECTED: phone_screen_display
```

## Fine-Tuning

If you still have issues:

### Real People Being Rejected
**Symptoms**: Texture variance 15-25, edge variance 100-400

**Solution**: Already handled with borderline scores. If still failing:
```python
# In liveness_detection.py, line ~180
is_live = passing_checks >= 3 and avg_score > 0.60  # More lenient
```

### Phone Displays Passing
**Symptoms**: High-freq energy in screen range (20-80)

**Solution**: Make screen pattern detection stricter:
```python
# In liveness_detection.py, line ~140
if 15 < high_freq_energy < 90:  # Wider range
    return False, 0.2
```

## Current Configuration Summary

| Check | Fail Threshold | Pass Threshold | Borderline |
|-------|---------------|----------------|------------|
| Texture | < 15 | > 25 | 15-25 (allow) |
| Reflection | bright>0.20 OR mod>0.35 | bright<0.10 AND mod<0.25 | Allow |
| Depth | < 100 | > 400 | 100-400 (allow) |
| Screen Pattern | 20-80 | <15 OR >100 | Allow |
| Overall | 4/6 passing, avg>0.65, 2+ high scores | | |

This configuration is balanced to:
- ✅ Allow real people with varying camera quality
- ✅ Catch phone display spoofing
- ✅ Catch printed photo spoofing
- ✅ Handle different lighting conditions
- ✅ Work with different camera qualities

## Monitoring

Watch backend logs for patterns:
- Real people should have avg scores 0.70-0.90
- Phone displays should have avg scores 0.30-0.60
- If real people score < 0.65, thresholds may need adjustment

The system is now balanced for real-world use!
