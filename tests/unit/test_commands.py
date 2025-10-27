"""Unit tests for commands module."""

from pathlib import Path

import pytest

from src.netmiko_collector.commands import (
    commands_to_strings,
    filter_commands,
    load_commands_from_file,
)
from src.netmiko_collector.models import Command


class TestLoadCommandsFromFile:
    """Tests for load_commands_from_file function."""
    
    def test_load_commands_simple(self, tmp_path):
        """Test loading simple commands file."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(
            "show version\n"
            "show interfaces\n"
            "show ip route\n"
        )
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 3
        assert commands[0].command_string == "show version"
        assert commands[1].command_string == "show interfaces"
        assert commands[2].command_string == "show ip route"
    
    def test_load_commands_with_comments(self, tmp_path):
        """Test that comments are ignored."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(
            "# This is a comment\n"
            "show version\n"
            "# Another comment\n"
            "show interfaces\n"
        )
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 2
        assert commands[0].command_string == "show version"
        assert commands[1].command_string == "show interfaces"
    
    def test_load_commands_with_blank_lines(self, tmp_path):
        """Test that blank lines are ignored."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(
            "show version\n"
            "\n"
            "\n"
            "show interfaces\n"
            "\n"
        )
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 2
        assert commands[0].command_string == "show version"
        assert commands[1].command_string == "show interfaces"
    
    def test_load_commands_with_whitespace(self, tmp_path):
        """Test that leading/trailing whitespace is trimmed."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(
            "  show version  \n"
            "\t show interfaces \t\n"
        )
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 2
        assert commands[0].command_string == "show version"
        assert commands[1].command_string == "show interfaces"
    
    def test_load_commands_mixed_content(self, tmp_path):
        """Test file with mix of commands, comments, and blank lines."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(
            "# Configuration commands\n"
            "\n"
            "show version\n"
            "  # Indented comment\n"
            "show interfaces\n"
            "\n"
            "# Network commands\n"
            "show ip route\n"
            "\n"
        )
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 3
        assert commands[0].command_string == "show version"
        assert commands[1].command_string == "show interfaces"
        assert commands[2].command_string == "show ip route"
    
    def test_load_commands_file_not_found(self, tmp_path):
        """Test error when commands file doesn't exist."""
        commands_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(FileNotFoundError, match="Commands file not found"):
            load_commands_from_file(commands_file)
    
    def test_load_commands_empty_file(self, tmp_path):
        """Test error when file has no valid commands."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text("")
        
        with pytest.raises(ValueError, match="No valid commands found"):
            load_commands_from_file(commands_file)
    
    def test_load_commands_only_comments(self, tmp_path):
        """Test error when file has only comments."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(
            "# Comment 1\n"
            "# Comment 2\n"
            "\n"
        )
        
        with pytest.raises(ValueError, match="No valid commands found"):
            load_commands_from_file(commands_file)
    
    def test_load_commands_single_command(self, tmp_path):
        """Test loading file with single command."""
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text("show version\n")
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 1
        assert commands[0].command_string == "show version"
    
    def test_load_commands_long_command(self, tmp_path):
        """Test loading file with long command."""
        long_cmd = "show running-config | include interface GigabitEthernet"
        commands_file = tmp_path / "commands.txt"
        commands_file.write_text(f"{long_cmd}\n")
        
        commands = load_commands_from_file(commands_file)
        
        assert len(commands) == 1
        assert commands[0].command_string == long_cmd


class TestCommandsToStrings:
    """Tests for commands_to_strings function."""
    
    def test_commands_to_strings_simple(self):
        """Test converting Command objects to strings."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
        ]
        
        strings = commands_to_strings(commands)
        
        assert len(strings) == 2
        assert strings[0] == "show version"
        assert strings[1] == "show interfaces"
    
    def test_commands_to_strings_empty_list(self):
        """Test converting empty list."""
        strings = commands_to_strings([])
        assert len(strings) == 0


class TestFilterCommands:
    """Tests for filter_commands function."""
    
    def test_filter_commands_no_filters(self):
        """Test that no filters returns all commands."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
            Command(command="show ip route"),
        ]
        
        filtered = filter_commands(commands)
        
        assert len(filtered) == 3
    
    def test_filter_commands_include_pattern(self):
        """Test include pattern filtering."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
            Command(command="show ip route"),
        ]
        
        filtered = filter_commands(commands, include_patterns=["interface"])
        
        assert len(filtered) == 1
        assert filtered[0].command_string == "show interfaces"
    
    def test_filter_commands_multiple_include_patterns(self):
        """Test multiple include patterns (OR logic)."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
            Command(command="show ip route"),
        ]
        
        filtered = filter_commands(
            commands,
            include_patterns=["interface", "route"]
        )
        
        assert len(filtered) == 2
        assert filtered[0].command_string == "show interfaces"
        assert filtered[1].command_string == "show ip route"
    
    def test_filter_commands_exclude_pattern(self):
        """Test exclude pattern filtering."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
            Command(command="show ip route"),
        ]
        
        filtered = filter_commands(commands, exclude_patterns=["interface"])
        
        assert len(filtered) == 2
        assert filtered[0].command_string == "show version"
        assert filtered[1].command_string == "show ip route"
    
    def test_filter_commands_include_and_exclude(self):
        """Test both include and exclude patterns."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
            Command(command="show interfaces status"),
            Command(command="show ip route"),
        ]
        
        filtered = filter_commands(
            commands,
            include_patterns=["show"],
            exclude_patterns=["status"]
        )
        
        assert len(filtered) == 3
        assert "show interfaces status" not in [c.command_string for c in filtered]
    
    def test_filter_commands_no_matches(self):
        """Test filtering that matches nothing."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
        ]
        
        filtered = filter_commands(commands, include_patterns=["configure"])
        
        assert len(filtered) == 0
    
    def test_filter_commands_exclude_all(self):
        """Test exclude pattern that removes everything."""
        commands = [
            Command(command="show version"),
            Command(command="show interfaces"),
        ]
        
        filtered = filter_commands(commands, exclude_patterns=["show"])
        
        assert len(filtered) == 0
