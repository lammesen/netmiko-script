"""Command management: loading commands from files.

This module handles reading commands from text files with support for
comments and blank lines.
"""

from pathlib import Path
from typing import List

from src.netmiko_collector.models import Command


def load_commands_from_file(commands_file: Path) -> List[Command]:
    """Load commands from text file.
    
    File format:
    - One command per line
    - Lines starting with # are comments (ignored)
    - Blank lines are ignored
    - Leading/trailing whitespace is trimmed
    
    Args:
        commands_file: Path to commands text file
        
    Returns:
        List of Command objects
        
    Raises:
        FileNotFoundError: If commands file doesn't exist
        ValueError: If no valid commands found
    """
    if not commands_file.exists():
        raise FileNotFoundError(f"Commands file not found: {commands_file}")
    
    commands: List[Command] = []
    
    with open(commands_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            # Strip whitespace
            line = line.strip()
            
            # Skip blank lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Create Command object
            command = Command(command=line)
            commands.append(command)
    
    if not commands:
        raise ValueError(f"No valid commands found in file: {commands_file}")
    
    return commands


def commands_to_strings(commands: List[Command]) -> List[str]:
    """Convert list of Command objects to list of command strings.
    
    Args:
        commands: List of Command objects
        
    Returns:
        List of command strings
    """
    return [cmd.command_string for cmd in commands]


def filter_commands(
    commands: List[Command],
    include_patterns: List[str] = None,
    exclude_patterns: List[str] = None,
) -> List[Command]:
    """Filter commands based on include/exclude patterns.
    
    Args:
        commands: List of Command objects
        include_patterns: List of patterns to include (keep only matching)
        exclude_patterns: List of patterns to exclude (remove matching)
        
    Returns:
        Filtered list of Command objects
    """
    filtered = commands.copy()
    
    # Apply include filter
    if include_patterns:
        filtered = [
            cmd for cmd in filtered
            if any(pattern in cmd.command_string for pattern in include_patterns)
        ]
    
    # Apply exclude filter
    if exclude_patterns:
        filtered = [
            cmd for cmd in filtered
            if not any(pattern in cmd.command_string for pattern in exclude_patterns)
        ]
    
    return filtered
