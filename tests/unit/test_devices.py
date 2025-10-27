"""Unit tests for devices module."""

from pathlib import Path

import pytest

from src.netmiko_collector.devices import (
    load_devices_from_csv,
    validate_devices,
)
from src.netmiko_collector.models import AuthMethod, Device, DeviceType


class TestLoadDevicesFromCsv:
    """Tests for load_devices_from_csv function."""
    
    def test_load_devices_minimal_csv(self, tmp_path):
        """Test loading devices with minimal CSV (only hostname)."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname\n"
            "router1.example.com\n"
            "switch1.example.com\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret"
        )
        
        assert len(devices) == 2
        assert devices[0].hostname == "router1.example.com"
        assert devices[0].username == "admin"
        assert devices[0].password == "secret"
        assert devices[0].port == 22
        assert devices[1].hostname == "switch1.example.com"
    
    def test_load_devices_full_csv(self, tmp_path):
        """Test loading devices with all columns."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname,ip,port,username,password,device_type,auth_method\n"
            "router1,192.168.1.1,22,admin,pass123,cisco_ios,password\n"
            "router2,192.168.1.2,2222,root,secret,cisco_nxos,key\n"
        )
        
        devices = load_devices_from_csv(csv_file)
        
        assert len(devices) == 2
        # When IP is provided, it becomes the hostname
        assert devices[0].hostname == "192.168.1.1"
        assert devices[0].ip == "192.168.1.1"
        assert devices[0].port == 22
        assert devices[0].username == "admin"
        assert devices[0].password == "pass123"
        assert devices[0].device_type == DeviceType.CISCO_IOS
        assert devices[0].auth_method == AuthMethod.PASSWORD
        
        assert devices[1].hostname == "192.168.1.2"
        assert devices[1].port == 2222
        assert devices[1].device_type == DeviceType.CISCO_NXOS
        assert devices[1].auth_method == AuthMethod.KEY
    
    def test_load_devices_with_defaults(self, tmp_path):
        """Test that defaults are applied when columns missing."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname,ip\n"
            "router1,192.168.1.1\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret",
            default_port=2222
        )
        
        assert len(devices) == 1
        assert devices[0].username == "admin"
        assert devices[0].password == "secret"
        assert devices[0].port == 2222
    
    def test_load_devices_override_defaults(self, tmp_path):
        """Test that per-device values override defaults."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname,username,password,port\n"
            "router1,custom_user,custom_pass,8022\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret",
            default_port=22
        )
        
        assert len(devices) == 1
        assert devices[0].username == "custom_user"
        assert devices[0].password == "custom_pass"
        assert devices[0].port == 8022
    
    def test_load_devices_semicolon_delimiter(self, tmp_path):
        """Test loading CSV with semicolon delimiter."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname;ip;port\n"
            "router1;192.168.1.1;22\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret"
        )
        
        assert len(devices) == 1
        assert devices[0].hostname == "192.168.1.1"  # IP becomes hostname
        assert devices[0].ip == "192.168.1.1"
    
    def test_load_devices_case_insensitive_headers(self, tmp_path):
        """Test that CSV headers are case-insensitive."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "HOSTNAME,IP,PORT\n"
            "router1,192.168.1.1,22\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret"
        )
        
        assert len(devices) == 1
        assert devices[0].hostname == "192.168.1.1"  # IP becomes hostname when provided
    
    def test_load_devices_whitespace_trimmed(self, tmp_path):
        """Test that whitespace is trimmed from values."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname , username , password \n"
            " router1 , admin , secret \n"
        )
        
        devices = load_devices_from_csv(csv_file)
        
        assert len(devices) == 1
        assert devices[0].hostname == "router1"
        assert devices[0].username == "admin"
        assert devices[0].password == "secret"
    
    def test_load_devices_file_not_found(self, tmp_path):
        """Test error when CSV file doesn't exist."""
        csv_file = tmp_path / "nonexistent.csv"
        
        with pytest.raises(FileNotFoundError, match="Device CSV file not found"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_missing_hostname_column(self, tmp_path):
        """Test error when hostname column is missing."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "ip,port\n"
            "192.168.1.1,22\n"
        )
        
        with pytest.raises(ValueError, match="CSV must have 'hostname' column"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_empty_csv(self, tmp_path):
        """Test error when CSV file is empty."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text("")
        
        with pytest.raises(ValueError, match="CSV file is empty or malformed"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_no_data_rows(self, tmp_path):
        """Test error when CSV has header but no data."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text("hostname\n")
        
        with pytest.raises(ValueError, match="No devices found"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_invalid_hostname(self, tmp_path):
        """Test error when hostname is invalid."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname\n"
            "invalid_hostname!\n"
        )
        
        with pytest.raises(ValueError, match="Invalid hostname"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_invalid_port(self, tmp_path):
        """Test error when port is invalid."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname,port\n"
            "router1,invalid\n"
        )
        
        with pytest.raises(ValueError, match="Invalid port number"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_port_out_of_range(self, tmp_path):
        """Test error when port is out of range."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname,port\n"
            "router1,70000\n"
        )
        
        with pytest.raises(ValueError, match="Port out of range"):
            load_devices_from_csv(csv_file)
    
    def test_load_devices_ip_defaults_to_hostname(self, tmp_path):
        """Test that IP defaults to hostname when not provided."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname\n"
            "192.168.1.1\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret"
        )
        
        assert len(devices) == 1
        assert devices[0].hostname == "192.168.1.1"
        assert devices[0].ip == "192.168.1.1"
    
    def test_load_devices_unknown_device_type(self, tmp_path):
        """Test that unknown device_type defaults to GENERIC."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname,device_type\n"
            "router1,unknown_vendor\n"
        )
        
        devices = load_devices_from_csv(
            csv_file,
            default_username="admin",
            default_password="secret"
        )
        
        assert len(devices) == 1
        assert devices[0].device_type == DeviceType.GENERIC  # Unknown types default to GENERIC
    
    def test_load_devices_error_line_number(self, tmp_path):
        """Test that error messages include line numbers."""
        csv_file = tmp_path / "devices.csv"
        csv_file.write_text(
            "hostname\n"
            "router1\n"
            "invalid_host!\n"
        )
        
        with pytest.raises(ValueError, match="Error on line 3"):
            load_devices_from_csv(csv_file)


