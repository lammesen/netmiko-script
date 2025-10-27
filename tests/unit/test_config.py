"""Unit tests for config module."""

from pathlib import Path

import pytest

from src.netmiko_collector.config import Config
from src.netmiko_collector.models import AuthMethod


class TestConfig:
    """Tests for Config dataclass."""
    
    def test_config_creation_minimal(self, tmp_path):
        """Test creating config with minimal required parameters."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file
        )
        
        assert config.devices_file == devices_file.resolve()
        assert config.commands_file == commands_file.resolve()
        assert config.auth_method == AuthMethod.PASSWORD
        assert config.ssh_timeout == 30
        assert config.max_workers == 5
    
    def test_config_path_expansion(self, tmp_path, monkeypatch):
        """Test that paths are expanded correctly."""
        monkeypatch.setenv("TEST_DIR", str(tmp_path))
        
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        config = Config(
            devices_file="$TEST_DIR/devices.csv",
            commands_file="$TEST_DIR/commands.txt"
        )
        
        assert config.devices_file.is_absolute()
        assert config.commands_file.is_absolute()
    
    def test_config_with_all_options(self, tmp_path):
        """Test config with all options specified."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        output_file = tmp_path / "output.json"
        key_file = tmp_path / "id_rsa"
        
        devices_file.touch()
        commands_file.touch()
        key_file.touch()
        
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            username="admin",
            password="secret",
            auth_method=AuthMethod.KEY,
            ssh_key_file=key_file,
            ssh_timeout=60,
            max_workers=10,
            output_file=output_file,
            output_format="JSON",
            verbose=True,
            debug=True
        )
        
        assert config.username == "admin"
        assert config.password == "secret"
        assert config.auth_method == AuthMethod.KEY
        assert config.ssh_key_file == key_file.resolve()
        assert config.ssh_timeout == 60
        assert config.max_workers == 10
        assert config.output_file == output_file.resolve()
        assert config.output_format == "json"  # Normalized to lowercase
        assert config.verbose is True
        assert config.debug is True
    
    def test_config_invalid_ssh_timeout(self, tmp_path):
        """Test config with invalid SSH timeout."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        with pytest.raises(ValueError, match="ssh_timeout must be positive"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                ssh_timeout=0
            )
        
        with pytest.raises(ValueError, match="ssh_timeout must be positive"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                ssh_timeout=-5
            )
    
    def test_config_invalid_max_workers(self, tmp_path):
        """Test config with invalid max_workers."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        with pytest.raises(ValueError, match="max_workers must be positive"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                max_workers=0
            )
    
    def test_config_invalid_output_format(self, tmp_path):
        """Test config with invalid output format."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        with pytest.raises(ValueError, match="Invalid output_format"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                output_format="invalid"
            )
    
    def test_config_valid_output_formats(self, tmp_path):
        """Test all valid output formats."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        for fmt in ["csv", "json", "yaml", "html", "xlsx"]:
            config = Config(
                devices_file=devices_file,
                commands_file=commands_file,
                output_format=fmt.upper()
            )
            assert config.output_format == fmt.lower()
    
    def test_config_key_auth_without_key_file(self, tmp_path):
        """Test KEY auth method without providing key file."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        with pytest.raises(ValueError, match="ssh_key_file required"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                auth_method=AuthMethod.KEY
            )
    
    def test_config_key_auth_nonexistent_key(self, tmp_path):
        """Test KEY auth with non-existent key file."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        key_file = tmp_path / "nonexistent_key"
        
        devices_file.touch()
        commands_file.touch()
        
        with pytest.raises(FileNotFoundError, match="SSH key file not found"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                auth_method=AuthMethod.KEY,
                ssh_key_file=key_file
            )
    
    def test_config_negative_values(self, tmp_path):
        """Test config with negative values where not allowed."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        with pytest.raises(ValueError, match="ssh_keepalive cannot be negative"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                ssh_keepalive=-1
            )
        
        with pytest.raises(ValueError, match="retry_attempts cannot be negative"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                retry_attempts=-1
            )
        
        with pytest.raises(ValueError, match="retry_delay cannot be negative"):
            Config(
                devices_file=devices_file,
                commands_file=commands_file,
                retry_delay=-1
            )
    
    def test_config_validate_input_files_success(self, tmp_path):
        """Test validate_input_files with existing files."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file
        )
        
        # Should not raise
        config.validate_input_files()
    
    def test_config_validate_input_files_missing_devices(self, tmp_path):
        """Test validate_input_files with missing devices file."""
        devices_file = tmp_path / "nonexistent.csv"
        commands_file = tmp_path / "commands.txt"
        commands_file.touch()
        
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file
        )
        
        with pytest.raises(FileNotFoundError, match="Devices file not found"):
            config.validate_input_files()
    
    def test_config_validate_input_files_missing_commands(self, tmp_path):
        """Test validate_input_files with missing commands file."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "nonexistent.txt"
        devices_file.touch()
        
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file
        )
        
        with pytest.raises(FileNotFoundError, match="Commands file not found"):
            config.validate_input_files()
    
    def test_config_needs_credentials_property(self, tmp_path):
        """Test needs_credentials property."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        key_file = tmp_path / "id_rsa"
        devices_file.touch()
        commands_file.touch()
        key_file.touch()
        
        # PASSWORD auth needs credentials
        config_pwd = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            auth_method=AuthMethod.PASSWORD
        )
        assert config_pwd.needs_credentials is True
        
        # KEY auth doesn't need username/password
        config_key = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            auth_method=AuthMethod.KEY,
            ssh_key_file=key_file
        )
        assert config_key.needs_credentials is False
    
    def test_config_has_username_property(self, tmp_path):
        """Test has_username property."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        config_no_user = Config(
            devices_file=devices_file,
            commands_file=commands_file
        )
        assert config_no_user.has_username is False
        
        config_empty_user = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            username=""
        )
        assert config_empty_user.has_username is False
        
        config_with_user = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            username="admin"
        )
        assert config_with_user.has_username is True
    
    def test_config_has_password_property(self, tmp_path):
        """Test has_password property."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        config_no_pwd = Config(
            devices_file=devices_file,
            commands_file=commands_file
        )
        assert config_no_pwd.has_password is False
        
        config_empty_pwd = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            password=""
        )
        assert config_empty_pwd.has_password is False
        
        config_with_pwd = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            password="secret"
        )
        assert config_with_pwd.has_password is True
    
    def test_config_to_dict(self, tmp_path):
        """Test to_dict method."""
        devices_file = tmp_path / "devices.csv"
        commands_file = tmp_path / "commands.txt"
        devices_file.touch()
        commands_file.touch()
        
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            username="admin",
            password="secret",
            ssh_timeout=45,
            max_workers=8
        )
        
        config_dict = config.to_dict()
        
        assert "devices_file" in config_dict
        assert "commands_file" in config_dict
        assert config_dict["username"] == "admin"
        # Password is excluded
        assert "password" not in config_dict
        assert config_dict["ssh_timeout"] == 45
        assert config_dict["max_workers"] == 8
        assert config_dict["auth_method"] == "password"
