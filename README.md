# Netmiko Device Command Collector

A production-ready Python script that uses Netmiko to SSH into multiple Cisco IOS devices, execute commands, and collect outputs into a CSV file.

## Features

- Connect to multiple Cisco devices via SSH
- Execute multiple commands on each device
- Collect all outputs into a single CSV file
- Comprehensive error handling and logging
- Session logs for each device connection
- Support for authentication failures and timeouts
- Timestamped outputs and results

## Requirements

- Python 3.7 or higher
- Netmiko library
- SSH access to target devices

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Input File Formats

### Devices File (CSV)

Create a CSV file with the following format:

```csv
hostname,ip_address,device_type
router1,192.168.1.1,cisco_ios
switch1,192.168.1.2,cisco_ios
router2,10.0.0.1,cisco_ios
```

**Required columns:**
- `hostname`: Friendly name for the device
- `ip_address`: IP address or hostname of the device
- `device_type`: Netmiko device type (e.g., cisco_ios, cisco_xe, cisco_nxos)

### Commands File (TXT)

Create a text file with one command per line:

```
show version
show ip interface brief
show running-config | include hostname
show inventory
```

**Notes:**
- Lines starting with `#` are treated as comments and ignored
- Blank lines are ignored
- Commands are executed in the order listed

## Usage

### Basic Usage

```bash
python netmiko_collector.py -d devices.csv -c commands.txt
```

This will:
- Prompt for SSH username
- Prompt for SSH password (hidden input)
- Execute commands on all devices
- Save results to `output_YYYYMMDD_HHMMSS.csv`

### Advanced Usage

**Specify output file:**
```bash
python netmiko_collector.py -d devices.csv -c commands.txt -o my_results.csv
```

**Provide username via command line:**
```bash
python netmiko_collector.py -d devices.csv -c commands.txt -u admin
```

**View help:**
```bash
python netmiko_collector.py --help
```

## Output

### CSV Output File

The script generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| timestamp | When the command was executed |
| hostname | Device hostname |
| ip_address | Device IP address |
| command | Command that was executed |
| output | Command output or error message |
| status | success or failed |

### Log Files

**Application Log (`netmiko_collector.log`):**
- Contains execution logs
- Connection status
- Errors and warnings
- Summary statistics

**Session Logs (`session_<hostname>_<timestamp>.log`):**
- Created for each device connection
- Contains raw SSH session data
- Useful for troubleshooting

## Example Output

```csv
timestamp,hostname,ip_address,command,output,status
2025-10-20 14:30:15,router1,192.168.1.1,show version,"Cisco IOS Software...",success
2025-10-20 14:30:18,router1,192.168.1.1,show ip interface brief,"Interface IP-Address...",success
2025-10-20 14:30:20,switch1,192.168.1.2,show version,Connection timeout - device unreachable,failed
```

## Error Handling

The script handles common errors gracefully:

- **Connection Timeout**: Device is unreachable
- **Authentication Failure**: Invalid credentials
- **Command Execution Error**: Command syntax or device issues
- **File Not Found**: Missing input files
- **Invalid CSV Format**: Malformed device file

All errors are logged and included in the output CSV with status='failed'.

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use interactive password prompt** (default behavior) instead of `-p` flag
3. **Restrict file permissions** on configuration files
4. **Review session logs** before sharing
5. **Use SSH keys** where possible (requires Netmiko configuration)

## Troubleshooting

### Connection Issues

1. Verify device IP addresses are correct
2. Check network connectivity: `ping <device_ip>`
3. Verify SSH is enabled on devices
4. Check firewall rules
5. Review session logs for detailed error messages

### Authentication Issues

1. Verify username and password
2. Check if account is locked
3. Verify privilege level (may need enable password for some commands)
4. Check device AAA configuration

### Command Execution Issues

1. Verify command syntax for device OS
2. Check user privilege level
3. Increase timeout values if needed (modify script)
4. Review device resource availability (CPU, memory)

## Customization

### Timeout Values

Edit `netmiko_collector.py` line 125-126:
```python
'timeout': 30,  # Connection timeout
```

And line 139:
```python
output = connection.send_command(command, read_timeout=60)
```

### Device Types

Supported device types include:
- `cisco_ios`
- `cisco_xe`
- `cisco_nxos`
- `cisco_asa`
- And many more (see Netmiko documentation)

### Enable Mode

To execute commands requiring enable mode, modify the connection section around line 136:
```python
connection = ConnectHandler(**device_params)
connection.enable()  # Add this line
```

## Example Workflow

1. Create your devices file:
```bash
notepad devices.csv
```

2. Create your commands file:
```bash
notepad commands.txt
```

3. Run the script:
```bash
python netmiko_collector.py -d devices.csv -c commands.txt -u admin
```

4. Enter password when prompted

5. Review results:
```bash
type output_*.csv
```

6. Check logs for issues:
```bash
type netmiko_collector.log
```

## License

This script is provided as-is for network automation purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files
3. Verify input file formats
4. Test connectivity manually

## Version History

- **1.0.0** (2025-10-20): Initial release
  - Basic SSH connectivity
  - Command execution
  - CSV output
  - Error handling
  - Logging