class TestValidateDevices:
    """Tests for validate_devices function."""
    
    def test_validate_devices_valid_list(self):
        """Test validation of valid device list."""
        devices = [
            Device(
                hostname="router1",
                username="admin",
                password="secret"
            ),
            Device(
                hostname="router2",
                username="admin",
                password="secret"
            ),
        ]
        
        errors = validate_devices(devices)
        assert len(errors) == 0
    
    def test_validate_devices_empty_list(self):
        """Test validation of empty device list."""
        errors = validate_devices([])
        assert len(errors) == 1
        assert "No devices provided" in errors[0]
    
    def test_validate_devices_duplicate_hostnames(self):
        """Test detection of duplicate hostnames."""
        devices = [
            Device(
                hostname="router1",
                username="admin",
                password="secret"
            ),
            Device(
                hostname="router1",
                username="admin",
                password="secret"
            ),
        ]
        
        errors = validate_devices(devices)
        assert len(errors) == 1
        assert "Duplicate hostnames" in errors[0]
        assert "router1" in errors[0]
    
    def test_validate_devices_missing_username(self):
        """Test detection of missing username for password auth."""
        devices = [
            Device(
                hostname="router1",
                username=None,
                password="secret",
                auth_method=AuthMethod.PASSWORD
            ),
        ]
        
        errors = validate_devices(devices)
        assert len(errors) == 1
        assert "username required" in errors[0]
    
    def test_validate_devices_missing_password(self):
        """Test detection of missing password for password auth."""
        devices = [
            Device(
                hostname="router1",
                username="admin",
                password=None,
                auth_method=AuthMethod.PASSWORD
            ),
        ]
        
        errors = validate_devices(devices)
        assert len(errors) == 1
        assert "password required" in errors[0]
    
    def test_validate_devices_key_auth_no_password_ok(self):
        """Test that KEY auth doesn't require password."""
        devices = [
            Device(
                hostname="router1",
                username="admin",
                password=None,
                auth_method=AuthMethod.KEY
            ),
        ]
        
        errors = validate_devices(devices)
        assert len(errors) == 0
    
    def test_validate_devices_multiple_errors(self):
        """Test that multiple errors are detected."""
        devices = [
            Device(
                hostname="router1",
                username="admin",
                password="secret"
            ),
            Device(
                hostname="router1",
                username=None,
                password=None,
                auth_method=AuthMethod.PASSWORD
            ),
        ]
        
        errors = validate_devices(devices)
        assert len(errors) > 1  # Duplicate + missing credentials
