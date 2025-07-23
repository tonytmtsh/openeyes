# OpenEyes Copilot Instructions

## Project Architecture

OpenEyes is a **real-time computer vision application** with **dual implementation approaches**:

### 1. Single-File Minimal Implementation (`simple_openeyes.py`)
- **Complete standalone script** - zero dependencies on modular architecture
- **Direct execution**: `python simple_openeyes.py` (using full venv path)
- **All functionality in one file**: CV pipeline, audio, main loop, global state management
- **Optimized for simplicity**: Minimal API surface, straightforward debugging

### 2. Multi-File Modular Architecture (`openeyes/` package)
- **`openeyes/core.py`**: Main business logic via the `OpenEyes` class - handles camera, CV detection, and audio
- **`openeyes/cli.py`**: Click-based CLI interface with commands: `run`, `camera`, `capture`, `set-music`, `tune`
- **`openeyes/utils.py`**: Configuration management and utility functions
- **Entry point**: `pyproject.toml` defines `openeyes = "openeyes.cli:main"` for CLI access

Both implementations share the **same core computer vision pipeline** and **audio integration** but differ in code organization.

## When to Use Which Implementation

### Choose Single-File (`simple_openeyes.py`) for:
- **Rapid prototyping** and initial concept validation
- **Educational purposes** - easier to understand the complete flow
- **Debugging CV algorithms** - all logic in one place
- **Quick fixes** - minimal context switching between files
- **Standalone deployment** - zero dependency on package structure

### Choose Modular (`openeyes/` package) for:
- **Production applications** with full CLI interface
- **Feature development** - adding new commands, configuration options
- **Testing** - comprehensive test coverage via class interfaces
- **Parameter tuning** - interactive `tune` command with real-time feedback
- **Extensibility** - adding new audio formats, detection models, etc.

## Core Computer Vision Pipeline

The heart of OpenEyes is **real-time eye state detection** using OpenCV Haar cascades - **identical logic in both implementations**:

1. **Multi-Model Detection**: Uses 4 cascades (face, general eye, left eye, right eye) from `cv2.data.haarcascades`
2. **Count-Based State Logic**: Face + 0 eyes = CLOSED, Face + 2+ eyes = OPEN, No face = NO FACE  
3. **Temporal Filtering**: CLOSED state requires 500ms consistency (`CLOSED_THRESHOLD = 0.5`)
4. **Overlap Filtering**: Removes duplicate eye detections using area-based overlap calculations
5. **Audio Integration**: pygame-based music playback triggers on CLOSED state

### Implementation-Specific Details:

**Single-File (`simple_openeyes.py`)**:
- `analyze_eye_state()`: Main state determination with global variables
- `main()`: Combined CV pipeline and display loop 
- Global state: `eye_state_history`, `eyes_closed_start_time`, `current_state`

**Modular (`openeyes/core.py`)**:
- `detect_eyes()`: Main CV pipeline with Haar cascade detection
- `_analyze_eye_state()`: Count-based state determination with filtering  
- `_get_filtered_eye_state()`: Temporal smoothing (immediate OPEN, delayed CLOSED)

## Development Environment

This project uses a **virtual environment pattern** with specific Python executable paths:
- Python commands must use: `/Users/tonythornton/source/python/openeyes/.venv/bin/python`
- Never use bare `python` - always use the full venv path
- Dependencies: `requirements.txt` (opencv, pygame, numpy) and `requirements-dev.txt` (testing)

## Audio System Integration

**pygame-based music playback** integrated with eye state detection - **consistent across both implementations**:
- Music files stored in `music/` folder (supports MP3, OGG, WAV, M4A)
- Pygame mixer initialized with specific settings: `frequency=22050, size=-16, channels=2, buffer=512`
- Music triggers: Start on CLOSED (loops), Stop on OPEN/NO_FACE (immediate)

### Implementation-Specific Audio Details:

**Single-File (`simple_openeyes.py`)**:
- `init_audio()`: Initialize pygame mixer
- `start_music()` / `stop_music()`: Global functions with `MUSIC_FILE` constant
- Global variable: `music_playing` for state tracking

**Modular (`openeyes/core.py`)**:
- `_initialize_audio()`: Class method initialization
- `_start_music()` / `_stop_music()`: Class methods with configurable file path
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

**Real-time parameter tuning** available in both implementations:

### Single-File (`simple_openeyes.py`)**:
- Built-in debug overlays: Eye count, face count, state history, timing info
- Visual feedback: Color-coded rectangles and state text on camera feed
- Simplified parameter access via direct variable modification

### Modular (`openeyes/core.py`)**:
- **Interactive `tune` command**: Real-time parameter adjustment with key controls
- **Visual feedback**: Raw vs filtered detections (red vs green rectangles)
- **Overlap threshold adjustment**: Fine-tune detection cleanup in real-time

**Debug Information** displayed on camera feed (both implementations):
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
/Users/tonythornton/source/python/openeyes/.venv/bin/python simple_openeyes.py
/Users/tonythornton/source/python/openeyes/.venv/bin/python -m openeyes.cli run --music-file music/wakeup.mp3
/Users/tonythornton/source/python/openeyes/.venv/bin/python -m pytest

# Wrong
python simple_openeyes.py
python -m openeyes.cli run
python -m pytest
```
