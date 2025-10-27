"""SSH operations using Netmiko with retry logic and error handling.

This module provides SSH connectivity and command execution functionality
using the Netmiko library with comprehensive error handling and retry logic.
"""

from typing import Optional
import time
from dataclasses import dataclass

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)

from .models import Device, Command, ExecutionResult, ExecutionStatus


@dataclass
class SSHConfig:
    """Configuration for SSH connection behavior."""
    
    timeout: int = 60
    """Connection timeout in seconds."""
    
    session_timeout: int = 60
    """Session timeout for command execution in seconds."""
    
    max_retries: int = 3
    """Maximum number of connection retry attempts."""
    
    retry_delay: int = 5
    """Delay between retry attempts in seconds."""
    
    read_timeout_override: Optional[int] = None
    """Override for read timeout if needed."""
    
    session_log: Optional[str] = None
    """Path to session log file if logging is enabled."""


class SSHConnection:
    """Manages SSH connection to a network device using Netmiko.
    
    This class handles connection establishment, command execution,
    and proper connection cleanup with retry logic.
    
    Example:
        >>> device = Device(hostname="router1", host="192.168.1.1")
        >>> with SSHConnection(device) as conn:
        ...     result = conn.execute_command(Command(command_text="show version"))
        ...     print(result.output)
    """
    
    def __init__(
        self,
        device: Device,
        ssh_config: Optional[SSHConfig] = None,
    ):
        """Initialize SSH connection manager.
        
        Args:
            device: Device to connect to
            ssh_config: SSH configuration options
        """
        self.device = device
        self.ssh_config = ssh_config or SSHConfig()
        self.connection: Optional[ConnectHandler] = None
        self._connected = False
    
    def __enter__(self) -> "SSHConnection":
        """Context manager entry - establish connection."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()
        return False
    
    def connect(self) -> None:
        """Establish SSH connection with retry logic.
        
        Raises:
            NetmikoTimeoutException: If connection timeout after all retries
            NetmikoAuthenticationException: If authentication fails
            Exception: For other connection errors
        """
        if self._connected:
            return
        
        device_params = {
            "device_type": self.device.device_type.value,
            "host": self.device.hostname,
            "port": self.device.port,
            "username": self.device.username,
            "timeout": self.ssh_config.timeout,
            "session_timeout": self.ssh_config.session_timeout,
        }
        
        # Add authentication
        if self.device.auth_method.value == "password":
            device_params["password"] = self.device.password or ""
        elif self.device.auth_method.value == "key":
            device_params["use_keys"] = True
            if self.device.ssh_key_file:
                device_params["key_file"] = self.device.ssh_key_file
        
        # Add optional parameters
        if self.ssh_config.session_log:
            device_params["session_log"] = self.ssh_config.session_log
        
        if self.ssh_config.read_timeout_override:
            device_params["read_timeout_override"] = self.ssh_config.read_timeout_override
        
        # Retry logic
        last_exception = None
        for attempt in range(1, self.ssh_config.max_retries + 1):
            try:
                self.connection = ConnectHandler(**device_params)
                self._connected = True
                return
            except NetmikoAuthenticationException:
                # Don't retry authentication failures
                raise
            except NetmikoTimeoutException as e:
                last_exception = e
                if attempt < self.ssh_config.max_retries:
                    time.sleep(self.ssh_config.retry_delay)
                    continue
                raise
            except Exception as e:
                last_exception = e
                if attempt < self.ssh_config.max_retries:
                    time.sleep(self.ssh_config.retry_delay)
                    continue
                raise
        
        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
    
    def disconnect(self) -> None:
        """Close SSH connection gracefully."""
        if self.connection and self._connected:
            try:
                self.connection.disconnect()
            except Exception:
                pass  # Best effort disconnect
            finally:
                self._connected = False
                self.connection = None
    
    def execute_command(self, command: Command) -> ExecutionResult:
        """Execute a command on the device.
        
        Args:
            command: Command to execute
            
        Returns:
            ExecutionResult with command output and status
            
        Raises:
            RuntimeError: If not connected
        """
        if not self._connected or not self.connection:
            raise RuntimeError("Not connected to device")
        
        try:
            output = self.connection.send_command(command.command)
            return ExecutionResult(
                device=self.device,
                command=command,
                output=output,
                status=ExecutionStatus.SUCCESS,
                error=None,
            )
        except NetmikoTimeoutException as e:
            return ExecutionResult(
                device=self.device,
                command=command,
                output="",
                status=ExecutionStatus.TIMEOUT,
                error=f"Command timeout: {str(e)}",
            )
        except Exception as e:
            return ExecutionResult(
                device=self.device,
                command=command,
                output="",
                status=ExecutionStatus.FAILED,
                error=f"Command execution error: {str(e)}",
            )
    
    @property
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self._connected and self.connection is not None


def execute_commands_on_device(
    device: Device,
    commands: list[Command],
    ssh_config: Optional[SSHConfig] = None,
) -> list[ExecutionResult]:
    """Execute multiple commands on a device with a single SSH connection.
    
    This is a convenience function that manages the connection lifecycle
    and executes all commands in sequence.
    
    Args:
        device: Device to connect to
        commands: List of commands to execute
        ssh_config: SSH configuration options
        
    Returns:
        List of ExecutionResult for each command
        
    Example:
        >>> device = Device(hostname="router1", host="192.168.1.1")
        >>> commands = [
        ...     Command(command_text="show version"),
        ...     Command(command_text="show ip interface brief"),
        ... ]
        >>> results = execute_commands_on_device(device, commands)
        >>> for result in results:
        ...     print(f"{result.command.command}: {result.status}")
    """
    results = []
    
    try:
        with SSHConnection(device, ssh_config) as conn:
            for command in commands:
                result = conn.execute_command(command)
                results.append(result)
    except NetmikoAuthenticationException as e:
        # Authentication failure - mark all commands as failed
        for command in commands:
            results.append(
                ExecutionResult(
                    device=device,
                    command=command,
                    output="",
                    status=ExecutionStatus.FAILED,
                    error=f"Authentication failed: {str(e)}",
                )
            )
    except NetmikoTimeoutException as e:
        # Connection timeout - mark all remaining commands as failed
        for command in commands:
            if not any(r.command == command for r in results):
                results.append(
                    ExecutionResult(
                        device=device,
                        command=command,
                        output="",
                        status=ExecutionStatus.TIMEOUT,
                        error=f"Connection timeout: {str(e)}",
                    )
                )
    except Exception as e:
        # Other errors - mark all remaining commands as failed
        for command in commands:
            if not any(r.command == command for r in results):
                results.append(
                    ExecutionResult(
                        device=device,
                        command=command,
                        output="",
                        status=ExecutionStatus.FAILED,
                        error=f"Connection error: {str(e)}",
                    )
                )
    
    return results
