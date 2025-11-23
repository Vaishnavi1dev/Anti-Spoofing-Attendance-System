# Backend Integration Guide

## Required Backend Endpoints for Authorization

Your backend should implement the following endpoints to support the role-based authorization system:

### Authentication Endpoints

#### POST /api/auth/login
Login and receive JWT token
```json
Request:
{
  "email": "user@example.com",
  "password": "your_password"
}

Response:
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

#### GET /api/auth/me
Get current authenticated user info
```json
Headers: Authorization: Bearer {token}

Response:
{
  "id": "user_id",
  "email": "user@example.com",
  "name": "User Name"
}
```

### User Role Management Endpoints

#### GET /api/auth/users/{user_id}/role
Get user's role (requires authentication)
```json
Headers: Authorization: Bearer {token}

Response:
{
  "user_id": "user_id",
  "role": "admin" | "teacher" | "student"
}
```

#### PUT /api/auth/users/{user_id}/role
Update user's role (admin only)
```json
Headers: Authorization: Bearer {token}

Request:
{
  "role": "admin" | "teacher" | "student"
}

Response: 200 OK
```

#### POST /api/auth/register
Register new user (admin only)
```json
Headers: Authorization: Bearer {token}

Request:
{
  "email": "newuser@example.com",
  "password": "your_password",
  "name": "New User",
  "role": "admin" | "teacher" | "student"
}

Response: 201 Created
```

#### GET /api/auth/users
Get all users (admin only)
```json
Headers: Authorization: Bearer {token}

Response:
[
  {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name",
    "role": "admin" | "teacher" | "student",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### DELETE /api/auth/users/{user_id}
Delete user (admin only)
```json
Headers: Authorization: Bearer {token}

Response: 204 No Content
```

## Database Schema Recommendations

### users table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_roles table
**CRITICAL**: Roles MUST be stored in a separate table for security
```sql
CREATE TYPE user_role AS ENUM ('admin', 'teacher', 'student');

CREATE TABLE user_roles (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role user_role NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role)
);
```

## Security Best Practices

1. **JWT Authentication**: Use secure JWT tokens with expiration
2. **Password Hashing**: Use bcrypt or similar for password storage
3. **Role Validation**: Always validate roles on the backend, never trust client-side role checks
4. **Separate Role Table**: Store roles in a dedicated table to prevent privilege escalation
5. **Admin-Only Endpoints**: Protect user management endpoints with admin role checks
6. **Token Refresh**: Implement token refresh mechanism for better security

## Frontend Integration

The frontend is configured to:
- Store JWT token in localStorage
- Automatically include token in all API requests
- Fall back to mock data if backend is unavailable (for demo purposes)
- Redirect users based on their role after login
- Protect routes based on user roles

To enable full backend integration, ensure your backend is running at `http://localhost:8000` or update the `API_BASE_URL` in `src/services/api.ts`.
