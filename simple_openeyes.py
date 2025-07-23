#!/usr/bin/env python3
"""
Simple OpenEyes - Minimal eye detection with music playback
"""

import cv2
import pygame
import time
import os

# Configuration
MUSIC_FILE = "music/wakeup.mp3"
CLOSED_THRESHOLD = 0.5  # 500ms
WINDOW_NAME = "OpenEyes - Simple"

# Global state
eye_state_history = []
eyes_closed_start_time = None
current_state = "NO FACE"
music_playing = False
face_detection_history = []

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
            pygame.mixer.music.play(-1)  # Loop indefinitely
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

def analyze_eye_state(faces, eyes_data):
    """Determine eye state from detection data"""
    global eye_state_history, eyes_closed_start_time, current_state
    
    current_time = time.time()
    
    # No face detected
    if len(faces) == 0:
        eye_state_history.append({"state": "NO_FACE", "time": current_time})
        eyes_closed_start_time = None
        current_state = "NO FACE"
        stop_music()
        return "NO FACE"
    
    # Count total eyes detected
    total_eyes = len(eyes_data)
    
    # Determine raw state - clearer logic for eye detection
    if total_eyes >= 2:
        raw_state = "OPEN"  # Both eyes detected = clearly open
    elif total_eyes == 1:
        raw_state = "OPEN"  # One eye detected = likely open (partial detection)
    else:  # total_eyes == 0
        raw_state = "CLOSED"  # No eyes detected = likely closed
    
    # Add to history
    eye_state_history.append({"state": raw_state, "time": current_time})
    
    # Keep only last 15 measurements for better smoothing
    if len(eye_state_history) > 15:
        eye_state_history.pop(0)
    
    # Handle OPEN state - immediate response
    if raw_state == "OPEN":
        eyes_closed_start_time = None
        current_state = "OPEN"
        stop_music()
        return "OPEN"
    
    # Handle CLOSED state with simpler temporal filtering
    if raw_state == "CLOSED":
        # Need at least 3 measurements for basic stability
        if len(eye_state_history) < 3:
            return current_state
        
        # Check last 3 measurements - require majority to be CLOSED
        recent_states = [s["state"] for s in eye_state_history[-3:]]
        closed_count = recent_states.count("CLOSED")
        
        if closed_count >= 2:  # At least 2 out of 3 recent measurements are CLOSED
            # Start timing if not already
            if eyes_closed_start_time is None:
                eyes_closed_start_time = current_time
                return current_state  # Don't change state yet
            
            # Check if closed long enough
            closed_duration = current_time - eyes_closed_start_time
            if closed_duration >= CLOSED_THRESHOLD:
                current_state = "CLOSED"
                start_music()
                return "CLOSED"
            else:
                return current_state  # Still waiting
        else:
            # Not consistently closed, reset
            eyes_closed_start_time = None
            current_state = "OPEN"
            stop_music()
            return "OPEN"
    
    return current_state

