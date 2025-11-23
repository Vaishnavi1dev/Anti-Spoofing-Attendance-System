import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Camera, Database, Cpu, Save } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const Settings = () => {
  const [suspicionThreshold, setSuspicionThreshold] = useState([10]);
  const [recognitionInterval, setRecognitionInterval] = useState([30]);
  const [challengeTimeout, setChallengeTimeout] = useState([15]);
  const [absenceTimeout, setAbsenceTimeout] = useState([10]);

  const handleSave = () => {
    toast.success("Settings saved successfully");
  };

  return (
    <DashboardLayout>
      <div className="p-8 max-w-4xl">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">System Settings</h1>
          <p className="text-muted-foreground">Configure detection and monitoring parameters</p>
        </div>

        {/* System Status */}
        <Card className="mb-6 shadow-md">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center justify-between p-3 bg-success-light rounded-lg">
                <div className="flex items-center gap-3">
                  <Camera className="w-5 h-5 text-success" />
                  <span className="font-medium">Camera</span>
                </div>
                <Badge className="bg-success text-success-foreground">Online</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-success-light rounded-lg">
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-success" />
                  <span className="font-medium">Database</span>
                </div>
                <Badge className="bg-success text-success-foreground">Connected</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-success-light rounded-lg">
                <div className="flex items-center gap-3">
                  <Cpu className="w-5 h-5 text-success" />
                  <span className="font-medium">AI Model</span>
                </div>
                <Badge className="bg-success text-success-foreground">Ready</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detection Settings */}
        <Card className="mb-6 shadow-md">
          <CardHeader>
            <CardTitle>Detection Parameters</CardTitle>
            <CardDescription>Adjust sensitivity and timing for face recognition</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Suspicion Threshold</Label>
                <span className="text-sm font-medium">{suspicionThreshold[0]}</span>
              </div>
              <Slider
                value={suspicionThreshold}
                onValueChange={setSuspicionThreshold}
                min={5}
                max={20}
                step={1}
                className="mb-1"
              />
              <p className="text-xs text-muted-foreground">
                Higher values require more suspicious behavior before triggering alerts
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Recognition Interval (frames)</Label>
                <span className="text-sm font-medium">{recognitionInterval[0]}</span>
              </div>
              <Slider
                value={recognitionInterval}
                onValueChange={setRecognitionInterval}
                min={10}
                max={60}
                step={5}
                className="mb-1"
              />
              <p className="text-xs text-muted-foreground">
                Frames between face recognition checks (lower = more frequent)
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Challenge Timeout (seconds)</Label>
                <span className="text-sm font-medium">{challengeTimeout[0]}</span>
              </div>
              <Slider
                value={challengeTimeout}
                onValueChange={setChallengeTimeout}
                min={5}
                max={30}
                step={5}
                className="mb-1"
              />
              <p className="text-xs text-muted-foreground">
                Time given to respond to liveness challenges
              </p>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>Absence Timeout (seconds)</Label>
                <span className="text-sm font-medium">{absenceTimeout[0]}</span>
              </div>
              <Slider
                value={absenceTimeout}
                onValueChange={setAbsenceTimeout}
                min={5}
                max={30}
                step={5}
                className="mb-1"
              />
              <p className="text-xs text-muted-foreground">
                Time before marking student as absent after losing face detection
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button onClick={handleSave} size="lg">
            <Save className="w-4 h-4 mr-2" />
            Save Settings
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;
