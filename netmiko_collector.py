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
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from getpass import getpass

try:
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
except ImportError:
    print("Error: Netmiko is not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netmiko_collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_devices(devices_file: str) -> List[Dict[str, str]]:
    """
    Load device information from a CSV file.

    Expected CSV format:
    hostname,ip_address,device_type
    router1,192.168.1.1,cisco_ios
    switch1,192.168.1.2,cisco_ios

    Args:
        devices_file: Path to the devices CSV file

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
        with open(devices_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_fields = {'hostname', 'ip_address', 'device_type'}

            for row_num, row in enumerate(reader, start=2):
                # Validate required fields
                if not required_fields.issubset(row.keys()):
                    raise ValueError(
                        f"CSV must contain columns: {', '.join(required_fields)}"
                    )

                devices.append({
                    'hostname': row['hostname'].strip(),
                    'ip_address': row['ip_address'].strip(),
                    'device_type': row['device_type'].strip()
                })

        if not devices:
            raise ValueError("No devices found in the file")

        logger.info(f"Loaded {len(devices)} device(s) from {devices_file}")
        return devices

    except csv.Error as e:
        raise ValueError(f"Error parsing CSV file: {e}")


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

    with open(commands_file, 'r', encoding='utf-8') as f:
        commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not commands:
        raise ValueError("No commands found in the file")

    logger.info(f"Loaded {len(commands)} command(s) from {commands_file}")
    return commands


def connect_and_execute(device: Dict[str, str], commands: List[str],
                       username: str, password: str) -> List[Dict[str, str]]:
    """
    Connect to a device and execute commands.

    Args:
        device: Device information dictionary
        commands: List of commands to execute
        username: SSH username
        password: SSH password

    Returns:
        List of result dictionaries containing command outputs
    """
    results = []
    hostname = device['hostname']

    device_params = {
        'device_type': device['device_type'],
        'host': device['ip_address'],
        'username': username,
        'password': password,
        'timeout': 30,
        'session_log': f'session_{hostname}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    }

    try:
        logger.info(f"Connecting to {hostname} ({device['ip_address']})...")
        connection = ConnectHandler(**device_params)

        logger.info(f"Successfully connected to {hostname}")

        # Execute each command
        for command in commands:
            logger.info(f"Executing '{command}' on {hostname}")
            try:
                output = connection.send_command(command, read_timeout=60)
                results.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'hostname': hostname,
                    'ip_address': device['ip_address'],
                    'command': command,
                    'output': output,
                    'status': 'success'
                })
                logger.info(f"Command '{command}' executed successfully on {hostname}")
            except Exception as e:
                error_msg = f"Error executing command: {str(e)}"
                logger.error(f"{error_msg} on {hostname}")
                results.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'hostname': hostname,
                    'ip_address': device['ip_address'],
                    'command': command,
                    'output': error_msg,
                    'status': 'failed'
                })

        connection.disconnect()
        logger.info(f"Disconnected from {hostname}")

    except NetmikoTimeoutException:
        error_msg = "Connection timeout - device unreachable"
        logger.error(f"{hostname}: {error_msg}")
        for command in commands:
            results.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hostname': hostname,
                'ip_address': device['ip_address'],
                'command': command,
                'output': error_msg,
                'status': 'failed'
            })

    except NetmikoAuthenticationException:
        error_msg = "Authentication failed - check credentials"
        logger.error(f"{hostname}: {error_msg}")
        for command in commands:
            results.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hostname': hostname,
                'ip_address': device['ip_address'],
                'command': command,
                'output': error_msg,
                'status': 'failed'
            })

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{hostname}: {error_msg}")
        for command in commands:
            results.append({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hostname': hostname,
                'ip_address': device['ip_address'],
                'command': command,
                'output': error_msg,
                'status': 'failed'
            })

    return results


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

    fieldnames = ['timestamp', 'hostname', 'ip_address', 'command', 'output', 'status']

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"Results saved to {output_file}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Collect command outputs from Cisco devices using Netmiko',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -d devices.csv -c commands.txt
  %(prog)s -d devices.csv -c commands.txt -o custom_output.csv
  %(prog)s -d devices.csv -c commands.txt -u admin
        """
    )

    parser.add_argument(
        '-d', '--devices',
        required=True,
        help='Path to devices CSV file (format: hostname,ip_address,device_type)'
    )

    parser.add_argument(
        '-c', '--commands',
        required=True,
        help='Path to commands text file (one command per line)'
    )

    parser.add_argument(
        '-o', '--output',
        default=f'output_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        help='Output CSV file name (default: output_YYYYMMDD_HHMMSS.csv)'
    )

    parser.add_argument(
        '-u', '--username',
        help='SSH username (will prompt if not provided)'
    )

    parser.add_argument(
        '-p', '--password',
        help='SSH password (NOT RECOMMENDED - use interactive prompt instead)'
    )

    args = parser.parse_args()

    # Load devices and commands
    try:
        devices = load_devices(args.devices)
        commands = load_commands(args.commands)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error loading input files: {e}")
        sys.exit(1)

    # Get credentials
    username = args.username or input("Enter SSH username: ")
    password = args.password or getpass("Enter SSH password: ")

    if not username or not password:
        logger.error("Username and password are required")
        sys.exit(1)

    # Process all devices
    logger.info(f"Starting command collection from {len(devices)} device(s)")
    all_results = []

    for device in devices:
        results = connect_and_execute(device, commands, username, password)
        all_results.extend(results)

    # Save results
    save_to_csv(all_results, args.output)

    # Summary
    total_commands = len(all_results)
    successful = sum(1 for r in all_results if r['status'] == 'success')
    failed = total_commands - successful

    logger.info("=" * 60)
    logger.info("SUMMARY:")
    logger.info(f"Total devices: {len(devices)}")
    logger.info(f"Total commands executed: {total_commands}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Output file: {args.output}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
