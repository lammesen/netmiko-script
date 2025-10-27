"""Tests for executor module."""

import pytest
from unittest.mock import Mock, patch
import time

from src.netmiko_collector.executor import (
    ExecutionStats,
    execute_on_devices,
    execute_on_device_batches,
)
from src.netmiko_collector.models import (
    Device,
    Command,
    ExecutionResult,
    ExecutionStatus,
    DeviceType,
)


@pytest.fixture
def test_devices():
    """Create test devices."""
    return [
        Device(hostname=f"192.168.1.{i}")
        for i in range(1, 6)
    ]


@pytest.fixture
def test_commands():
    """Create test commands."""
    return [
        Command(command="show version"),
        Command(command="show ip interface brief"),
    ]


@pytest.fixture
def test_results(test_devices, test_commands):
    """Create test results."""
    return [
        ExecutionResult(
            device=device,
            command=command,
            output=f"Output for {device.hostname} {command.command}",
            status=ExecutionStatus.SUCCESS,
        )
        for device in test_devices
        for command in test_commands
    ]


class TestExecutionStats:
    """Tests for ExecutionStats class."""
    
    def test_initialization(self):
        """Test ExecutionStats initialization."""
        stats = ExecutionStats()
        assert stats.total_devices == 0
        assert stats.completed_devices == 0
        assert stats.successful_devices == 0
        assert stats.failed_devices == 0
        assert stats.total_commands == 0
        assert stats.successful_commands == 0
        assert stats.failed_commands == 0
        assert stats.start_time is None
        assert stats.end_time is None
    
    def test_start(self):
        """Test starting execution tracking."""
        stats = ExecutionStats()
        stats.start(device_count=10, command_count=5)
        
        assert stats.total_devices == 10
        assert stats.total_commands == 50  # 10 devices * 5 commands
        assert stats.start_time is not None
        assert stats.end_time is None
    
    def test_finish(self):
        """Test finishing execution tracking."""
        stats = ExecutionStats()
        stats.start(device_count=5, command_count=2)
        time.sleep(0.1)
        stats.finish()
        
        assert stats.end_time is not None
        assert stats.duration > 0
    
    def test_record_device_results_success(self):
        """Test recording successful device results."""
        device = Device(hostname="192.168.1.1")
        command1 = Command(command="show version")
        command2 = Command(command="show ip int brief")
        
        results = [
            ExecutionResult(device=device, command=command1, status=ExecutionStatus.SUCCESS, output="output1"),
            ExecutionResult(device=device, command=command2, status=ExecutionStatus.SUCCESS, output="output2"),
        ]
        
        stats = ExecutionStats()
        stats.start(device_count=1, command_count=2)
        stats.record_device_results(results)
        
        assert stats.completed_devices == 1
        assert stats.successful_devices == 1
        assert stats.failed_devices == 0
        assert stats.successful_commands == 2
        assert stats.failed_commands == 0
    
    def test_record_device_results_failure(self):
        """Test recording failed device results."""
        device = Device(hostname="192.168.1.1")
        command1 = Command(command="show version")
        command2 = Command(command="show ip int brief")
        
        results = [
            ExecutionResult(device=device, command=command1, status=ExecutionStatus.SUCCESS, output="output1"),
            ExecutionResult(device=device, command=command2, status=ExecutionStatus.FAILED, error="error"),
        ]
        
        stats = ExecutionStats()
        stats.start(device_count=1, command_count=2)
        stats.record_device_results(results)
        
        assert stats.completed_devices == 1
        assert stats.successful_devices == 0  # Device had at least one failure
        assert stats.failed_devices == 1
        assert stats.successful_commands == 1
        assert stats.failed_commands == 1
    
    def test_duration(self):
        """Test duration calculation."""
        stats = ExecutionStats()
        assert stats.duration == 0.0
        
        stats.start(device_count=1, command_count=1)
        time.sleep(0.1)
        duration1 = stats.duration
        assert duration1 > 0.1
        
        stats.finish()
        duration2 = stats.duration
        assert duration2 >= duration1
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        stats = ExecutionStats()
        stats.start(device_count=10, command_count=2)
        
        assert stats.progress_percentage == 0.0
        
        device = Device(hostname="192.168.1.1")
        command = Command(command="show version")
        result = ExecutionResult(device=device, command=command, status=ExecutionStatus.SUCCESS, output="output")
        
        stats.record_device_results([result])
        assert stats.progress_percentage == 10.0
        
        stats.record_device_results([result])
        assert stats.progress_percentage == 20.0
    
    def test_progress_percentage_zero_devices(self):
        """Test progress percentage with zero devices."""
        stats = ExecutionStats()
        assert stats.progress_percentage == 0.0
    
    def test_to_dict(self):
        """Test converting stats to dictionary."""
        stats = ExecutionStats()
        stats.start(device_count=5, command_count=2)
        
        device = Device(hostname="192.168.1.1")
        command = Command(command="show version")
        result = ExecutionResult(device=device, command=command, status=ExecutionStatus.SUCCESS, output="output")
        stats.record_device_results([result])
        
        stats.finish()
        
        stats_dict = stats.to_dict()
        assert stats_dict["total_devices"] == 5
        assert stats_dict["completed_devices"] == 1
        assert stats_dict["total_commands"] == 10
        assert stats_dict["successful_commands"] == 1
        assert "duration" in stats_dict
        assert "progress_percentage" in stats_dict


