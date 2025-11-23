import { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Clock, TrendingUp } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { apiService } from "@/services/api";

const MyAttendance = () => {
  const { user } = useAuth();
  const [attendanceRecords, setAttendanceRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalClasses: 0,
    attended: 0,
    attendanceRate: 0,
    avgDuration: "0h 0m",
  });

  useEffect(() => {
    loadMyAttendance();
  }, []);

  const loadMyAttendance = async () => {
    try {
      setLoading(true);
      // Get current user's student attendance
      const response = await apiService.getStudentAttendance(user?.studentId || '', 30);
      const records = response.data || [];
      
      setAttendanceRecords(records);
      
      // Calculate stats
      const attended = records.filter((r: any) => r.status === 'present').length;
      const total = records.length;
      const rate = total > 0 ? Math.round((attended / total) * 100) : 0;
      
      setStats({
        totalClasses: total,
        attended: attended,
        attendanceRate: rate,
        avgDuration: "2h 15m", // TODO: Calculate from actual data
      });
    } catch (error) {
      console.error("Failed to load attendance:", error);
    } finally {
      setLoading(false);
    }
  };

  // Mock attendance data for the student (fallback)
  const mockAttendanceRecords = [
    {
      date: "2024-01-20",
      entry_time: "09:00 AM",
      exit_time: "11:30 AM",
      duration: "2h 30m",
      status: "present",
    },
    {
      date: "2024-01-19",
      entry_time: "09:05 AM",
      exit_time: "11:35 AM",
      duration: "2h 30m",
      status: "present",
    },
    {
      date: "2024-01-18",
      entry_time: "09:15 AM",
      exit_time: "11:20 AM",
      duration: "2h 5m",
      status: "late",
    },
    {
      date: "2024-01-17",
      entry_time: "-",
      exit_time: "-",
      duration: "-",
      status: "absent",
    },
  ];



  return (
    <DashboardLayout>
      <div className="p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">My Attendance</h1>
          <p className="text-muted-foreground">
            {user?.name} ({user?.studentId})
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Attendance Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">{stats.attendanceRate}%</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stats.attended} of {stats.totalClasses} classes
              </p>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Classes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalClasses}</div>
              <p className="text-xs text-muted-foreground mt-1">This semester</p>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Classes Attended
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-success">{stats.attended}</div>
              <p className="text-xs text-muted-foreground mt-1">Present</p>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg Duration
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgDuration}</div>
              <p className="text-xs text-muted-foreground mt-1">Per class</p>
            </CardContent>
          </Card>
        </div>

        {/* Attendance Records */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Attendance History</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">Loading...</div>
            ) : attendanceRecords.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">No attendance records found</div>
            ) : (
              <div className="space-y-4">
                {attendanceRecords.map((record, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 min-w-[120px]">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="font-medium">{record.date}</span>
                    </div>
                    
                    {record.status === "present" || record.status === "late" ? (
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>In: {record.entry_time}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          <span>Out: {record.exit_time}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <TrendingUp className="w-4 h-4" />
                          <span>{record.duration}</span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">No attendance recorded</span>
                    )}
                  </div>

                  <Badge
                    variant={
                      record.status === "present"
                        ? "default"
                        : record.status === "late"
                        ? "secondary"
                        : "destructive"
                    }
                  >
                    {record.status.toUpperCase()}
                  </Badge>
                </div>
              ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default MyAttendance;
