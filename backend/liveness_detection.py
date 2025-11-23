"""
Advanced Liveness Detection for Anti-Spoofing
Detects if a face is real (live person) or fake (photo/video/mask)
"""

import cv2
import numpy as np
from collections import deque
from datetime import datetime

class LivenessDetector:
    """
    Multi-method liveness detection to prevent spoofing attacks
    """
    
    def __init__(self):
        self.movement_threshold = 2.0  # Minimum movement for liveness
        self.texture_threshold = 15.0  # Minimum texture variance
        self.blink_frames = deque(maxlen=30)  # Track eye aspect ratio
        self.head_pose_history = deque(maxlen=20)
        
    def check_movement(self, movement_history):
        """
        Check if there's natural head movement
        Photos/videos on screen tend to be static
        """
        if len(movement_history) < 10:
            return True, 0.5  # Not enough data yet
        
        movements = list(movement_history)
        avg_movement = np.mean(movements)
        std_movement = np.std(movements)
        
        # Real people have variable movement
        # Photos/screens are too static or too uniform
        if avg_movement < 1.0 and std_movement < 0.5:
            return False, 0.2  # Too static - likely photo
        
        if avg_movement > 0.5 and std_movement > 0.3:
            return True, 0.9  # Good natural movement
        
        return True, 0.6  # Borderline
    
    def check_texture(self, face_img):
        """
        Analyze texture patterns
        Real faces have more texture variation than printed photos
        """
        if face_img is None or face_img.size == 0:
            return True, 0.5
        
        # Convert to grayscale
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img
        
        # Calculate Laplacian variance (texture measure)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        
        print(f"  Texture variance: {variance:.2f}")
        
        # Real faces have higher texture variance
        # Balanced thresholds
        if variance < 15:
            return False, 0.2  # Very smooth - likely printed photo or screen
        elif variance > 25:
            return True, 0.9  # Good texture - likely real
        else:
            return True, 0.6  # Borderline - allow but lower score
    
    def check_color_diversity(self, face_img):
        """
        Check color distribution
        Real faces have natural color variation
        Printed photos often have limited color range
        """
        if face_img is None or face_img.size == 0:
            return True, 0.5
        
        # Calculate color histogram
        hist_b = cv2.calcHist([face_img], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([face_img], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([face_img], [2], None, [256], [0, 256])
        
        # Calculate entropy (color diversity)
        def entropy(hist):
            hist = hist / hist.sum()
            hist = hist[hist > 0]
            return -np.sum(hist * np.log2(hist))
        
        avg_entropy = (entropy(hist_b) + entropy(hist_g) + entropy(hist_r)) / 3
        
        # Real faces have higher color entropy
        if avg_entropy < 4.0:
            return False, 0.4  # Limited colors - likely photo
        elif avg_entropy > 5.5:
            return True, 0.9  # Good color diversity
        else:
            return True, 0.6
    
    def check_reflection(self, face_img):
        """
        Detect screen reflections or glare
        Photos on screens often have characteristic reflections
        """
        if face_img is None or face_img.size == 0:
            return True, 0.5
        
        # Convert to grayscale
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img
        
        # Find very bright spots (potential reflections)
        _, bright_spots = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        bright_ratio = np.sum(bright_spots > 0) / bright_spots.size
        
        # Also check for moderate bright spots (screen glow)
        _, moderate_bright = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        moderate_ratio = np.sum(moderate_bright > 0) / moderate_bright.size
        
        print(f"  Bright spots: {bright_ratio:.4f}, Moderate: {moderate_ratio:.4f}")
        
        # Too many bright spots suggest screen reflection
        # Balanced thresholds
        if bright_ratio > 0.20 or moderate_ratio > 0.35:
            return False, 0.2  # Likely screen reflection or glow
        elif bright_ratio < 0.10 and moderate_ratio < 0.25:
            return True, 0.9  # No suspicious reflections
        else:
            return True, 0.6  # Borderline - allow but lower score
    
    def check_screen_pattern(self, face_img):
        """
        Detect screen pixel patterns
        Phone/monitor screens have characteristic pixel grids
        """
        if face_img is None or face_img.size == 0:
            return True, 0.5
        
        # Convert to grayscale
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img
        
        # Apply FFT to detect regular patterns (screen pixels)
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
        
        # Check for high-frequency regular patterns
        h, w = magnitude_spectrum.shape
        center_h, center_w = h // 2, w // 2
        
        # Sample high-frequency regions
        high_freq_region = magnitude_spectrum[center_h-10:center_h+10, center_w+w//4:center_w+w//3]
        high_freq_energy = np.mean(high_freq_region)
        
        print(f"  High-freq energy: {high_freq_energy:.2f}")
        
        # Screens have more high-frequency energy due to pixel grid
        # Very high values (>100) are actually from camera noise, not screens
        # Screens typically have moderate high-freq energy (20-80)
        if 20 < high_freq_energy < 80:
            return False, 0.3  # Likely screen with pixel pattern
        elif high_freq_energy < 15 or high_freq_energy > 100:
            return True, 0.9  # No screen pattern (too low or camera noise)
        else:
            return True, 0.6  # Borderline
    
    def check_depth_cues(self, face_img):
        """
        Check for depth information
        Real 3D faces have different depth cues than flat photos
        """
        if face_img is None or face_img.size == 0:
            return True, 0.5
        
        # Convert to grayscale
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img
        
        # Calculate gradient magnitude (edge strength)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(sobelx**2 + sobely**2)
        
        # Real faces have more varied edge strengths
        edge_variance = np.var(gradient_mag)
        
        print(f"  Edge variance: {edge_variance:.2f}")
        
        # Balanced thresholds for depth detection
        if edge_variance < 100:
            return False, 0.3  # Too uniform - likely flat photo or screen
        elif edge_variance > 400:
            return True, 0.9  # Good depth variation
        else:
            return True, 0.6  # Borderline - allow but lower score
    
    def detect_liveness(self, face_img, movement_history=None):
        """
        Comprehensive liveness detection
        Returns: (is_live, confidence, details)
        """
        checks = {}
        scores = []
        
        # 1. Movement check
        if movement_history and len(movement_history) > 0:
            is_live, score = self.check_movement(movement_history)
            checks['movement'] = {'is_live': is_live, 'score': score}
            scores.append(score)
        
        # 2. Texture check
        is_live, score = self.check_texture(face_img)
        checks['texture'] = {'is_live': is_live, 'score': score}
        scores.append(score)
        
        # 3. Color diversity check
        is_live, score = self.check_color_diversity(face_img)
        checks['color'] = {'is_live': is_live, 'score': score}
        scores.append(score)
        
        # 4. Reflection check
        is_live, score = self.check_reflection(face_img)
        checks['reflection'] = {'is_live': is_live, 'score': score}
        scores.append(score)
        
        # 5. Depth cues check
        is_live, score = self.check_depth_cues(face_img)
        checks['depth'] = {'is_live': is_live, 'score': score}
        scores.append(score)
        
        # 6. Screen pattern check (NEW - specifically for phone displays)
        is_live, score = self.check_screen_pattern(face_img)
        checks['screen_pattern'] = {'is_live': is_live, 'score': score}
        scores.append(score)
        
        # Calculate overall confidence
        avg_score = np.mean(scores)
        
        # Determine if live based on multiple checks
        # Balanced approach - need majority of checks to pass
        passing_checks = sum(1 for check in checks.values() if check['is_live'] and check['score'] > 0.5)
        high_score_checks = sum(1 for check in checks.values() if check['score'] > 0.7)
        failing_checks = sum(1 for check in checks.values() if not check['is_live'])
        
        # Balanced criteria:
        # - Need at least 4/6 checks passing
        # - Average score > 0.65
        # - At least 2 high-confidence checks
        # - No more than 2 checks failing badly
        is_live = passing_checks >= 4 and avg_score > 0.65 and high_score_checks >= 2 and failing_checks <= 2
        
        print(f"  Liveness decision: passing={passing_checks}/6, high_score={high_score_checks}/6, avg={avg_score:.2f}, is_live={is_live}")
        
        return is_live, avg_score, checks
    
    def get_spoofing_type(self, checks):
        """
        Determine likely spoofing method based on failed checks
        """
        # Check for screen pattern first (most specific)
        if 'screen_pattern' in checks and not checks['screen_pattern']['is_live']:
            return "phone_screen_display"
        
        if not checks['texture']['is_live'] and not checks['depth']['is_live']:
            return "printed_photo"
        
        if not checks['reflection']['is_live']:
            return "screen_display"
        
        if not checks['movement']['is_live']:
            return "static_image"
        
        if not checks['color']['is_live']:
            return "low_quality_reproduction"
        
        return "unknown_spoof"


class EnhancedStudentTracker:
    """
    Enhanced student tracker with liveness detection
    """
    
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.movement_history = deque(maxlen=30)
        self.last_position = None
        self.suspicion_score = 0
        self.last_seen = datetime.now()
        self.entry_logged = False
        
        # Liveness tracking
        self.liveness_detector = LivenessDetector()
        self.liveness_checks = []
        self.liveness_score = 1.0
        self.is_live = True
        self.spoofing_detected = False
        self.spoofing_type = None
    
    def update_metrics(self, bbox, face_img=None):
        """
        Update tracking metrics including liveness
        """
        # Update position and movement
        current_center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        if self.last_position:
            movement = np.sqrt(
                (current_center[0] - self.last_position[0])**2 + 
                (current_center[1] - self.last_position[1])**2
            )
            self.movement_history.append(movement)
        self.last_position = current_center
        self.last_seen = datetime.now()
        
        # Liveness detection
        if face_img is not None:
            is_live, confidence, checks = self.liveness_detector.detect_liveness(
                face_img, 
                self.movement_history
            )
            
            self.is_live = is_live
            self.liveness_score = confidence
            self.liveness_checks.append({
                'timestamp': datetime.now(),
                'is_live': is_live,
                'confidence': confidence,
                'checks': checks
            })
            
            # Keep only recent checks
            if len(self.liveness_checks) > 10:
                self.liveness_checks.pop(0)
            
            # Detect spoofing
            if not is_live:
                self.spoofing_detected = True
                self.spoofing_type = self.liveness_detector.get_spoofing_type(checks)
                self.suspicion_score += 5  # High suspicion for spoofing
            else:
                self.spoofing_detected = False
                self.spoofing_type = None
        
        # Calculate suspicion based on movement (existing logic)
        if len(self.movement_history) >= 20:
            avg_movement = np.mean(list(self.movement_history))
            if avg_movement < 2:
                self.suspicion_score += 1
            else:
                self.suspicion_score = max(0, self.suspicion_score - 0.5)
    
    def is_suspicious(self):
        """
        Check if behavior is suspicious (including spoofing)
        """
        return self.suspicion_score > 10 or self.spoofing_detected
    
    def get_status(self):
        """
        Get current status with liveness info
        """
        return {
            'student_id': self.student_id,
            'name': self.name,
            'is_live': self.is_live,
            'liveness_score': self.liveness_score,
            'spoofing_detected': self.spoofing_detected,
            'spoofing_type': self.spoofing_type,
            'suspicion_score': self.suspicion_score,
            'is_suspicious': self.is_suspicious()
        }
