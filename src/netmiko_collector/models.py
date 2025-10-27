"""
Data models for network devices, commands, and execution results.

This module defines the core data structures using dataclasses with
proper validation and type hints for type safety.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DeviceType(Enum):
    """Supported network device types."""

    CISCO_IOS = "cisco_ios"
    CISCO_NXOS = "cisco_nxos"
    CISCO_XE = "cisco_xe"
    CISCO_XR = "cisco_xr"
    ARISTA_EOS = "arista_eos"
    JUNIPER_JUNOS = "juniper_junos"
    HP_COMWARE = "hp_comware"
    HP_PROCURVE = "hp_procurve"
    PALO_ALTO = "paloalto_panos"
    FORTINET = "fortinet"
    DELL_OS10 = "dell_os10"
    GENERIC = "generic"

    @classmethod
    def from_string(cls, value: str) -> "DeviceType":
        """Convert string to DeviceType, handling variations."""
        # Normalize the input
        normalized = value.lower().replace("-", "_").replace(" ", "_")

        # Direct match
        for device_type in cls:
            if device_type.value == normalized:
                return device_type

        # Try without vendor prefix for backwards compatibility
        for device_type in cls:
            if device_type.name.lower() == normalized:
                return device_type

        # Default to generic if no match
        return cls.GENERIC


class AuthMethod(Enum):
    """SSH authentication methods."""

    PASSWORD = "password"
    KEY = "key"
    AGENT = "agent"

    @classmethod
    def from_string(cls, value: str) -> "AuthMethod":
        """Convert string to AuthMethod."""
        normalized = value.lower().strip()
        for method in cls:
            if method.value == normalized:
                return method
        # Default to PASSWORD if no match
        return cls.PASSWORD


class ExecutionStatus(Enum):
    """Status of command execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    AUTH_FAILED = "auth_failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class Device:
    """
    Represents a network device to connect to.

    Attributes:
        hostname: Device hostname or IP address
        device_type: Type of network device
        username: SSH username (optional, can use global default)
        password: SSH password (optional, can prompt or use key)
        port: SSH port (default: 22)
        auth_method: Authentication method (password, key, agent)
        ssh_key_file: Path to SSH private key file (optional)
        proxy_jump: SSH proxy/jump server (optional)
        ssh_config: Path to SSH config file (optional)
        tags: Device tags for filtering/grouping
        enabled_commands: Whether device supports enable mode
    """

    hostname: str
    device_type: DeviceType = DeviceType.CISCO_IOS
    username: Optional[str] = None
    password: Optional[str] = None
    port: int = 22
    auth_method: AuthMethod = AuthMethod.PASSWORD
    ssh_key_file: Optional[str] = None
    proxy_jump: Optional[str] = None
    ssh_config: Optional[str] = None
    tags: frozenset[str] = field(default_factory=frozenset)
    enabled_commands: bool = True

    def __post_init__(self) -> None:
        """Validate device configuration."""
        if not self.hostname:
            raise ValueError("Device hostname cannot be empty")
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")

    @property
    def display_name(self) -> str:
        """Get a human-friendly display name for the device."""
        return f"{self.hostname}:{self.port}" if self.port != 22 else self.hostname
    
    @property
    def ip(self) -> str:
        """Get IP address (alias for hostname for backward compatibility)."""
        return self.hostname
    
    @property
    def host(self) -> str:
        """Get host (alias for hostname for backward compatibility)."""
        return self.hostname

    def has_tag(self, tag: str) -> bool:
        """Check if device has a specific tag."""
        return tag.lower() in (t.lower() for t in self.tags)


@dataclass(frozen=True)
class Command:
    """
    Represents a command to execute on devices.

    Attributes:
        command: The command string to execute
        command_string: Alias for command (for backward compatibility)
        description: Human-readable description (optional)
        timeout: Command timeout in seconds (default: 60)
        requires_enable: Whether command requires enable mode
        expect_string: Expected prompt after command (optional)
    """

    command: str
    description: Optional[str] = None
    timeout: int = 60
    requires_enable: bool = False
    expect_string: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate command configuration."""
        if not self.command or not self.command.strip():
            raise ValueError("Command cannot be empty")
        if self.timeout < 1:
            raise ValueError(f"Invalid timeout: {self.timeout}")

    @property
    def display_name(self) -> str:
        """Get a human-friendly display name for the command."""
        return self.description if self.description else self.command
    
    @property
    def command_string(self) -> str:
        """Get command string (alias for backward compatibility)."""
        return self.command
    
    @property
    def text(self) -> str:
        """Get command text (alias for command)."""
        return self.command


@dataclass
class ExecutionResult:
    """
    Result of executing a command on a device.

    Attributes:
        device: The device the command was executed on
        command: The command that was executed
        status: Execution status
        output: Command output (if successful)
        error: Error message (if failed)
        timestamp: When the command was executed
        duration: How long the command took (seconds)
        retries: Number of retry attempts
    """

    device: Device
    command: Command
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    retries: int = 0

    @property
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS

    @property
    def is_failure(self) -> bool:
        """Check if execution failed."""
        return self.status in (ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT)
    
    @property
    def hostname(self) -> str:
        """Get hostname from device."""
        return self.device.hostname
    
    @property
    def outputs(self) -> dict:
        """Get outputs dict (for compatibility)."""
        if self.output:
            return {self.command.command: self.output}
        return {}
    
    @property
    def error_message(self) -> str:
        """Get error message (alias for error)."""
        return self.error

    def to_dict(self) -> dict:
        """Convert result to dictionary for serialization."""
        return {
            "hostname": self.device.hostname,
            "device_type": self.device.device_type.value,
            "command": self.command.command,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "duration": self.duration,
            "retries": self.retries,
        }
