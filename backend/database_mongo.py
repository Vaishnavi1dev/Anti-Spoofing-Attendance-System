from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os
from bson import ObjectId

class AttendanceDatabase:
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="classroom_attendance"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (default: local)
            db_name: Database name
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        
        # Collections
        self.students = self.db.students
        self.student_photos = self.db.student_photos
        self.attendance = self.db.attendance
        self.suspicious_activity = self.db.suspicious_activity
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        # Students indexes
        self.students.create_index([("student_id", ASCENDING)], unique=True)
        self.students.create_index([("name", ASCENDING)])
        
        # Photos indexes
        self.student_photos.create_index([("student_id", ASCENDING)])
        self.student_photos.create_index([("photo_type", ASCENDING)])
        
        # Attendance indexes
        self.attendance.create_index([("student_id", ASCENDING), ("date", DESCENDING)])
        self.attendance.create_index([("date", DESCENDING)])
        
        # Suspicious activity indexes
        self.suspicious_activity.create_index([("student_id", ASCENDING)])
        self.suspicious_activity.create_index([("timestamp", DESCENDING)])
        self.suspicious_activity.create_index([("resolved", ASCENDING)])
    
    # ==================== STUDENT MANAGEMENT ====================
    
    def add_student(self, student_id, name, email=None, phone=None):
        """Add a new student"""
        try:
            student_doc = {
                "student_id": student_id,
                "name": name,
                "email": email,
                "phone": phone,
                "created_at": datetime.now()
            }
            self.students.insert_one(student_doc)
            return True
        except Exception as e:
            print(f"Error adding student: {e}")
            return False
    
    def get_student(self, student_id):
        """Get student details"""
        student = self.students.find_one({"student_id": student_id})
        if student:
            student['_id'] = str(student['_id'])
            return student
        return None
    
    def get_all_students(self):
        """Get all students"""
        students = list(self.students.find().sort("name", ASCENDING))
        for student in students:
            student['_id'] = str(student['_id'])
        return students
    
    def update_student(self, student_id, name=None, email=None, phone=None):
        """Update student details"""
        update_fields = {}
        
        if name:
            update_fields["name"] = name
        if email:
            update_fields["email"] = email
        if phone:
            update_fields["phone"] = phone
        
        if update_fields:
            result = self.students.update_one(
                {"student_id": student_id},
                {"$set": update_fields}
            )
            return result.modified_count > 0
        return False
    
    def delete_student(self, student_id):
        """Delete a student and all related data"""
        # Delete photos
        self.student_photos.delete_many({"student_id": student_id})
        
        # Delete attendance records
        self.attendance.delete_many({"student_id": student_id})
        
        # Delete suspicious activities
        self.suspicious_activity.delete_many({"student_id": student_id})
        
        # Delete student
        result = self.students.delete_one({"student_id": student_id})
        return result.deleted_count > 0
    
    # ==================== PHOTO MANAGEMENT ====================
    
    def add_student_photo(self, student_id, photo_path, photo_type=None, description=None):
        """
        Add a photo for a student
        
        Args:
            student_id: Student ID
            photo_path: Path to photo file
            photo_type: Type of photo (front, left, right, with_glasses, without_glasses)
            description: Optional description
        """
        photo_doc = {
            "student_id": student_id,
            "photo_path": photo_path,
            "photo_type": photo_type,
            "description": description,
            "created_at": datetime.now()
        }
        result = self.student_photos.insert_one(photo_doc)
        return str(result.inserted_id)
    
    def get_student_photos(self, student_id):
        """Get all photos for a student"""
        photos = list(self.student_photos.find({"student_id": student_id}).sort("created_at", ASCENDING))
        for photo in photos:
            photo['_id'] = str(photo['_id'])
            photo['photo_id'] = photo['_id']
        return photos
    
    def get_all_student_photos(self):
        """Get all photos for all students (for face recognition)"""
        pipeline = [
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$unwind": "$student_info"
            },
            {
                "$project": {
                    "photo_path": 1,
                    "student_id": 1,
                    "name": "$student_info.name",
                    "photo_type": 1
                }
            }
        ]
        
        photos = list(self.student_photos.aggregate(pipeline))
        for photo in photos:
            photo['_id'] = str(photo['_id'])
        return photos
    
    def delete_photo(self, photo_id):
        """Delete a specific photo"""
        try:
            # Get photo info
            photo = self.student_photos.find_one({"_id": ObjectId(photo_id)})
            
            if photo:
                photo_path = photo['photo_path']
                
                # Delete from database
                self.student_photos.delete_one({"_id": ObjectId(photo_id)})
                
                # Delete file if exists
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                
                return True
        except Exception as e:
            print(f"Error deleting photo: {e}")
        return False
    
    # ==================== ATTENDANCE MANAGEMENT ====================
    
    def mark_entry(self, student_id, entry_time=None):
        """Mark student entry"""
        if entry_time is None:
            entry_time = datetime.now()
        
        date = entry_time.date()
        
        # Check if attendance record exists for today
        existing = self.attendance.find_one({
            "student_id": student_id,
            "date": datetime.combine(date, datetime.min.time())
        })
        
        if existing:
            # Update entry time
            self.attendance.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "entry_time": entry_time,
                        "status": "present"
                    }
                }
            )
        else:
            # Create new attendance record
            attendance_doc = {
                "student_id": student_id,
                "date": datetime.combine(date, datetime.min.time()),
                "entry_time": entry_time,
                "exit_time": None,
                "status": "present",
                "suspicion_score": 0,
                "notes": None
            }
            self.attendance.insert_one(attendance_doc)
    
    def mark_exit(self, student_id, exit_time=None):
        """Mark student exit"""
        if exit_time is None:
            exit_time = datetime.now()
        
        date = exit_time.date()
        
        self.attendance.update_one(
            {
                "student_id": student_id,
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "$set": {"exit_time": exit_time}
            }
        )
    
    def update_suspicion_score(self, student_id, score, date=None):
        """Update suspicion score for a student"""
        if date is None:
            date = datetime.now().date()
        
        self.attendance.update_one(
            {
                "student_id": student_id,
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "$set": {"suspicion_score": score}
            }
        )
    
    def add_attendance_note(self, student_id, note, date=None):
        """Add a note to attendance record"""
        if date is None:
            date = datetime.now().date()
        
        self.attendance.update_one(
            {
                "student_id": student_id,
                "date": datetime.combine(date, datetime.min.time())
            },
            {
                "$set": {"notes": note}
            }
        )
    
    def get_today_attendance(self):
        """Get today's attendance"""
        today = datetime.combine(datetime.now().date(), datetime.min.time())
        
        pipeline = [
            {
                "$match": {"date": today}
            },
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$unwind": "$student_info"
            },
            {
                "$project": {
                    "student_id": 1,
                    "name": "$student_info.name",
                    "entry_time": 1,
                    "exit_time": 1,
                    "status": 1,
                    "suspicion_score": 1,
                    "notes": 1
                }
            },
            {
                "$sort": {"entry_time": ASCENDING}
            }
        ]
        
        attendance = list(self.attendance.aggregate(pipeline))
        for record in attendance:
            record['_id'] = str(record['_id'])
        return attendance
    
    def get_attendance_by_date(self, date):
        """Get attendance for a specific date"""
        date_obj = datetime.combine(date, datetime.min.time())
        
        pipeline = [
            {
                "$match": {"date": date_obj}
            },
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$unwind": "$student_info"
            },
            {
                "$project": {
                    "student_id": 1,
                    "name": "$student_info.name",
                    "entry_time": 1,
                    "exit_time": 1,
                    "status": 1,
                    "suspicion_score": 1,
                    "notes": 1
                }
            },
            {
                "$sort": {"entry_time": ASCENDING}
            }
        ]
        
        attendance = list(self.attendance.aggregate(pipeline))
        for record in attendance:
            record['_id'] = str(record['_id'])
        return attendance
    
    def get_student_attendance_history(self, student_id, limit=30):
        """Get attendance history for a student"""
        attendance = list(
            self.attendance.find({"student_id": student_id})
            .sort("date", DESCENDING)
            .limit(limit)
        )
        
        for record in attendance:
            record['_id'] = str(record['_id'])
        return attendance
    
    def get_attendance_by_date_range(self, start_date, end_date):
        """Get attendance for a date range"""
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.min.time())
        
        pipeline = [
            {
                "$match": {
                    "date": {"$gte": start_dt, "$lte": end_dt}
                }
            },
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$unwind": "$student_info"
            },
            {
                "$project": {
                    "student_id": 1,
                    "name": "$student_info.name",
                    "date": 1,
                    "entry_time": 1,
                    "exit_time": 1,
                    "status": 1,
                    "suspicion_score": 1
                }
            },
            {
                "$sort": {"date": DESCENDING, "entry_time": ASCENDING}
            }
        ]
        
        attendance = list(self.attendance.aggregate(pipeline))
        for record in attendance:
            record['_id'] = str(record['_id'])
        return attendance
    
    # ==================== SUSPICIOUS ACTIVITY ====================
    
    def log_suspicious_activity(self, student_id, activity_type, description):
        """Log suspicious activity"""
        activity_doc = {
            "student_id": student_id,
            "timestamp": datetime.now(),
            "activity_type": activity_type,
            "description": description,
            "resolved": False
        }
        result = self.suspicious_activity.insert_one(activity_doc)
        return str(result.inserted_id)
    
    def get_suspicious_activities(self, resolved=False, limit=50):
        """Get suspicious activities"""
        pipeline = [
            {
                "$match": {"resolved": resolved}
            },
            {
                "$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {
                "$unwind": "$student_info"
            },
            {
                "$project": {
                    "activity_id": {"$toString": "$_id"},
                    "student_id": 1,
                    "name": "$student_info.name",
                    "timestamp": 1,
                    "activity_type": 1,
                    "description": 1,
                    "resolved": 1
                }
            },
            {
                "$sort": {"timestamp": DESCENDING}
            },
            {
                "$limit": limit
            }
        ]
        
        activities = list(self.suspicious_activity.aggregate(pipeline))
        for activity in activities:
            activity['_id'] = str(activity['_id'])
        return activities
    
    def resolve_suspicious_activity(self, activity_id):
        """Mark suspicious activity as resolved"""
        try:
            result = self.suspicious_activity.update_one(
                {"_id": ObjectId(activity_id)},
                {"$set": {"resolved": True}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error resolving activity: {e}")
            return False
    
    def get_student_suspicious_activities(self, student_id, limit=20):
        """Get suspicious activities for a specific student"""
        activities = list(
            self.suspicious_activity.find({"student_id": student_id})
            .sort("timestamp", DESCENDING)
            .limit(limit)
        )
        
        for activity in activities:
            activity['_id'] = str(activity['_id'])
            activity['activity_id'] = activity['_id']
        return activities
    
    # ==================== STATISTICS ====================
    
    def get_attendance_stats(self, start_date=None, end_date=None):
        """Get attendance statistics"""
        match_stage = {}
        
        if start_date and end_date:
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.min.time())
            match_stage = {"date": {"$gte": start_dt, "$lte": end_dt}}
        
        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {
                "$group": {
                    "_id": None,
                    "total_students": {"$addToSet": "$student_id"},
                    "total_records": {"$sum": 1},
                    "present_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}
                    },
                    "avg_suspicion": {"$avg": "$suspicion_score"}
                }
            }
        ]
        
        result = list(self.attendance.aggregate(pipeline))
        
        if result:
            stats = result[0]
            return {
                'total_students': len(stats['total_students']),
                'total_records': stats['total_records'],
                'present_count': stats['present_count'],
                'avg_suspicion': stats['avg_suspicion'] or 0
            }
        
        return {
            'total_students': 0,
            'total_records': 0,
            'present_count': 0,
            'avg_suspicion': 0
        }
    
    def get_student_stats(self, student_id):
        """Get statistics for a specific student"""
        pipeline = [
            {"$match": {"student_id": student_id}},
            {
                "$group": {
                    "_id": None,
                    "total_days": {"$sum": 1},
                    "present_days": {
                        "$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}
                    },
                    "avg_suspicion": {"$avg": "$suspicion_score"},
                    "total_suspicion_incidents": {
                        "$sum": {"$cond": [{"$gt": ["$suspicion_score", 5]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = list(self.attendance.aggregate(pipeline))
        
        if result:
            stats = result[0]
            attendance_rate = (stats['present_days'] / stats['total_days'] * 100) if stats['total_days'] > 0 else 0
            
            return {
                'total_days': stats['total_days'],
                'present_days': stats['present_days'],
                'attendance_rate': round(attendance_rate, 2),
                'avg_suspicion': round(stats['avg_suspicion'] or 0, 2),
                'total_suspicion_incidents': stats['total_suspicion_incidents']
            }
        
        return {
            'total_days': 0,
            'present_days': 0,
            'attendance_rate': 0,
            'avg_suspicion': 0,
            'total_suspicion_incidents': 0
        }
    
    # ==================== UTILITY METHODS ====================
    
    def close(self):
        """Close database connection"""
        self.client.close()
    
    def clear_all_data(self):
        """Clear all data (use with caution!)"""
        self.students.delete_many({})
        self.student_photos.delete_many({})
        self.attendance.delete_many({})
        self.suspicious_activity.delete_many({})
