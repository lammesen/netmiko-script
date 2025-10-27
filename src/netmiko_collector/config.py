"""Configuration management for netmiko-collector.

This module handles loading and managing configuration from multiple sources:
- Command-line arguments
- Environment variables
- Configuration files
- Default values
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.netmiko_collector.models import AuthMethod
from src.netmiko_collector.utils import expand_path


@dataclass
class Config:
    """Application configuration with sensible defaults."""
    
    # Input files
    devices_file: Path
    commands_file: Path
    
    # Authentication
    username: Optional[str] = None
    password: Optional[str] = None
    auth_method: AuthMethod = AuthMethod.PASSWORD
    ssh_key_file: Optional[Path] = None
    ssh_config_file: Optional[Path] = None
    
    # SSH settings
    ssh_timeout: int = 30
    ssh_keepalive: int = 5
    global_delay_factor: float = 1.0
    
    # Execution settings
    max_workers: int = 5
    retry_attempts: int = 3
    retry_delay: int = 5
    
    # Output settings
    output_file: Path = Path("output.csv")
    output_format: str = "csv"
    verbose: bool = False
    debug: bool = False
    
    # Session logging
    session_log_dir: Optional[Path] = None
    
    def __post_init__(self):
        """Validate and normalize configuration values."""
        # Expand paths
        self.devices_file = expand_path(str(self.devices_file))
        self.commands_file = expand_path(str(self.commands_file))
        self.output_file = expand_path(str(self.output_file))
        
        if self.ssh_key_file:
            self.ssh_key_file = expand_path(str(self.ssh_key_file))
        
        if self.ssh_config_file:
            self.ssh_config_file = expand_path(str(self.ssh_config_file))
        
        if self.session_log_dir:
            self.session_log_dir = expand_path(str(self.session_log_dir))
        
        # Validate numeric values
        if self.ssh_timeout <= 0:
            raise ValueError("ssh_timeout must be positive")
        
        if self.ssh_keepalive < 0:
            raise ValueError("ssh_keepalive cannot be negative")
        
        if self.global_delay_factor <= 0:
            raise ValueError("global_delay_factor must be positive")
        
        if self.max_workers <= 0:
            raise ValueError("max_workers must be positive")
        
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts cannot be negative")
        
        if self.retry_delay < 0:
            raise ValueError("retry_delay cannot be negative")
        
        # Validate output format
        valid_formats = {"csv", "json", "yaml", "html", "xlsx"}
        if self.output_format.lower() not in valid_formats:
            raise ValueError(
                f"Invalid output_format: {self.output_format}. "
                f"Must be one of: {', '.join(valid_formats)}"
            )
        
        self.output_format = self.output_format.lower()
        
        # If using SSH key auth, validate key file exists
        if self.auth_method == AuthMethod.KEY:
            if not self.ssh_key_file:
                raise ValueError("ssh_key_file required when using KEY auth method")
            if not self.ssh_key_file.exists():
                raise FileNotFoundError(f"SSH key file not found: {self.ssh_key_file}")
    
    def validate_input_files(self) -> None:
        """Validate that required input files exist.
        
        Raises:
            FileNotFoundError: If devices or commands file doesn't exist
        """
        if not self.devices_file.exists():
            raise FileNotFoundError(f"Devices file not found: {self.devices_file}")
        
        if not self.commands_file.exists():
            raise FileNotFoundError(f"Commands file not found: {self.commands_file}")
    
    @property
    def needs_credentials(self) -> bool:
        """Check if credentials are needed based on auth method."""
        return self.auth_method == AuthMethod.PASSWORD
    
    @property
    def has_username(self) -> bool:
        """Check if username is provided."""
        return self.username is not None and len(self.username) > 0
    
    @property
    def has_password(self) -> bool:
        """Check if password is provided."""
        return self.password is not None and len(self.password) > 0
    
    def to_dict(self) -> dict:
        """Convert config to dictionary (for serialization).
        
        Note: Excludes password for security.
        
        Returns:
            Dictionary representation of config
        """
        return {
            "devices_file": str(self.devices_file),
            "commands_file": str(self.commands_file),
            "username": self.username,
            "auth_method": self.auth_method.value,
            "ssh_key_file": str(self.ssh_key_file) if self.ssh_key_file else None,
            "ssh_config_file": str(self.ssh_config_file) if self.ssh_config_file else None,
            "ssh_timeout": self.ssh_timeout,
            "ssh_keepalive": self.ssh_keepalive,
            "global_delay_factor": self.global_delay_factor,
            "max_workers": self.max_workers,
            "retry_attempts": self.retry_attempts,
            "retry_delay": self.retry_delay,
            "output_file": str(self.output_file),
            "output_format": self.output_format,
            "verbose": self.verbose,
            "debug": self.debug,
            "session_log_dir": str(self.session_log_dir) if self.session_log_dir else None,
        }
