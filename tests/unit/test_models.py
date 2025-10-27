"""
Unit tests for data models.

Tests the Device, Command, and ExecutionResult dataclasses including
validation, properties, and conversion methods.
"""

import pytest
from datetime import datetime
from src.netmiko_collector.models import (
    Device,
    Command,
    ExecutionResult,
    DeviceType,
    AuthMethod,
    ExecutionStatus,
)


class TestDeviceType:
    """Tests for DeviceType enum."""

    def test_from_string_exact_match(self):
        """Test exact string match."""
        assert DeviceType.from_string("cisco_ios") == DeviceType.CISCO_IOS
        assert DeviceType.from_string("arista_eos") == DeviceType.ARISTA_EOS

    def test_from_string_case_insensitive(self):
        """Test case-insensitive matching."""
        assert DeviceType.from_string("CISCO_IOS") == DeviceType.CISCO_IOS
        assert DeviceType.from_string("Cisco_Ios") == DeviceType.CISCO_IOS

    def test_from_string_with_dashes(self):
        """Test handling of dashes in type names."""
        assert DeviceType.from_string("cisco-ios") == DeviceType.CISCO_IOS
        assert DeviceType.from_string("hp-comware") == DeviceType.HP_COMWARE

    def test_from_string_enum_name(self):
        """Test matching by enum name."""
        assert DeviceType.from_string("CISCO_IOS") == DeviceType.CISCO_IOS

    def test_from_string_unknown_defaults_to_generic(self):
        """Test that unknown types default to GENERIC."""
        assert DeviceType.from_string("unknown_device") == DeviceType.GENERIC
        assert DeviceType.from_string("made_up_type") == DeviceType.GENERIC


class TestDevice:
    """Tests for Device dataclass."""

    def test_device_creation_minimal(self):
        """Test creating device with minimal required fields."""
        device = Device(hostname="192.168.1.1", device_type=DeviceType.CISCO_IOS)
        assert device.hostname == "192.168.1.1"
        assert device.device_type == DeviceType.CISCO_IOS
        assert device.port == 22
        assert device.username is None
        assert device.password is None
        assert device.enabled_commands is True

    def test_device_creation_full(self):
        """Test creating device with all fields."""
        device = Device(
            hostname="router1.example.com",
            device_type=DeviceType.CISCO_IOS,
            username="admin",
            password="secret",
            port=2222,
            proxy_jump="jumphost.example.com",
            ssh_config="/path/to/config",
            tags=frozenset({"production", "datacenter1"}),
            enabled_commands=False,
        )
        assert device.hostname == "router1.example.com"
        assert device.username == "admin"
        assert device.port == 2222
        assert device.has_tag("production")
        assert device.has_tag("datacenter1")
        assert device.enabled_commands is False

    def test_device_empty_hostname_raises_error(self):
        """Test that empty hostname raises ValueError."""
        with pytest.raises(ValueError, match="hostname cannot be empty"):
            Device(hostname="", device_type=DeviceType.CISCO_IOS)

    def test_device_invalid_port_raises_error(self):
        """Test that invalid ports raise ValueError."""
        with pytest.raises(ValueError, match="Invalid port number"):
            Device(hostname="192.168.1.1", device_type=DeviceType.CISCO_IOS, port=0)

        with pytest.raises(ValueError, match="Invalid port number"):
            Device(hostname="192.168.1.1", device_type=DeviceType.CISCO_IOS, port=99999)

    def test_device_display_name_standard_port(self):
        """Test display name with standard SSH port."""
        device = Device(hostname="router1", device_type=DeviceType.CISCO_IOS, port=22)
        assert device.display_name == "router1"

    def test_device_display_name_custom_port(self):
        """Test display name with custom port."""
        device = Device(hostname="router1", device_type=DeviceType.CISCO_IOS, port=2222)
        assert device.display_name == "router1:2222"

    def test_device_has_tag_case_insensitive(self):
        """Test tag checking is case-insensitive."""
        device = Device(
            hostname="router1",
            device_type=DeviceType.CISCO_IOS,
            tags=frozenset({"Production", "DataCenter"}),
        )
        assert device.has_tag("production")
        assert device.has_tag("PRODUCTION")
        assert device.has_tag("datacenter")
        assert not device.has_tag("staging")

    def test_device_is_frozen(self):
        """Test that Device instances are immutable."""
        device = Device(hostname="router1", device_type=DeviceType.CISCO_IOS)
        with pytest.raises(AttributeError):
            device.hostname = "router2"  # type: ignore


