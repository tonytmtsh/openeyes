"""
Tests for the CLI module.
"""

import pytest
from click.testing import CliRunner
from openeyes.cli import cli


class TestCLI:
    """Test cases for the CLI interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "OpenEyes CLI" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
    
    def test_run_command(self):
        """Test the run command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['run'])
        assert result.exit_code == 0
        assert "Starting OpenEyes" in result.output
    
    def test_info_command_table(self):
        """Test the info command with table format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info'])
        assert result.exit_code == 0
        assert "OpenEyes Information" in result.output
        assert "Version:" in result.output
    
    def test_info_command_json(self):
        """Test the info command with JSON format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info', '--format', 'json'])
        assert result.exit_code == 0
        assert '"name"' in result.output
        assert '"OpenEyes"' in result.output
    
    def test_info_command_yaml(self):
        """Test the info command with YAML format."""
        runner = CliRunner()
        result = runner.invoke(cli, ['info', '--format', 'yaml'])
        assert result.exit_code == 0
        assert "name: OpenEyes" in result.output
    
    def test_init_config_command(self):
        """Test the init-config command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['init-config', '--output', 'test_config.json'])
            assert result.exit_code == 0
            assert "Default configuration saved" in result.output
            
            # Verify the file was created
            import os
            assert os.path.exists('test_config.json')
    
    def test_run_with_verbose(self):
        """Test running with verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--verbose', 'run'])
        assert result.exit_code == 0
