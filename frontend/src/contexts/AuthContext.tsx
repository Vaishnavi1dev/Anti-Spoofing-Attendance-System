import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { apiService } from "@/services/api";

export type UserRole = "admin" | "teacher" | "student";

interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  studentId?: string; // Only for students
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string, role: UserRole) => Promise<void>;
  logout: () => void;
  hasRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem("auth_token");
    const userData = localStorage.getItem("user_data");
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const login = async (email: string, password: string, selectedRole: UserRole) => {
    try {
      // Attempt to login via backend API
      try {
        const loginResponse = await apiService.login(email, password);
        
        // Store token
        localStorage.setItem("auth_token", loginResponse.access_token);
        
        // Get user role from login response
        const backendRole = loginResponse.user.role;
        
        // Verify the user has the role they selected
        if (backendRole !== selectedRole) {
          throw new Error("You don't have permission to login as " + selectedRole);
        }
        
        const userData: User = {
          id: loginResponse.user.email, // Use email as ID since backend doesn't return _id in login
          email: loginResponse.user.email,
          name: loginResponse.user.name,
          role: backendRole,
          ...(selectedRole === "student" && loginResponse.user.student_id && { studentId: loginResponse.user.student_id }),
        };
        
        localStorage.setItem("user_data", JSON.stringify(userData));
        setUser(userData);
        
        // Redirect based on role
        if (userData.role === "student") {
          navigate("/my-attendance");
        } else {
          navigate("/dashboard");
        }
        return;
      } catch (apiError) {
        console.warn("Backend API not available, using mock login for demo");
        
        // Fallback to mock login for demo purposes
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Use the selected role for mock login
        const mockUser: User = {
          id: selectedRole === "admin" ? "1" : selectedRole === "teacher" ? "2" : "3",
          email,
          name: `${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)} User`,
          role: selectedRole,
          ...(selectedRole === "student" && { studentId: "STU001" }),
        };
        
        localStorage.setItem("auth_token", "mock_token");
        localStorage.setItem("user_data", JSON.stringify(mockUser));
        setUser(mockUser);
        
        // Redirect based on role
        if (mockUser.role === "student") {
          navigate("/my-attendance");
        } else {
          navigate("/dashboard");
        }
      }
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : "Login failed");
    }
  };

  const logout = () => {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user_data");
    setUser(null);
    navigate("/login");
  };

  const hasRole = (roles: UserRole[]) => {
    return user ? roles.includes(user.role) : false;
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
