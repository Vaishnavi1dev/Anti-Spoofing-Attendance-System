import { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { Camera, Users, AlertTriangle, BarChart3, Settings, LogOut, CalendarCheck, UserCog, ClipboardList } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

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
    <div className="min-h-screen flex bg-background">
      {/* Sidebar */}
      <aside className="w-64 bg-sidebar text-sidebar-foreground flex flex-col">
        <div className="p-6 border-b border-sidebar-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sidebar-primary rounded-lg flex items-center justify-center">
              <Camera className="w-6 h-6 text-sidebar-primary-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-lg">Smart Classroom</h1>
              <p className="text-xs text-sidebar-foreground/70">{user?.name}</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-sidebar-border">
          <Button
            variant="ghost"
            className="w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-sidebar-accent/50"
            onClick={logout}
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default DashboardLayout;
