import { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { Camera, Users, AlertTriangle, BarChart3, Settings, LogOut, CalendarCheck, UserCog, ClipboardList } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { DotGridBackground } from "@/components/DotGridBackground";

interface DashboardLayoutProps {
  children: ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { user, logout, hasRole } = useAuth();

  const getNavItems = () => {
    if (hasRole(["student"])) {
      return [
        { icon: CalendarCheck, label: "My Attendance", path: "/my-attendance" },
        { icon: Settings, label: "Settings", path: "/settings" },
      ];
    }
    
    // Admin-only items
    if (hasRole(["admin"])) {
      return [
        { icon: Camera, label: "Live Monitor", path: "/dashboard" },
        { icon: Users, label: "Students", path: "/students" },
        { icon: ClipboardList, label: "Attendance", path: "/attendance" },
        { icon: AlertTriangle, label: "Suspicious", path: "/suspicious" },
        { icon: BarChart3, label: "Analytics", path: "/analytics" },
        { icon: UserCog, label: "User Management", path: "/user-management" },
        { icon: Settings, label: "Settings", path: "/settings" },
      ];
    }
    
    // Teacher nav items
    return [
      { icon: Camera, label: "Live Monitor", path: "/dashboard" },
      { icon: Users, label: "Students", path: "/students" },
      { icon: ClipboardList, label: "Attendance", path: "/attendance" },
      { icon: AlertTriangle, label: "Suspicious", path: "/suspicious" },
      { icon: BarChart3, label: "Analytics", path: "/analytics" },
      { icon: Settings, label: "Settings", path: "/settings" },
    ];
  };

  const navItems = getNavItems();

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* DotGrid Background */}
      <DotGridBackground />
      
      {/* Sidebar */}
      <aside className="relative z-20 w-64 bg-black/20 backdrop-blur-xl border-r border-white/5 text-white flex flex-col">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg shadow-purple-500/50">
              <Camera className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-white">Smart Classroom</h1>
              <p className="text-xs text-gray-300">{user?.name}</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? "bg-white/20 backdrop-blur-sm text-white shadow-lg"
                    : "text-gray-300 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-white/10">
          <Button
            variant="ghost"
            className="w-full justify-start text-gray-300 hover:text-white hover:bg-white/10"
            onClick={logout}
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="relative z-20 flex-1 overflow-auto">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
