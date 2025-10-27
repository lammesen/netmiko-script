"""Tests for ui module."""

from unittest.mock import Mock, patch

import pytest

from src.netmiko_collector.models import (
    Device,
    Command,
    ExecutionResult,
    ExecutionStatus,
    DeviceType,
    AuthMethod,
)
from src.netmiko_collector.ui import (
    create_device_summary,
    create_panel,
    create_progress_bar,
    create_results_table,
    print_error,
    print_success,
    print_warning,
)


# Test fixtures
@pytest.fixture
def device():
    """Create a test device."""
    return Device(
        hostname="192.168.1.1",
        device_type=DeviceType.CISCO_IOS,
        username="admin",
        password="password",
    )


@pytest.fixture
def command():
    """Create a test command."""
    return Command(command="show version")


class TestCreateProgressBar:
    """Tests for create_progress_bar function."""

    def test_creates_progress_bar_with_default_description(self):
        """Test creating progress bar with default description."""
        progress = create_progress_bar(total=10)
        assert progress is not None

    def test_creates_progress_bar_with_custom_description(self):
        """Test creating progress bar with custom description."""
        progress = create_progress_bar(total=5, description="Custom task")
        assert progress is not None


class TestCreateResultsTable:
    """Tests for create_results_table function."""

    def test_creates_table_with_empty_results(self):
        """Test creating table with no results."""
        table = create_results_table([])
        assert table is not None

    def test_creates_table_with_successful_results(self, device, command):
        """Test creating table with successful execution results."""
        results = [
            ExecutionResult(
                device=device,
                command=command,
                status=ExecutionStatus.SUCCESS,
                output="output1",
                duration=1.5,
            ),
        ]
        table = create_results_table(results)
        assert table is not None

    def test_creates_table_with_failed_results(self, device, command):
        """Test creating table with failed execution results."""
        results = [
            ExecutionResult(
                device=device,
                command=command,
                status=ExecutionStatus.FAILED,
                error="Connection failed",
                duration=0.5,
            ),
        ]
        table = create_results_table(results)
        assert table is not None

    def test_creates_table_with_timeout_results(self, device, command):
        """Test creating table with timeout results."""
        results = [
            ExecutionResult(
                device=device,
                command=command,
                status=ExecutionStatus.TIMEOUT,
                error="Timeout",
                duration=30.0,
            ),
        ]
        table = create_results_table(results)
        assert table is not None

    def test_creates_table_with_auth_failed_results(self, device, command):
        """Test creating table with auth failed results."""
        results = [
            ExecutionResult(
                device=device,
                command=command,
                status=ExecutionStatus.AUTH_FAILED,
                error="Authentication failed",
            ),
        ]
        table = create_results_table(results)
        assert table is not None

    def test_creates_table_with_multiple_results(self):
        """Test creating table with multiple results of different statuses."""
        device1 = Device(
            hostname="192.168.1.1",
            username="admin",
            password="password",
        )
        device2 = Device(
            hostname="192.168.1.2",
            username="admin",
            password="password",
        )
        device3 = Device(
            hostname="192.168.1.3",
            username="admin",
            password="password",
        )
        cmd = Command(command="show version")

        results = [
            ExecutionResult(
                device=device1,
                command=cmd,
                status=ExecutionStatus.SUCCESS,
                output="output1\noutput2",
                duration=1.0,
            ),
            ExecutionResult(
                device=device2,
                command=cmd,
                status=ExecutionStatus.FAILED,
                error="Error",
                duration=0.5,
            ),
            ExecutionResult(
                device=device3,
                command=cmd,
                status=ExecutionStatus.TIMEOUT,
                error="Timeout",
            ),
        ]
        table = create_results_table(results)
        assert table is not None


class TestCreatePanel:
    """Tests for create_panel function."""

    def test_creates_panel_with_default_style(self):
        """Test creating panel with default style."""
        panel = create_panel("Test content", "Test Title")
        assert panel is not None

    def test_creates_panel_with_custom_style(self):
        """Test creating panel with custom style."""
        panel = create_panel("Test content", "Test Title", style="red")
        assert panel is not None


class TestPrintFunctions:
    """Tests for print functions."""

    @patch("src.netmiko_collector.ui.console")
    def test_print_error(self, mock_console):
        """Test print_error function."""
        print_error("Test error message")
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "ERROR" in call_args
        assert "Test error message" in call_args

    @patch("src.netmiko_collector.ui.console")
    def test_print_success(self, mock_console):
        """Test print_success function."""
        print_success("Test success message")
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "SUCCESS" in call_args
        assert "Test success message" in call_args

    @patch("src.netmiko_collector.ui.console")
    def test_print_warning(self, mock_console):
        """Test print_warning function."""
        print_warning("Test warning message")
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "WARNING" in call_args
        assert "Test warning message" in call_args


class TestCreateDeviceSummary:
    """Tests for create_device_summary function."""

    def test_creates_summary_with_empty_results(self):
        """Test creating summary with no results."""
        summary = create_device_summary([])
        assert "Total Devices: 0" in summary
        assert "Success: 0" in summary

    def test_creates_summary_with_all_successful_results(self):
        """Test creating summary with all successful results."""
        cmd = Command(command="show version")
        results = [
            ExecutionResult(
                device=Device(
                    hostname=f"192.168.1.{i}",
                    device_type=DeviceType.CISCO_IOS,
                    username="admin",
                    password="password",
                ),
                command=cmd,
                status=ExecutionStatus.SUCCESS,
                output="output",
                duration=1.0,
            )
            for i in range(1, 4)
        ]
        summary = create_device_summary(results)
        assert "Total Devices: 3" in summary
        assert "Success: 3" in summary
        assert "Failed: 0" in summary

    def test_creates_summary_with_mixed_results(self):
        """Test creating summary with mixed result statuses."""
        cmd = Command(command="show version")
        device1 = Device(
            hostname="192.168.1.1",
            username="admin",
            password="password",
        )
        device2 = Device(
            hostname="192.168.1.2",
            username="admin",
            password="password",
        )
        device3 = Device(
            hostname="192.168.1.3",
            username="admin",
            password="password",
        )
        device4 = Device(
            hostname="192.168.1.4",
            username="admin",
            password="password",
        )

        results = [
            ExecutionResult(device=device1, command=cmd, status=ExecutionStatus.SUCCESS, output="output", duration=1.0),
            ExecutionResult(device=device2, command=cmd, status=ExecutionStatus.FAILED, error="Error"),
            ExecutionResult(device=device3, command=cmd, status=ExecutionStatus.TIMEOUT, error="Timeout"),
            ExecutionResult(device=device4, command=cmd, status=ExecutionStatus.AUTH_FAILED, error="Auth failed"),
        ]
        summary = create_device_summary(results)
        assert "Total Devices: 4" in summary
        assert "Success: 1" in summary
        assert "Failed: 1" in summary
        assert "Timeout: 1" in summary
        assert "Auth Failed: 1" in summary

