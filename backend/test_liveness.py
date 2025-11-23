"""Test liveness detection on images"""
import cv2
import sys
from liveness_detection import LivenessDetector

if len(sys.argv) < 2:
    print("Usage: python test_liveness.py <image_path>")
    print("Example: python test_liveness.py photos/students/245524733014/245524733014_front_1763808955.181779.jpg")
    sys.exit(1)

image_path = sys.argv[1]

# Load image
img = cv2.imread(image_path)
if img is None:
    print(f"Failed to load image: {image_path}")
    sys.exit(1)

print(f"\n=== Testing Liveness Detection ===")
print(f"Image: {image_path}")
print(f"Size: {img.shape}")

# Create detector
detector = LivenessDetector()

# Run detection
is_live, confidence, checks = detector.detect_liveness(img)

print(f"\n=== Results ===")
print(f"Is Live: {is_live}")
print(f"Confidence: {confidence:.2%}")

print(f"\n=== Individual Checks ===")
for check_name, check_result in checks.items():
    status = "✓ PASS" if check_result['is_live'] else "✗ FAIL"
    print(f"{check_name:20s}: {status} (score: {check_result['score']:.2f})")

if not is_live:
    spoofing_type = detector.get_spoofing_type(checks)
    print(f"\n⚠️  SPOOFING DETECTED: {spoofing_type}")
else:
    print(f"\n✅ LIVE PERSON DETECTED")

print(f"\n=== Recommendation ===")
if is_live:
    print("✅ This image would PASS liveness check - attendance would be marked")
else:
    print("❌ This image would FAIL liveness check - attendance would NOT be marked")
    print(f"   Suspected spoofing type: {spoofing_type}")
