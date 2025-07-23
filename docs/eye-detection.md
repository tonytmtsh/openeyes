# Eye Detection Feature

## Overview

OpenEyes now includes comprehensive eye detection capabilities using OpenCV's
Haar cascade classifiers, with advanced **eye open/closed state detection**.
This feature can detect faces, multiple types of eyes, and determine whether
eyes are open or closed in real-time camera feeds or static images.

## Key Features

- **Real-time Eye State Detection**: Detects when eyes are OPEN or CLOSED
- **Temporal Filtering**: Only reports CLOSED after eyes have been closed for
  more than 500ms
- **Visual Feedback**: Displays "EYES: OPEN" or "EYES: CLOSED" prominently on
  screen
- **Multi-model Detection**: Uses four different Haar cascade models for
  comprehensive detection
- **Robust Analysis**: Combines multiple detection methods for accurate results

## Detection Models

The eye detection system uses four different Haar cascade models:

1. **Face Detection**: `haarcascade_frontalface_default.xml` - Detects frontal
   faces
2. **General Eye Detection**: `haarcascade_eye.xml` - Detects general eye
   patterns
3. **Left Eye Detection**: `haarcascade_lefteye_2splits.xml` - Specifically
   trained for left eyes
4. **Right Eye Detection**: `haarcascade_righteye_2splits.xml` - Specifically
   trained for right eyes

## Usage

### CLI Commands

#### View Camera Feed with Eye Detection

```bash
openeyes camera
```

This will:

- Start your default camera (camera index 0)
- Display a live feed with eye detection overlays
- Show detection statistics (number of faces and eyes detected)
- **Display real-time eye state (OPEN/CLOSED) with 500ms delay filtering**
- Display interactive controls

#### Interactive Controls

- **'q'**: Quit the camera feed
- **'s'**: Save current frame with detections
- **'d'**: Toggle eye detection on/off

### Programmatic Usage

```python
from openeyes.core import OpenEyes
import cv2

# Initialize OpenEyes
app = OpenEyes()

# Start camera and show feed with eye detection
app.show_camera_feed(detect_eyes=True)

# Or capture a single frame and detect eyes
frame = app.capture_frame()
if frame is not None:
    processed_frame, detection_data = app.detect_eyes(frame)
    
    # detection_data contains detailed information about detected faces and eyes
    for face in detection_data:
        print(f"Face at: {face['face']}")
        print(f"General eyes: {len(face['eyes'])}")
        print(f"Left eyes: {len(face['left_eyes'])}")
        print(f"Right eyes: {len(face['right_eyes'])}")
```

## Detection Output

The `detect_eyes()` method returns a tuple containing:

1. **Processed Frame**: The original frame with detection rectangles drawn (if
   enabled)
2. **Detection Data**: A list of dictionaries, one for each detected face

### Detection Data Structure

```python
{
    'face': {'x': int, 'y': int, 'width': int, 'height': int},
    'eyes': [{'x': int, 'y': int, 'width': int, 'height': int}, ...],
    'left_eyes': [{'x': int, 'y': int, 'width': int, 'height': int}, ...],
    'right_eyes': [{'x': int, 'y': int, 'width': int, 'height': int}, ...]
}
```

## Eye State Detection

### How It Works

The system uses a **count-based approach** to determine eye state by analyzing
the number of detected eyes:

1. **Eye Count Analysis**: Counts total detected eyes from all detection models
   (general, left, right)
2. **State Classification**:
   - **NO FACE**: No face detected → Yellow "NO FACE"
   - **EYES OPEN**: Face detected with 2+ eyes → Green "EYES: OPEN" (immediate)
   - **EYES CLOSED**: Face detected with 0 eyes → Red "EYES: CLOSED" (500ms
     delay)
   - **Partial Detection**: Face detected with 1 eye → Treated as OPEN
3. **Temporal Filtering**: Only CLOSED state requires 500ms confirmation to
   avoid false positives
4. **Visual Display**: Real-time feedback with color-coded status

### Detection Logic

- **Face + 0 Eyes = CLOSED** (after 500ms delay)
- **Face + 1 Eye = OPEN** (immediate - handles partial occlusion)
- **Face + 2+ Eyes = OPEN** (immediate)
- **No Face = NO FACE** (immediate)

### Algorithm Benefits

- **Simple & Reliable**: Based on existing eye detection counts rather than
  complex calculations
- **Fast Response**: OPEN states respond immediately for better user experience
- **Stable CLOSED Detection**: 500ms delay prevents false CLOSED readings from
  blinking
- **Robust**: Handles partial occlusion (glasses, hair, hand) gracefully

### Visual Feedback

- **"EYES: OPEN"** - Green text when 1+ eyes detected
- **"EYES: CLOSED"** - Red text when 0 eyes detected for >500ms
- **"NO FACE"** - Yellow text when no face is detected
- **Detection Stats**: Shows detailed eye counts (G:general L:left R:right)##
  Visual Indicators

When detection rectangles are enabled:

- **Blue rectangles**: Detected faces (labeled "Face")
- **Green rectangles**: General eye detections (labeled "Eye")
- **Red rectangles**: Left eye detections (labeled "L")
- **Magenta rectangles**: Right eye detections (labeled "R")

## Configuration

The detection parameters can be adjusted by modifying the `detect_eyes()` method
parameters:

- `scaleFactor`: How much the image size is reduced at each scale (default: 1.1)
- `minNeighbors`: How many neighbors each detection should have to be valid
  (default: 5)
- `minSize`: Minimum possible face/eye size (default: varies by detector)

## Troubleshooting

### Models Not Loading

If you see "Some detection models failed to load", it means OpenCV's Haar
cascade files are not available. This can happen if:

- OpenCV was not installed properly
- The cascade files are missing from your OpenCV installation

### Poor Detection Performance

If detection is not working well:

- Ensure good lighting
- Face the camera directly
- Remove glasses if they interfere with detection
- Adjust camera distance (try 1-3 feet from camera)

### Camera Issues

If the camera doesn't start:

- Check that no other applications are using the camera
- Try a different camera index: `openeyes camera --camera 1`
- Verify camera permissions on macOS/Windows

## Technical Details

- **Detection Method**: Haar Cascade Classifiers
- **Processing**: Real-time frame-by-frame detection
- **Performance**: Optimized for standard webcam resolutions (640x480)
- **Dependencies**: OpenCV, NumPy
- **Color Space**: BGR to Grayscale conversion for detection

The eye detection feature integrates seamlessly with the existing OpenEyes
architecture and follows the same configuration and error handling patterns.
