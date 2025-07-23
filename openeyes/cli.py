"""
Command Line Interface for OpenEyes.
"""

import click
from typing import Optional
import sys
import logging

from .core import OpenEyes, main as core_main
from .utils import load_config, save_config

# Set up logger for CLI
logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=str, help='Path to configuration file')
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
            ctx.obj['config'] = load_config(config)
            click.echo(f"Loaded configuration from {config}")
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            sys.exit(1)
    else:
        ctx.obj['config'] = {}


@cli.command()
@click.option('--input', '-i', type=str, help='Input data or file path')
@click.option('--output', '-o', type=str, help='Output file path')
@click.pass_context
def run(ctx: click.Context, input: Optional[str], output: Optional[str]) -> None:
    """
    Run the main OpenEyes application.
    """
    click.echo("Starting OpenEyes...")
    
    # Initialize OpenEyes with configuration
    app = OpenEyes(ctx.obj.get('config'))
    
    # Process input if provided
    if input:
        click.echo(f"Processing input: {input}")
        result = app.process(input)
        
        if output:
            # Save result to output file
            with open(output, 'w') as f:
                f.write(str(result))
            click.echo(f"Result saved to {output}")
        else:
            click.echo(f"Result: {result}")
    else:
        # Run default behavior - just log that we're running
        logger.info("Running OpenEyes with default behavior")
        click.echo("OpenEyes is running!")


@cli.command()
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'yaml', 'table']), 
              default='table',
              help='Output format')
@click.pass_context
def info(ctx: click.Context, output_format: str) -> None:
    """
    Display information about OpenEyes.
    """
    app = OpenEyes(ctx.obj.get('config'))
    version = app.get_version()
    
    if output_format == 'json':
        import json
        info_data = {
            'name': 'OpenEyes',
            'version': version,
            'description': 'A Python project'
        }
        click.echo(json.dumps(info_data, indent=2))
    elif output_format == 'yaml':
        click.echo(f"name: OpenEyes")
        click.echo(f"version: {version}")
        click.echo(f"description: A Python project")
    else:  # table format
        click.echo("OpenEyes Information")
        click.echo("=" * 20)
        click.echo(f"Version: {version}")
        click.echo(f"Description: A Python project")


@cli.command()
@click.option('--output', '-o', type=str, required=True, 
              help='Path to save the configuration file')
@click.pass_context
def init_config(ctx: click.Context, output: str) -> None:
    """
    Create a default configuration file.
    """
    default_config = {
        "app_name": "OpenEyes",
        "debug": False,
        "log_level": "INFO",
        "settings": {
            "max_retries": 3,
            "timeout": 30
        }
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


if __name__ == '__main__':
    main()
