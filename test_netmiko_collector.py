#!/usr/bin/env python3
"""
Unit tests for netmiko_collector.py
"""

import csv
import os
import tempfile
import pytest
from netmiko_collector import load_devices, load_commands, save_to_csv


class TestLoadDevices:
    """Test the load_devices function."""

    def test_load_devices_valid(self):
        """Test loading valid devices CSV."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("hostname,ip_address,device_type\n")
            f.write("router1,192.168.1.1,cisco_ios\n")
            f.write("switch1,192.168.1.2,cisco_ios\n")
            temp_file = f.name

        try:
            devices = load_devices(temp_file)
            assert len(devices) == 2
            assert devices[0]["hostname"] == "router1"
            assert devices[0]["ip_address"] == "192.168.1.1"
            assert devices[0]["device_type"] == "cisco_ios"
            assert devices[1]["hostname"] == "switch1"
        finally:
            os.unlink(temp_file)

    def test_load_devices_with_optional_fields(self):
        """Test loading devices CSV with optional fields."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("hostname,ip_address,device_type,ssh_config_file,use_keys,key_file\n")
            f.write("router1,192.168.1.1,cisco_ios,~/.ssh/config,true,~/.ssh/id_rsa\n")
            f.write("switch1,192.168.1.2,cisco_ios,,,\n")
            temp_file = f.name

        try:
            devices = load_devices(temp_file)
            assert len(devices) == 2
            assert devices[0]["ssh_config_file"] == "~/.ssh/config"
            assert devices[0]["use_keys"] == "true"
            assert devices[0]["key_file"] == "~/.ssh/id_rsa"
            assert "ssh_config_file" not in devices[1]
        finally:
            os.unlink(temp_file)

    def test_load_devices_file_not_found(self):
        """Test error when devices file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_devices("nonexistent.csv")

    def test_load_devices_missing_required_field(self):
        """Test error when required field is missing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("hostname,ip_address\n")
            f.write("router1,192.168.1.1\n")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="CSV must contain columns"):
                load_devices(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_devices_empty_required_value(self):
        """Test error when required field value is empty."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("hostname,ip_address,device_type\n")
            f.write("router1,,cisco_ios\n")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="missing values"):
                load_devices(temp_file)
        finally:
            os.unlink(temp_file)


class TestLoadCommands:
    """Test the load_commands function."""

    def test_load_commands_valid(self):
        """Test loading valid commands file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("show version\n")
            f.write("show ip interface brief\n")
            f.write("# This is a comment\n")
            f.write("\n")
            f.write("show running-config\n")
            temp_file = f.name

        try:
            commands = load_commands(temp_file)
            assert len(commands) == 3
            assert "show version" in commands
            assert "show ip interface brief" in commands
            assert "show running-config" in commands
            assert "# This is a comment" not in commands
        finally:
            os.unlink(temp_file)

    def test_load_commands_file_not_found(self):
        """Test error when commands file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_commands("nonexistent.txt")

    def test_load_commands_empty_file(self):
        """Test error when commands file is empty."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("# Only comments\n")
            f.write("\n")
            temp_file = f.name

        try:
            with pytest.raises(ValueError, match="No commands found"):
                load_commands(temp_file)
        finally:
            os.unlink(temp_file)


class TestSaveToCSV:
    """Test the save_to_csv function."""

    def test_save_to_csv_valid(self):
        """Test saving results to CSV."""
        results = [
            {
                "timestamp": "2025-10-20 14:30:15",
                "hostname": "router1",
                "ip_address": "192.168.1.1",
                "command": "show version",
                "output": "Cisco IOS...",
                "status": "success",
            },
            {
                "timestamp": "2025-10-20 14:30:18",
                "hostname": "router1",
                "ip_address": "192.168.1.1",
                "command": "show ip interface brief",
                "output": "Interface...",
                "status": "success",
            },
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            save_to_csv(results, temp_file)

            # Verify the file was created and contains correct data
            with open(temp_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["hostname"] == "router1"
                assert rows[0]["command"] == "show version"
                assert rows[0]["status"] == "success"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_save_to_csv_empty_results(self):
        """Test saving empty results (should not create file)."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
            temp_file = f.name

        try:
            # Remove the temp file so we can check if save_to_csv creates it
            os.unlink(temp_file)
            save_to_csv([], temp_file)
            # File should not be created for empty results
            assert not os.path.exists(temp_file)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
