// Mock API for demo/portfolio deployment

// Check if we're in demo mode
export const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true' || !import.meta.env.VITE_API_URL;

// Demo credentials
export const demoCredentials = {
  admin: {
    email: "admin@classroom.com",
    password: "admin123",
    name: "Admin User",
    role: "admin"
  },
  teacher: {
    email: "teacher@classroom.com",
    password: "teacher123",
    name: "Demo Teacher",
    role: "teacher"
  },
  student: {
    email: "student@classroom.com",
    password: "student123",
    name: "John Doe",
    role: "student",
    student_id: "STU001"
  }
};

export const mockStudents = [
  { 
    student_id: "STU001", 
    name: "John Doe", 
    email: "john@example.com", 
    phone: "+1234567890",
    photos: [],
    stats: { total_days: 30, present_days: 28, attendance_rate: 93.3 }
  },
  { 
    student_id: "STU002", 
    name: "Jane Smith", 
    email: "jane@example.com", 
    phone: "+1234567891",
    photos: [],
    stats: { total_days: 30, present_days: 30, attendance_rate: 100 }
  },
  { 
    student_id: "STU003", 
    name: "Mike Johnson", 
    email: "mike@example.com", 
    phone: "+1234567892",
    photos: [],
    stats: { total_days: 30, present_days: 25, attendance_rate: 83.3 }
  },
  { 
    student_id: "STU004", 
    name: "Sarah Williams", 
    email: "sarah@example.com", 
    phone: "+1234567893",
    photos: [],
    stats: { total_days: 30, present_days: 29, attendance_rate: 96.7 }
  },
  { 
    student_id: "STU005", 
    name: "David Brown", 
    email: "david@example.com", 
    phone: "+1234567894",
    photos: [],
    stats: { total_days: 30, present_days: 27, attendance_rate: 90 }
  },
];

export const mockAttendance = [
  { 
    student_id: "STU001", 
    name: "John Doe", 
    entry_time: "2024-01-16T09:00:00", 
    exit_time: "2024-01-16T15:30:00",
    status: "present",
    suspicion_score: 0
  },
  { 
    student_id: "STU002", 
    name: "Jane Smith", 
    entry_time: "2024-01-16T09:05:00", 
    exit_time: "2024-01-16T15:35:00",
    status: "present",
    suspicion_score: 0
  },
  { 
    student_id: "STU003", 
    name: "Mike Johnson", 
    entry_time: "2024-01-16T09:10:00", 
    exit_time: null,
    status: "present",
    suspicion_score: 0
  },
  { 
    student_id: "STU004", 
    name: "Sarah Williams", 
    entry_time: "2024-01-16T08:55:00", 
    exit_time: "2024-01-16T15:40:00",
    status: "present",
    suspicion_score: 0
  },
];

export const mockSuspiciousActivities = [
  {
    _id: "1",
    student_id: "STU003",
    student_name: "Mike Johnson",
    activity_type: "spoofing_attempt",
    description: "Liveness check failed. Suspected photo spoofing.",
    timestamp: "2024-01-15T10:30:00",
    resolved: false
  },
  {
    _id: "2",
    student_id: "UNKNOWN",
    student_name: "Unknown Person",
    activity_type: "unknown_person",
    description: "Unrecognized person detected in classroom.",
    timestamp: "2024-01-15T14:20:00",
    resolved: false
  },
];

export const mockStats = {
  total_students: 5,
  present_today: 4,
  absent_today: 1,
  attendance_rate: 80,
  suspicious_activities: 2,
  average_attendance_rate: 92.6
};

export const mockUser = {
  email: "teacher@classroom.com",
  name: "Demo Teacher",
  role: "teacher",
  is_active: true
};

export const mockUsers = [
  { 
    _id: "1", 
    email: "admin@classroom.com", 
    name: "Admin User", 
    role: "admin", 
    is_active: true 
  },
  { 
    _id: "2", 
    email: "teacher@classroom.com", 
    name: "Demo Teacher", 
    role: "teacher", 
    is_active: true 
  },
  { 
    _id: "3", 
    email: "student@classroom.com", 
    name: "John Doe", 
    role: "student", 
    is_active: true, 
    student_id: "STU001" 
  },
];

// Simulate API delay for realism
const delay = (ms: number = 300) => new Promise(resolve => setTimeout(resolve, ms));

