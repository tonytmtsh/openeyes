#!/usr/bin/env python3
"""
Ultra Low RAM OpenEyes - Minimal memory usage version
Uses smallest possible camera resolution and B&W display for maximum RAM savings
"""

import cv2
import pygame
import time
import os

# Configuration
MUSIC_FILE = "music/wakeup.mp3"
CLOSED_THRESHOLD = 0.3  # Shorter delay
WINDOW_NAME = "OpenEyes - Low RAM"

# Minimal global state (less RAM)
current_state = "NO FACE"
music_playing = False
eyes_closed_start = None
frame_count = 0
last_face_position = None  # Track last good face position
face_confidence = 0  # Track how confident we are about face position

def init_audio():
    """Initialize pygame audio system"""
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        return True
    except:
        return False

def start_music():
    """Start playing music"""
    global music_playing
    if not music_playing and os.path.exists(MUSIC_FILE):
        try:
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.play(-1)
            music_playing = True
        except:
            pass

def stop_music():
    """Stop playing music"""
    global music_playing
    if music_playing:
        try:
            pygame.mixer.music.stop()
            music_playing = False
        except:
            pass

def analyze_eyes_simple(faces, eyes_count):
    """Ultra-simple eye state analysis - no history, minimal RAM"""
    global current_state, eyes_closed_start, music_playing
    
    current_time = time.time()
    
    # No face = no processing needed
    if len(faces) == 0:
        eyes_closed_start = None
        current_state = "NO FACE"
        stop_music()
        return "NO FACE"
    
    # Simple logic: 0 eyes = closed, 1+ eyes = open
    if eyes_count == 0:
        # Start timing if not already
        if eyes_closed_start is None:
            eyes_closed_start = current_time
            return current_state
        
        # Check if closed long enough
        if current_time - eyes_closed_start >= CLOSED_THRESHOLD:
            current_state = "CLOSED"
            start_music()
            return "CLOSED"
        else:
            return current_state
    else:
        # Eyes open - immediate response
        eyes_closed_start = None
        current_state = "OPEN"
        stop_music()
        return "OPEN"

