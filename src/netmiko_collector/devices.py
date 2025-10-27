"""Device management: loading and parsing devices from CSV files.

This module handles reading device inventory from CSV files and converting
them into Device objects with proper validation.
"""

import csv
from pathlib import Path
from typing import List, Optional

from .models import AuthMethod, Device, DeviceType
from .utils import validate_hostname, validate_port


def load_devices_from_csv(
    csv_file: Path,
    default_username: Optional[str] = None,
    default_password: Optional[str] = None,
    default_port: int = 22,
) -> List[Device]:
    """Load devices from CSV file.
    
    CSV format (columns can be in any order):
    - hostname (required): Device hostname or IP
    - ip (optional): IP address if different from hostname
    - port (optional): SSH port, defaults to 22
    - username (optional): Override default username
    - password (optional): Override default password
    - device_type (optional): cisco_ios, cisco_nxos, etc.
    - auth_method (optional): password or key
    
    Args:
        csv_file: Path to CSV file
        default_username: Default username for all devices
        default_password: Default password for all devices
        default_port: Default SSH port
        
    Returns:
        List of Device objects
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is malformed or required fields missing
    """
    if not csv_file.exists():
        raise FileNotFoundError(f"Device CSV file not found: {csv_file}")
    
    devices: List[Device] = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        # Detect delimiter (support both comma and semicolon)
        sample = f.read(1024)
        f.seek(0)
        
        delimiter = ',' if ',' in sample else ';'
        reader = csv.DictReader(f, delimiter=delimiter)
        
        if not reader.fieldnames:
            raise ValueError(f"CSV file is empty or malformed: {csv_file}")
        
        # Normalize fieldnames (lowercase, strip whitespace)
        reader.fieldnames = [name.lower().strip() for name in reader.fieldnames]
        
        if 'hostname' not in reader.fieldnames:
            raise ValueError(
                f"CSV must have 'hostname' column. Found columns: {reader.fieldnames}"
            )
        
        for line_num, row in enumerate(reader, start=2):  # start=2 because of header
            try:
                device = _parse_device_row(
                    row,
                    default_username=default_username,
                    default_password=default_password,
                    default_port=default_port,
                )
                devices.append(device)
            except ValueError as e:
                raise ValueError(f"Error on line {line_num}: {e}") from e
    
    if not devices:
        raise ValueError(f"No devices found in CSV file: {csv_file}")
    
    return devices


def _parse_device_row(
    row: dict,
    default_username: Optional[str],
    default_password: Optional[str],
    default_port: int,
) -> Device:
    """Parse a single CSV row into a Device object.
    
    Args:
        row: Dictionary from CSV DictReader
        default_username: Default username
        default_password: Default password
        default_port: Default port
        
    Returns:
        Device object
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Required field
    hostname = row.get('hostname', '').strip()
    if not hostname:
        raise ValueError("hostname is required")
    
    if not validate_hostname(hostname):
        raise ValueError(f"Invalid hostname: {hostname}")
    
    # Optional IP field (if provided, use it as hostname)
    ip = row.get('ip', '').strip()
    if ip:
        hostname = ip  # Use IP as hostname if provided
    
    # Port handling
    port_str = row.get('port', '').strip()
    if port_str:
        try:
            port = int(port_str)
        except ValueError:
            raise ValueError(f"Invalid port number: {port_str}")
        
        if not validate_port(port):
            raise ValueError(f"Port out of range (1-65535): {port}")
    else:
        port = default_port
    
    # Credentials
    username = row.get('username', '').strip() or default_username
    password = row.get('password', '').strip() or default_password
    
    # Device type
    device_type_str = row.get('device_type', '').strip()
    if device_type_str:
        try:
            device_type = DeviceType.from_string(device_type_str)
        except ValueError:
            # If not a recognized type, default to CISCO_IOS
            device_type = DeviceType.CISCO_IOS
    else:
        device_type = DeviceType.CISCO_IOS
    
    # Auth method
    auth_method_str = row.get('auth_method', '').strip()
    if auth_method_str:
        try:
            auth_method = AuthMethod.from_string(auth_method_str)
        except ValueError:
            auth_method = AuthMethod.PASSWORD
    else:
        auth_method = AuthMethod.PASSWORD
    
    return Device(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        device_type=device_type,
        auth_method=auth_method,
    )


def validate_devices(devices: List[Device]) -> List[str]:
    """Validate a list of devices and return any errors.
    
    Args:
        devices: List of Device objects to validate
        
    Returns:
        List of error messages (empty if all valid)
    """
    errors = []
    
    if not devices:
        errors.append("No devices provided")
        return errors
    
    # Check for duplicate hostnames
    hostnames = [d.hostname for d in devices]
    duplicates = [h for h in hostnames if hostnames.count(h) > 1]
    if duplicates:
        unique_duplicates = list(set(duplicates))
        errors.append(f"Duplicate hostnames found: {', '.join(unique_duplicates)}")
    
    # Check that all devices have required credentials
    for device in devices:
        if device.auth_method == AuthMethod.PASSWORD:
            if not device.username:
                errors.append(f"Device {device.hostname}: username required for password auth")
            if not device.password:
                errors.append(f"Device {device.hostname}: password required for password auth")
    
    return errors