class TestExecuteOnDevices:
    """Tests for execute_on_devices function."""
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_devices_success(self, mock_execute, test_devices, test_commands):
        """Test successful execution on multiple devices."""
        # Mock successful execution for all devices
        def mock_exec(device, commands, ssh_config):
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        results, stats = execute_on_devices(
            test_devices,
            test_commands,
            max_workers=5,
        )
        
        # Verify all commands on all devices were executed
        assert len(results) == len(test_devices) * len(test_commands)
        assert all(r.status == ExecutionStatus.SUCCESS for r in results)
        
        # Verify stats
        assert stats.total_devices == len(test_devices)
        assert stats.completed_devices == len(test_devices)
        assert stats.successful_devices == len(test_devices)
        assert stats.failed_devices == 0
        assert stats.successful_commands == len(test_devices) * len(test_commands)
        assert stats.failed_commands == 0
        assert stats.duration > 0
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_devices_partial_failure(self, mock_execute, test_devices, test_commands):
        """Test execution with some device failures."""
        # Mock: first device succeeds, second fails, rest succeed
        def mock_exec(device, commands, ssh_config):
            if device.hostname == "192.168.1.2":
                return [
                    ExecutionResult(
                        device=device,
                        command=cmd,
                        output="",
                        status=ExecutionStatus.FAILED,
                        error="Connection failed",
                    )
                    for cmd in commands
                ]
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        results, stats = execute_on_devices(
            test_devices,
            test_commands,
            max_workers=5,
        )
        
        # Verify results
        assert len(results) == len(test_devices) * len(test_commands)
        failed_results = [r for r in results if r.status == ExecutionStatus.FAILED]
        assert len(failed_results) == len(test_commands)  # One device failed
        
        # Verify stats
        assert stats.total_devices == len(test_devices)
        assert stats.completed_devices == len(test_devices)
        assert stats.successful_devices == len(test_devices) - 1
        assert stats.failed_devices == 1
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_devices_with_callback(self, mock_execute, test_devices, test_commands):
        """Test execution with progress callback."""
        # Mock successful execution
        def mock_exec(device, commands, ssh_config):
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        # Track callback invocations
        callback_calls = []
        
        def progress_callback(stats, device, results):
            callback_calls.append((stats.completed_devices, device.hostname, len(results)))
        
        results, stats = execute_on_devices(
            test_devices,
            test_commands,
            max_workers=5,
            progress_callback=progress_callback,
        )
        
        # Verify callback was called for each device
        assert len(callback_calls) == len(test_devices)
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_devices_executor_exception(self, mock_execute, test_devices, test_commands):
        """Test handling of executor exceptions."""
        # Mock: raise exception for one device
        def mock_exec(device, commands, ssh_config):
            if device.hostname == "192.168.1.2":
                raise Exception("Unexpected error")
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        results, stats = execute_on_devices(
            test_devices,
            test_commands,
            max_workers=5,
        )
        
        # Verify all commands are accounted for
        assert len(results) == len(test_devices) * len(test_commands)
        
        # Verify failed device results
        failed_results = [r for r in results if "Executor error" in r.error]
        assert len(failed_results) == len(test_commands)


class TestExecuteOnDeviceBatches:
    """Tests for execute_on_device_batches function."""
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_device_batches_single_batch(self, mock_execute, test_devices, test_commands):
        """Test batch execution with devices fitting in one batch."""
        # Mock successful execution
        def mock_exec(device, commands, ssh_config):
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        results, stats = execute_on_device_batches(
            test_devices,
            test_commands,
            batch_size=10,  # Larger than device count
            max_workers=5,
        )
        
        # Verify all commands executed
        assert len(results) == len(test_devices) * len(test_commands)
        assert stats.total_devices == len(test_devices)
        assert stats.completed_devices == len(test_devices)
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_device_batches_multiple_batches(self, mock_execute, test_devices, test_commands):
        """Test batch execution with multiple batches."""
        # Mock successful execution
        def mock_exec(device, commands, ssh_config):
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        results, stats = execute_on_device_batches(
            test_devices,
            test_commands,
            batch_size=2,  # Process 2 devices at a time
            max_workers=2,
        )
        
        # Verify all commands executed
        assert len(results) == len(test_devices) * len(test_commands)
        assert stats.total_devices == len(test_devices)
        assert stats.completed_devices == len(test_devices)
        assert all(r.status == ExecutionStatus.SUCCESS for r in results)
    
    @patch("src.netmiko_collector.executor.execute_commands_on_device")
    def test_execute_on_device_batches_with_callback(self, mock_execute, test_devices, test_commands):
        """Test batch execution with progress callback."""
        # Mock successful execution
        def mock_exec(device, commands, ssh_config):
            return [
                ExecutionResult(
                    device=device,
                    command=cmd,
                    output=f"Output for {device.hostname}",
                    status=ExecutionStatus.SUCCESS,
                )
                for cmd in commands
            ]
        
        mock_execute.side_effect = mock_exec
        
        # Track callback invocations
        callback_calls = []
        
        def progress_callback(stats, device, results):
            callback_calls.append(device.hostname)
        
        results, stats = execute_on_device_batches(
            test_devices,
            test_commands,
            batch_size=2,
            max_workers=2,
            progress_callback=progress_callback,
        )
        
        # Verify callback was called for each device
        assert len(callback_calls) == len(test_devices)
