import { UserRole } from "@/contexts/AuthContext";

const API_BASE_URL = "http://localhost:8000/api";

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

interface UserRoleResponse {
  user_id: string;
  role: UserRole;
}

class ApiService {
  private getAuthHeaders() {
    const token = localStorage.getItem("auth_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(error.detail || "Login failed");
    }

    return response.json();
  }

  async getUserRole(userId: string): Promise<UserRole> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}/role`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch user role");
    }

    const data: UserRoleResponse = await response.json();
    return data.role;
  }

  async getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch user info");
    }

    return response.json();
  }

  async updateUserRole(userId: string, role: UserRole): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}/role`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ role }),
    });

    if (!response.ok) {
      throw new Error("Failed to update user role");
    }
  }

  async registerUser(
    email: string,
    password: string,
    name: string,
    role: UserRole
  ): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ email, password, name, role }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Failed to register user" }));
      throw new Error(error.detail || "Failed to register user");
    }
  }

  async getAllUsers() {
    const response = await fetch(`${API_BASE_URL}/auth/users`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch users");
    }

    return response.json();
  }

  async deleteUser(userId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/users/${userId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to delete user");
    }
  }

  // Student Management
  async getAllStudents() {
    const response = await fetch(`${API_BASE_URL}/students`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch students");
    }

    return response.json();
  }

  async getStudent(studentId: string) {
    const response = await fetch(`${API_BASE_URL}/students/${studentId}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch student");
    }

    return response.json();
  }

  async createStudent(data: {
    student_id: string;
    name: string;
    email?: string;
    phone?: string;
  }) {
    const response = await fetch(`${API_BASE_URL}/students`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Failed to create student" }));
      throw new Error(error.detail || "Failed to create student");
    }

    return response.json();
  }

  async updateStudent(studentId: string, data: {
    name?: string;
    email?: string;
    phone?: string;
  }) {
    const response = await fetch(`${API_BASE_URL}/students/${studentId}`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error("Failed to update student");
    }

    return response.json();
  }

  async deleteStudent(studentId: string) {
    const response = await fetch(`${API_BASE_URL}/students/${studentId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to delete student");
    }

    return response.json();
  }

  async getStudentPhotos(studentId: string) {
    const response = await fetch(`${API_BASE_URL}/students/${studentId}/photos`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch photos");
    }

    return response.json();
  }

  async getTodayAttendance() {
    const response = await fetch(`${API_BASE_URL}/attendance/today`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch attendance");
    }

    return response.json();
  }

  async getAttendanceByDate(date: string) {
    const response = await fetch(`${API_BASE_URL}/attendance/date/${date}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch attendance");
    }

    return response.json();
  }

  async getAttendanceByDateRange(startDate: string, endDate: string) {
    const response = await fetch(`${API_BASE_URL}/attendance/range?start_date=${startDate}&end_date=${endDate}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch attendance");
    }

    return response.json();
  }

  async getStudentAttendance(studentId: string, limit: number = 30) {
    const response = await fetch(`${API_BASE_URL}/attendance/student/${studentId}?limit=${limit}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch student attendance");
    }

    return response.json();
  }

  async getAttendanceStats(startDate?: string, endDate?: string) {
    let url = `${API_BASE_URL}/stats`;
    if (startDate && endDate) {
      url += `?start_date=${startDate}&end_date=${endDate}`;
    }
    
    const response = await fetch(url, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch stats");
    }

    return response.json();
  }

  async getSuspiciousActivities(resolved: boolean = false) {
    const response = await fetch(`${API_BASE_URL}/suspicious?resolved=${resolved}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch suspicious activities");
    }

    return response.json();
  }

  async resolveSuspiciousActivity(activityId: string) {
    const response = await fetch(`${API_BASE_URL}/suspicious/resolve`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ activity_id: activityId }),
    });

    if (!response.ok) {
      throw new Error("Failed to resolve activity");
    }

    return response.json();
  }

  // Camera Management
  async startCamera() {
    const response = await fetch(`${API_BASE_URL}/camera/start`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to start camera");
    }

    return response.json();
  }

  async stopCamera() {
    const response = await fetch(`${API_BASE_URL}/camera/stop`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to stop camera");
    }

    return response.json();
  }

  async getCameraStatus() {
    const response = await fetch(`${API_BASE_URL}/camera/status`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error("Failed to get camera status");
    }

    return response.json();
  }

  // WebSocket connection for camera feed
  connectCameraWebSocket(onMessage: (data: any) => void, onError?: (error: any) => void) {
    const token = localStorage.getItem("auth_token");
    const wsUrl = `ws://localhost:8000/ws/camera?token=${token}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };
    
    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (onError) onError(error);
    };
    
    ws.onclose = () => {
      console.log("WebSocket connection closed");
    };
    
    return ws;
  }
}

export const apiService = new ApiService();
