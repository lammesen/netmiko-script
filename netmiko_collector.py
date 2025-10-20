#!/usr/bin/env python3
"""
Netmiko Device Command Collector

This script connects to multiple Cisco IOS devices via SSH using Netmiko,
executes a list of commands on each device, and saves the output to a CSV file.

Author: Network Automation
Date: 2025-10-20
"""

import csv
import sys
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants for boolean value parsing
TRUTHY_VALUES = ("true", "yes", "1")

# Default configuration file
CONFIG_FILE = Path.home() / ".netmiko_collector_config.json"

try:
    from netmiko import ConnectHandler
    from netmiko.exceptions import (
        NetmikoTimeoutException,
        NetmikoAuthenticationException,
    )
except ImportError:
    print(
        "Error: Netmiko is not installed. Please run: pip install -r requirements.txt"
    )
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("netmiko_collector.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def load_config() -> Dict:
    """
    Load configuration from file.

    Returns:
        Configuration dictionary with default values if file doesn't exist
    """
    default_config = {
        "default_device_type": "cisco_ios",
        "strip_whitespace": True,
        "max_workers": 5,
        "connection_timeout": 30,
        "command_timeout": 60,
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_config, **config}
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Failed to load config file: %s. Using defaults.", e)

    return default_config


def save_config(config: Dict) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration dictionary to save
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved to %s", CONFIG_FILE)
    except IOError as e:
        logger.error("Failed to save config file: %s", e)


def show_settings_menu(config: Dict) -> Dict:
    """
    Display interactive settings menu and allow user to modify configuration.

    Args:
        config: Current configuration dictionary

    Returns:
        Updated configuration dictionary
    """
    while True:
        print("\n" + "=" * 60)
        print("SETTINGS MENU")
        print("=" * 60)
        print(f"1. Default Device Type: {config['default_device_type']}")
        print(f"2. Strip Whitespace from Output: {config['strip_whitespace']}")
        print(f"3. Max Concurrent Workers: {config['max_workers']}")
        print(f"4. Connection Timeout (seconds): {config['connection_timeout']}")
        print(f"5. Command Timeout (seconds): {config['command_timeout']}")
        print("6. Save Settings")
        print("7. Reset to Defaults")
        print("8. Back to Main Menu")
        print("=" * 60)

        choice = input("\nEnter your choice (1-8): ").strip()

        if choice == "1":
            prompt = "Enter default device type "
            prompt += f"[{config['default_device_type']}]: "
            new_value = input(prompt).strip()
            if new_value:
                config['default_device_type'] = new_value
                print(f"✓ Default device type set to: {new_value}")

        elif choice == "2":
            current = "yes" if config['strip_whitespace'] else "no"
            prompt = f"Strip whitespace? (yes/no) [{current}]: "
            new_value = input(prompt).strip().lower()
            if new_value in ["yes", "y", "true", "1"]:
                config['strip_whitespace'] = True
                print("✓ Whitespace stripping enabled")
            elif new_value in ["no", "n", "false", "0"]:
                config['strip_whitespace'] = False
                print("✓ Whitespace stripping disabled")

        elif choice == "3":
            try:
                prompt = "Enter max workers (1-20) "
                prompt += f"[{config['max_workers']}]: "
                new_value = input(prompt).strip()
                if new_value:
                    workers = int(new_value)
                    if 1 <= workers <= 20:
                        config['max_workers'] = workers
                        print(f"✓ Max workers set to: {workers}")
                    else:
                        print("✗ Value must be between 1 and 20")
            except ValueError:
                print("✗ Invalid number")

        elif choice == "4":
            try:
                prompt = "Enter connection timeout "
                prompt += f"[{config['connection_timeout']}]: "
                new_value = input(prompt).strip()
                if new_value:
                    timeout = int(new_value)
                    if timeout > 0:
                        config['connection_timeout'] = timeout
                        msg = f"✓ Connection timeout set to: {timeout} seconds"
                        print(msg)
                    else:
                        print("✗ Timeout must be positive")
            except ValueError:
                print("✗ Invalid number")

        elif choice == "5":
            try:
                prompt = "Enter command timeout "
                prompt += f"[{config['command_timeout']}]: "
                new_value = input(prompt).strip()
                if new_value:
                    timeout = int(new_value)
                    if timeout > 0:
                        config['command_timeout'] = timeout
                        msg = f"✓ Command timeout set to: {timeout} seconds"
                        print(msg)
                    else:
                        print("✗ Timeout must be positive")
            except ValueError:
                print("✗ Invalid number")

        elif choice == "6":
            save_config(config)
            print("✓ Settings saved successfully")

        elif choice == "7":
            confirm = input("Reset all settings to defaults? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                config = load_config()
                config['default_device_type'] = "cisco_ios"
                config['strip_whitespace'] = True
                config['max_workers'] = 5
                config['connection_timeout'] = 30
                config['command_timeout'] = 60
                print("✓ Settings reset to defaults")

        elif choice == "8":
            break

        else:
            print("✗ Invalid choice. Please enter 1-8.")

    return config


def load_devices(
    devices_file: str,
    default_device_type: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Load device information from a CSV file.

    Expected CSV format:
    hostname,ip_address,device_type,ssh_config_file,use_keys,key_file
    router1,192.168.1.1,cisco_ios,,,
    switch1,192.168.1.2,cisco_ios,~/.ssh/config,true,~/.ssh/id_rsa

    Required fields: hostname, ip_address
    Optional fields: device_type, ssh_config_file, use_keys, key_file

    If device_type is not provided in CSV and default_device_type is set,
    the default will be used.

    Args:
        devices_file: Path to the devices CSV file
        default_device_type: Default device type to use if not specified

    Returns:
        List of device dictionaries

    Raises:
        FileNotFoundError: If the devices file doesn't exist
        ValueError: If the CSV format is invalid
    """
    devices = []

    if not Path(devices_file).exists():
        raise FileNotFoundError(f"Devices file not found: {devices_file}")

    try:
        with open(devices_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required_fields = {"hostname", "ip_address"}
            optional_fields = {"device_type", "ssh_config_file", "use_keys", "key_file"}

            for row_num, row in enumerate(reader, start=2):
                # Validate required fields
                if not required_fields.issubset(row.keys()):
                    msg = "CSV must contain columns: "
                    msg += f"{', '.join(required_fields)}"
                    raise ValueError(msg)

                normalized_row = {}
                missing_values = []

                for field in required_fields:
                    value = row.get(field)
                    if value is None:
                        missing_values.append(field)
                        continue

                    trimmed = value.strip()
                    if not trimmed:
                        missing_values.append(field)
                        continue

                    normalized_row[field] = trimmed

                if missing_values:
                    fields = ', '.join(sorted(missing_values))
                    msg = "Row {} has missing values for: {}".format(
                        row_num, fields
                    )
                    raise ValueError(msg)

                # Process optional fields
                for field in optional_fields:
                    value = row.get(field, "").strip()
                    if value:
                        normalized_row[field] = value

                # Apply default device_type if not specified
                if "device_type" not in normalized_row and default_device_type:
                    normalized_row["device_type"] = default_device_type

                # Verify device_type is set
                if "device_type" not in normalized_row:
                    msg = f"Row {row_num}: device_type not specified "
                    msg += "and no default provided"
                    raise ValueError(msg)

                devices.append(normalized_row)

        if not devices:
            raise ValueError("No devices found in the file")

        logger.info("Loaded %d device(s) from %s", len(devices), devices_file)
        return devices

    except csv.Error as e:
        raise ValueError(f"Error parsing CSV file: {e}") from e


def load_commands(commands_file: str) -> List[str]:
    """
    Load commands from a text file (one command per line).

    Args:
        commands_file: Path to the commands file

    Returns:
        List of commands to execute

    Raises:
        FileNotFoundError: If the commands file doesn't exist
    """
    if not Path(commands_file).exists():
        raise FileNotFoundError(f"Commands file not found: {commands_file}")

    with open(commands_file, "r", encoding="utf-8") as f:
        commands = []
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            commands.append(stripped)

    if not commands:
        raise ValueError("No commands found in the file")

    logger.info("Loaded %d command(s) from %s", len(commands), commands_file)
    return commands


def connect_and_execute(
    device: Dict[str, str],
    commands: List[str],
    username: str,
    password: str,
    global_ssh_config: str = None,
    strip_whitespace: bool = True,
    connection_timeout: int = 30,
    command_timeout: int = 60
) -> List[Dict[str, str]]:
    """
    Connect to a device and execute commands.

    Args:
        device: Device information dictionary
        commands: List of commands to execute
        username: SSH username
        password: SSH password
        global_ssh_config: Global SSH config file path (optional)
        strip_whitespace: Strip extra whitespace from output
        connection_timeout: Connection timeout in seconds (default: 30)
        command_timeout: Command execution timeout in seconds

    Returns:
        List of result dictionaries containing command outputs
    """
    results = []
    hostname = device["hostname"]

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    device_params = {
        "device_type": device["device_type"],
        "host": device["ip_address"],
        "username": username,
        "password": password,
        "timeout": connection_timeout,
        "session_log": f"session_{hostname}_{timestamp}.log",
    }

    # Add SSH config file support (device-specific or global)
    ssh_config_file = device.get("ssh_config_file")
    if not ssh_config_file:
        ssh_config_file = global_ssh_config
    if ssh_config_file:
        device_params["ssh_config_file"] = ssh_config_file

    # Add SSH key authentication support
    if device.get("use_keys"):
        use_keys_value = device["use_keys"].lower()
        if use_keys_value in TRUTHY_VALUES:
            device_params["use_keys"] = True
            if device.get("key_file"):
                device_params["key_file"] = device["key_file"]

    try:
        logger.info("Connecting to %s (%s)...", hostname, device['ip_address'])
        connection = ConnectHandler(**device_params)

        logger.info("Successfully connected to %s", hostname)

        # Execute each command
        for command in commands:
            logger.info("Executing '%s' on %s", command, hostname)
            try:
                output = connection.send_command(
                    command, read_timeout=command_timeout
                )

                # Strip extra whitespace if enabled
                if strip_whitespace:
                    # Remove leading/trailing whitespace from each line
                    lines = output.splitlines()
                    output = '\n'.join(line.rstrip() for line in lines).strip()

                results.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "hostname": hostname,
                        "ip_address": device["ip_address"],
                        "command": command,
                        "output": output,
                        "status": "success",
                    }
                )
                logger.info(
                    "Command '%s' executed successfully on %s",
                    command, hostname
                )
            except Exception as cmd_error:
                error_msg = f"Error executing command: {str(cmd_error)}"
                logger.error("%s on %s", error_msg, hostname)
                results.append(
                    {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "hostname": hostname,
                        "ip_address": device["ip_address"],
                        "command": command,
                        "output": error_msg,
                        "status": "failed",
                    }
                )

        connection.disconnect()
        logger.info("Disconnected from %s", hostname)

    except NetmikoTimeoutException:
        error_msg = "Connection timeout - device unreachable"
        logger.error("%s: %s", hostname, error_msg)
        for command in commands:
            results.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hostname": hostname,
                    "ip_address": device["ip_address"],
                    "command": command,
                    "output": error_msg,
                    "status": "failed",
                }
            )

    except NetmikoAuthenticationException:
        error_msg = "Authentication failed - check credentials"
        logger.error("%s: %s", hostname, error_msg)
        for command in commands:
            results.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hostname": hostname,
                    "ip_address": device["ip_address"],
                    "command": command,
                    "output": error_msg,
                    "status": "failed",
                }
            )

    except Exception as conn_error:
        error_msg = f"Unexpected error: {str(conn_error)}"
        logger.error("%s: %s", hostname, error_msg)
        for command in commands:
            results.append(
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "hostname": hostname,
                    "ip_address": device["ip_address"],
                    "command": command,
                    "output": error_msg,
                    "status": "failed",
                }
            )

    return results


def process_device_concurrent(
    device: Dict[str, str],
    commands: List[str],
    username: str,
    password: str,
    global_ssh_config: str,
    strip_whitespace: bool,
    connection_timeout: int,
    command_timeout: int
) -> List[Dict[str, str]]:
    """
    Wrapper function for concurrent device processing.

    Args:
        device: Device information dictionary
        commands: List of commands to execute
        username: SSH username
        password: SSH password
        global_ssh_config: Global SSH config file path
        strip_whitespace: Whether to strip whitespace from output
        connection_timeout: Connection timeout in seconds
        command_timeout: Command timeout in seconds

    Returns:
        List of result dictionaries
    """
    return connect_and_execute(
        device, commands, username, password,
        global_ssh_config, strip_whitespace,
        connection_timeout, command_timeout
    )


def process_devices_parallel(
    devices: List[Dict[str, str]],
    commands: List[str],
    username: str,
    password: str,
    global_ssh_config: str,
    strip_whitespace: bool,
    connection_timeout: int,
    command_timeout: int,
    max_workers: int = 5
) -> List[Dict[str, str]]:
    """
    Process multiple devices in parallel using ThreadPoolExecutor.

    Args:
        devices: List of device dictionaries
        commands: List of commands to execute
        username: SSH username
        password: SSH password
        global_ssh_config: Global SSH config file path
        strip_whitespace: Whether to strip whitespace from output
        connection_timeout: Connection timeout in seconds
        command_timeout: Command timeout in seconds
        max_workers: Maximum number of concurrent workers

    Returns:
        List of all results from all devices
    """
    all_results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all device processing tasks
        future_to_device = {
            executor.submit(
                process_device_concurrent,
                device, commands, username, password,
                global_ssh_config, strip_whitespace,
                connection_timeout, command_timeout
            ): device for device in devices
        }

        # Collect results as they complete
        for future in as_completed(future_to_device):
            device = future_to_device[future]
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as exc:
                logger.error(
                    "Device %s generated an exception: %s",
                    device['hostname'], exc
                )
                # Add error results for all commands
                for command in commands:
                    all_results.append({
                        "timestamp": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "hostname": device["hostname"],
                        "ip_address": device["ip_address"],
                        "command": command,
                        "output": f"Exception during processing: {str(exc)}",
                        "status": "failed",
                    })

    return all_results


def save_to_csv(results: List[Dict[str, str]], output_file: str) -> None:
    """
    Save command outputs to a CSV file.

    Args:
        results: List of result dictionaries
        output_file: Path to the output CSV file
    """
    if not results:
        logger.warning("No results to save")
        return

    fieldnames = [
        "timestamp", "hostname", "ip_address",
        "command", "output", "status"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    logger.info("Results saved to %s", output_file)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Collect command outputs from network devices using Netmiko",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -d devices.csv -c commands.txt
  %(prog)s -d devices.csv -c commands.txt -o custom_output.csv
  %(prog)s -d devices.csv -c commands.txt -u admin
  %(prog)s --interactive  # Interactive mode with settings menu
  %(prog)s -d devices.csv -c commands.txt --device-type cisco_ios
  %(prog)s -d devices.csv -c commands.txt --workers 10
        """,
    )

    parser.add_argument(
        "-d",
        "--devices",
        help="Path to devices CSV file "
             "(format: hostname,ip_address[,device_type])",
    )

    parser.add_argument(
        "-c",
        "--commands",
        help="Path to commands text file (one command per line)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        help="Output CSV file name (default: output_YYYYMMDD_HHMMSS.csv)",
    )

    parser.add_argument(
        "-u", "--username", help="SSH username (will prompt if not provided)"
    )

    parser.add_argument(
        "-p",
        "--password",
        help="SSH password (NOT RECOMMENDED - use interactive prompt instead)",
    )

    parser.add_argument(
        "-s",
        "--ssh-config",
        help="Path to SSH config file for proxy/jump server configuration",
    )

    parser.add_argument(
        "--device-type",
        help="Default device type for devices without type specified "
             "(e.g., cisco_ios, cisco_xe)",
    )

    parser.add_argument(
        "--no-strip-whitespace",
        action="store_true",
        help="Disable automatic whitespace stripping from command outputs",
    )

    parser.add_argument(
        "--workers",
        type=int,
        help="Maximum number of concurrent workers "
             "(default: from config or 5)",
    )

    parser.add_argument(
        "--connection-timeout",
        type=int,
        help="Connection timeout in seconds (default: from config or 30)",
    )

    parser.add_argument(
        "--command-timeout",
        type=int,
        help="Command execution timeout in seconds "
             "(default: from config or 60)",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch interactive mode with main menu",
    )

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Interactive mode
    if args.interactive:
        while True:
            print("\n" + "=" * 60)
            print("NETMIKO DEVICE COMMAND COLLECTOR")
            print("=" * 60)
            print("1. Run Collection")
            print("2. Settings")
            print("3. View Current Configuration")
            print("4. Exit")
            print("=" * 60)

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
                # Get input files
                devices_file = input("Enter path to devices CSV file: ").strip()
                if not devices_file:
                    print("✗ Devices file is required")
                    continue

                commands_file = input(
                    "Enter path to commands text file: "
                ).strip()
                if not commands_file:
                    print("✗ Commands file is required")
                    continue

                # Get credentials
                username = input("Enter SSH username: ").strip()
                if not username:
                    print("✗ Username is required")
                    continue

                password = getpass("Enter SSH password: ")
                if not password:
                    print("✗ Password is required")
                    continue

                # Get optional parameters
                prompt = f"Enter output filename [{args.output}]: "
                output_file = input(prompt).strip()
                if not output_file:
                    output_file = args.output

                prompt = "Enter SSH config file path (or press Enter to skip): "
                ssh_config = input(prompt).strip()

                try:
                    devices = load_devices(
                        devices_file, config['default_device_type']
                    )
                    commands = load_commands(commands_file)

                    logger.info(
                        "Starting command collection from %d device(s) "
                        "with %d worker(s)",
                        len(devices), config['max_workers']
                    )

                    # Process devices in parallel
                    all_results = process_devices_parallel(
                        devices, commands, username, password,
                        ssh_config if ssh_config else None,
                        config['strip_whitespace'],
                        config['connection_timeout'],
                        config['command_timeout'],
                        config['max_workers']
                    )

                    # Save results
                    save_to_csv(all_results, output_file)

                    # Summary
                    total_commands = len(all_results)
                    successful = sum(
                        1 for r in all_results if r["status"] == "success"
                    )
                    failed = total_commands - successful

                    print("\n" + "=" * 60)
                    print("COLLECTION COMPLETE!")
                    print("=" * 60)
                    print(f"Total devices: {len(devices)}")
                    print(f"Total commands executed: {total_commands}")
                    print(f"Successful: {successful}")
                    print(f"Failed: {failed}")
                    print(f"Output file: {output_file}")
                    print("=" * 60)

                except (FileNotFoundError, ValueError) as load_error:
                    print(f"✗ Error: {load_error}")
                    continue

            elif choice == "2":
                config = show_settings_menu(config)

            elif choice == "3":
                print("\n" + "=" * 60)
                print("CURRENT CONFIGURATION")
                print("=" * 60)
                print(f"Default Device Type: {config['default_device_type']}")
                print(f"Strip Whitespace: {config['strip_whitespace']}")
                print(f"Max Workers: {config['max_workers']}")
                print(f"Connection Timeout: {config['connection_timeout']} seconds")
                print(f"Command Timeout: {config['command_timeout']} seconds")
                print(f"Config File: {CONFIG_FILE}")
                print("=" * 60)

            elif choice == "4":
                print("\nGoodbye!")
                sys.exit(0)

            else:
                print("✗ Invalid choice. Please enter 1-4.")

        return

    # Command-line mode (non-interactive)
    if not args.devices or not args.commands:
        parser.error(
            "--devices and --commands are required "
            "(or use --interactive mode)"
        )

    # Override config with command-line arguments
    if args.device_type:
        config['default_device_type'] = args.device_type
    if args.no_strip_whitespace:
        config['strip_whitespace'] = False
    if args.workers:
        config['max_workers'] = args.workers
    if args.connection_timeout:
        config['connection_timeout'] = args.connection_timeout
    if args.command_timeout:
        config['command_timeout'] = args.command_timeout

    # Load devices and commands
    try:
        devices = load_devices(args.devices, config['default_device_type'])
        commands = load_commands(args.commands)
    except (FileNotFoundError, ValueError) as load_error:
        logger.error("Error loading input files: %s", load_error)
        sys.exit(1)

    # Get credentials
    username = args.username or input("Enter SSH username: ")
    password = args.password or getpass("Enter SSH password: ")

    if not username or not password:
        logger.error("Username and password are required")
        sys.exit(1)

    # Process all devices in parallel
    logger.info(
        "Starting command collection from %d device(s) with %d worker(s)",
        len(devices), config['max_workers']
    )

    all_results = process_devices_parallel(
        devices, commands, username, password,
        args.ssh_config,
        config['strip_whitespace'],
        config['connection_timeout'],
        config['command_timeout'],
        config['max_workers']
    )

    # Save results
    save_to_csv(all_results, args.output)

    # Summary
    total_commands = len(all_results)
    successful = sum(1 for r in all_results if r["status"] == "success")
    failed = total_commands - successful

    logger.info("=" * 60)
    logger.info("SUMMARY:")
    logger.info("Total devices: %d", len(devices))
    logger.info("Total commands executed: %d", total_commands)
    logger.info("Successful: %d", successful)
    logger.info("Failed: %d", failed)
    logger.info("Output file: %s", args.output)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
