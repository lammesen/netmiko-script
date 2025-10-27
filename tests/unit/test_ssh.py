"""Tests for SSH operations module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from src.netmiko_collector.ssh import (
    SSHConfig,
    SSHConnection,
    execute_commands_on_device,
)
from src.netmiko_collector.models import (
    Device,
    Command,
    ExecutionStatus,
    DeviceType,
    AuthMethod,
)


@pytest.fixture
def test_device():
    """Create a test device."""
    return Device(
        hostname="192.168.1.1",
        username="admin",
        password="secret",
        device_type=DeviceType.CISCO_IOS,
        auth_method=AuthMethod.PASSWORD,
    )


@pytest.fixture
def test_commands():
    """Create test commands."""
    return [
        Command(command="show version"),
        Command(command="show ip interface brief"),
    ]


class TestSSHConfig:
    """Tests for SSHConfig dataclass."""
    
    def test_default_values(self):
        """Test SSHConfig with default values."""
        config = SSHConfig()
        assert config.timeout == 60
        assert config.session_timeout == 60
        assert config.max_retries == 3
        assert config.retry_delay == 5
        assert config.read_timeout_override is None
        assert config.session_log is None
    
    def test_custom_values(self):
        """Test SSHConfig with custom values."""
        config = SSHConfig(
            timeout=120,
            session_timeout=90,
            max_retries=5,
            retry_delay=10,
            read_timeout_override=150,
            session_log="/tmp/session.log",
        )
        assert config.timeout == 120
        assert config.session_timeout == 90
        assert config.max_retries == 5
        assert config.retry_delay == 10
        assert config.read_timeout_override == 150
        assert config.session_log == "/tmp/session.log"


class TestSSHConnection:
    """Tests for SSHConnection class."""
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_connect_success(self, mock_connect, test_device):
        """Test successful SSH connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SSHConnection(test_device)
        conn.connect()
        
        assert conn.is_connected
        assert mock_connect.called
        
        # Verify connection parameters
        call_args = mock_connect.call_args[1]
        assert call_args["device_type"] == "cisco_ios"
        assert call_args["host"] == "192.168.1.1"
        assert call_args["username"] == "admin"
        assert call_args["password"] == "secret"
        
        conn.disconnect()
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_connect_with_ssh_key(self, mock_connect):
        """Test SSH connection with key authentication."""
        device = Device(
            hostname="192.168.1.1",
            username="admin",
            device_type=DeviceType.CISCO_IOS,
            auth_method=AuthMethod.KEY,
            ssh_key_file="/home/user/.ssh/id_rsa",
        )
        
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SSHConnection(device)
        conn.connect()
        
        call_args = mock_connect.call_args[1]
        assert call_args["use_keys"] is True
        assert call_args["key_file"] == "/home/user/.ssh/id_rsa"
        
        conn.disconnect()
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_connect_with_custom_config(self, mock_connect, test_device):
        """Test connection with custom SSH config."""
        config = SSHConfig(
            timeout=120,
            session_timeout=90,
            session_log="/tmp/session.log",
        )
        
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SSHConnection(test_device, config)
        conn.connect()
        
        call_args = mock_connect.call_args[1]
        assert call_args["timeout"] == 120
        assert call_args["session_timeout"] == 90
        assert call_args["session_log"] == "/tmp/session.log"
        
        conn.disconnect()
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_connect_authentication_failure(self, mock_connect, test_device):
        """Test connection with authentication failure."""
        mock_connect.side_effect = NetmikoAuthenticationException("Auth failed")
        
        conn = SSHConnection(test_device)
        
        with pytest.raises(NetmikoAuthenticationException):
            conn.connect()
        
        assert not conn.is_connected
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    @patch("src.netmiko_collector.ssh.time.sleep")
    def test_connect_timeout_with_retry(self, mock_sleep, mock_connect, test_device):
        """Test connection timeout with retry logic."""
        config = SSHConfig(max_retries=3, retry_delay=1)
        
        # Fail twice, succeed on third attempt
        mock_connection = Mock()
        mock_connect.side_effect = [
            NetmikoTimeoutException("Timeout 1"),
            NetmikoTimeoutException("Timeout 2"),
            mock_connection,
        ]
        
        conn = SSHConnection(test_device, config)
        conn.connect()
        
        assert conn.is_connected
        assert mock_connect.call_count == 3
        assert mock_sleep.call_count == 2
        
        conn.disconnect()
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    @patch("src.netmiko_collector.ssh.time.sleep")
    def test_connect_timeout_all_retries_fail(self, mock_sleep, mock_connect, test_device):
        """Test connection timeout when all retries fail."""
        config = SSHConfig(max_retries=3, retry_delay=1)
        
        mock_connect.side_effect = NetmikoTimeoutException("Timeout")
        
        conn = SSHConnection(test_device, config)
        
        with pytest.raises(NetmikoTimeoutException):
            conn.connect()
        
        assert not conn.is_connected
        assert mock_connect.call_count == 3
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_context_manager(self, mock_connect, test_device):
        """Test SSHConnection as context manager."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        with SSHConnection(test_device) as conn:
            assert conn.is_connected
            assert conn.connection == mock_connection
        
        # Verify disconnect was called
        assert mock_connection.disconnect.called
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_command_success(self, mock_connect, test_device):
        """Test successful command execution."""
        mock_connection = Mock()
        mock_connection.send_command.return_value = "Command output"
        mock_connect.return_value = mock_connection
        
        command = Command(command="show version")
        
        with SSHConnection(test_device) as conn:
            result = conn.execute_command(command)
        
        assert result.status == ExecutionStatus.SUCCESS
        assert result.output == "Command output"
        assert result.error is None
        assert result.device == test_device
        assert result.command == command
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_command_timeout(self, mock_connect, test_device):
        """Test command execution timeout."""
        mock_connection = Mock()
        mock_connection.send_command.side_effect = NetmikoTimeoutException("Timeout")
        mock_connect.return_value = mock_connection
        
        command = Command(command="show version")
        
        with SSHConnection(test_device) as conn:
            result = conn.execute_command(command)
        
        assert result.status == ExecutionStatus.TIMEOUT
        assert result.output == ""
        assert "Command timeout" in result.error
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_command_error(self, mock_connect, test_device):
        """Test command execution error."""
        mock_connection = Mock()
        mock_connection.send_command.side_effect = Exception("Command error")
        mock_connect.return_value = mock_connection
        
        command = Command(command="show version")
        
        with SSHConnection(test_device) as conn:
            result = conn.execute_command(command)
        
        assert result.status == ExecutionStatus.FAILED
        assert result.output == ""
        assert "Command execution error" in result.error
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_command_not_connected(self, mock_connect, test_device):
        """Test command execution when not connected."""
        command = Command(command="show version")
        
        conn = SSHConnection(test_device)
        
        with pytest.raises(RuntimeError, match="Not connected"):
            conn.execute_command(command)
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_disconnect_graceful(self, mock_connect, test_device):
        """Test graceful disconnect."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        conn = SSHConnection(test_device)
        conn.connect()
        assert conn.is_connected
        
        conn.disconnect()
        assert not conn.is_connected
        assert mock_connection.disconnect.called
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_disconnect_with_error(self, mock_connect, test_device):
        """Test disconnect when disconnect() raises error."""
        mock_connection = Mock()
        mock_connection.disconnect.side_effect = Exception("Disconnect error")
        mock_connect.return_value = mock_connection
        
        conn = SSHConnection(test_device)
        conn.connect()
        
        # Should not raise exception
        conn.disconnect()
        assert not conn.is_connected


