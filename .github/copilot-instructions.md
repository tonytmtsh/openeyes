# OpenEyes Copilot Instructions

## Project Architecture

OpenEyes is a modern Python application with a **three-layer architecture**:
- **`openeyes/core.py`**: Main business logic via the `OpenEyes` class
- **`openeyes/cli.py`**: Click-based CLI interface with commands: `run`, `info`, `init-config`
- **`openeyes/utils.py`**: Configuration management and utility functions

The entry point is defined in `pyproject.toml` as `openeyes = "openeyes.cli:main"`, enabling CLI access via both `python -m openeyes.cli` and the installed `openeyes` command.

## Development Environment

This project uses a **virtual environment pattern** with specific Python executable paths:
- Python commands must use: `/Users/tonythornton/source/python/openeyes/.venv/bin/python`
- Never use bare `python` - always use the full venv path
- Dependencies are split: `requirements.txt` (runtime) and `requirements-dev.txt` (development)

## CLI Command Patterns

The CLI follows a **context-passing pattern** using Click's `@click.pass_context`:
```python
@cli.command()
@click.pass_context
def command_name(ctx: click.Context, ...):
    config = ctx.obj.get('config', {})
    app = OpenEyes(config)
```

Configuration is loaded at the CLI root level and passed down via `ctx.obj['config']`.

## Configuration System

JSON-based configuration with a **default structure** in `cli.py:init_config()`:
```json
{
    "app_name": "OpenEyes",
    "debug": false,
    "log_level": "INFO",
    "settings": {
        "max_retries": 3,
        "timeout": 30
    }
}
```

Load/save via `utils.load_config()` and `utils.save_config()` with proper error handling.

## Testing Strategy

- **Class-based tests** in `tests/test_*.py` files
- CLI testing uses `click.testing.CliRunner` with `invoke()` method
- Coverage target: 86%+ (current coverage shown in pytest output)
- Run tests: `/Users/tonythornton/source/python/openeyes/.venv/bin/python -m pytest`

## Code Quality Workflow

Uses **pre-commit hooks** (.pre-commit-config.yaml) with these tools:
- **Black**: Code formatting (line-length: 88)
- **Flake8**: Linting with `.flake8` config
- **MyPy**: Type checking with strict settings in `pyproject.toml`
- Install hooks: `pre-commit install`

## Key Conventions

1. **Logging**: Use module-level logger `logger = logging.getLogger(__name__)` 
2. **Type hints**: Required for all functions (enforced by mypy)
3. **Import structure**: Core imports utils, CLI imports both core and utils
4. **Error handling**: CLI commands use `click.echo(err=True)` and `sys.exit(1)` for errors
5. **Package structure**: `openeyes/__init__.py` exposes main classes via `__all__`

## Running Commands

Always prefix Python commands with the venv path:
```bash
# Correct
/Users/tonythornton/source/python/openeyes/.venv/bin/python -m pytest
/Users/tonythornton/source/python/openeyes/.venv/bin/python -m openeyes.cli run

# Wrong
python -m pytest
python -m openeyes.cli run
```
