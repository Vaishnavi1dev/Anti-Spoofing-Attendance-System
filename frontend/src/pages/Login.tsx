import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Camera, Copy, Check } from "lucide-react";
import { useAuth, UserRole } from "@/contexts/AuthContext";
import { isDemoMode, demoCredentials } from "@/services/mockApi";
import { DotGridBackground } from "@/components/DotGridBackground";

const Login = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password, role);
      toast.success("Login successful!");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Login failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = (demoRole: 'admin' | 'teacher' | 'student') => {
    const creds = demoCredentials[demoRole];
    setEmail(creds.email);
    setPassword(creds.password);
    setRole(creds.role as UserRole);
    toast.success(`Demo credentials loaded for ${demoRole}`);
  };

  const copyToClipboard = (text: string, field: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
    toast.success("Copied to clipboard!");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* DotGrid Background */}
      <DotGridBackground />
      
      {/* Content */}
      <div className="relative z-20 w-full max-w-6xl flex flex-col lg:flex-row gap-8">
        {/* Login Card */}
        <Card className="w-full lg:w-1/2 shadow-2xl bg-black/20 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-all duration-300">
          <CardHeader className="space-y-6 text-center pb-8">
            <div className="mx-auto w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/50 transform hover:scale-110 transition-transform duration-300">
              <Camera className="w-10 h-10 text-white" />
            </div>
            <div>
              <CardTitle className="text-3xl font-bold text-white drop-shadow-2xl bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Smart Classroom
              </CardTitle>
              <CardDescription className="text-gray-300 text-base mt-2">
                AI-Powered Attendance System
              </CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleLogin} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="role" className="text-white font-semibold text-sm">Login As</Label>
                <Select value={role} onValueChange={(value: UserRole) => setRole(value)}>
                  <SelectTrigger id="role" className="bg-white/5 backdrop-blur-sm border-white/10 text-white h-12 hover:bg-white/10 transition-all">
                    <SelectValue placeholder="Select your role" />
                  </SelectTrigger>
                  <SelectContent className="bg-black/95 backdrop-blur-2xl border-white/20">
                    <SelectItem value="student" className="text-white hover:bg-white/10 focus:bg-white/10">👨‍🎓 Student</SelectItem>
                    <SelectItem value="teacher" className="text-white hover:bg-white/10 focus:bg-white/10">👨‍🏫 Teacher</SelectItem>
                    <SelectItem value="admin" className="text-white hover:bg-white/10 focus:bg-white/10">👨‍💼 Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="email" className="text-white font-semibold text-sm">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your.email@classroom.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="bg-white/5 backdrop-blur-sm border-white/10 text-white placeholder:text-gray-500 h-12 hover:bg-white/10 focus:bg-white/10 transition-all"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-white font-semibold text-sm">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="bg-white/5 backdrop-blur-sm border-white/10 text-white placeholder:text-gray-500 h-12 hover:bg-white/10 focus:bg-white/10 transition-all"
                />
              </div>
              <Button 
                type="submit" 
                className="w-full h-12 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 transition-all duration-300 transform hover:scale-[1.02]" 
                disabled={isLoading}
              >
                {isLoading ? "Signing in..." : "Sign In"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Demo Credentials Card */}
        {isDemoMode && (
          <Card className="w-full lg:w-1/2 shadow-2xl border-2 border-purple-500/20 bg-black/20 backdrop-blur-xl hover:border-purple-500/40 transition-all duration-300">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl text-white drop-shadow-lg flex items-center gap-2">
                <span className="text-3xl">🎨</span>
                Demo Credentials
              </CardTitle>
              <CardDescription className="text-gray-300 text-base">
                Click any card to auto-fill and explore different roles
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Admin */}
              <div 
                className="group p-5 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/10 backdrop-blur-md border border-purple-400/30 cursor-pointer hover:border-purple-400/60 hover:from-purple-500/30 hover:to-purple-600/20 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-xl hover:shadow-purple-500/20"
                onClick={() => handleDemoLogin('admin')}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-bold text-purple-300 drop-shadow text-lg flex items-center gap-2">
                    <span className="text-2xl">👨‍💼</span>
                    Admin
                  </span>
                  <span className="text-xs text-gray-300 bg-purple-500/20 px-3 py-1 rounded-full">Full Access</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/90">{demoCredentials.admin.email}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 text-white hover:bg-white/20 transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(demoCredentials.admin.email, 'admin-email');
                      }}
                    >
                      {copiedField === 'admin-email' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/90">{demoCredentials.admin.password}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 text-white hover:bg-white/20 transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(demoCredentials.admin.password, 'admin-pass');
                      }}
                    >
                      {copiedField === 'admin-pass' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Teacher */}
              <div 
                className="group p-5 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/10 backdrop-blur-md border border-blue-400/30 cursor-pointer hover:border-blue-400/60 hover:from-blue-500/30 hover:to-blue-600/20 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-xl hover:shadow-blue-500/20"
                onClick={() => handleDemoLogin('teacher')}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-bold text-blue-300 drop-shadow text-lg flex items-center gap-2">
                    <span className="text-2xl">👨‍🏫</span>
                    Teacher
                  </span>
                  <span className="text-xs text-gray-300 bg-blue-500/20 px-3 py-1 rounded-full">Management</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/90">{demoCredentials.teacher.email}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 text-white hover:bg-white/20 transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(demoCredentials.teacher.email, 'teacher-email');
                      }}
                    >
                      {copiedField === 'teacher-email' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/90">{demoCredentials.teacher.password}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 text-white hover:bg-white/20 transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(demoCredentials.teacher.password, 'teacher-pass');
                      }}
                    >
                      {copiedField === 'teacher-pass' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
              </div>

              {/* Student */}
              <div 
                className="group p-5 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/10 backdrop-blur-md border border-green-400/30 cursor-pointer hover:border-green-400/60 hover:from-green-500/30 hover:to-green-600/20 transition-all duration-300 transform hover:scale-[1.02] hover:shadow-xl hover:shadow-green-500/20"
                onClick={() => handleDemoLogin('student')}
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="font-bold text-green-300 drop-shadow text-lg flex items-center gap-2">
                    <span className="text-2xl">👨‍🎓</span>
                    Student
                  </span>
                  <span className="text-xs text-gray-300 bg-green-500/20 px-3 py-1 rounded-full">Personal View</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/90">{demoCredentials.student.email}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 text-white hover:bg-white/20 transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(demoCredentials.student.email, 'student-email');
                      }}
                    >
                      {copiedField === 'student-email' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm text-white/90">{demoCredentials.student.password}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100 text-white hover:bg-white/20 transition-all"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(demoCredentials.student.password, 'student-pass');
                      }}
                    >
                      {copiedField === 'student-pass' ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
              </div>

              <div className="pt-3 text-sm text-gray-300 text-center flex items-center justify-center gap-2">
                <span className="text-xl">💡</span>
                <span>Click any card to auto-fill credentials</span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Login;
