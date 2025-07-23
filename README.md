# OpenEy- **Advanced Eye Detection**: Multi-model eye detection using Haar cascades

- Face detection
- General eye detection
- Left/right eye specific detection
- **Eye Open/Closed State Detection**: Count-based detection with 500ms
  filtering
  - Face + 0 eyes = CLOSED (after delay)
  - Face + 2+ eyes = OPEN (immediate)
  - No face = NO FACE (immediate) Python application for real-time camera access
    and computer vision, featuring advanced eye detection capabilities using
    OpenCV Haar cascades.

## Features

- **Real-time Camera Access**: Live camera feed with interactive controls
- **Advanced Eye Detection**: Multi-model eye detection using Haar cascades
  - Face detection
  - General eye detection
  - Left/right eye specific detection
  - **Eye Open/Closed State Detection**: Real-time detection with 500ms
    filtering
- **Visual Feedback**: Prominent display of "EYES: OPEN" or "EYES: CLOSED"
  status
- **Interactive Controls**: Save frames, toggle detection, real-time feedback
- **CLI Interface**: Easy-to-use command-line interface
- **Extensible Architecture**: Clean, modular design for adding new features##
  Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd openeyes
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start - Camera with Eye Detection

```bash
# Start live camera feed with eye detection
openeyes camera

# Show help for camera options
openeyes camera --help
```

### CLI Commands

```bash
# Show application information
openeyes info

# Initialize configuration file
openeyes init-config

# Capture a single frame
openeyes capture
```

### Python API

```python
from openeyes.core import OpenEyes

# Initialize OpenEyes
app = OpenEyes()

# Start camera with eye detection
app.show_camera_feed(detect_eyes=True)

# Or capture and analyze a single frame
frame = app.capture_frame()
if frame is not None:
    processed_frame, detections = app.detect_eyes(frame)
    print(f"Found {len(detections)} faces")
```

For detailed eye detection documentation, see
[docs/eye-detection.md](docs/eye-detection.md).

## Development

1. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

2. Run tests:

```bash
pytest
```

3. Run linting:

```bash
flake8 openeyes/
black openeyes/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

[Choose an appropriate license]
