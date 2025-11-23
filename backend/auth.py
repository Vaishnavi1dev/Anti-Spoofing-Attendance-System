"""
Authentication module for Smart Classroom Attendance System
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from pydantic import BaseModel

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    role: str = "teacher"  # teacher, admin, student

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    email: str
    name: str
    role: str
    is_active: bool = True
    created_at: datetime

# Password utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data

# User database operations (using MongoDB)
class UserManager:
    def __init__(self, db):
        self.db = db
        self.users = db.db.users
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for users collection"""
        self.users.create_index([("email", 1)], unique=True)
    
    def create_user(self, user_data: UserCreate):
        """Create a new user"""
        # Check if user exists
        if self.users.find_one({"email": user_data.email}):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "name": user_data.name,
            "role": user_data.role,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        # Insert user
        result = self.users.insert_one(user_doc)
        
        # Return user without password
        user_doc.pop("hashed_password")
        user_doc["_id"] = str(result.inserted_id)
        return user_doc
    
    def authenticate_user(self, email: str, password: str):
        """Authenticate user with email and password (admin/teacher)"""
        user = self.users.find_one({"email": email})
        if not user:
            return False
        if not verify_password(password, user["hashed_password"]):
            return False
        return user
    
    def authenticate_student(self, email: str, password: str, db):
        """Authenticate student with email and password"""
        student = db.students.find_one({"email": email})
        if not student or not student.get("password"):
            return False
        if not verify_password(password, student["password"]):
            return False
        # Return user-like object for consistency
        return {
            "email": student["email"],
            "name": student["name"],
            "role": "student",
            "student_id": student["student_id"],
            "is_active": True
        }
    
    def get_user_by_email(self, email: str):
        """Get user by email"""
        user = self.users.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
            user.pop("hashed_password", None)
        return user
    
    def get_all_users(self):
        """Get all users (admin only)"""
        users = list(self.users.find({}, {"hashed_password": 0}))
        for user in users:
            user["_id"] = str(user["_id"])
        return users
    
    def update_user(self, email: str, update_data: dict):
        """Update user data"""
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        result = self.users.update_one(
            {"email": email},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def delete_user(self, email: str):
        """Delete user"""
        result = self.users.delete_one({"email": email})
        return result.deleted_count > 0

# Dependency to get current user
def get_current_user(token_data: TokenData = Depends(verify_token), user_manager: UserManager = None):
    """Get current authenticated user"""
    if not user_manager:
        raise HTTPException(status_code=500, detail="User manager not initialized")
    
    user = user_manager.get_user_by_email(token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# Role-based access control
def get_current_user_with_manager(user_manager: UserManager):
    """Create a dependency that gets current user with the provided user_manager"""
    def _get_current_user(token_data: TokenData = Depends(verify_token)):
        return get_current_user(token_data, user_manager)
    return _get_current_user

def require_role(required_role: str, user_manager: UserManager):
    """Decorator to require specific role"""
    def role_checker(current_user: dict = Depends(get_current_user_with_manager(user_manager))):
        if current_user["role"] != required_role and current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker

# Convenience functions - these need to be called with user_manager
def require_teacher(user_manager: UserManager):
    return require_role("teacher", user_manager)

def require_admin(user_manager: UserManager):
    return require_role("admin", user_manager)