import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Plus, Search, User, Mail, Phone, Image, Upload as UploadIcon, Trash2 } from "lucide-react";
import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiService } from "@/services/api";
import { PhotoUpload } from "@/components/PhotoUpload";
import { StudentPhotoUploader } from "@/components/StudentPhotoUploader";
import { toast } from "sonner";

interface Student {
  student_id: string;
  name: string;
  email?: string;
  phone?: string;
  photoCount?: number;
}

const Students = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [newStudent, setNewStudent] = useState({
    student_id: "",
    name: "",
    email: "",
    phone: "",
  });
  const { hasRole } = useAuth();
  
  const canEdit = hasRole(["admin", "teacher"]);

  // Fetch students from API
  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await apiService.getAllStudents();
      if (response.success) {
        // Fetch photos for each student
        const studentsWithPhotos = await Promise.all(
          (response.data || []).map(async (student: Student) => {
            try {
              const photosResponse = await apiService.getStudentPhotos(student.student_id);
              return {
                ...student,
                photoCount: photosResponse.data?.length || 0
              };
            } catch {
              return { ...student, photoCount: 0 };
            }
          })
        );
        setStudents(studentsWithPhotos);
      }
    } catch (error) {
      toast.error("Failed to load students");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = async () => {
    // Validate required fields
    if (!newStudent.student_id || !newStudent.name) {
      toast.error("Student ID and Name are required");
      return;
    }

    setIsSubmitting(true);
    try {
      console.log("Adding student:", newStudent);
      
      // Step 1: Create student
      await apiService.createStudent(newStudent);
      
      // Step 2: Upload photos if any
      const tempPhotos = (window as any).tempStudentPhotos || [];
      if (tempPhotos.length > 0) {
        toast.info(`Uploading ${tempPhotos.length} photo(s)...`);
        
        let uploadedCount = 0;
        for (const photo of tempPhotos) {
          try {
            const formData = new FormData();
            formData.append('file', photo.file);
            formData.append('photo_type', photo.type);
            formData.append('description', `${photo.type} photo`);

            const token = localStorage.getItem('auth_token');
            const response = await fetch(
              `http://localhost:8000/api/students/${newStudent.student_id}/photos`,
              {
                method: 'POST',
                headers: {
                  Authorization: `Bearer ${token}`,
                },
                body: formData,
              }
            );

            if (response.ok) {
              uploadedCount++;
            }
          } catch (error) {
            console.error("Photo upload error:", error);
          }
        }
        
        toast.success(`Student added with ${uploadedCount} photo(s)!`);
      } else {
        toast.success("Student added successfully!");
      }
      
      // Clear temp photos
      delete (window as any).tempStudentPhotos;
      
      setShowAddDialog(false);
      setNewStudent({ student_id: "", name: "", email: "", phone: "" });
      fetchStudents();
    } catch (error: any) {
      console.error("Add student error:", error);
      toast.error(error.message || "Failed to add student");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePhotoUploadSuccess = () => {
    toast.success("Photo uploaded!");
    fetchStudents();
  };

  const handleDeleteStudent = async (studentId: string, studentName: string) => {
    if (!confirm(`Are you sure you want to delete ${studentName}? This will also delete all their photos and attendance records.`)) {
      return;
    }

    try {
      await apiService.deleteStudent(studentId);
      toast.success(`${studentName} deleted successfully`);
      fetchStudents();
    } catch (error: any) {
      toast.error(error.message || "Failed to delete student");
    }
  };

  const filteredStudents = students.filter((student) =>
    student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.student_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    student.email?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <DashboardLayout>
      <div className="p-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">Student Management</h1>
            <p className="text-muted-foreground">
              {canEdit ? "Manage student profiles and photos" : "View student profiles"}
            </p>
          </div>
          {canEdit && (
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Add Student
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-3xl max-h-[95vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Add New Student</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  {/* Student Details */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="student_id">
                        Student ID <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="student_id"
                        placeholder="STU001"
                        value={newStudent.student_id}
                        onChange={(e) => setNewStudent({ ...newStudent, student_id: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="name">
                        Full Name <span className="text-red-500">*</span>
                      </Label>
                      <Input
                        id="name"
                        placeholder="John Doe"
                        value={newStudent.name}
                        onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="email">Email (Optional)</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="john@school.com"
                        value={newStudent.email}
                        onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="phone">Phone (Optional)</Label>
                      <Input
                        id="phone"
                        placeholder="+1234567890"
                        value={newStudent.phone}
                        onChange={(e) => setNewStudent({ ...newStudent, phone: e.target.value })}
                      />
                    </div>
                  </div>

                  {/* Photo Upload Section */}
                  <div className="border-t pt-4 mt-4">
                    <div className="bg-blue-50 p-3 rounded-lg mb-3">
                      <Label className="text-base font-semibold mb-2 block">
                        📸 Student Photos (Optional)
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Upload at least 1 photo for face recognition. More photos (up to 5) improve accuracy.
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        💡 Tip: Different angles and lighting conditions help the system recognize students better
                      </p>
                    </div>
                    <StudentPhotoUploader 
                      onPhotosChange={(photos) => {
                        // Store photos temporarily
                        (window as any).tempStudentPhotos = photos;
                        console.log('Photos updated:', photos.length);
                      }}
                    />
                  </div>

                  <Button 
                    onClick={handleAddStudent} 
                    className="w-full"
                    disabled={isSubmitting || !newStudent.student_id || !newStudent.name}
                  >
                    {isSubmitting ? "Adding..." : "Add Student"}
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          )}
        </div>

        {/* Search Bar */}
        <Card className="mb-6 shadow-sm">
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search students by name, ID, or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Students Grid */}
        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading students...</p>
          </div>
        ) : filteredStudents.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No students found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {filteredStudents.map((student) => (
              <Card key={student.student_id} className="shadow-md hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center text-center">
                    {/* Avatar */}
                    <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                      <User className="w-10 h-10 text-primary" />
                    </div>

                    {/* Student Info */}
                    <h3 className="font-semibold text-lg mb-1">{student.name}</h3>
                    <Badge variant="secondary" className="mb-3">
                      {student.student_id}
                    </Badge>

                    <div className="w-full space-y-2 text-sm text-muted-foreground mb-4">
                      {student.email && (
                        <div className="flex items-center justify-center gap-2">
                          <Mail className="w-4 h-4" />
                          <span className="truncate">{student.email}</span>
                        </div>
                      )}
                      {student.phone && (
                        <div className="flex items-center justify-center gap-2">
                          <Phone className="w-4 h-4" />
                          <span>{student.phone}</span>
                        </div>
                      )}
                      <div className="flex items-center justify-center gap-2">
                        <Image className="w-4 h-4" />
                        <span>{student.photoCount || 0} photos</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="w-full space-y-2">
                      <div className="flex gap-2">
                        {canEdit && (
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button 
                                variant="outline" 
                                size="sm" 
                                className="flex-1"
                                onClick={() => setSelectedStudent(student)}
                              >
                                <UploadIcon className="w-4 h-4 mr-1" />
                                Photos
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-2xl">
                              <DialogHeader>
                                <DialogTitle>Upload Photos for {student.name}</DialogTitle>
                              </DialogHeader>
                              <PhotoUpload 
                                studentId={student.student_id}
                                onUploadSuccess={handlePhotoUploadSuccess}
                              />
                            </DialogContent>
                          </Dialog>
                        )}
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="flex-1"
                          onClick={() => {
                            setSelectedStudent(student);
                            setShowViewDialog(true);
                          }}
                        >
                          View
                        </Button>
                      </div>
                      {canEdit && (
                        <Button 
                          variant="destructive" 
                          size="sm" 
                          className="w-full"
                          onClick={() => handleDeleteStudent(student.student_id, student.name)}
                        >
                          <Trash2 className="w-4 h-4 mr-1" />
                          Delete
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* View Student Dialog */}
        {selectedStudent && (
          <Dialog open={showViewDialog} onOpenChange={setShowViewDialog}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Student Details</DialogTitle>
              </DialogHeader>
              <div className="space-y-6">
                {/* Student Info */}
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
                    <User className="w-10 h-10 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold">{selectedStudent.name}</h3>
                    <Badge variant="secondary">{selectedStudent.student_id}</Badge>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Email</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Mail className="w-4 h-4 text-muted-foreground" />
                      <span>{selectedStudent.email || 'Not provided'}</span>
                    </div>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Phone</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Phone className="w-4 h-4 text-muted-foreground" />
                      <span>{selectedStudent.phone || 'Not provided'}</span>
                    </div>
                  </div>
                </div>

                {/* Photos */}
                <div>
                  <Label className="text-sm font-medium text-muted-foreground mb-2 block">
                    Photos ({selectedStudent.photoCount || 0})
                  </Label>
                  <div className="flex items-center gap-2 p-4 border rounded-lg">
                    <Image className="w-5 h-5 text-muted-foreground" />
                    <span className="text-sm">
                      {selectedStudent.photoCount || 0} photo(s) uploaded for face recognition
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-4 border-t">
                  {canEdit && (
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" className="flex-1">
                          <UploadIcon className="w-4 h-4 mr-2" />
                          Upload Photos
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Upload Photos for {selectedStudent.name}</DialogTitle>
                        </DialogHeader>
                        <PhotoUpload 
                          studentId={selectedStudent.student_id}
                          onUploadSuccess={() => {
                            handlePhotoUploadSuccess();
                            setShowViewDialog(false);
                          }}
                        />
                      </DialogContent>
                    </Dialog>
                  )}
                  <Button 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => setShowViewDialog(false)}
                  >
                    Close
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Students;
