import { useEffect, useRef, useState } from "react";
import { Camera } from "lucide-react";

interface CameraFeedProps {
  isActive: boolean;
  onError?: (error: string) => void;
}

export const CameraFeed = ({ isActive, onError }: CameraFeedProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [detectedStudents, setDetectedStudents] = useState<any[]>([]);
  const [unknownFaces, setUnknownFaces] = useState<any[]>([]);

  useEffect(() => {
    if (isActive) {
      startCamera();
    } else {
      stopCamera();
    }

    return () => {
      stopCamera();
    };
  }, [isActive]);

  const startCamera = async () => {
    try {
      setIsLoading(true);
      setHasError(false);
      
      console.log("🎥 Requesting camera access...");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user"
        },
        audio: false
      });

      console.log("✅ Camera access granted");
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        
        // Wait for video to be ready
        videoRef.current.onloadedmetadata = () => {
          console.log("📹 Video metadata loaded");
          videoRef.current?.play().then(() => {
            console.log("▶️ Video playing");
            setIsLoading(false);
            
            // Start face recognition loop (every 3 seconds)
            intervalRef.current = setInterval(() => {
              captureAndRecognize();
            }, 3000);
          }).catch(err => {
            console.error("❌ Play error:", err);
            setHasError(true);
            setIsLoading(false);
            onError?.("Failed to play video");
          });
        };
      }
    } catch (error: any) {
      console.error("❌ Camera error:", error);
      setHasError(true);
      setIsLoading(false);
      
      let errorMessage = "Failed to access camera";
      if (error.name === 'NotAllowedError') {
        errorMessage = "Camera permission denied";
      } else if (error.name === 'NotFoundError') {
        errorMessage = "No camera found";
      } else if (error.name === 'NotReadableError') {
        errorMessage = "Camera is in use";
      }
      
      onError?.(errorMessage);
    }
  };

  const captureAndRecognize = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob
    canvas.toBlob(async (blob) => {
      if (!blob) return;

      try {
        const formData = new FormData();
        formData.append('file', blob, 'frame.jpg');

        const token = localStorage.getItem('auth_token');
        const response = await fetch('http://localhost:8000/api/camera/recognize', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          console.log('Recognition result:', data);
          setDetectedStudents(data.detected_students || []);
          setUnknownFaces(data.unknown_faces || []);
          
          // Alert if unknown person detected
          if (data.unknown_count > 0) {
            console.warn(`⚠️ ${data.unknown_count} unknown person(s) detected!`);
          }
        }
      } catch (error) {
        console.error('Recognition error:', error);
      }
    }, 'image/jpeg', 0.8);
  };

  const stopCamera = () => {
    console.log("⏹️ Stopping camera");
    
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => {
        track.stop();
        console.log("🛑 Track stopped:", track.label);
      });
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setDetectedStudents([]);
    setUnknownFaces([]);
  };

  if (!isActive) {
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-muted">
        <div className="text-center">
          <Camera className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Camera feed stopped</p>
          <p className="text-sm text-muted-foreground/70">Click start to begin monitoring</p>
        </div>
      </div>
    );
  }

  return (
    <div className="absolute inset-0 bg-black">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-20">
          <div className="text-center text-white">
            <Camera className="w-16 h-16 mx-auto mb-4 animate-pulse" />
            <p>Loading camera...</p>
          </div>
        </div>
      )}
      
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-900/20 z-20">
          <div className="text-center text-white">
            <Camera className="w-16 h-16 mx-auto mb-4" />
            <p>Camera error</p>
            <p className="text-sm">Check console for details</p>
          </div>
        </div>
      )}

      <video
        ref={videoRef}
        className="absolute inset-0 w-full h-full object-cover"
        autoPlay
        playsInline
        muted
        style={{ transform: 'scaleX(-1)' }}
      />
      
      <canvas ref={canvasRef} className="hidden" />

      {/* Live indicator */}
      <div className="absolute top-2 left-2 bg-black/70 text-white px-3 py-1 rounded-full text-sm flex items-center gap-2 z-10">
        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
        Live
      </div>

      {/* Detected Students and Unknown Persons */}
      {(detectedStudents.length > 0 || unknownFaces.length > 0) && (
        <div className="absolute bottom-2 left-2 right-2 bg-black/70 text-white p-3 rounded-lg z-10">
          {detectedStudents.length > 0 && (
            <>
              <p className="text-xs font-semibold mb-2">✓ Detected:</p>
              {detectedStudents.map((student, index) => {
                const isSpoofing = student.status === 'spoofing' || student.status === 'spoofing_detected';
                const livenessScore = student.liveness_score || 1.0;
                
                return (
                  <div key={index} className={`flex items-center gap-2 text-sm mb-1 ${isSpoofing ? 'text-red-400' : ''}`}>
                    <div className={`w-2 h-2 rounded-full ${isSpoofing ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></div>
                    <span className="font-medium">{student.name}</span>
                    <span className="text-xs text-gray-300">({student.student_id})</span>
                    {isSpoofing && (
                      <span className="text-xs text-red-400 font-bold">⚠️ SPOOF!</span>
                    )}
                    {livenessScore < 0.7 && !isSpoofing && (
                      <span className="text-xs text-yellow-400">Low liveness: {(livenessScore * 100).toFixed(0)}%</span>
                    )}
                  </div>
                );
              })}
            </>
          )}
          
          {unknownFaces.length > 0 && (
            <>
              <p className="text-xs font-semibold mb-2 mt-3 text-orange-400">⚠️ Unknown Persons Detected:</p>
              {unknownFaces.map((face, index) => (
                <div key={index} className="flex items-center gap-2 text-sm mb-1 text-orange-300">
                  <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
                  <span className="font-medium">Unknown Person #{index + 1}</span>
                  <span className="text-xs">(Logged as suspicious)</span>
                </div>
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
};