export class MockApiService {
  async login(email: string, password: string) {
    await delay();
    
    // Check for specific demo credentials - ONLY allow these
    if (email === demoCredentials.admin.email && password === demoCredentials.admin.password) {
      return {
        access_token: "demo_token_admin_" + Date.now(),
        token_type: "bearer",
        user: {
          email: demoCredentials.admin.email,
          name: demoCredentials.admin.name,
          role: demoCredentials.admin.role,
          is_active: true
        }
      };
    }
    
    if (email === demoCredentials.teacher.email && password === demoCredentials.teacher.password) {
      return {
        access_token: "demo_token_teacher_" + Date.now(),
        token_type: "bearer",
        user: {
          email: demoCredentials.teacher.email,
          name: demoCredentials.teacher.name,
          role: demoCredentials.teacher.role,
          is_active: true
        }
      };
    }
    
    if (email === demoCredentials.student.email && password === demoCredentials.student.password) {
      return {
        access_token: "demo_token_student_" + Date.now(),
        token_type: "bearer",
        user: {
          email: demoCredentials.student.email,
          name: demoCredentials.student.name,
          role: demoCredentials.student.role,
          is_active: true,
          student_id: demoCredentials.student.student_id
        }
      };
    }
    
    // Reject any other credentials
    throw new Error("Invalid credentials. Please use the demo credentials provided.");
  }

  async getCurrentUser() {
    await delay();
    return { success: true, user: mockUser };
  }

  async getUserRole(userId: string) {
    await delay();
    return "teacher";
  }

  async getAllUsers() {
    await delay();
    return { success: true, data: mockUsers };
  }

  async getAllStudents() {
    await delay();
    return { success: true, data: mockStudents };
  }

  async getStudent(studentId: string) {
    await delay();
    const student = mockStudents.find(s => s.student_id === studentId);
    return { success: true, data: student || mockStudents[0] };
  }

  async createStudent(data: any) {
    await delay();
    return { success: true, message: "Student created successfully (demo)" };
  }

  async updateStudent(studentId: string, data: any) {
    await delay();
    return { success: true, message: "Student updated successfully (demo)" };
  }

  async deleteStudent(studentId: string) {
    await delay();
    return { success: true, message: "Student deleted successfully (demo)" };
  }

  async getTodayAttendance() {
    await delay();
    return { success: true, data: mockAttendance };
  }

  async getAttendanceByDate(date: string) {
    await delay();
    return { success: true, data: mockAttendance };
  }

  async getAttendanceByDateRange(startDate: string, endDate: string) {
    await delay();
    return { success: true, data: mockAttendance };
  }

  async getStudentAttendance(studentId: string, limit: number = 30) {
    await delay();
    return { success: true, data: mockAttendance.filter(a => a.student_id === studentId) };
  }

  async getAttendanceStats(startDate?: string, endDate?: string) {
    await delay();
    return { success: true, data: mockStats };
  }

  async getSuspiciousActivities(resolved: boolean = false) {
    await delay();
    return { 
      success: true, 
      data: mockSuspiciousActivities.filter(a => a.resolved === resolved) 
    };
  }

  async resolveSuspiciousActivity(activityId: string) {
    await delay();
    return { success: true, message: "Activity resolved (demo)" };
  }

  async startCamera() {
    await delay();
    return { success: true, message: "Camera started (demo mode - no actual camera)" };
  }

  async stopCamera() {
    await delay();
    return { success: true, message: "Camera stopped (demo)" };
  }

  async getCameraStatus() {
    await delay();
    return { success: true, data: { active: false, connected_clients: 0 } };
  }

  async registerUser(email: string, password: string, name: string, role: string) {
    await delay();
    return { success: true, message: "User registered successfully (demo)" };
  }

  async updateUserRole(userId: string, role: string) {
    await delay();
    return { success: true, message: "User role updated (demo)" };
  }

  async deleteUser(userId: string) {
    await delay();
    return { success: true, message: "User deleted (demo)" };
  }

  async getStudentPhotos(studentId: string) {
    await delay();
    return { success: true, data: [] };
  }

  connectCameraWebSocket(onMessage: any, onError?: any) {
    // Return a mock WebSocket
    return {
      close: () => {},
      send: () => {},
      onmessage: null,
      onerror: null,
      onclose: null
    };
  }
}
