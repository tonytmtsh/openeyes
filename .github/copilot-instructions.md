# OpenEyes Copilot Instructions

## Project Architecture

OpenEyes is a **real-time computer vision application** with a specialized **three-layer architecture**:
- **`openeyes/core.py`**: Main business logic via the `OpenEyes` class - handles camera, CV detection, and audio
- **`openeyes/cli.py`**: Click-based CLI interface with commands: `run`, `camera`, `capture`, `set-music`, `tune`
- **`openeyes/utils.py`**: Configuration management and utility functions

The entry point is defined in `pyproject.toml` as `openeyes = "openeyes.cli:main"`, enabling CLI access via both `python -m openeyes.cli` and the installed `openeyes` command.

## Core Computer Vision Pipeline

The heart of OpenEyes is **real-time eye state detection** using OpenCV Haar cascades:

1. **Multi-Model Detection**: Uses 4 cascades (face, general eye, left eye, right eye) from `cv2.data.haarcascades`
2. **Count-Based State Logic**: Face + 0 eyes = CLOSED, Face + 2+ eyes = OPEN, No face = NO FACE
3. **Temporal Filtering**: CLOSED state requires 500ms consistency (`eye_closed_threshold = 0.5`)
4. **Overlap Filtering**: `_filter_overlapping_detections()` removes duplicate eye detections
5. **Audio Integration**: pygame-based music playback triggers on CLOSED state

Key methods in `OpenEyes` class:
- `detect_eyes()`: Main CV pipeline with Haar cascade detection
- `_analyze_eye_state()`: Count-based state determination with filtering
- `_get_filtered_eye_state()`: Temporal smoothing (immediate OPEN, delayed CLOSED)

## Development Environment

This project uses a **virtual environment pattern** with specific Python executable paths:
- Python commands must use: `/Users/tonythornton/source/python/openeyes/.venv/bin/python`
- Never use bare `python` - always use the full venv path
- Dependencies: `requirements.txt` (opencv, pygame, numpy) and `requirements-dev.txt` (testing)

## Audio System Integration

**pygame-based music playback** integrated with eye state detection:
- Music files stored in `music/` folder (supports MP3, OGG, WAV, M4A)
- Pygame mixer initialized in `_initialize_audio()` with specific settings
- Music triggers: Start on CLOSED (loops), Stop on OPEN/NO_FACE (immediate)
- CLI options: `--music-file`, `set-music` command, runtime 'm' key toggle

## CLI Command Patterns

The CLI follows a **context-passing pattern** using Click's `@click.pass_context`:
```python
@cli.command()
@click.pass_context
def command_name(ctx: click.Context, ...):
    config = ctx.obj.get('config', {})
    app = OpenEyes(config)
```

**Key Commands**:
- `run --music-file path/to/file.mp3`: Main application with audio
- `camera`: Live feed with eye detection
- `tune`: Interactive parameter tuning with real-time feedback
- `set-music`: Configure music file for closed-eye playback

## Computer Vision Debugging

**Real-time parameter tuning** via `tune` command:
- Interactive key controls for Haar cascade parameters (scale_factor, minNeighbors, minSize, maxSize)
- Visual feedback shows raw vs filtered detections (red vs green rectangles)
- Overlap threshold adjustment for detection cleanup

**Debug Information** displayed on camera feed:
- Raw eye counts by type: `(G:X L:Y R:Z)` (General, Left, Right)
- Filtered count after overlap removal
- Music status and playback state
- Eye state with color coding (Green=OPEN, Red=CLOSED, Yellow=NO_FACE)

## Testing Strategy

- **Class-based tests** in `tests/test_*.py` files
- CLI testing uses `click.testing.CliRunner` with `invoke()` method
- Computer vision testing via mock frames and detection validation
- Run tests: `/Users/tonythornton/source/python/openeyes/.venv/bin/python -m pytest`

## Code Quality Workflow

Uses **pre-commit hooks** (.pre-commit-config.yaml) with these tools:
- **Black**: Code formatting (line-length: 88)
- **Flake8**: Linting with `.flake8` config
- **MyPy**: Type checking with strict settings in `pyproject.toml`

## Key Conventions

1. **Logging**: Use module-level logger `logger = logging.getLogger(__name__)` 
2. **Type hints**: Required for all functions (enforced by mypy)
3. **CV Data Structures**: Detection data as `List[Dict[str, Any]]` with standardized keys
4. **Error handling**: CLI commands use `click.echo(err=True)` and `sys.exit(1)` for errors
5. **State management**: Temporal filtering via history lists and timestamps

## Running Commands

Always prefix Python commands with the venv path:
```bash
# Correct
/Users/tonythornton/source/python/openeyes/.venv/bin/python -m openeyes.cli run --music-file music/wakeup.mp3
/Users/tonythornton/source/python/openeyes/.venv/bin/python -m pytest

# Wrong
python -m openeyes.cli run
python -m pytest
```
