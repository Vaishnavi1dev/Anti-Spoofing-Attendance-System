import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, Square, Save, Camera, AlertTriangle, CheckCircle2, Clock } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { apiService } from "@/services/api";
import { CameraFeed } from "@/components/CameraFeed";

interface AttendanceRecord {
  student_id: string;
  name: string;
  entry_time: string;
  exit_time?: string;
  status: string;
  suspicion_score: number;
}

interface SuspiciousActivity {
  activity_id: string;
  student_id: string;
  name: string;
  timestamp: string;
  activity_type: string;
  description: string;
  resolved: boolean;
}

const Dashboard = () => {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([]);
  const [suspiciousActivities, setSuspiciousActivities] = useState<SuspiciousActivity[]>([]);
  const [stats, setStats] = useState({
    present: 0,
    suspicious: 0,
    total: 0
  });

  // Load data on mount and refresh every 30 seconds
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      // Load today's attendance
      const attendanceResponse = await apiService.getTodayAttendance();
      const attendanceData = attendanceResponse.data || [];
      setAttendance(attendanceData);

      // Load suspicious activities
      const suspiciousResponse = await apiService.getSuspiciousActivities();
      const suspiciousData = suspiciousResponse.data || [];
      setSuspiciousActivities(suspiciousData.filter((a: SuspiciousActivity) => !a.resolved).slice(0, 5));

      // Calculate stats
      const presentCount = attendanceData.filter((a: AttendanceRecord) => a.status === 'present').length;
      const suspiciousCount = suspiciousData.filter((a: SuspiciousActivity) => !a.resolved).length;
      
      setStats({
        present: presentCount,
        suspicious: suspiciousCount,
        total: attendanceData.length
      });
    } catch (error) {
      console.error("Failed to load data:", error);
    }
  };

  const handleStartMonitoring = async () => {
    setIsMonitoring(true);
    toast.success("Camera started - Monitoring active");

    // Start backend monitoring (optional)
    try {
      await apiService.startCamera();
    } catch (error) {
      console.warn("Backend monitoring not available:", error);
    }
  };

  const handleStopMonitoring = async () => {
    setIsMonitoring(false);
    toast.info("Monitoring stopped");

    // Stop backend monitoring
    try {
      await apiService.stopCamera();
    } catch (error) {
      console.warn("Backend stop failed:", error);
    }
  };

  const handleCameraError = (error: string) => {
    toast.error(error);
    setIsMonitoring(false);
  };

  const handleSaveReport = async () => {
    try {
      const attendance = await apiService.getTodayAttendance();
      toast.success("Attendance report saved");
      console.log("Attendance data:", attendance);
    } catch (error) {
      toast.error("Failed to save report");
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return time.toLocaleDateString();
  };

  return (
    <DashboardLayout>
      <div className="p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">Live Monitoring</h1>
          <p className="text-muted-foreground">Real-time classroom attendance tracking</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Present</p>
                  <p className="text-3xl font-bold text-success">{stats.present}</p>
                </div>
                <div className="w-12 h-12 bg-success-light rounded-full flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Suspicious</p>
                  <p className="text-3xl font-bold text-warning">{stats.suspicious}</p>
                </div>
                <div className="w-12 h-12 bg-warning-light rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-warning" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total</p>
                  <p className="text-3xl font-bold text-primary">{stats.total}</p>
                </div>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Camera className="w-6 h-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Camera Feed */}
          <div className="lg:col-span-2">
            <Card className="shadow-md">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Camera className="w-5 h-5" />
                    Camera Feed
                  </CardTitle>
                  <Badge variant={isMonitoring ? "default" : "secondary"}>
                    {isMonitoring ? "Live" : "Stopped"}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="aspect-video bg-black rounded-lg relative overflow-hidden">
                  <CameraFeed isActive={isMonitoring} onError={handleCameraError} />
                </div>

                <div className="flex gap-2 mt-4">
                  {!isMonitoring ? (
                    <Button onClick={handleStartMonitoring} className="flex-1" variant="success">
                      <Play className="w-4 h-4 mr-2" />
                      Start Monitoring
                    </Button>
                  ) : (
                    <Button onClick={handleStopMonitoring} className="flex-1" variant="danger">
                      <Square className="w-4 h-4 mr-2" />
                      Stop Monitoring
                    </Button>
                  )}
                  <Button onClick={handleSaveReport} variant="outline">
                    <Save className="w-4 h-4 mr-2" />
                    Save Report
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Alerts Panel */}
          <div className="lg:col-span-1">
            <Card className="shadow-md h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Live Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-[500px] overflow-y-auto">
                  {suspiciousActivities.length === 0 ? (
                    <div className="text-center py-8">
                      <CheckCircle2 className="w-12 h-12 text-success mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground">No suspicious activities</p>
                      <p className="text-xs text-muted-foreground">All clear!</p>
                    </div>
                  ) : (
                    suspiciousActivities.map((activity) => (
                      <div 
                        key={activity.activity_id} 
                        className="p-3 border border-warning/20 bg-warning-light rounded-lg"
                      >
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-warning/20 rounded-full flex items-center justify-center flex-shrink-0">
                            <AlertTriangle className="w-5 h-5 text-warning" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-sm capitalize">
                              {activity.activity_type.replace(/_/g, ' ')}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {activity.name}: {activity.description}
                            </p>
                            <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                              <Clock className="w-3 h-3" />
                              <span>{formatTimeAgo(activity.timestamp)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}

                  {/* Recent attendance entries */}
                  {attendance.slice(0, 3).map((record) => (
                    <div 
                      key={record.student_id} 
                      className="p-3 border border-success/20 bg-success-light rounded-lg"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 bg-success/20 rounded-full flex items-center justify-center flex-shrink-0">
                          <CheckCircle2 className="w-5 h-5 text-success" />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">Verified</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {record.name} marked present
                          </p>
                          <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                            <Clock className="w-3 h-3" />
                            <span>{formatTimeAgo(record.entry_time)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
