import { useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

interface PhotoUploadProps {
  studentId: string;
  onUploadSuccess: () => void;
}

export function PhotoUpload({ studentId, onUploadSuccess }: PhotoUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [photoType, setPhotoType] = useState('front');
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const photoTypes = [
    { value: 'front', label: 'Front View' },
    { value: 'left', label: 'Left Profile' },
    { value: 'right', label: 'Right Profile' },
    { value: 'with_glasses', label: 'With Glasses' },
    { value: 'without_glasses', label: 'Without Glasses' },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        toast.error('File size must be less than 5MB');
        return;
      }
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      if (droppedFile.size > 5 * 1024 * 1024) {
        toast.error('File size must be less than 5MB');
        return;
      }
      setFile(droppedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(droppedFile);
    } else {
      toast.error('Please drop an image file');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('photo_type', photoType);
    formData.append('description', `${photoType} photo`);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(
        `http://localhost:8000/api/students/${studentId}/photos`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (response.ok) {
        toast.success('Photo uploaded successfully!');
        setFile(null);
        setPreview(null);
        onUploadSuccess();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Upload failed!');
      }
    } catch (error) {
      toast.error('Upload error! Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <CardContent className="pt-6 space-y-4">
        {/* Photo Type Dropdown */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Photo Type
          </label>
          <Select value={photoType} onValueChange={setPhotoType}>
            <SelectTrigger>
              <SelectValue placeholder="Select photo type" />
            </SelectTrigger>
            <SelectContent>
              {photoTypes.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
          className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer"
        >
          {preview ? (
            <div className="relative">
              <img
                src={preview}
                alt="Preview"
                className="max-h-64 mx-auto rounded-lg"
              />
              <Button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                }}
                variant="destructive"
                size="icon"
                className="absolute top-2 right-2"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div>
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-sm text-gray-600 mb-2">
                Drag and drop photo here, or click to select
              </p>
              <p className="text-xs text-gray-500 mb-4">
                JPG, PNG (max 5MB)
              </p>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <Button variant="outline" asChild>
                  <span>
                    <ImageIcon className="w-4 h-4 mr-2" />
                    Choose File
                  </span>
                </Button>
              </label>
            </div>
          )}
        </div>

        {/* Upload Button */}
        {file && (
          <Button
            onClick={handleUpload}
            disabled={uploading}
            className="w-full"
          >
            {uploading ? 'Uploading...' : 'Upload Photo'}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
