"""Concurrent command execution across multiple devices.

This module provides ThreadPoolExecutor-based orchestration for executing
commands on multiple network devices concurrently with progress tracking.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Optional
import time

from .models import Device, Command, ExecutionResult, ExecutionStatus
from .ssh import SSHConfig, execute_commands_on_device


class ExecutionStats:
    """Statistics for command execution across devices."""
    
    def __init__(self):
        """Initialize execution statistics."""
        self.total_devices = 0
        self.completed_devices = 0
        self.successful_devices = 0
        self.failed_devices = 0
        self.total_commands = 0
        self.successful_commands = 0
        self.failed_commands = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
    
    def start(self, device_count: int, command_count: int) -> None:
        """Start tracking execution."""
        self.total_devices = device_count
        self.total_commands = device_count * command_count
        self.start_time = time.time()
    
    def finish(self) -> None:
        """Finish tracking execution."""
        self.end_time = time.time()
    
    def record_device_results(self, results: list[ExecutionResult]) -> None:
        """Record results for a completed device."""
        self.completed_devices += 1
        
        device_success = all(r.is_success for r in results)
        if device_success:
            self.successful_devices += 1
        else:
            self.failed_devices += 1
        
        for result in results:
            if result.is_success:
                self.successful_commands += 1
            else:
                self.failed_commands += 1
    
    @property
    def duration(self) -> float:
        """Get execution duration in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    @property
    def progress_percentage(self) -> float:
        """Get completion percentage."""
        if self.total_devices == 0:
            return 0.0
        return (self.completed_devices / self.total_devices) * 100
    
    def to_dict(self) -> dict:
        """Convert statistics to dictionary."""
        return {
            "total_devices": self.total_devices,
            "completed_devices": self.completed_devices,
            "successful_devices": self.successful_devices,
            "failed_devices": self.failed_devices,
            "total_commands": self.total_commands,
            "successful_commands": self.successful_commands,
            "failed_commands": self.failed_commands,
            "duration": self.duration,
            "progress_percentage": self.progress_percentage,
        }


def execute_on_devices(
    devices: list[Device],
    commands: list[Command],
    max_workers: int = 10,
    ssh_config: Optional[SSHConfig] = None,
    progress_callback: Optional[Callable[[ExecutionStats, Device, list[ExecutionResult]], None]] = None,
) -> tuple[list[ExecutionResult], ExecutionStats]:
    """Execute commands on multiple devices concurrently.
    
    This function uses ThreadPoolExecutor to run commands on devices in parallel,
    with configurable worker count and optional progress tracking.
    
    Args:
        devices: List of devices to execute commands on
        commands: List of commands to execute on each device
        max_workers: Maximum number of concurrent device connections
        ssh_config: SSH configuration options
        progress_callback: Optional callback(stats, device, results) called after each device completes
        
    Returns:
        Tuple of (all_results, execution_stats)
        
    Example:
        >>> devices = [Device(hostname="router1"), Device(hostname="router2")]
        >>> commands = [Command(command="show version")]
        >>> results, stats = execute_on_devices(devices, commands, max_workers=5)
        >>> print(f"Completed {stats.completed_devices}/{stats.total_devices} devices")
        >>> print(f"Success rate: {stats.successful_commands}/{stats.total_commands}")
    """
    stats = ExecutionStats()
    stats.start(len(devices), len(commands))
    
    all_results: list[ExecutionResult] = []
    
    # Use ThreadPoolExecutor for concurrent execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all device tasks
        future_to_device = {
            executor.submit(
                execute_commands_on_device,
                device,
                commands,
                ssh_config,
            ): device
            for device in devices
        }
        
        # Process results as they complete
        for future in as_completed(future_to_device):
            device = future_to_device[future]
            
            try:
                results = future.result()
                all_results.extend(results)
                stats.record_device_results(results)
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(stats, device, results)
                    
            except Exception as e:
                # If something went wrong outside of execute_commands_on_device
                # Create failed results for all commands
                failed_results = [
                    ExecutionResult(
                        device=device,
                        command=cmd,
                        output="",
                        status=ExecutionStatus.FAILED,
                        error=f"Executor error: {str(e)}",
                    )
                    for cmd in commands
                ]
                all_results.extend(failed_results)
                stats.record_device_results(failed_results)
                
                if progress_callback:
                    progress_callback(stats, device, failed_results)
    
    stats.finish()
    return all_results, stats


def execute_on_device_batches(
    devices: list[Device],
    commands: list[Command],
    batch_size: int,
    max_workers: int = 10,
    ssh_config: Optional[SSHConfig] = None,
    progress_callback: Optional[Callable[[ExecutionStats, Device, list[ExecutionResult]], None]] = None,
) -> tuple[list[ExecutionResult], ExecutionStats]:
    """Execute commands on devices in batches.
    
    This function processes devices in batches, useful for very large device
    inventories to avoid overwhelming the network or system resources.
    
    Args:
        devices: List of devices to execute commands on
        commands: List of commands to execute on each device
        batch_size: Number of devices to process per batch
        max_workers: Maximum number of concurrent device connections per batch
        ssh_config: SSH configuration options
        progress_callback: Optional callback(stats, device, results) called after each device completes
        
    Returns:
        Tuple of (all_results, execution_stats)
        
    Example:
        >>> devices = [Device(hostname=f"router{i}") for i in range(100)]
        >>> commands = [Command(command="show version")]
        >>> # Process 20 devices at a time with 5 concurrent workers
        >>> results, stats = execute_on_device_batches(
        ...     devices, commands, batch_size=20, max_workers=5
        ... )
    """
    stats = ExecutionStats()
    stats.start(len(devices), len(commands))
    
    all_results: list[ExecutionResult] = []
    
    # Process devices in batches
    for i in range(0, len(devices), batch_size):
        batch_devices = devices[i:i + batch_size]
        
        # Execute on this batch
        batch_results, _ = execute_on_devices(
            batch_devices,
            commands,
            max_workers=max_workers,
            ssh_config=ssh_config,
            progress_callback=progress_callback,
        )
        
        all_results.extend(batch_results)
        
        # Update overall stats manually since we're not using the batch stats
        for device in batch_devices:
            device_results = [r for r in batch_results if r.device == device]
            stats.record_device_results(device_results)
    
    stats.finish()
    return all_results, stats
