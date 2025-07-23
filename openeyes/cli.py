"""
Command Line Interface for OpenEyes.
"""

import click
from typing import Optional
import sys
import logging

from .core import OpenEyes
from .utils import load_config, save_config

# Set up logger for CLI
logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=str, help="Path to configuration file")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, config: Optional[str]) -> None:
    """
    OpenEyes CLI - A powerful Python application.

    Use --help with any command for more information.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)

    # Set up logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Load configuration if provided
    if config:
        try:
            ctx.obj["config"] = load_config(config)
            click.echo(f"Loaded configuration from {config}")
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)
    else:
        ctx.obj["config"] = {}


@cli.command()
@click.option("--input", "-i", type=str, help="Input data or file path")
@click.option("--output", "-o", type=str, help="Output file path")
@click.option(
    "--music-file",
    type=click.Path(exists=True),
    help="Path to music file to play when eyes are closed (MP3, OGG, WAV)",
)
@click.pass_context
def run(ctx: click.Context, input: Optional[str], output: Optional[str], music_file: Optional[str]) -> None:
    """
    Run the main OpenEyes application.
    """
    click.echo("Starting OpenEyes...")

    # Initialize OpenEyes with configuration
    app = OpenEyes(ctx.obj.get("config"))
    
    # Set music file if provided
    if music_file:
        if app.set_music_file(music_file):
            click.echo(f"Music file set: {music_file}")
        else:
            click.echo(f"Failed to set music file: {music_file}", err=True)

    # Process input if provided
    if input:
        click.echo(f"Processing input: {input}")
        result = app.process(input)

        if output:
            # Save result to output file
            with open(output, "w") as f:
                f.write(str(result))
            click.echo(f"Result saved to {output}")
        else:
            click.echo(f"Result: {result}")
    else:
        # Run default behavior - start camera with eye detection
        logger.info("Running OpenEyes with default behavior")
        try:
            app.show_camera_feed()
        except KeyboardInterrupt:
            click.echo("\nOpenEyes stopped by user")
        except Exception as e:
            logger.error(f"Error running OpenEyes: {e}")
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)


@cli.command()
@click.option("--camera", "-cam", type=int, default=0, help="Camera index (default: 0)")
@click.pass_context
def camera(ctx: click.Context, camera: int) -> None:
    """
    Show live camera feed.
    """
    click.echo(f"Starting camera {camera}...")

    # Initialize OpenEyes with configuration
    app = OpenEyes(ctx.obj.get("config"))

    try:
        app.show_camera_feed(f"OpenEyes Camera {camera}")
    except Exception as e:
        click.echo(f"Error accessing camera: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--camera", "-cam", type=int, default=0, help="Camera index (default: 0)")
@click.option("--output", "-o", type=str, help="Output filename (optional)")
@click.pass_context
def capture(ctx: click.Context, camera: int, output: Optional[str]) -> None:
    """
    Capture a single frame from camera.
    """
    click.echo(f"Capturing from camera {camera}...")

    # Initialize OpenEyes with configuration
    app = OpenEyes(ctx.obj.get("config"))

    try:
        if app.start_camera(camera):
            filename = app.save_frame(output)
            click.echo(f"Frame captured and saved as: {filename}")
            app.stop_camera()
        else:
            click.echo("Failed to start camera", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error capturing frame: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("music_file", type=click.Path(exists=True))
@click.pass_context
def set_music(ctx: click.Context, music_file: str) -> None:
    """Set music file to play when eyes are closed."""
    config = ctx.obj.get("config", {})
    app = OpenEyes(config)
    
    if app.set_music_file(music_file):
        click.echo(f"Music file set successfully: {music_file}")
    else:
        click.echo(f"Failed to set music file: {music_file}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def tune(ctx: click.Context) -> None:
    """Interactive parameter tuning for eye detection."""
    config = ctx.obj.get("config", {})
    app = OpenEyes(config)
    
    try:
        app.tune_detection_parameters()
    except KeyboardInterrupt:
        click.echo("\nParameter tuning stopped by user", err=True)
    except Exception as e:
        logger.error(f"Parameter tuning failed: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "yaml", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def info(ctx: click.Context, output_format: str) -> None:
    """
    Display information about OpenEyes.
    """
    app = OpenEyes(ctx.obj.get("config"))
    version = app.get_version()

    if output_format == "json":
        import json

        info_data = {
            "name": "OpenEyes",
            "version": version,
            "description": "A Python project",
        }
        click.echo(json.dumps(info_data, indent=2))
    elif output_format == "yaml":
        click.echo("name: OpenEyes")
        click.echo(f"version: {version}")
        click.echo("description: A Python project")
    else:  # table format
        click.echo("OpenEyes Information")
        click.echo("=" * 20)
        click.echo(f"Version: {version}")
        click.echo("Description: A Python project")


@cli.command()
@click.option(
    "--output",
    "-o",
    type=str,
    required=True,
    help="Path to save the configuration file",
)
@click.pass_context
def init_config(ctx: click.Context, output: str) -> None:
    """
    Create a default configuration file.
    """
    default_config = {
        "app_name": "OpenEyes",
        "debug": False,
        "log_level": "INFO",
        "settings": {"max_retries": 3, "timeout": 30},
    }

    try:
        save_config(default_config, output)
        click.echo(f"Default configuration saved to {output}")
    except Exception as e:
        click.echo(f"Error saving configuration: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
