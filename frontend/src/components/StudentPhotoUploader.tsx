import { useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

interface PhotoWithType {
  file: File;
  preview: string;
  type: string;
}

interface StudentPhotoUploaderProps {
  onPhotosChange: (photos: PhotoWithType[]) => void;
}

export function StudentPhotoUploader({ onPhotosChange }: StudentPhotoUploaderProps) {
  const [photos, setPhotos] = useState<PhotoWithType[]>([]);
  const [currentPhotoType, setCurrentPhotoType] = useState('front');

  console.log('StudentPhotoUploader rendered with', photos.length, 'photos');

  const photoTypes = [
    { value: 'front', label: 'Front View', color: 'bg-blue-500' },
    { value: 'left', label: 'Left Profile', color: 'bg-green-500' },
    { value: 'right', label: 'Right Profile', color: 'bg-yellow-500' },
    { value: 'with_glasses', label: 'With Glasses', color: 'bg-purple-500' },
    { value: 'without_glasses', label: 'Without Glasses', color: 'bg-pink-500' },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    addFiles(files);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
  };

  const addFiles = (files: File[]) => {
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    if (imageFiles.length === 0) {
      return;
    }

    const newPhotos: PhotoWithType[] = [];
    let processed = 0;

    imageFiles.forEach((file) => {
      if (file.size > 5 * 1024 * 1024) {
        return; // Skip files larger than 5MB
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        newPhotos.push({
          file,
          preview: reader.result as string,
          type: currentPhotoType
        });
        
        processed++;
        if (processed === imageFiles.length) {
          const updatedPhotos = [...photos, ...newPhotos];
          setPhotos(updatedPhotos);
          onPhotosChange(updatedPhotos);
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removePhoto = (index: number) => {
    const updatedPhotos = photos.filter((_, i) => i !== index);
    setPhotos(updatedPhotos);
    onPhotosChange(updatedPhotos);
  };

  const updatePhotoType = (index: number, newType: string) => {
    const updatedPhotos = [...photos];
    updatedPhotos[index].type = newType;
    setPhotos(updatedPhotos);
    onPhotosChange(updatedPhotos);
  };

  const getTypeColor = (type: string) => {
    return photoTypes.find(t => t.value === type)?.color || 'bg-gray-500';
  };

  const getTypeLabel = (type: string) => {
    return photoTypes.find(t => t.value === type)?.label || type;
  };

  return (
    <div className="space-y-4">
      {/* Photo Type Selector */}
      <div>
        <Label className="text-sm font-medium mb-2 block">
          Default Photo Type for New Uploads
        </Label>
        <Select value={currentPhotoType} onValueChange={setCurrentPhotoType}>
          <SelectTrigger>
            <SelectValue placeholder="Select photo type" />
          </SelectTrigger>
          <SelectContent>
            {photoTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${type.color}`}></div>
                  {type.label}
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer bg-muted/30"
      >
        <Upload className="mx-auto h-10 w-10 text-gray-400 mb-3" />
        <p className="text-sm text-gray-600 mb-2">
          Drag and drop photos here, or click to select
        </p>
        <p className="text-xs text-gray-500 mb-3">
          JPG, PNG (max 5MB per file)
        </p>
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handleFileChange}
          className="hidden"
          id="multi-file-upload"
        />
        <label htmlFor="multi-file-upload">
          <Button variant="outline" size="sm" asChild>
            <span>
              <ImageIcon className="w-4 h-4 mr-2" />
              Choose Files
            </span>
          </Button>
        </label>
      </div>

      {/* Photo Preview Grid */}
      {photos.length > 0 && (
        <div>
          <Label className="text-sm font-medium mb-2 block">
            Uploaded Photos ({photos.length})
          </Label>
          <div className="grid grid-cols-2 gap-3">
            {photos.map((photo, index) => (
              <div key={index} className="relative group border rounded-lg overflow-hidden">
                <img
                  src={photo.preview}
                  alt={`Preview ${index + 1}`}
                  className="w-full h-32 object-cover"
                />
                
                {/* Overlay with controls */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2">
                  <Select 
                    value={photo.type} 
                    onValueChange={(value) => updatePhotoType(index, value)}
                  >
                    <SelectTrigger className="w-[140px] h-8 text-xs bg-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {photoTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value} className="text-xs">
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <Button
                    onClick={(e) => {
                      e.stopPropagation();
                      removePhoto(index);
                    }}
                    variant="destructive"
                    size="sm"
                    className="h-7 text-xs"
                    type="button"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Remove
                  </Button>
                </div>

                {/* Photo Type Badge */}
                <Badge 
                  className={`absolute top-2 left-2 text-xs ${getTypeColor(photo.type)} text-white`}
                >
                  {getTypeLabel(photo.type)}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}

      {photos.length === 0 && (
        <p className="text-xs text-center text-muted-foreground">
          No photos uploaded yet. Add at least 1 photo for face recognition (or add later).
        </p>
      )}
      
      {photos.length > 0 && photos.length < 5 && (
        <p className="text-xs text-center text-success">
          ✓ {photos.length} photo(s) uploaded. You can add more for better accuracy (recommended: 5 total).
        </p>
      )}
      
      {photos.length >= 5 && (
        <p className="text-xs text-center text-success font-medium">
          ✓ Excellent! {photos.length} photos uploaded for optimal recognition accuracy.
        </p>
      )}
    </div>
  );
}

function Label({ children, className, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) {
  return (
    <label className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`} {...props}>
      {children}
    </label>
  );
}
