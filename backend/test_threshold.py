"""Test different recognition thresholds to find optimal value"""
import cv2
import numpy as np
from database_mongo import AttendanceDatabase
from deepface import DeepFace
import os
import shutil

# Initialize database
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
db = AttendanceDatabase(connection_string=MONGODB_URI)

print("=== Recognition Threshold Testing ===\n")

# Get all photos
all_photos = db.get_all_student_photos()
print(f"Found {len(all_photos)} photos in database\n")

if len(all_photos) < 2:
    print("Need at least 2 photos from different students to test")
    exit(1)

# Create temp database
temp_db = "temp_threshold_test"
os.makedirs(temp_db, exist_ok=True)

print("Setting up test database...")
for photo in all_photos:
    if os.path.exists(photo['photo_path']):
        dest = os.path.join(temp_db, f"{photo['student_id']}_{os.path.basename(photo['photo_path'])}")
        shutil.copy2(photo['photo_path'], dest)

# Test each photo against the database
print("\n=== Testing Each Photo ===\n")

results = []

for test_photo in all_photos[:5]:  # Test first 5 photos
    if not os.path.exists(test_photo['photo_path']):
        continue
    
    print(f"Testing: {test_photo['student_id']} - {test_photo['photo_type']}")
    
    try:
        result = DeepFace.find(
            img_path=test_photo['photo_path'],
            db_path=temp_db,
            model_name="VGG-Face",
            enforce_detection=False,
            silent=True,
            distance_metric="cosine"
        )
        
        if len(result) > 0 and len(result[0]) > 0:
            # Show top 3 matches
            print("  Top matches:")
            for i in range(min(3, len(result[0]))):
                match = result[0].iloc[i]
                match_path = match['identity']
                distance = match.get('VGG-Face_cosine', 1.0)
                student_id = os.path.basename(match_path).split('_')[0]
                
                is_correct = student_id == test_photo['student_id']
                marker = "✓" if is_correct else "✗"
                
                print(f"    {i+1}. {marker} {student_id}: distance={distance:.4f}, confidence={((1-distance)*100):.1f}%")
                
                if i == 0:  # Best match
                    results.append({
                        'actual': test_photo['student_id'],
                        'predicted': student_id,
                        'distance': distance,
                        'correct': is_correct
                    })
        print()
    except Exception as e:
        print(f"  Error: {e}\n")

# Cleanup
if os.path.exists(temp_db):
    shutil.rmtree(temp_db)

# Analyze results
print("\n=== Analysis ===\n")

if results:
    correct_matches = [r for r in results if r['correct']]
    incorrect_matches = [r for r in results if not r['correct']]
    
    print(f"Total tests: {len(results)}")
    print(f"Correct matches: {len(correct_matches)}")
    print(f"Incorrect matches: {len(incorrect_matches)}")
    print(f"Accuracy: {(len(correct_matches)/len(results)*100):.1f}%\n")
    
    if correct_matches:
        correct_distances = [r['distance'] for r in correct_matches]
        print(f"Correct match distances:")
        print(f"  Min: {min(correct_distances):.4f}")
        print(f"  Max: {max(correct_distances):.4f}")
        print(f"  Avg: {np.mean(correct_distances):.4f}\n")
    
    if incorrect_matches:
        incorrect_distances = [r['distance'] for r in incorrect_matches]
        print(f"Incorrect match distances:")
        print(f"  Min: {min(incorrect_distances):.4f}")
        print(f"  Max: {max(incorrect_distances):.4f}")
        print(f"  Avg: {np.mean(incorrect_distances):.4f}\n")
        
        print("Incorrect matches detail:")
        for r in incorrect_matches:
            print(f"  {r['actual']} → {r['predicted']} (distance: {r['distance']:.4f})")
        print()
    
    # Recommend threshold
    print("=== Threshold Recommendations ===\n")
    
    all_distances = [r['distance'] for r in results]
    
    thresholds = [0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
    
    print("Threshold | Correct | Incorrect | Accuracy")
    print("----------|---------|-----------|----------")
    
    for threshold in thresholds:
        accepted = [r for r in results if r['distance'] <= threshold]
        correct = [r for r in accepted if r['correct']]
        incorrect = [r for r in accepted if not r['correct']]
        
        if accepted:
            accuracy = len(correct) / len(accepted) * 100
        else:
            accuracy = 0
        
        print(f"  {threshold:.2f}    |   {len(correct):2d}    |    {len(incorrect):2d}     | {accuracy:6.1f}%")
    
    print("\n💡 Recommendation:")
    if incorrect_matches:
        max_incorrect_dist = max([r['distance'] for r in incorrect_matches])
        recommended = max(0.2, max_incorrect_dist - 0.05)
        print(f"   Set threshold to {recommended:.2f} or lower to prevent false positives")
    else:
        print(f"   Current threshold (0.3) seems good - no false positives detected")
    
    if correct_matches:
        max_correct_dist = max([r['distance'] for r in correct_matches])
        print(f"   But keep it above {max_correct_dist:.2f} to allow correct matches")

else:
    print("No results to analyze")

print("\n=== Tips ===")
print("1. Lower threshold = stricter matching (fewer false positives)")
print("2. Higher threshold = more lenient (more matches but more errors)")
print("3. Ideal: threshold between max correct distance and min incorrect distance")
print("4. Upload more photos per student to improve accuracy")
print("5. Ensure photos are clear, well-lit, and properly labeled")
