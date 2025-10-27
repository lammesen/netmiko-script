"""
Netmiko Collector - Enterprise Network Automation CLI

A modern, modular CLI application for batch network device management using SSH.
Supports multiple vendors, parallel execution, and various output formats.
"""

__version__ = "2.0.0"
__author__ = "lammesen"
__license__ = "MIT"

# Public API exports
from .models import Device, Command, ExecutionResult

__all__ = [
    "Device",
    "Command",
    "ExecutionResult",
    "__version__",
]