def main():
    """Main application loop"""
    # Initialize
    if not init_audio():
        print("Warning: Audio initialization failed")
    
    # Load detection models - try multiple face cascades
    face_cascade1 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt.xml")
    face_cascade2 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    face_cascade3 = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
    
    # Use the best available cascade
    face_cascade = None
    for cascade in [face_cascade1, face_cascade2, face_cascade3]:
        if not cascade.empty():
            face_cascade = cascade
            break
    
    if face_cascade is None or face_cascade.empty():
        print("Error: Could not load any face detection models")
        return
    
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye_tree_eyeglasses.xml")
    # Fallback to regular eye detection if eyeglasses cascade doesn't exist
    if eye_cascade.empty():
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        
    left_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_lefteye_2splits.xml")
    right_eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_righteye_2splits.xml")
    
    if eye_cascade.empty():
        print("Error: Could not load eye detection models")
        return
    
    # Start camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not open camera")
        return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("OpenEyes Simple - Press 'q' to quit")
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces - multiple passes for better detection
            raw_faces1 = face_cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=5, minSize=(40, 40), maxSize=(350, 350))
            raw_faces2 = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=4, minSize=(60, 60), maxSize=(400, 400))
            raw_faces3 = face_cascade.detectMultiScale(gray, scaleFactor=1.12, minNeighbors=6, minSize=(30, 30), maxSize=(250, 250))
            
            # Combine all face detections
            all_faces = []
            for faces in [raw_faces1, raw_faces2, raw_faces3]:
                for face in faces:
                    all_faces.append(face)
            
            # Remove duplicate faces (similar to eye overlap filtering)
            raw_faces = []
            for (x1, y1, w1, h1) in all_faces:
                is_duplicate = False
                for (x2, y2, w2, h2) in raw_faces:
                    # Check for significant overlap
                    overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                    overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                    overlap_area = overlap_x * overlap_y
                    area1 = w1 * h1
                    area2 = w2 * h2
                    if overlap_area > 0.5 * min(area1, area2):  # 50% overlap threshold
                        is_duplicate = True
                        break
                if not is_duplicate:
                    raw_faces.append((x1, y1, w1, h1))
            
            # Filter to get only the largest face (main face)
            if len(raw_faces) > 0:
                frame_center_x = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2
                
                # Score faces based on size and distance from center
                scored_faces = []
                for (x, y, w, h) in raw_faces:
                    area = w * h
                    face_center_x = x + w // 2
                    face_center_y = y + h // 2
                    
                    # Distance from frame center
                    distance = ((face_center_x - frame_center_x) ** 2 + (face_center_y - frame_center_y) ** 2) ** 0.5
                    
                    # Score: larger area is better, closer to center is better
                    score = area / (1 + distance * 0.01)  # Small penalty for distance
                    scored_faces.append((x, y, w, h, score))
                
                # Select the best scoring face
                best_face = max(scored_faces, key=lambda f: f[4])
                raw_faces = [(best_face[0], best_face[1], best_face[2], best_face[3])]
            
            # Add face detection stability
            global face_detection_history
            face_detection_history.append(len(raw_faces) > 0)
            if len(face_detection_history) > 5:
                face_detection_history.pop(0)
            
            # Use stable face detection - require majority of recent frames to have faces
            if len(face_detection_history) >= 3:
                face_count = sum(face_detection_history)
                if face_count >= len(face_detection_history) * 0.6:  # 60% of recent frames have faces
                    faces = raw_faces if len(raw_faces) > 0 else []
                else:
                    faces = []
            else:
                faces = raw_faces
            
            eyes_data = []
            
            # Process each face
            for (x, y, w, h) in faces:
                # Draw face rectangle
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                
                # Extract face region
                roi_gray = gray[y:y + h, x:x + w]
                roi_color = frame[y:y + h, x:x + w]
                
                # Detect eyes in face region - simplified and more reliable
                eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=5, minSize=(8, 8), maxSize=(50, 50))
                
                # Simple overlap filtering - keep only non-overlapping eyes
                filtered_eyes = []
                for (ex1, ey1, ew1, eh1) in eyes:
                    is_overlapping = False
                    for (ex2, ey2, ew2, eh2) in filtered_eyes:
                        # Check for overlap
                        if (abs(ex1 - ex2) < max(ew1, ew2) * 0.5 and 
                            abs(ey1 - ey2) < max(eh1, eh2) * 0.5):
                            is_overlapping = True
                            break
                    if not is_overlapping:
                        filtered_eyes.append((ex1, ey1, ew1, eh1))
                
                # Limit to maximum 2 eyes and prefer larger ones
                if len(filtered_eyes) > 2:
                    # Sort by area (larger first) and take top 2
                    filtered_eyes.sort(key=lambda eye: eye[2] * eye[3], reverse=True)
                    filtered_eyes = filtered_eyes[:2]
                
                # Draw eye rectangles and collect eye data
                for (ex, ey, ew, eh) in filtered_eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    eyes_data.append((ex, ey, ew, eh))
                
                # Only process first face
                break
            
            # Analyze eye state
            eye_state = analyze_eye_state(faces, eyes_data)
            
            # Display eye state
            if eye_state == "OPEN":
                state_color = (0, 255, 0)  # Green
                display_text = "EYES: OPEN"
            elif eye_state == "CLOSED":
                state_color = (0, 0, 255)  # Red
                display_text = "EYES: CLOSED"
            else:
                state_color = (255, 255, 0)  # Yellow
                display_text = "NO FACE"
            
            # Add background for text
            cv2.rectangle(frame, (5, 5), (300, 100), (0, 0, 0), -1)
            
            # Display state and eye count
            cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, state_color, 2)
            cv2.putText(frame, f"Eyes: {len(eyes_data)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Faces: {len(faces)}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show recent eye state history for debugging
            if len(eye_state_history) >= 3:
                recent = [s["state"] for s in eye_state_history[-3:]]
                history_text = " ".join([s[:1] for s in recent])  # First letter of each state
                cv2.putText(frame, f"History: {history_text}", (310, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Show timing info for debugging
            if eyes_closed_start_time is not None:
                elapsed = time.time() - eyes_closed_start_time
                cv2.putText(frame, f"Closed: {elapsed:.1f}s", (320, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Show music status
            if music_playing:
                cv2.putText(frame, "♪ MUSIC ♪", (200, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
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

if __name__ == "__main__":
    main()
