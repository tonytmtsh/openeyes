"""
Core functionality for the OpenEyes project.
"""

from typing import Optional, Dict, Any, Tuple, List
import logging
import cv2
import numpy as np
import time
import pygame
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenEyes:
    """
    Main class for OpenEyes functionality.

    This class provides the primary interface for the OpenEyes application.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenEyes instance.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.camera = None
        self.is_camera_active = False

        # Initialize face and eye detection cascades
        self.face_cascade = None
        self.eye_cascade = None
        self.left_eye_cascade = None
        self.right_eye_cascade = None
        self._load_detection_models()

        # Eye state tracking for open/closed detection
        self.eye_state_history = []  # Track recent eye states
        self.eyes_closed_start_time = None  # When eyes first closed
        self.current_eye_state = "NO FACE"  # Current displayed state
        self.eye_closed_threshold = 0.5  # 500ms in seconds
        self.max_history_length = 10  # Keep last 10 measurements

        # Audio/Music playback setup
        self.music_enabled = True  # Enable/disable music playback
        self.music_playing = False  # Track if music is currently playing
        self.music_file = None  # Path to music file to play
        self.pygame_initialized = False
        self._initialize_audio()

        logger.info("OpenEyes instance initialized")

    def _load_detection_models(self) -> None:
        """Load OpenCV Haar cascade models for face and eye detection."""
        try:
            # Load face detection cascade
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )

            # Load eye detection cascades
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_eye.xml"
            )
            self.left_eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_lefteye_2splits.xml"
            )
            self.right_eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_righteye_2splits.xml"
            )

            # Verify cascades loaded successfully
            if (
                self.face_cascade.empty()
                or self.eye_cascade.empty()
                or self.left_eye_cascade.empty()
                or self.right_eye_cascade.empty()
            ):
                logger.warning(
                    "Some detection models failed to load. "
                    "Eye detection may not work properly."
                )
            else:
                logger.info("Eye detection models loaded successfully")

        except Exception as e:
            logger.error(f"Error loading detection models: {e}")
            self.face_cascade = None
            self.eye_cascade = None

    def _initialize_audio(self) -> None:
        """Initialize pygame audio system for music playback."""
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.pygame_initialized = True
            logger.info("Audio system initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize audio system: {e}")
            self.pygame_initialized = False
            self.music_enabled = False

    def set_music_file(self, file_path: str) -> bool:
        """
        Set the music file to play when eyes are closed.
        
        Args:
            file_path: Path to the music file (supports MP3, OGG, WAV)
            
        Returns:
            True if file is valid and set successfully, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Music file not found: {file_path}")
            return False
        
        # Check file extension
        valid_extensions = ['.mp3', '.ogg', '.wav', '.m4a']
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in valid_extensions:
            logger.error(f"Unsupported audio format: {file_ext}. Supported: {valid_extensions}")
            return False
        
        self.music_file = file_path
        logger.info(f"Music file set to: {file_path}")
        return True

    def _start_music(self) -> None:
        """Start playing music when eyes are closed."""
        if not self.music_enabled or not self.pygame_initialized or not self.music_file:
            return
        
        if self.music_playing:
            return  # Already playing
        
        try:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_playing = True
            logger.info("Started playing music for closed eyes")
        except Exception as e:
            logger.error(f"Failed to start music: {e}")

    def _stop_music(self) -> None:
        """Stop playing music when eyes are opened."""
        if not self.pygame_initialized or not self.music_playing:
            return
        
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
            logger.info("Stopped music - eyes opened")
        except Exception as e:
            logger.error(f"Failed to stop music: {e}")

    def toggle_music(self) -> bool:
        """
        Toggle music playback on/off.
        
        Returns:
            Current music enabled state
        """
        if not self.pygame_initialized:
            logger.warning("Cannot toggle music - audio system not initialized")
            return False
        
        self.music_enabled = not self.music_enabled
        if not self.music_enabled and self.music_playing:
            self._stop_music()
        
        logger.info(f"Music playback {'enabled' if self.music_enabled else 'disabled'}")
        return self.music_enabled

    def _filter_overlapping_detections(self, detections: List[Dict[str, Any]], overlap_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Filter out overlapping eye detections to reduce duplicates.
        
        Args:
            detections: List of eye detection dictionaries
            overlap_threshold: Minimum overlap ratio to consider detections as duplicates
            
        Returns:
            Filtered list of detections
        """
        if len(detections) <= 1:
            return detections
        
        # Sort by area (larger detections first)
        detections_with_area = []
        for det in detections:
            area = det['width'] * det['height']
            detections_with_area.append((det, area))
        
        detections_with_area.sort(key=lambda x: x[1], reverse=True)
        
        filtered = []
        for det, area in detections_with_area:
            overlap_found = False
            
            for existing_det in filtered:
                # Calculate overlap
                x1 = max(det['x'], existing_det['x'])
                y1 = max(det['y'], existing_det['y'])
                x2 = min(det['x'] + det['width'], existing_det['x'] + existing_det['width'])
                y2 = min(det['y'] + det['height'], existing_det['y'] + existing_det['height'])
                
                if x2 > x1 and y2 > y1:
                    intersection = (x2 - x1) * (y2 - y1)
                    union = area + (existing_det['width'] * existing_det['height']) - intersection
                    overlap_ratio = intersection / union if union > 0 else 0
                    
                    if overlap_ratio > overlap_threshold:
                        overlap_found = True
                        break
            
            if not overlap_found:
                filtered.append(det)
        
        return filtered

    def _analyze_eye_state(
        self, detection_data: List[Dict[str, Any]], frame: np.ndarray
    ) -> str:
        """
        Analyze current eye state based on detected eye count with temporal filtering.

        Args:
            detection_data: Eye detection results
            frame: Current frame for analysis

        Returns:
            Current eye state: "OPEN", "CLOSED", or "NO FACE"
        """
        current_time = time.time()

        if not detection_data:
            # No face detected
            self._update_eye_state_history("NO_FACE", current_time)
            self.eyes_closed_start_time = None
            self.current_eye_state = "NO FACE"
            return "NO FACE"

        # Analyze the first (primary) detected face
        face = detection_data[0]  # Use the first/largest face
        
        # Focus primarily on general eye detection (most reliable)
        # Filter overlapping detections to get cleaner results
        all_eyes = []
        
        # Add general eye detections
        general_eyes = face.get("eyes", [])
        all_eyes.extend(general_eyes)
        
        # Optionally add left/right eye detections if general detection missed them
        # but only if we don't have many general detections already
        if len(general_eyes) < 2:
            left_eyes = face.get("left_eyes", [])
            right_eyes = face.get("right_eyes", [])
            all_eyes.extend(left_eyes)
            all_eyes.extend(right_eyes)
        
        # Filter overlapping detections
        filtered_eyes = self._filter_overlapping_detections(all_eyes, overlap_threshold=0.4)
        total_eyes = len(filtered_eyes)
        
        # Determine eye state based on filtered count
        if total_eyes >= 2:
            # Two or more eyes detected = OPEN
            eyes_state = "OPEN"
        elif total_eyes == 0:
            # No eyes detected = CLOSED
            eyes_state = "CLOSED"
        else:
            # One eye detected = treat as partially open (OPEN for now)
            eyes_state = "OPEN"  # Treat single eye as open

        self._update_eye_state_history(eyes_state, current_time)

        # Apply temporal filtering for display
        return self._get_filtered_eye_state(current_time)

    def _update_eye_state_history(self, eyes_state: str, timestamp: float) -> None:
        """Update the history of eye states."""
        self.eye_state_history.append({"state": eyes_state, "timestamp": timestamp})

        # Keep only recent history
        if len(self.eye_state_history) > self.max_history_length:
            self.eye_state_history.pop(0)

    def _get_filtered_eye_state(self, current_time: float) -> str:
        """
        Apply temporal filtering to determine final eye state.
        - OPEN and NO FACE: Immediate response
        - CLOSED: Only report after > 500ms delay
        """
        if not self.eye_state_history:
            return "NO FACE"

        # Get the most recent state
        recent_state = self.eye_state_history[-1]["state"]
        
        # Handle NO FACE immediately
        if recent_state == "NO_FACE":
            self.eyes_closed_start_time = None
            self.current_eye_state = "NO FACE"
            # Stop music if playing
            if self.music_playing:
                self._stop_music()
            return "NO FACE"
        
        # Handle OPEN immediately
        if recent_state == "OPEN":
            self.eyes_closed_start_time = None
            self.current_eye_state = "OPEN"
            # Stop music if playing
            if self.music_playing:
                self._stop_music()
            return "OPEN"
        
        # Handle CLOSED with temporal filtering (500ms delay)
        if recent_state == "CLOSED":
            # Check if recent detections consistently show closed eyes
            recent_states = [state["state"] for state in self.eye_state_history[-3:]]
            mostly_closed = recent_states.count("CLOSED") >= len(recent_states) * 0.6
            
            if mostly_closed:
                # Eyes appear consistently closed, start/continue timing
                if self.eyes_closed_start_time is None:
                    self.eyes_closed_start_time = current_time
                    # Return current state (don't change immediately)
                    return self.current_eye_state
                
                # Check if eyes have been closed long enough
                closed_duration = current_time - self.eyes_closed_start_time
                if closed_duration >= self.eye_closed_threshold:
                    self.current_eye_state = "CLOSED"
                    # Start music when eyes are confirmed closed
                    if not self.music_playing:
                        self._start_music()
                    return "CLOSED"
                else:
                    # Still in delay period, maintain current state
                    return self.current_eye_state
            else:
                # Not consistently closed, reset timing
                self.eyes_closed_start_time = None
                self.current_eye_state = "OPEN"
                # Stop music if playing
                if self.music_playing:
                    self._stop_music()
                return "OPEN"

        return self.current_eye_state

    def detect_eyes(
        self, frame: np.ndarray, draw_rectangles: bool = True
    ) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Detect eyes in the given frame.

        Args:
            frame: Input frame as numpy array
            draw_rectangles: Whether to draw detection rectangles on the frame

        Returns:
            Tuple of (processed_frame, detection_data)
            detection_data contains list of detected faces with eye information
        """
        if self.face_cascade is None or self.eye_cascade is None:
            logger.warning("Detection models not loaded")
            return frame, []

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        detection_data = []
        processed_frame = frame.copy()

        for x, y, w, h in faces:
            face_info = {
                "face": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "eyes": [],
                "left_eyes": [],
                "right_eyes": [],
            }

            # Draw face rectangle
            if draw_rectangles:
                cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(
                    processed_frame,
                    "Face",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2,
                )

            # Extract face region for eye detection
            roi_gray = gray[y : y + h, x : x + w]
            roi_color = processed_frame[y : y + h, x : x + w]

            # Detect general eyes with more restrictive parameters
            eyes = self.eye_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.2, minNeighbors=8, minSize=(15, 15), maxSize=(50, 50)
            )

            for ex, ey, ew, eh in eyes:
                eye_info = {
                    "x": int(x + ex),
                    "y": int(y + ey),
                    "width": int(ew),
                    "height": int(eh),
                }
                face_info["eyes"].append(eye_info)

                if draw_rectangles:
                    cv2.rectangle(
                        roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2
                    )
                    cv2.putText(
                        roi_color,
                        "Eye",
                        (ex, ey - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 255, 0),
                        1,
                    )

            # Detect left eyes specifically with more restrictive parameters
            left_eyes = self.left_eye_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.2, minNeighbors=6, minSize=(15, 15), maxSize=(45, 45)
            )

            for ex, ey, ew, eh in left_eyes:
                eye_info = {
                    "x": int(x + ex),
                    "y": int(y + ey),
                    "width": int(ew),
                    "height": int(eh),
                }
                face_info["left_eyes"].append(eye_info)

                if draw_rectangles:
                    cv2.rectangle(
                        roi_color, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2
                    )
                    cv2.putText(
                        roi_color,
                        "L",
                        (ex, ey - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 0, 255),
                        1,
                    )

            # Detect right eyes specifically with more restrictive parameters
            right_eyes = self.right_eye_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.2, minNeighbors=6, minSize=(15, 15), maxSize=(45, 45)
            )

            for ex, ey, ew, eh in right_eyes:
                eye_info = {
                    "x": int(x + ex),
                    "y": int(y + ey),
                    "width": int(ew),
                    "height": int(eh),
                }
                face_info["right_eyes"].append(eye_info)

                if draw_rectangles:
                    cv2.rectangle(
                        roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 255), 2
                    )
                    cv2.putText(
                        roi_color,
                        "R",
                        (ex, ey - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 0, 255),
                        1,
                    )

            detection_data.append(face_info)

        # Analyze eye state (open/closed) with temporal filtering
        eye_state = self._analyze_eye_state(detection_data, frame)

        # Add eye state display to the processed frame
        if draw_rectangles:
            # Determine color and text based on eye state
            if eye_state == "OPEN":
                state_color = (0, 255, 0)  # Green for OPEN
                display_text = "EYES: OPEN"
            elif eye_state == "CLOSED":
                state_color = (0, 0, 255)  # Red for CLOSED
                display_text = "EYES: CLOSED"
            else:  # NO FACE
                state_color = (255, 255, 0)  # Yellow for NO FACE
                display_text = "NO FACE"

            # Add a background rectangle for better visibility
            text_size = cv2.getTextSize(
                display_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3
            )[0]
            cv2.rectangle(
                processed_frame, (5, 70), (text_size[0] + 15, 110), (0, 0, 0), -1
            )
            
            # Draw eye state text prominently
            cv2.putText(
                processed_frame,
                display_text,
                (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                state_color,
                3,
            )

        return processed_frame, detection_data

    def start_camera(self, camera_index: int = 0) -> bool:
        """
        Start the camera capture.

        Args:
            camera_index: Camera device index (0 for default camera)

        Returns:
            True if camera started successfully, False otherwise
        """
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {camera_index}")
                return False

            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            self.is_camera_active = True
            logger.info(f"Camera {camera_index} started successfully")
            return True

        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False

    def stop_camera(self) -> None:
        """Stop the camera capture and release resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.is_camera_active = False
        cv2.destroyAllWindows()
        logger.info("Camera stopped")

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.

        Returns:
            Frame as numpy array if successful, None otherwise
        """
        if not self.is_camera_active or self.camera is None:
            logger.warning("Camera is not active")
            return None

        ret, frame = self.camera.read()
        if not ret:
            logger.error("Failed to capture frame")
            return None

        return frame

    def show_camera_feed(
        self, window_name: str = "OpenEyes Camera", detect_eyes: bool = True
    ) -> None:
        """
        Display live camera feed in a window.

        Args:
            window_name: Name of the display window
            detect_eyes: Whether to perform eye detection
        """
        if not self.start_camera():
            logger.error("Failed to start camera")
            return

        logger.info(
            "Starting camera feed. Press 'q' to quit, "
            "'s' to save frame, 'd' to toggle detection, 'm' to toggle music"
        )

        try:
            while True:
                frame = self.capture_frame()
                if frame is None:
                    break

                # Perform eye detection if enabled
                if detect_eyes:
                    processed_frame, detection_data = self.detect_eyes(frame)

                    # Add detailed detection statistics
                    total_faces = len(detection_data)
                    if detection_data:
                        face = detection_data[0]  # Show stats for primary face
                        general_eyes = len(face.get("eyes", []))
                        left_eyes = len(face.get("left_eyes", []))
                        right_eyes = len(face.get("right_eyes", []))
                        total_raw_eyes = general_eyes + left_eyes + right_eyes
                        
                        # Calculate filtered count for display
                        all_eyes = []
                        all_eyes.extend(face.get("eyes", []))
                        if len(face.get("eyes", [])) < 2:
                            all_eyes.extend(face.get("left_eyes", []))
                            all_eyes.extend(face.get("right_eyes", []))
                        filtered_count = len(self._filter_overlapping_detections(all_eyes, overlap_threshold=0.4))
                        
                        cv2.putText(
                            processed_frame,
                            f"Face: {total_faces} | Raw Eyes: {total_raw_eyes} (G:{general_eyes} L:{left_eyes} R:{right_eyes}) | Filtered: {filtered_count}",
                            (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 255),
                            2,
                        )
                        
                        # Add music status
                        music_status = "🎵 ON" if self.music_enabled else "🎵 OFF"
                        music_color = (0, 255, 0) if self.music_enabled else (0, 0, 255)
                        cv2.putText(
                            processed_frame,
                            f"Music: {music_status}",
                            (10, 90),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            music_color,
                            2,
                        )
                        
                        if self.music_playing:
                            cv2.putText(
                                processed_frame,
                                "♪ Playing ♪",
                                (150, 90),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 255),
                                2,
                            )
                    else:
                        cv2.putText(
                            processed_frame,
                            "No face detected",
                            (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            2,
                        )
                else:
                    processed_frame = frame
                    detection_data = []

                # Add timestamp and info overlay
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(
                    processed_frame,
                    f"OpenEyes - {timestamp}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
                cv2.putText(
                    processed_frame,
                    "Press 'q' to quit, 's' to save, 'd' to toggle detection, 'm' to toggle music",
                    (10, processed_frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                # Display the frame
                cv2.imshow(window_name, processed_frame)

                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    filename = f"openeyes_capture_{int(time.time())}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    logger.info(f"Frame saved as {filename}")
                elif key == ord("d"):
                    detect_eyes = not detect_eyes
                    logger.info(
                        f"Eye detection {'enabled' if detect_eyes else 'disabled'}"
                    )
                elif key == ord("m"):
                    music_status = self.toggle_music()
                    logger.info(f"Music {'enabled' if music_status else 'disabled'}")

        except KeyboardInterrupt:
            logger.info("Camera feed interrupted by user")
        finally:
            # Clean up audio
            if self.music_playing:
                self._stop_music()
            self.stop_camera()

    def save_frame(self, filename: Optional[str] = None) -> str:
        """
        Save current camera frame to file.

        Args:
            filename: Optional filename. If None, generates timestamp-based name

        Returns:
            Path to saved file
        """
        frame = self.capture_frame()
        if frame is None:
            raise RuntimeError("Failed to capture frame")

        if filename is None:
            filename = f"openeyes_capture_{int(time.time())}.jpg"

        cv2.imwrite(filename, frame)
        logger.info(f"Frame saved as {filename}")
        return filename

    def process(self, data: Any) -> Any:
        """
        Process data using OpenEyes.

        Args:
            data: Input data to process

        Returns:
            Processed data
        """
        logger.info("Processing data...")
        # Add your core processing logic here
        return data

    def get_version(self) -> str:
        """Get the current version of OpenEyes."""
        from . import __version__

        return __version__

    def tune_detection_parameters(self) -> None:
        """
        Interactive tuning of detection parameters for better eye detection.
        Press keys to adjust parameters in real-time.
        """
        if not self.start_camera():
            logger.error("Failed to start camera")
            return

        # Tunable parameters
        scale_factor = 1.2
        min_neighbors = 8
        min_size = 15
        max_size = 50
        overlap_threshold = 0.4

        print("Detection Parameter Tuning")
        print("Controls:")
        print("  'w'/'s' - Increase/Decrease scale_factor (±0.05)")
        print("  'e'/'d' - Increase/Decrease min_neighbors (±1)")
        print("  'r'/'f' - Increase/Decrease min_size (±5)")
        print("  't'/'g' - Increase/Decrease max_size (±5)")
        print("  'y'/'h' - Increase/Decrease overlap_threshold (±0.1)")
        print("  'q' - Quit")

        try:
            while True:
                frame = self.capture_frame()
                if frame is None:
                    break

                # Apply current parameters to eye detection
                faces = self.face_cascade.detectMultiScale(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30),
                )

                detection_data = []
                if len(faces) > 0:
                    # Process largest face
                    face_x, face_y, face_w, face_h = faces[0]
                    roi_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)[face_y:face_y+face_h, face_x:face_x+face_w]
                    
                    # Detect eyes with current parameters
                    eyes = self.eye_cascade.detectMultiScale(
                        roi_gray,
                        scaleFactor=scale_factor,
                        minNeighbors=min_neighbors,
                        minSize=(min_size, min_size),
                        maxSize=(max_size, max_size)
                    )
                    
                    # Apply filtering
                    eye_list = [(ex, ey, ew, eh) for ex, ey, ew, eh in eyes]
                    filtered_eyes = self._filter_overlapping_detections(eye_list, overlap_threshold)
                    
                    # Draw results
                    cv2.rectangle(frame, (face_x, face_y), (face_x + face_w, face_y + face_h), (255, 0, 0), 2)
                    
                    # Draw raw eyes in red
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(frame, (face_x + ex, face_y + ey), (face_x + ex + ew, face_y + ey + eh), (0, 0, 255), 2)
                    
                    # Draw filtered eyes in green
                    for (ex, ey, ew, eh) in filtered_eyes:
                        cv2.rectangle(frame, (face_x + ex, face_y + ey), (face_x + ex + ew, face_y + ey + eh), (0, 255, 0), 3)
                    
                    # Display stats
                    cv2.putText(frame, f"Raw: {len(eyes)} | Filtered: {len(filtered_eyes)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display current parameters
                param_text = [
                    f"scale_factor: {scale_factor:.2f}",
                    f"min_neighbors: {min_neighbors}",
                    f"min_size: {min_size}",
                    f"max_size: {max_size}",
                    f"overlap_threshold: {overlap_threshold:.1f}"
                ]
                
                for i, text in enumerate(param_text):
                    cv2.putText(frame, text, (10, 60 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                
                cv2.imshow("Parameter Tuning", frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('w'):
                    scale_factor = min(2.0, scale_factor + 0.05)
                elif key == ord('s'):
                    scale_factor = max(1.05, scale_factor - 0.05)
                elif key == ord('e'):
                    min_neighbors = min(20, min_neighbors + 1)
                elif key == ord('d'):
                    min_neighbors = max(1, min_neighbors - 1)
                elif key == ord('r'):
                    min_size = min(100, min_size + 5)
                elif key == ord('f'):
                    min_size = max(5, min_size - 5)
                elif key == ord('t'):
                    max_size = min(200, max_size + 5)
                elif key == ord('g'):
                    max_size = max(min_size + 5, max_size - 5)
                elif key == ord('y'):
                    overlap_threshold = min(1.0, overlap_threshold + 0.1)
                elif key == ord('h'):
                    overlap_threshold = max(0.0, overlap_threshold - 0.1)

        finally:
            cv2.destroyAllWindows()
            self.stop_camera()
            
        print(f"\nFinal parameters:")
        print(f"scale_factor: {scale_factor}")
        print(f"min_neighbors: {min_neighbors}")
        print(f"min_size: {min_size}")
        print(f"max_size: {max_size}")
        print(f"overlap_threshold: {overlap_threshold}")


def main() -> None:
    """Main entry point for the application."""
    logger.info("Starting OpenEyes application")
    # Add your main application logic here
    print("OpenEyes is running!")


if __name__ == "__main__":
    main()