class TestCommand:
    """Tests for Command dataclass."""

    def test_command_creation_minimal(self):
        """Test creating command with minimal required fields."""
        cmd = Command(command="show version")
        assert cmd.command == "show version"
        assert cmd.description is None
        assert cmd.timeout == 60
        assert cmd.requires_enable is False
        assert cmd.expect_string is None

    def test_command_creation_full(self):
        """Test creating command with all fields."""
        cmd = Command(
            command="show running-config",
            description="Get running configuration",
            timeout=120,
            requires_enable=True,
            expect_string="#",
        )
        assert cmd.command == "show running-config"
        assert cmd.description == "Get running configuration"
        assert cmd.timeout == 120
        assert cmd.requires_enable is True
        assert cmd.expect_string == "#"

    def test_command_empty_raises_error(self):
        """Test that empty command raises ValueError."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            Command(command="")

        with pytest.raises(ValueError, match="Command cannot be empty"):
            Command(command="   ")

    def test_command_invalid_timeout_raises_error(self):
        """Test that invalid timeout raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timeout"):
            Command(command="show version", timeout=0)

        with pytest.raises(ValueError, match="Invalid timeout"):
            Command(command="show version", timeout=-1)

    def test_command_display_name_with_description(self):
        """Test display name uses description if available."""
        cmd = Command(command="show version", description="Get device version")
        assert cmd.display_name == "Get device version"

    def test_command_display_name_without_description(self):
        """Test display name uses command if no description."""
        cmd = Command(command="show version")
        assert cmd.display_name == "show version"

    def test_command_is_frozen(self):
        """Test that Command instances are immutable."""
        cmd = Command(command="show version")
        with pytest.raises(AttributeError):
            cmd.command = "show interfaces"  # type: ignore


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    @pytest.fixture
    def sample_device(self) -> Device:
        """Create a sample device for testing."""
        return Device(hostname="router1", device_type=DeviceType.CISCO_IOS)

    @pytest.fixture
    def sample_command(self) -> Command:
        """Create a sample command for testing."""
        return Command(command="show version")

    def test_execution_result_creation(self, sample_device, sample_command):
        """Test creating execution result."""
        result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.SUCCESS,
            output="Cisco IOS Version 15.0",
            duration=1.5,
        )
        assert result.device == sample_device
        assert result.command == sample_command
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output == "Cisco IOS Version 15.0"
        assert result.duration == 1.5
        assert result.retries == 0
        assert isinstance(result.timestamp, datetime)

    def test_execution_result_is_success(self, sample_device, sample_command):
        """Test is_success property."""
        result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.SUCCESS,
        )
        assert result.is_success is True
        assert result.is_failure is False

    def test_execution_result_is_failure(self, sample_device, sample_command):
        """Test is_failure property."""
        failed_result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.FAILED,
            error="Connection timeout",
        )
        assert failed_result.is_success is False
        assert failed_result.is_failure is True

        timeout_result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.TIMEOUT,
        )
        assert timeout_result.is_success is False
        assert timeout_result.is_failure is True

    def test_execution_result_to_dict(self, sample_device, sample_command):
        """Test converting result to dictionary."""
        timestamp = datetime(2025, 10, 27, 12, 0, 0)
        result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.SUCCESS,
            output="test output",
            error="",
            timestamp=timestamp,
            duration=2.5,
            retries=1,
        )

        result_dict = result.to_dict()
        assert result_dict["hostname"] == "router1"
        assert result_dict["device_type"] == "cisco_ios"
        assert result_dict["command"] == "show version"
        assert result_dict["status"] == "success"
        assert result_dict["output"] == "test output"
        assert result_dict["error"] == ""
        assert result_dict["timestamp"] == "2025-10-27T12:00:00"
        assert result_dict["duration"] == 2.5
        assert result_dict["retries"] == 1

    def test_execution_result_with_retries(self, sample_device, sample_command):
        """Test result with retry attempts."""
        result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.SUCCESS,
            retries=3,
        )
        assert result.retries == 3

    def test_execution_result_pending_status(self, sample_device, sample_command):
        """Test pending status."""
        result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.PENDING,
        )
        assert result.is_success is False
        assert result.is_failure is False

    def test_execution_result_is_mutable(self, sample_device, sample_command):
        """Test that ExecutionResult is mutable (not frozen)."""
        result = ExecutionResult(
            device=sample_device,
            command=sample_command,
            status=ExecutionStatus.PENDING,
        )
        # Should be able to update mutable fields
        result.status = ExecutionStatus.SUCCESS
        result.output = "Updated output"
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output == "Updated output"
