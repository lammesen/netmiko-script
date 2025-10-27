"""Utility functions for path expansion, validation, and common operations.

This module provides pure utility functions used throughout the application.
All functions are stateless and have no side effects beyond their documented behavior.
"""

import os
import re
from pathlib import Path
from typing import Optional


def expand_path(path: str) -> Path:
    """Expand user home directory and environment variables in path.
    
    Args:
        path: Path string that may contain ~ or environment variables
        
    Returns:
        Expanded Path object
        
    Examples:
        >>> expand_path("~/documents/file.txt")
        Path("/home/user/documents/file.txt")
        >>> expand_path("$HOME/data")
        Path("/home/user/data")
    """
    expanded = os.path.expanduser(os.path.expandvars(path))
    return Path(expanded).resolve()


def validate_hostname(hostname: str) -> bool:
    """Validate hostname format according to RFC 1123.
    
    Args:
        hostname: Hostname string to validate
        
    Returns:
        True if hostname is valid, False otherwise
        
    Examples:
        >>> validate_hostname("router1.example.com")
        True
        >>> validate_hostname("192.168.1.1")
        True
        >>> validate_hostname("invalid_hostname!")
        False
    """
    if not hostname or len(hostname) > 253:
        return False
    
    # Allow IP addresses
    if is_valid_ip(hostname):
        return True
    
    # Hostname pattern: alphanumeric, hyphens, dots
    # Each label must start/end with alphanumeric, max 63 chars
    hostname_pattern = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
        r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    return bool(hostname_pattern.match(hostname))


def is_valid_ip(ip_address: str) -> bool:
    """Check if string is a valid IPv4 address.
    
    Args:
        ip_address: String to validate as IPv4 address
        
    Returns:
        True if valid IPv4 address, False otherwise
        
    Examples:
        >>> is_valid_ip("192.168.1.1")
        True
        >>> is_valid_ip("256.1.1.1")
        False
        >>> is_valid_ip("not.an.ip")
        False
    """
    if not ip_address:
        return False
    
    parts = ip_address.split('.')
    if len(parts) != 4:
        return False
    
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, TypeError):
        return False


def validate_port(port: int) -> bool:
    """Validate port number is in valid range.
    
    Args:
        port: Port number to validate
        
    Returns:
        True if port is in valid range (1-65535), False otherwise
        
    Examples:
        >>> validate_port(22)
        True
        >>> validate_port(65535)
        True
        >>> validate_port(0)
        False
        >>> validate_port(70000)
        False
    """
    return 1 <= port <= 65535


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement: Character to replace invalid characters with
        
    Returns:
        Sanitized filename safe for filesystem use
        
    Examples:
        >>> sanitize_filename("output:file*.txt")
        'output_file_.txt'
        >>> sanitize_filename("data/file.csv")
        'data_file.csv'
    """
    # Remove or replace characters invalid in filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, replacement, filename)
    
    # Remove control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
    
    # Trim spaces and dots from ends
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty and contains valid characters
    # If only underscores or whitespace remain, return 'unnamed'
    if not sanitized or sanitized.replace(replacement, '').strip() == '':
        return "unnamed"
    
    return sanitized


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length, adding suffix if truncated.
    
    Args:
        text: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated (default: "...")
        
    Returns:
        Truncated string
        
    Examples:
        >>> truncate_string("This is a long string", 10)
        'This is...'
        >>> truncate_string("Short", 10)
        'Short'
    """
    if len(text) <= max_length:
        return text
    
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    return text[:max_length - len(suffix)] + suffix


def parse_csv_line(line: str, delimiter: str = ",") -> list[str]:
    """Parse a CSV line handling quoted fields correctly.
    
    Args:
        line: CSV line to parse
        delimiter: Field delimiter (default: comma)
        
    Returns:
        List of parsed fields with quotes removed and whitespace stripped
        
    Examples:
        >>> parse_csv_line('field1,"field 2",field3')
        ['field1', 'field 2', 'field3']
        >>> parse_csv_line('a,b,c')
        ['a', 'b', 'c']
    """
    import csv
    from io import StringIO
    
    reader = csv.reader(StringIO(line), delimiter=delimiter)
    fields = next(reader, [])
    return [field.strip() for field in fields]


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
        
    Examples:
        >>> format_duration(45)
        '45.0s'
        >>> format_duration(125)
        '2m 5.0s'
        >>> format_duration(3665)
        '1h 1m 5.0s'
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.1f}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m {remaining_seconds:.1f}s"


def get_file_size_str(size_bytes: int) -> str:
    """Convert file size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string with appropriate unit
        
    Examples:
        >>> get_file_size_str(1024)
        '1.0 KB'
        >>> get_file_size_str(1536)
        '1.5 KB'
        >>> get_file_size_str(1048576)
        '1.0 MB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