def main():
    """Ultra low RAM main loop"""
    global frame_count
    
    # Initialize
    if not init_audio():
        print("Warning: Audio initialization failed")
    
    # Load multiple cascades for different angles
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    face_cascade_alt = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    face_cascade_alt2 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    
    if face_cascade.empty() or eye_cascade.empty():
        print("Error: Could not load detection models")
        return
    
    # Start camera with MINIMAL resolution (saves lots of RAM)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return
    
    # Ultra-low resolution but slightly bigger for better detection
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 240)   # Slightly bigger
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 180)  # Slightly bigger
    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # Minimal buffer
    
    print("OpenEyes Low RAM - Press 'q' to quit")
    print(f"Resolution: 240x180 (low RAM B&W mode)")
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Convert to grayscale immediately (save RAM by using grayscale for everything)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Improve contrast for better detection
            gray = cv2.equalizeHist(gray)
            # Use grayscale as display frame (B&W camera effect + saves RAM)
            frame = gray
            
            # Try multiple detection approaches for different angles
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1,   # More sensitive
                minNeighbors=2,    # Less strict
                minSize=(20, 20),  # Smaller minimum
                maxSize=(160, 160) # Larger maximum
            )
            
            # If no frontal faces, try profile faces
            if len(faces) == 0:
                faces = face_cascade_alt.detectMultiScale(
                    gray, 
                    scaleFactor=1.1,
                    minNeighbors=2,
                    minSize=(20, 20),
                    maxSize=(160, 160)
                )
            
            # If still no faces, try alternative frontal detector (different angles)
            if len(faces) == 0:
                faces = face_cascade_alt2.detectMultiScale(
                    gray, 
                    scaleFactor=1.1,
                    minNeighbors=2,
                    minSize=(20, 20),
                    maxSize=(160, 160)
                )
            
            # If still nothing, be more aggressive with the main detector
            if len(faces) == 0:
                faces = face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.05,  # Very sensitive
                    minNeighbors=1,    # Very permissive
                    minSize=(15, 15),  # Very small
                    maxSize=(170, 170) # Larger
                )
            
            # Smart face detection with confidence tracking
            eyes_count = 0
            global last_face_position, face_confidence
            
            if len(faces) > 0:
                x, y, w, h = faces[0]  # Just the first face
                
                # Very lenient stability check - allow lots of movement for angle changes
                if last_face_position is None or abs(x - last_face_position[0]) < 100:
                    last_face_position = (x, y, w, h)
                    face_confidence = min(face_confidence + 3, 15)  # Boost confidence more, higher max
                    
                    # Draw face rectangle (white on B&W)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255), 2)
                    
                    # Extract face region
                    roi_gray = gray[y:y + h, x:x + w]
                    roi_frame = frame[y:y + h, x:x + w]
                    
                    # Eye detection - much more sensitive
                    eyes_raw = eye_cascade.detectMultiScale(
                        roi_gray, 
                        scaleFactor=1.05,  # Very sensitive
                        minNeighbors=1,     # Very permissive
                        minSize=(2, 2),     # Very tiny eyes
                        maxSize=(35, 35)    # Larger range
                    )
                    
                    # Filter eyes - only keep ones in upper 60% of face (avoid nose/mouth)
                    eyes = []
                    face_height = h
                    upper_face_limit = int(face_height * 0.6)  # Only upper 60% of face
                    
                    for (ex, ey, ew, eh) in eyes_raw:
                        if ey < upper_face_limit:  # Only eyes in upper face
                            # Check for overlaps with existing eyes
                            is_overlap = False
                            for (existing_ex, existing_ey, existing_ew, existing_eh) in eyes:
                                # Calculate overlap
                                overlap_x = max(0, min(ex + ew, existing_ex + existing_ew) - max(ex, existing_ex))
                                overlap_y = max(0, min(ey + eh, existing_ey + existing_eh) - max(ey, existing_ey))
                                overlap_area = overlap_x * overlap_y
                                
                                current_area = ew * eh
                                if overlap_area > current_area * 0.3:  # 30% overlap threshold
                                    is_overlap = True
                                    break
                            
                            if not is_overlap:
                                eyes.append((ex, ey, ew, eh))
                    
                    # Limit to maximum 2 eyes (realistic)
                    if len(eyes) > 2:
                        # Keep the 2 largest eyes
                        eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
                    
                    eyes_count = len(eyes)
                    
                    # Draw eyes
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_frame, (ex, ey), (ex + ew, ey + eh), (255), 2)
                        
            elif last_face_position is not None and face_confidence > 0:
                # No face detected, but we had one recently - keep trying in last location
                x, y, w, h = last_face_position
                face_confidence -= 1  # Reduce confidence slower for angle changes
                
                # Draw dimmer rectangle to show we're using last position
                cv2.rectangle(frame, (x, y), (x + w, y + h), (128), 1)
                
                # Still try to find eyes in the last known face location
                if y + h <= frame.shape[0] and x + w <= frame.shape[1]:  # Bounds check
                    roi_gray = gray[y:y + h, x:x + w]
                    roi_frame = frame[y:y + h, x:x + w]
                    
                    eyes_raw = eye_cascade.detectMultiScale(
                        roi_gray, 
                        scaleFactor=1.1,
                        minNeighbors=1,
                        minSize=(3, 3),
                        maxSize=(30, 30)
                    )
                    
                    # Same filtering for confidence mode
                    eyes = []
                    face_height = h
                    upper_face_limit = int(face_height * 0.6)
                    
                    for (ex, ey, ew, eh) in eyes_raw:
                        if ey < upper_face_limit:  # Only eyes in upper face
                            # Check for overlaps
                            is_overlap = False
                            for (existing_ex, existing_ey, existing_ew, existing_eh) in eyes:
                                overlap_x = max(0, min(ex + ew, existing_ex + existing_ew) - max(ex, existing_ex))
                                overlap_y = max(0, min(ey + eh, existing_ey + existing_eh) - max(ey, existing_ey))
                                overlap_area = overlap_x * overlap_y
                                current_area = ew * eh
                                if overlap_area > current_area * 0.3:
                                    is_overlap = True
                                    break
                            if not is_overlap:
                                eyes.append((ex, ey, ew, eh))
                    
                    # Limit to 2 eyes
                    if len(eyes) > 2:
                        eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
                    
                    eyes_count = len(eyes)
                    
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_frame, (ex, ey), (ex + ew, ey + eh), (128), 1)
            else:
                # Completely lost - reset
                last_face_position = None
                face_confidence = 0
            
            # Simple eye state analysis
            eye_state = analyze_eyes_simple(faces, eyes_count)
            
            # Display (high contrast text for B&W readability)
            if eye_state == "OPEN":
                color = 255  # Bright white
                text = "OPEN"
            elif eye_state == "CLOSED":
                color = 0    # Black text (high contrast)
                text = "CLOSED"
            else:
                color = 128  # Gray
                text = "NO FACE"
            
            # High contrast display with background for readability
            # Bigger text box for 240x180
            cv2.rectangle(frame, (2, 2), (150, 85), 255, -1)  # White background
            cv2.rectangle(frame, (2, 2), (150, 85), 0, 1)     # Black border
            
            cv2.putText(frame, text, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 2)  # Black text
            cv2.putText(frame, f"Faces:{len(faces) if 'faces' in locals() else 0}", (5, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)
            cv2.putText(frame, f"Eyes:{eyes_count}", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)
            cv2.putText(frame, f"Conf:{face_confidence}", (5, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)
            
            # Show music status with high contrast
            if music_playing:
                cv2.putText(frame, "MUSIC ON", (100, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)
            
            # Display frame
            cv2.imshow(WINDOW_NAME, frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        pass
    
    finally:
        # Cleanup
        stop_music()
        camera.release()
        cv2.destroyAllWindows()
        pygame.quit()
        print(f"Processed {frame_count} frames")

if __name__ == "__main__":
    main()
