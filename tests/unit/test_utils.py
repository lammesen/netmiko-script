"""Unit tests for utils module."""

import os
from pathlib import Path

import pytest

from src.netmiko_collector.utils import (
    expand_path,
    format_duration,
    get_file_size_str,
    is_valid_ip,
    parse_csv_line,
    sanitize_filename,
    truncate_string,
    validate_hostname,
    validate_port,
)


class TestExpandPath:
    """Tests for expand_path function."""
    
    def test_expand_home_directory(self):
        """Test expansion of ~ to home directory."""
        result = expand_path("~/documents/file.txt")
        assert str(result).startswith(os.path.expanduser("~"))
        assert result.is_absolute()
    
    def test_expand_environment_variable(self, monkeypatch):
        """Test expansion of environment variables."""
        monkeypatch.setenv("TEST_DIR", "/tmp/test")
        result = expand_path("$TEST_DIR/file.txt")
        assert "/tmp/test/file.txt" in str(result)
    
    def test_absolute_path_unchanged(self):
        """Test absolute path is resolved but not changed."""
        result = expand_path("/absolute/path/file.txt")
        assert result.is_absolute()
        assert "absolute" in str(result)
    
    def test_relative_path_resolved(self):
        """Test relative path is resolved to absolute."""
        result = expand_path("relative/path.txt")
        assert result.is_absolute()


class TestValidateHostname:
    """Tests for validate_hostname function."""
    
    def test_valid_hostname(self):
        """Test valid hostname formats."""
        assert validate_hostname("router1.example.com")
        assert validate_hostname("server-01.local")
        assert validate_hostname("host123")
        assert validate_hostname("my-router.subdomain.example.com")
    
    def test_valid_ip_address(self):
        """Test IP addresses are valid hostnames."""
        assert validate_hostname("192.168.1.1")
        assert validate_hostname("10.0.0.1")
        assert validate_hostname("172.16.0.1")
    
    def test_invalid_hostname_empty(self):
        """Test empty hostname is invalid."""
        assert not validate_hostname("")
        assert not validate_hostname("   ")
    
    def test_invalid_hostname_too_long(self):
        """Test hostname exceeding 253 characters is invalid."""
        long_hostname = "a" * 254
        assert not validate_hostname(long_hostname)
    
    def test_invalid_hostname_special_chars(self):
        """Test hostname with invalid special characters."""
        assert not validate_hostname("host_name!")
        assert not validate_hostname("server@domain.com")
        assert not validate_hostname("router#1")
    
    def test_hostname_with_trailing_dot(self):
        """Test hostname with trailing dot (FQDN format)."""
        # Trailing dot makes it invalid in our simple validator
        assert not validate_hostname("example.com.")


class TestIsValidIp:
    """Tests for is_valid_ip function."""
    
    def test_valid_ip_addresses(self):
        """Test valid IPv4 addresses."""
        assert is_valid_ip("192.168.1.1")
        assert is_valid_ip("10.0.0.1")
        assert is_valid_ip("172.16.0.1")
        assert is_valid_ip("255.255.255.255")
        assert is_valid_ip("0.0.0.0")
    
    def test_invalid_ip_out_of_range(self):
        """Test IP with octets out of range."""
        assert not is_valid_ip("256.1.1.1")
        assert not is_valid_ip("192.168.1.256")
        assert not is_valid_ip("300.300.300.300")
    
    def test_invalid_ip_wrong_format(self):
        """Test IP with wrong format."""
        assert not is_valid_ip("192.168.1")
        assert not is_valid_ip("192.168.1.1.1")
        assert not is_valid_ip("not.an.ip.address")
        assert not is_valid_ip("192.168.1.a")
    
    def test_invalid_ip_empty(self):
        """Test empty string is invalid."""
        assert not is_valid_ip("")


