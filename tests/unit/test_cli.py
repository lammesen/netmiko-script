"""Tests for CLI module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

from src.netmiko_collector.cli import app
from src.netmiko_collector.models import Device, Command, ExecutionResult, ExecutionStatus
from src.netmiko_collector.executor import ExecutionStats


runner = CliRunner()


@pytest.fixture
def temp_devices_file(tmp_path):
    """Create a temporary devices CSV file."""
    devices_file = tmp_path / "devices.csv"
    devices_file.write_text(
        "hostname,ip,username,password\n"
        "router1,192.168.1.1,admin,password123\n"
        "router2,192.168.1.2,admin,password123\n"
    )
    return devices_file


@pytest.fixture
def temp_commands_file(tmp_path):
    """Create a temporary commands file."""
    commands_file = tmp_path / "commands.txt"
    commands_file.write_text("show version\nshow ip interface brief\n")
    return commands_file


@pytest.fixture
def mock_devices():
    """Create mock devices."""
    return [
        Device(hostname="192.168.1.1", username="admin", password="pass"),
        Device(hostname="192.168.1.2", username="admin", password="pass"),
    ]


@pytest.fixture
def mock_commands():
    """Create mock commands."""
    return [
        Command(command="show version"),
        Command(command="show ip interface brief"),
    ]


@pytest.fixture
def mock_results():
    """Create mock execution results."""
    return [
        ExecutionResult(
            device=Device(hostname="192.168.1.1"),
            command=Command(command="show version"),
            output="Cisco IOS Version 15.1",
            duration=1.5,
            status=ExecutionStatus.SUCCESS,
        ),
        ExecutionResult(
            device=Device(hostname="192.168.1.2"),
            command=Command(command="show version"),
            output="Cisco IOS Version 15.2",
            duration=1.3,
            status=ExecutionStatus.SUCCESS,
        ),
    ]


class TestCLI:
    """Test suite for CLI commands."""

    def test_version_flag(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "netmiko-collector version" in result.stdout

    def test_help_flag(self):
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Network device automation tool" in result.stdout
        assert "--devices" in result.stdout
        assert "--commands" in result.stdout

    def test_missing_required_options(self):
        """Test that missing required options causes error."""
        result = runner.invoke(app, [])
        assert result.exit_code != 0

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    @patch("src.netmiko_collector.cli.get_formatter")
    def test_successful_execution(
        self,
        mock_get_formatter,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
        mock_results,
    ):
        """Test successful command execution."""
        output_file = tmp_path / "output.csv"
        
        # Setup mocks
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        
        stats = ExecutionStats()
        stats.total_devices = 2
        stats.completed_devices = 2
        stats.successful_devices = 2
        stats.failed_devices = 0
        stats.start_time = 0.0
        stats.end_time = 2.8
        mock_execute.return_value = stats
        
        mock_formatter = Mock()
        mock_formatter.format.return_value = "device,command,output\nrouter1,show version,output1\n"
        mock_get_formatter.return_value = mock_formatter
        
        # Run CLI
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
                "--output", str(output_file),
            ],
        )
        
        # Assertions
        assert result.exit_code == 0
        assert mock_load_devices.called
        assert mock_load_commands.called
        assert mock_execute.called
        assert output_file.exists()

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    @patch("src.netmiko_collector.cli.get_formatter")
    def test_execution_with_failures(
        self,
        mock_get_formatter,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
    ):
        """Test execution with some failures."""
        output_file = tmp_path / "output.csv"
        
        # Setup mocks
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        
        stats = ExecutionStats(
            total=2,
            completed=2,
            successful=1,
            failed=1,
            duration=2.8,
        )
        mock_execute.return_value = stats
        
        mock_formatter = Mock()
        mock_formatter.format.return_value = "device,command,output\nrouter1,show version,output1\n"
        mock_get_formatter.return_value = mock_formatter
        
        # Run CLI
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
                "--output", str(output_file),
            ],
        )
        
        # Should exit with code 1 due to failures
        assert result.exit_code == 1

    def test_nonexistent_devices_file(self, temp_commands_file, tmp_path):
        """Test error handling for nonexistent devices file."""
        result = runner.invoke(
            app,
            [
                "--devices", str(tmp_path / "nonexistent.csv"),
                "--commands", str(temp_commands_file),
            ],
        )
        assert result.exit_code != 0

    def test_nonexistent_commands_file(self, temp_devices_file, tmp_path):
        """Test error handling for nonexistent commands file."""
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(tmp_path / "nonexistent.txt"),
            ],
        )
        assert result.exit_code != 0

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    @patch("src.netmiko_collector.cli.get_formatter")
    def test_custom_output_format(
        self,
        mock_get_formatter,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
    ):
        """Test custom output format."""
        output_file = tmp_path / "output.json"
        
        # Setup mocks
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        
        stats = ExecutionStats()
        stats.total_devices = 2
        stats.completed_devices = 2
        stats.successful_devices = 2
        stats.failed_devices = 0
        stats.start_time = 0.0
        stats.end_time = 2.8
        mock_execute.return_value = stats
        
        mock_formatter = Mock()
        mock_formatter.format.return_value = '{"results": []}'
        mock_get_formatter.return_value = mock_formatter
        
        # Run CLI with JSON format
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
                "--output", str(output_file),
                "--format", "json",
            ],
        )
        
        assert result.exit_code == 0
        assert mock_get_formatter.called_with("json")

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    @patch("src.netmiko_collector.cli.get_formatter")
    def test_custom_workers(
        self,
        mock_get_formatter,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
    ):
        """Test custom number of workers."""
        output_file = tmp_path / "output.csv"
        
        # Setup mocks
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        
        stats = ExecutionStats()
        stats.total_devices = 2
        stats.completed_devices = 2
        stats.successful_devices = 2
        stats.failed_devices = 0
        stats.start_time = 0.0
        stats.end_time = 2.8
        mock_execute.return_value = stats
        
        mock_formatter = Mock()
        mock_formatter.format.return_value = "output"
        mock_get_formatter.return_value = mock_formatter
        
        # Run CLI with custom workers
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
                "--output", str(output_file),
                "--workers", "5",
            ],
        )
        
        assert result.exit_code == 0

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    def test_load_devices_error(
        self,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
    ):
        """Test error handling when loading devices fails."""
        mock_load_devices.side_effect = ValueError("Invalid device file")
        
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
            ],
        )
        
        assert result.exit_code == 3  # Invalid input error

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    def test_load_commands_error(
        self,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
    ):
        """Test error handling when loading commands fails."""
        mock_load_devices.return_value = mock_devices
        mock_load_commands.side_effect = ValueError("Invalid commands file")
        
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
            ],
        )
        
        assert result.exit_code == 3  # Invalid input error

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    def test_execution_error(
        self,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
    ):
        """Test error handling during execution."""
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        mock_execute.side_effect = Exception("Execution failed")
        
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
            ],
        )
        
        assert result.exit_code == 1  # Generic error

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    @patch("src.netmiko_collector.cli.get_formatter")
    def test_progress_callback(
        self,
        mock_get_formatter,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
        mock_results,
    ):
        """Test that progress callback is set up correctly."""
        output_file = tmp_path / "output.csv"
        
        # Setup mocks
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        
        def execute_side_effect(devices, commands, max_workers, progress_callback):
            # Simulate calling progress callback for each result
            for result in mock_results:
                progress_callback(result)
            return ExecutionStats(
                total=2,
                completed=2,
                successful=2,
                failed=0,
                duration=2.8,
            )
        
        mock_execute.side_effect = execute_side_effect
        
        mock_formatter = Mock()
        mock_formatter.format.return_value = "output"
        mock_get_formatter.return_value = mock_formatter
        
        # Run CLI
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
                "--output", str(output_file),
            ],
        )
        
        assert result.exit_code == 0
        # Verify execute was called with progress_callback parameter
        call_kwargs = mock_execute.call_args[1]
        assert "progress_callback" in call_kwargs
        assert callable(call_kwargs["progress_callback"])

    @patch("src.netmiko_collector.cli.load_devices_from_csv")
    @patch("src.netmiko_collector.cli.load_commands_from_file")
    @patch("src.netmiko_collector.cli.execute_on_devices")
    @patch("src.netmiko_collector.cli.get_formatter")
    def test_no_results(
        self,
        mock_get_formatter,
        mock_execute,
        mock_load_commands,
        mock_load_devices,
        temp_devices_file,
        temp_commands_file,
        tmp_path,
        mock_devices,
        mock_commands,
    ):
        """Test handling of no results."""
        output_file = tmp_path / "output.csv"
        
        # Setup mocks
        mock_load_devices.return_value = mock_devices
        mock_load_commands.return_value = mock_commands
        
        # No results scenario
        def execute_side_effect(devices, commands, max_workers, progress_callback):
            # Don't call progress_callback
            return ExecutionStats(
                total=2,
                completed=0,
                successful=0,
                failed=2,
                duration=0.1,
            )
        
        mock_execute.side_effect = execute_side_effect
        
        mock_formatter = Mock()
        mock_get_formatter.return_value = mock_formatter
        
        # Run CLI
        result = runner.invoke(
            app,
            [
                "--devices", str(temp_devices_file),
                "--commands", str(temp_commands_file),
                "--output", str(output_file),
            ],
        )
        
        # Should handle empty results gracefully
        assert "No results to write" in result.stdout or result.exit_code == 1
