import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, Eye, User, Clock } from "lucide-react";

const Suspicious = () => {
  // Mock suspicious activities
  const activities = [
    {
      id: 1,
      studentId: "STU001",
      name: "John Doe",
      timestamp: "2024-01-20 09:15:00",
      type: "static_behavior",
      description: "No movement detected for 30 seconds",
      resolved: false,
    },
    {
      id: 2,
      studentId: "STU005",
      name: "Unknown",
      timestamp: "2024-01-20 09:10:00",
      type: "unknown_face",
      description: "Unregistered face detected at desk 12",
      resolved: false,
    },
    {
      id: 3,
      studentId: "STU003",
      name: "Michael Johnson",
      timestamp: "2024-01-20 09:05:00",
      type: "spoofing_attempt",
      description: "Possible photo spoofing detected",
      resolved: true,
    },
  ];

  return (
    <DashboardLayout>
      <div className="p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">Suspicious Activity Log</h1>
          <p className="text-muted-foreground">Monitor and resolve security alerts</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Pending</p>
                  <p className="text-3xl font-bold text-danger">2</p>
                </div>
                <div className="w-12 h-12 bg-danger-light rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-danger" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Resolved</p>
                  <p className="text-3xl font-bold text-success">1</p>
                </div>
                <div className="w-12 h-12 bg-success-light rounded-full flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-success" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Activities List */}
        <Card className="shadow-md">
          <CardHeader>
            <CardTitle>Activity Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className={`p-4 rounded-lg border ${
                    activity.resolved
                      ? "border-success/20 bg-success-light"
                      : "border-danger/20 bg-danger-light"
                  }`}
                >
                  <div className="flex items-start gap-4">
                    {/* Avatar */}
                    <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center flex-shrink-0">
                      <User className="w-6 h-6 text-muted-foreground" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <div>
                          <h3 className="font-semibold">{activity.name}</h3>
                          <p className="text-sm text-muted-foreground">{activity.studentId}</p>
                        </div>
                        <Badge variant={activity.resolved ? "default" : "destructive"}>
                          {activity.resolved ? "Resolved" : "Pending"}
                        </Badge>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm">
                          <span className="font-medium">Type: </span>
                          {activity.type.replace(/_/g, " ").toUpperCase()}
                        </p>
                        <p className="text-sm">{activity.description}</p>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="w-4 h-4" />
                          <span>{activity.timestamp}</span>
                        </div>
                      </div>

                      {/* Actions */}
                      {!activity.resolved && (
                        <div className="flex gap-2 mt-4">
                          <Button size="sm" variant="success">
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Resolve
                          </Button>
                          <Button size="sm" variant="outline">
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Suspicious;