class TestValidatePort:
    """Tests for validate_port function."""
    
    def test_valid_ports(self):
        """Test valid port numbers."""
        assert validate_port(1)
        assert validate_port(22)
        assert validate_port(80)
        assert validate_port(443)
        assert validate_port(8080)
        assert validate_port(65535)
    
    def test_invalid_port_zero(self):
        """Test port 0 is invalid."""
        assert not validate_port(0)
    
    def test_invalid_port_negative(self):
        """Test negative port is invalid."""
        assert not validate_port(-1)
        assert not validate_port(-100)
    
    def test_invalid_port_too_high(self):
        """Test port above 65535 is invalid."""
        assert not validate_port(65536)
        assert not validate_port(70000)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_sanitize_invalid_chars(self):
        """Test removal of invalid filename characters."""
        assert sanitize_filename("output:file*.txt") == "output_file_.txt"
        assert sanitize_filename('file<>name.csv') == "file__name.csv"
        assert sanitize_filename('path/to/file.txt') == "path_to_file.txt"
    
    def test_sanitize_control_chars(self):
        """Test removal of control characters."""
        result = sanitize_filename("file\x00name.txt")
        assert "\x00" not in result
    
    def test_sanitize_trim_spaces_dots(self):
        """Test trimming of leading/trailing spaces and dots."""
        assert sanitize_filename("  filename.txt  ") == "filename.txt"
        assert sanitize_filename("..filename..") == "filename"
    
    def test_sanitize_empty_result(self):
        """Test empty filename after sanitization becomes 'unnamed'."""
        assert sanitize_filename("***") == "unnamed"
        assert sanitize_filename("   ") == "unnamed"
    
    def test_sanitize_custom_replacement(self):
        """Test custom replacement character."""
        result = sanitize_filename("file:name", replacement="-")
        assert result == "file-name"


class TestTruncateString:
    """Tests for truncate_string function."""
    
    def test_truncate_long_string(self):
        """Test truncation of long string."""
        result = truncate_string("This is a long string", 10)
        assert result == "This is..."
        assert len(result) == 10
    
    def test_no_truncate_short_string(self):
        """Test short string is not truncated."""
        result = truncate_string("Short", 10)
        assert result == "Short"
    
    def test_truncate_exact_length(self):
        """Test string exactly at max length."""
        result = truncate_string("Exactly10!", 10)
        assert result == "Exactly10!"
    
    def test_truncate_custom_suffix(self):
        """Test custom suffix."""
        result = truncate_string("Long string here", 10, suffix=">>")
        assert result == "Long str>>"
        assert len(result) == 10
    
    def test_truncate_suffix_longer_than_max(self):
        """Test suffix longer than max length."""
        result = truncate_string("Text", 2, suffix="...")
        assert result == ".."


class TestParseCsvLine:
    """Tests for parse_csv_line function."""
    
    def test_parse_simple_csv(self):
        """Test parsing simple CSV line."""
        result = parse_csv_line("field1,field2,field3")
        assert result == ["field1", "field2", "field3"]
    
    def test_parse_quoted_fields(self):
        """Test parsing CSV with quoted fields."""
        result = parse_csv_line('field1,"field 2",field3')
        assert result == ["field1", "field 2", "field3"]
    
    def test_parse_quoted_with_comma(self):
        """Test parsing quoted field containing comma."""
        result = parse_csv_line('a,"b,c",d')
        assert result == ["a", "b,c", "d"]
    
    def test_parse_with_spaces(self):
        """Test parsing with spaces around fields."""
        result = parse_csv_line(" field1 , field2 , field3 ")
        assert result == ["field1", "field2", "field3"]
    
    def test_parse_empty_fields(self):
        """Test parsing with empty fields."""
        result = parse_csv_line("a,,c")
        assert result == ["a", "", "c"]
    
    def test_parse_custom_delimiter(self):
        """Test parsing with custom delimiter."""
        result = parse_csv_line("a|b|c", delimiter="|")
        assert result == ["a", "b", "c"]


class TestFormatDuration:
    """Tests for format_duration function."""
    
    def test_format_seconds_only(self):
        """Test formatting duration less than a minute."""
        assert format_duration(45) == "45.0s"
        assert format_duration(0.5) == "0.5s"
    
    def test_format_minutes_seconds(self):
        """Test formatting duration with minutes."""
        assert format_duration(125) == "2m 5.0s"
        assert format_duration(60) == "1m 0.0s"
    
    def test_format_hours_minutes_seconds(self):
        """Test formatting duration with hours."""
        assert format_duration(3665) == "1h 1m 5.0s"
        assert format_duration(7200) == "2h 0m 0.0s"
    
    def test_format_zero_duration(self):
        """Test formatting zero duration."""
        assert format_duration(0) == "0.0s"


class TestGetFileSizeStr:
    """Tests for get_file_size_str function."""
    
    def test_bytes(self):
        """Test formatting bytes."""
        assert get_file_size_str(100) == "100.0 B"
        assert get_file_size_str(1023) == "1023.0 B"
    
    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert get_file_size_str(1024) == "1.0 KB"
        assert get_file_size_str(1536) == "1.5 KB"
    
    def test_megabytes(self):
        """Test formatting megabytes."""
        assert get_file_size_str(1048576) == "1.0 MB"
        assert get_file_size_str(5242880) == "5.0 MB"
    
    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert get_file_size_str(1073741824) == "1.0 GB"
    
    def test_zero_size(self):
        """Test formatting zero size."""
        assert get_file_size_str(0) == "0.0 B"
