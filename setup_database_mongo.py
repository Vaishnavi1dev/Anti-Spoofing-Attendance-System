"""
MongoDB Database Setup Script
Run this to add students and their photos to MongoDB
"""

import os
from database_mongo import AttendanceDatabase
import shutil

def setup_database():
    """Initialize MongoDB database"""
    
    print("🔧 Connecting to MongoDB...")
    
    # You can change the connection string here
    # For local MongoDB: "mongodb://localhost:27017/"
    # For MongoDB Atlas: "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/"
    
    connection_string = input("MongoDB Connection String (press Enter for local): ").strip()
    if not connection_string:
        connection_string = "mongodb://localhost:27017/"
    
    try:
        db = AttendanceDatabase(connection_string=connection_string)
        print("✅ Connected to MongoDB!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("\n💡 Make sure MongoDB is running:")
        print("   - Local: Start MongoDB service")
        print("   - Atlas: Check your connection string")
        return None
    
    # Create photos directory structure
    os.makedirs("photos", exist_ok=True)
    os.makedirs("photos/students", exist_ok=True)
    
    print("\n" + "="*60)
    print("DATABASE SETUP COMPLETE")
    print("="*60)
    
    return db

def add_student_interactive(db):
    """Interactive student addition"""
    print("\n📝 Add New Student")
    print("-" * 40)
    
    student_id = input("Student ID (e.g., STU001): ").strip()
    if not student_id:
        print("❌ Student ID is required!")
        return
    
    # Check if student exists
    if db.get_student(student_id):
        print(f"⚠️  Student {student_id} already exists!")
        return
    
    name = input("Full Name: ").strip()
    if not name:
        print("❌ Name is required!")
        return
    
    email = input("Email (optional): ").strip() or None
    phone = input("Phone (optional): ").strip() or None
    
    # Add student
    if db.add_student(student_id, name, email, phone):
        print(f"✅ Student {name} added successfully!")
        
        # Add photos
        print(f"\n📸 Add photos for {name}")
        print("Photo types: front, left, right, with_glasses, without_glasses")
        
        student_dir = os.path.join("photos", "students", student_id)
        os.makedirs(student_dir, exist_ok=True)
        
        while True:
            photo_path = input("\nPhoto file path (or 'done' to finish): ").strip()
            if photo_path.lower() == 'done':
                break
            
            if not os.path.exists(photo_path):
                print(f"❌ File not found: {photo_path}")
                continue
            
            photo_type = input("Photo type (front/left/right/with_glasses/without_glasses): ").strip()
            description = input("Description (optional): ").strip() or None
            
            # Copy photo to student directory
            ext = os.path.splitext(photo_path)[1]
            new_filename = f"{student_id}_{photo_type}{ext}"
            new_path = os.path.join(student_dir, new_filename)
            
            shutil.copy2(photo_path, new_path)
            
            # Add to database
            db.add_student_photo(student_id, new_path, photo_type, description)
            print(f"✅ Photo added: {new_filename}")
        
        print(f"\n✅ Student {name} setup complete!")
    else:
        print("❌ Failed to add student!")

def list_students(db):
    """List all students"""
    students = db.get_all_students()
    
    if not students:
        print("\n📋 No students in database")
        return
    
    print("\n📋 Registered Students")
    print("="*80)
    print(f"{'ID':<12} {'Name':<25} {'Email':<30} {'Photos':<10}")
    print("-"*80)
    
    for student in students:
        photos = db.get_student_photos(student['student_id'])
        print(f"{student['student_id']:<12} {student['name']:<25} "
              f"{student.get('email', 'N/A') or 'N/A':<30} {len(photos):<10}")
    
    print("="*80)
    print(f"Total: {len(students)} students")

def view_student_photos(db):
    """View photos for a student"""
    student_id = input("\nEnter Student ID: ").strip()
    
    student = db.get_student(student_id)
    if not student:
        print(f"❌ Student {student_id} not found!")
        return
    
    photos = db.get_student_photos(student_id)
    
    print(f"\n📸 Photos for {student['name']}")
    print("="*80)
    
    if not photos:
        print("No photos found")
        return
    
    for i, photo in enumerate(photos, 1):
        print(f"\n{i}. Type: {photo.get('photo_type', 'N/A') or 'N/A'}")
        print(f"   Path: {photo['photo_path']}")
        print(f"   Description: {photo.get('description', 'N/A') or 'N/A'}")
        print(f"   Added: {photo['created_at']}")

def delete_student_interactive(db):
    """Delete a student"""
    student_id = input("\nEnter Student ID to delete: ").strip()
    
    student = db.get_student(student_id)
    if not student:
        print(f"❌ Student {student_id} not found!")
        return
    
    confirm = input(f"⚠️  Delete {student['name']}? This will remove all photos and attendance records! (yes/no): ")
    if confirm.lower() == 'yes':
        db.delete_student(student_id)
        print(f"✅ Student {student['name']} deleted!")
    else:
        print("❌ Deletion cancelled")

def bulk_import_from_folder(db):
    """Bulk import students from a folder structure
    
    Expected structure:
    import_folder/
        student_id_1/
            front.jpg
            left.jpg
            right.jpg
            with_glasses.jpg
        student_id_2/
            ...
    """
    folder_path = input("\nEnter folder path containing student folders: ").strip()
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return
    
    imported = 0
    
    for student_folder in os.listdir(folder_path):
        student_path = os.path.join(folder_path, student_folder)
        
        if not os.path.isdir(student_path):
            continue
        
        student_id = student_folder
        name = input(f"\nName for {student_id}: ").strip()
        
        if not name:
            print(f"⏭️  Skipping {student_id}")
            continue
        
        # Add student
        if not db.add_student(student_id, name):
            print(f"⚠️  Student {student_id} already exists, adding photos only")
        
        # Create student directory
        student_dir = os.path.join("photos", "students", student_id)
        os.makedirs(student_dir, exist_ok=True)
        
        # Import photos
        photo_count = 0
        for photo_file in os.listdir(student_path):
            if photo_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                src_path = os.path.join(student_path, photo_file)
                
                # Determine photo type from filename
                photo_name = os.path.splitext(photo_file)[0].lower()
                photo_type = photo_name if photo_name in ['front', 'left', 'right', 'with_glasses', 'without_glasses'] else 'other'
                
                # Copy to student directory
                ext = os.path.splitext(photo_file)[1]
                new_filename = f"{student_id}_{photo_type}_{photo_count}{ext}"
                dest_path = os.path.join(student_dir, new_filename)
                
                shutil.copy2(src_path, dest_path)
                db.add_student_photo(student_id, dest_path, photo_type)
                photo_count += 1
        
        print(f"✅ Imported {name} with {photo_count} photos")
        imported += 1
    
    print(f"\n✅ Bulk import complete! Imported {imported} students")

def view_statistics(db):
    """View database statistics"""
    print("\n📊 Database Statistics")
    print("="*60)
    
    students = db.get_all_students()
    print(f"Total Students: {len(students)}")
    
    today_attendance = db.get_today_attendance()
    print(f"Present Today: {len(today_attendance)}")
    
    suspicious = db.get_suspicious_activities(resolved=False)
    print(f"Unresolved Suspicious Activities: {len(suspicious)}")
    
    stats = db.get_attendance_stats()
    print(f"\nAll-Time Statistics:")
    print(f"  Total Attendance Records: {stats['total_records']}")
    print(f"  Average Suspicion Score: {stats['avg_suspicion']:.2f}")

def test_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB Connection...")
    
    connection_string = input("MongoDB Connection String (press Enter for local): ").strip()
    if not connection_string:
        connection_string = "mongodb://localhost:27017/"
    
    try:
        db = AttendanceDatabase(connection_string=connection_string)
        print("✅ Connection successful!")
        
        # Test operations
        print("\n📝 Testing database operations...")
        students = db.get_all_students()
        print(f"✅ Can read students: {len(students)} found")
        
        db.close()
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

def main():
    """Main menu"""
    db = setup_database()
    
    if not db:
        return
    
    while True:
        print("\n" + "="*60)
        print("MONGODB ATTENDANCE DATABASE SETUP")
        print("="*60)
        print("1. Add Student")
        print("2. List All Students")
        print("3. View Student Photos")
        print("4. Delete Student")
        print("5. Bulk Import from Folder")
        print("6. View Statistics")
        print("7. Test Connection")
        print("8. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            add_student_interactive(db)
        elif choice == '2':
            list_students(db)
        elif choice == '3':
            view_student_photos(db)
        elif choice == '4':
            delete_student_interactive(db)
        elif choice == '5':
            bulk_import_from_folder(db)
        elif choice == '6':
            view_statistics(db)
        elif choice == '7':
            test_connection()
        elif choice == '8':
            print("\n👋 Goodbye!")
            db.close()
            break
        else:
            print("❌ Invalid option!")

if __name__ == "__main__":
    main()