class TestExecuteCommandsOnDevice:
    """Tests for execute_commands_on_device function."""
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_multiple_commands_success(self, mock_connect, test_device, test_commands):
        """Test executing multiple commands successfully."""
        mock_connection = Mock()
        mock_connection.send_command.side_effect = [
            "Version output",
            "Interface output",
        ]
        mock_connect.return_value = mock_connection
        
        results = execute_commands_on_device(test_device, test_commands)
        
        assert len(results) == 2
        assert all(r.status == ExecutionStatus.SUCCESS for r in results)
        assert results[0].output == "Version output"
        assert results[1].output == "Interface output"
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_commands_authentication_failure(self, mock_connect, test_device, test_commands):
        """Test command execution with authentication failure."""
        mock_connect.side_effect = NetmikoAuthenticationException("Auth failed")
        
        results = execute_commands_on_device(test_device, test_commands)
        
        assert len(results) == 2
        assert all(r.status == ExecutionStatus.FAILED for r in results)
        assert all("Authentication failed" in r.error for r in results)
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_commands_connection_timeout(self, mock_connect, test_device, test_commands):
        """Test command execution with connection timeout."""
        config = SSHConfig(max_retries=1)
        mock_connect.side_effect = NetmikoTimeoutException("Connection timeout")
        
        results = execute_commands_on_device(test_device, test_commands, config)
        
        assert len(results) == 2
        assert all(r.status == ExecutionStatus.TIMEOUT for r in results)
        assert all("Connection timeout" in r.error for r in results)
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_commands_generic_error(self, mock_connect, test_device, test_commands):
        """Test command execution with generic error."""
        mock_connect.side_effect = Exception("Connection error")
        
        results = execute_commands_on_device(test_device, test_commands)
        
        assert len(results) == 2
        assert all(r.status == ExecutionStatus.FAILED for r in results)
        assert all("Connection error" in r.error for r in results)
    
    @patch("src.netmiko_collector.ssh.ConnectHandler")
    def test_execute_commands_partial_success(self, mock_connect, test_device, test_commands):
        """Test command execution with partial success."""
        mock_connection = Mock()
        # First command succeeds, second times out
        mock_connection.send_command.side_effect = [
            "Version output",
            NetmikoTimeoutException("Command timeout"),
        ]
        mock_connect.return_value = mock_connection
        
        results = execute_commands_on_device(test_device, test_commands)
        
        assert len(results) == 2
        assert results[0].status == ExecutionStatus.SUCCESS
        assert results[0].output == "Version output"
        assert results[1].status == ExecutionStatus.TIMEOUT
        assert "Command timeout" in results[1].error
