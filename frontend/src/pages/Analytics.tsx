import DashboardLayout from "@/components/DashboardLayout";
import { GlassCard, GlassCardContent, GlassCardHeader, GlassCardTitle } from "@/components/ui/glass-card";
import { TrendingUp, Users, Clock, AlertTriangle } from "lucide-react";

const Analytics = () => {
  return (
    <DashboardLayout>
      <div className="p-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">Analytics & Reports</h1>
          <p className="text-muted-foreground">Track attendance trends and performance</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <GlassCard className="shadow-sm">
            <GlassCardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white/70">Attendance Rate</p>
                  <p className="text-3xl font-bold text-white">92%</p>
                  <p className="text-xs text-success flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    +5% from last week
                  </p>
                </div>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Users className="w-6 h-6 text-primary" />
                </div>
              </div>
            </GlassCardContent>
          </GlassCard>

          <GlassCard className="shadow-sm">
            <GlassCardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white/70">Avg Duration</p>
                  <p className="text-3xl font-bold text-white">2.5h</p>
                  <p className="text-xs text-white/70 mt-1">Per session</p>
                </div>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Clock className="w-6 h-6 text-primary" />
                </div>
              </div>
            </GlassCardContent>
          </GlassCard>

          <GlassCard className="shadow-sm">
            <GlassCardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white/70">Total Students</p>
                  <p className="text-3xl font-bold text-white">30</p>
                  <p className="text-xs text-white/70 mt-1">Registered</p>
                </div>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Users className="w-6 h-6 text-primary" />
                </div>
              </div>
            </GlassCardContent>
          </GlassCard>

          <GlassCard className="shadow-sm">
            <GlassCardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-white/70">Alerts</p>
                  <p className="text-3xl font-bold text-white">8</p>
                  <p className="text-xs text-warning flex items-center gap-1 mt-1">
                    <AlertTriangle className="w-3 h-3" />
                    2 pending
                  </p>
                </div>
                <div className="w-12 h-12 bg-warning-light rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-warning" />
                </div>
              </div>
            </GlassCardContent>
          </GlassCard>
        </div>

        {/* Charts Placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GlassCard className="shadow-md">
            <GlassCardHeader>
              <GlassCardTitle>Daily Attendance Trend</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              <div className="h-64 bg-black/20 rounded-lg flex items-center justify-center">
                <p className="text-white/70">Chart placeholder - Line chart</p>
              </div>
            </GlassCardContent>
          </GlassCard>

          <GlassCard className="shadow-md">
            <GlassCardHeader>
              <GlassCardTitle>Status Distribution</GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              <div className="h-64 bg-black/20 rounded-lg flex items-center justify-center">
                <p className="text-white/70">Chart placeholder - Pie chart</p>
              </div>
            </GlassCardContent>
          </GlassCard>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Analytics;
