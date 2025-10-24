# Netmiko Device Command Collector

A production-ready Python CLI tool that uses Netmiko to SSH into multiple Cisco IOS devices, execute commands, and collect outputs into multiple formats. **Now with modern Typer CLI framework and beautiful Rich UI!**

## Features

### Core Functionality
- Connect to multiple network devices via SSH (Cisco IOS, IOS-XE, NX-OS, and more)
- Execute multiple commands on each device
- **Concurrent/parallel processing** for faster execution (configurable 1-20 worker threads)
- Collect outputs in multiple formats (CSV, JSON, HTML, Markdown, Excel)
- Comprehensive error handling and logging
- Timestamped outputs and results

### Modern CLI ✨ NEW in v4.0
- **🚀 Typer CLI Framework** - Modern command-line interface with subcommands
- **📝 Organized Commands** - Intuitive command structure (`run`, `edit`, `view`, `config`, `sample`)
- **🎨 Rich Integration** - Beautiful terminal output with colors, tables, and panels
- **✨ Smart File Detection** - Automatically finds and uses files in current directory
- **🎯 Smart Defaults** - Press Enter to accept sensible defaults in prompts
- **📋 Interactive Autocomplete** - Clean, minimal command suggestions as you type
- **💡 Excellent Help System** - Comprehensive `--help` at every command level

### Advanced Features
- **📊 Real-time progress bars** - Visual feedback during execution (Rich or tqdm)
- **🔄 Automatic retry logic** - Configurable retry on connection failures with exponential backoff
- **🔐 Enable mode support** - Automatically enter privileged EXEC mode
- **🔧 Flexible session logging** - Optional session logs (disabled by default for security)
- **⚡ Path expansion** - Automatic `~` expansion for SSH config and key files
- **✅ Key file validation** - Checks SSH key file existence before connection

### Configuration & Usability
- **Automatic whitespace stripping** from command outputs (optional)
- **Default device type** configuration to simplify device CSV files
- **Persistent configuration** saved to ~/.netmiko_collector_config.json
- **SSH proxy/jump server support** - Connect through bastion hosts
- **SSH key authentication** - Password-less authentication support
- **Smart defaults** - Sensible configuration out of the box

## Requirements

- Python 3.7 or higher
- **Typer library** (required - modern CLI framework)
- **Netmiko library** (required - network automation)
- **Rich library** (recommended - beautiful CLI formatting, included with typer[all])
- **Click library** (required - CLI toolkit, included with typer)
- tqdm library (optional - fallback progress bars)
- tenacity library (optional - for retry logic)
- openpyxl library (optional - for Excel output)
- prompt_toolkit library (optional - interactive command autocomplete)
- SSH access to target devices

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

**Note:** For the best experience, install all dependencies including `typer[all]` which includes Rich for beautiful formatting. The script requires Typer but will work without optional libraries like tqdm, tenacity, openpyxl, and prompt_toolkit.

## Input File Formats

### Devices File (CSV)

Create a CSV file with the following format:

```csv
hostname,ip_address,device_type,ssh_config_file,use_keys,key_file
router1,192.168.1.1,cisco_ios,,,
switch1,192.168.1.2,cisco_ios,,,
router2,10.0.0.1,cisco_ios,~/.ssh/config,true,~/.ssh/id_rsa
```

**Required columns:**
- `hostname`: Friendly name for the device
- `ip_address`: IP address or hostname of the device (can be an alias from SSH config)

**Optional columns:**
- `device_type`: Netmiko device type (e.g., cisco_ios, cisco_xe, cisco_nxos). If not specified, the default device type from settings or CLI will be used.
- `ssh_config_file`: Path to SSH config file for this device (e.g., ~/.ssh/config)
- `use_keys`: Set to "true", "yes", or "1" to enable SSH key authentication
- `key_file`: Path to SSH private key file (e.g., ~/.ssh/id_rsa)

**Simplified format (using default device type):**
```csv
hostname,ip_address
router1,192.168.1.1
switch1,192.168.1.2
router2,10.0.0.1
```

When using the simplified format, specify the device type using `--device-type` CLI option or in the interactive settings menu.

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

## Output Formats 🎨 NEW in v3.0

The script now supports multiple beautiful output formats! Choose from CSV, JSON, HTML, Markdown, or Excel.

### Available Formats

| Format | Description | Best For | File Extension |
|--------|-------------|----------|----------------|
| **CSV** | Traditional comma-separated values | Excel, data processing, scripts | `.csv` |
| **JSON** | Structured data format | APIs, automation, parsing | `.json` |
| **HTML** | Interactive web report with Bootstrap | Viewing in browser, presentations | `.html` |
| **Markdown** | Documentation format | Documentation, GitHub | `.md` |
| **Excel** | Spreadsheet with formatting | Sharing, reporting, analysis | `.xlsx` |

### Format Features

**CSV (Default)**
- Compatible with all spreadsheet applications
- Easy to parse programmatically
- Flat structure with one row per command

**JSON**
- Hierarchical structure grouped by device
- Includes metadata (timestamps, statistics)
- Perfect for API integration and automation

**HTML** ✨
- Beautiful Bootstrap 5.3 styling
- Interactive accordion sections for each device
- Color-coded success/failure indicators
- Responsive design works on mobile
- Success rate progress bar
- Statistics dashboard with cards
- Dark terminal-style output display
- No external dependencies - opens in any browser

**Markdown**
- GitHub-compatible formatting
- Perfect for documentation and wikis
- Includes summary statistics
- Code blocks for command outputs
- Easy to read in text editors

**Excel** 📊
- Two worksheets: Summary and Detailed Results
- Color-coded status cells (green=success, red=failed)
- Formatted headers with colors
- Auto-sized columns
- Frozen header row
- Professional appearance

### Using Output Formats

**Command Line:**
```bash
# Single format
python netmiko_collector.py -d devices.csv -c commands.txt -f html

# Multiple formats
python netmiko_collector.py -d devices.csv -c commands.txt -f csv json html

# All formats at once
python netmiko_collector.py -d devices.csv -c commands.txt -f all
```

**Interactive Mode:**
When running in interactive mode, you'll be prompted to select your preferred output format:
```
Available output formats:
  1. CSV (default)
  2. JSON (structured data)
  3. HTML (beautiful web report)
  4. Markdown (documentation)
  5. Excel (spreadsheet with formatting)
  6. All formats
Select format (1-6 or enter for CSV):
```

### Output Examples

**HTML Report Screenshot:**
- Gradient header with device collection title
- 4 colored statistics cards (devices, commands, successful, failed)
- Success rate progress bar
- Collapsible accordion for each device and command
- Terminal-style output display with syntax highlighting

**Excel Workbook:**
- **Summary Sheet**: Overview statistics with colored metrics
- **Detailed Results Sheet**: All data with color-coded status column

**JSON Structure:**
```json
{
  "generated_at": "2025-10-24 14:30:00",
  "total_devices": 3,
  "total_commands": 9,
  "devices": [
    {
      "hostname": "router1",
      "ip_address": "192.168.1.1",
      "commands": [
        {
          "timestamp": "2025-10-24 14:30:15",
          "command": "show version",
          "output": "...",
          "status": "success"
        }
      ]
    }
  ]
}
```

## Usage

The tool uses a modern Typer-based CLI with organized subcommands. Get help at any level with `--help`.

### Quick Start

**View all available commands:**
```bash
python netmiko_collector.py --help
```

**Run a collection (interactive mode - detects files automatically):**
```bash
python netmiko_collector.py run
```

**Run with specific files:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt
```

### Command Structure

The CLI is organized into intuitive subcommands:

| Command | Description |
|---------|-------------|
| `run` | Run command collection on network devices |
| `edit` | Edit devices or commands files |
| `view` | View output files interactively |
| `config` | Manage configuration settings (show/set/reset) |
| `sample` | Create sample files (devices/commands) |

### Run Command - Execute Collections

The `run` command is the main command for collecting data from devices.

**Basic usage (interactive mode with auto-detection):**
```bash
python netmiko_collector.py run
```
This will:
- Auto-detect `devices.csv` and `commands.txt` in current directory
- Prompt for confirmation to use detected files
- Prompt for SSH username and password
- Execute commands on all devices
- Save results with timestamp

**Specify files explicitly:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt
```

**Provide username:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt -u admin
```

**Multiple output formats:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt -f json html
python netmiko_collector.py run -d devices.csv -c commands.txt -f all
```

**Custom output filename:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt -o my_results
```

**Increase workers for faster execution:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt -w 10
```

**Enable privileged EXEC mode:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt --enable-mode
```

**Use default device type:**
```bash
python netmiko_collector.py run -d devices.csv -c commands.txt --device-type cisco_ios
```

**All run options:**
```bash
python netmiko_collector.py run --help
```

Options include: `--devices`, `--commands`, `--output`, `--format`, `--username`, `--workers`, `--connection-timeout`, `--command-timeout`, `--enable-mode`, `--enable-password`, `--enable-session-logging`, `--no-strip-whitespace`, `--no-retry`

### Edit Command - Manage Files

Edit your input files with smart detection and autocomplete.

**Edit devices file (auto-detects or creates):**
```bash
python netmiko_collector.py edit devices
```

**Edit commands file (with autocomplete):**
```bash
python netmiko_collector.py edit commands
```

The edit command:
- Automatically detects files in current directory
- Asks for confirmation before using detected files
- Offers to create files if not found
- Opens commands.txt with interactive autocomplete (if prompt_toolkit installed)
- Uses your system's default editor for devices.csv

### View Command - Browse Outputs

View generated output files interactively.

```bash
python netmiko_collector.py view
```

This displays all output files and lets you select one to view. File viewer behavior:
- **HTML files**: Opens in web browser
- **Excel files**: Opens in spreadsheet application
- **JSON/Markdown**: Displays with syntax highlighting
- **CSV**: Displays in terminal

### Config Commands - Settings Management

Manage persistent configuration settings.

**Show current configuration:**
```bash
python netmiko_collector.py config show
```

**Update configuration interactively:**
```bash
python netmiko_collector.py config set
```

This prompts for each setting:
- Default device type
- Strip whitespace preference
- Max workers
- Connection/command timeouts
- Enable session logging
- Enable mode
- Retry on failure

**Reset to defaults:**
```bash
python netmiko_collector.py config reset
```

### Sample Commands - Quick Setup

Create sample template files instantly.

**Create sample devices.csv:**
```bash
python netmiko_collector.py sample devices
```

**Create sample commands.txt:**
```bash
python netmiko_collector.py sample commands
```

### Advanced Examples

**High-performance collection:**
```bash
python netmiko_collector.py run \
  -d devices.csv \
  -c commands.txt \
  -u admin \
  --device-type cisco_ios \
  -w 15 \
  --enable-mode \
  --connection-timeout 45 \
  -o production_audit \
  -f csv json html
```

**Quick setup workflow:**
```bash
# Create sample files
python netmiko_collector.py sample devices
python netmiko_collector.py sample commands

# Edit files
python netmiko_collector.py edit devices
python netmiko_collector.py edit commands

# Configure settings
python netmiko_collector.py config set

# Run collection
python netmiko_collector.py run

# View results
python netmiko_collector.py view
```

### Smart Features in Action

The CLI includes several quality-of-life improvements:

**Auto-Detection:**
When running `run` or `edit` commands without file arguments, the tool:
1. Checks current directory for `devices.csv` or `commands.txt`
2. Asks for confirmation: "Use this file? (yes/no) [yes]:"
3. If not found, offers to create new or browse for existing file

**Smart Defaults:**
All yes/no prompts have sensible defaults:
- Common actions: Default to `[yes]` - just press Enter
- Destructive actions: Default to `[no]` - must explicitly confirm
- Settings: Default to `[current]` - keeps existing value

**Interactive Autocomplete:**
When editing commands.txt (with prompt_toolkit installed):
- Clean, minimal dropdown with command suggestions
- Fuzzy matching for quick command entry
- Device-type aware suggestions
- Simple gray/cyan color scheme

## Proxy/Jump Server Configuration

You can connect to devices through a proxy or jump server using SSH configuration files.

### Method 1: Global SSH Config File

Use the `-s` or `--ssh-config` option to specify an SSH config file for all devices:

```bash
python netmiko_collector.py -d devices.csv -c commands.txt -u admin -s ~/.ssh/config
```

### Method 2: Per-Device SSH Config File

Specify the SSH config file for individual devices in the devices.csv file:

```csv
hostname,ip_address,device_type,ssh_config_file,use_keys,key_file
router1,router1-alias,cisco_ios,~/.ssh/config,true,~/.ssh/id_rsa
```

### SSH Config File Example

Create an SSH config file (e.g., `~/.ssh/config`) with your proxy settings:

```
# Jump server configuration
Host jumphost
    HostName 10.0.0.1
    User jumpuser
    IdentityFile ~/.ssh/jump_key

# Target device through jump server
Host router1-alias
    HostName 192.168.1.1
    User netadmin
    ProxyCommand ssh -W %h:%p jumphost
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

In this configuration:
- `jumphost` is the proxy/jump server
- `router1-alias` is the target device accessed through the jump server
- `ProxyCommand` establishes the connection through the jump host
- Use the alias (router1-alias) in the devices.csv file's ip_address column

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

### Configuration File

Settings are automatically saved to `~/.netmiko_collector_config.json` and include:
- Default device type (e.g., cisco_ios)
- Whitespace stripping preference (true/false)
- Maximum concurrent workers (1-20)
- Connection timeout (seconds)
- Command timeout (seconds)
- **NEW in v3.0:** Enable session logging (true/false)
- **NEW in v3.0:** Enable mode support (true/false)
- **NEW in v3.0:** Retry on failure (true/false)

You can modify these settings through:
1. Interactive settings menu (`--interactive` mode) - **Recommended**
2. Command-line arguments (overrides config file for that run)
3. Manually editing the JSON file

### Concurrent Processing

The script uses ThreadPoolExecutor to process multiple devices in parallel:
- **Default**: 5 concurrent workers
- **Configurable**: 1-20 workers via settings or `--workers` option
- **Benefits**: Significantly faster execution on large device inventories
- **Consideration**: Higher values may impact network or system resources

### Whitespace Stripping

Automatic whitespace cleanup from command outputs:
- **Default**: Enabled
- **Effect**: Removes trailing spaces from each line and leading/trailing blank lines
- **Toggle**: Use `--no-strip-whitespace` or configure in settings menu
- **Benefits**: Cleaner CSV output, easier parsing

### Timeout Values

Customize connection and command execution timeouts:
- **Connection timeout** (default 30s): Time to establish SSH connection
- **Command timeout** (default 60s): Maximum time to wait for command completion
- **Adjust via**: Settings menu or CLI arguments (`--connection-timeout`, `--command-timeout`)

### Device Types

Supported device types include:
- `cisco_ios`
- `cisco_xe`
- `cisco_nxos`
- `cisco_asa`
- And many more (see Netmiko documentation)

### Enable Mode (v3.0)

Enable mode is now fully configurable:
- **Via Settings Menu**: Configure in interactive mode settings
- **Via CLI**: Use `--enable-mode` flag
- **With Enable Password**: Use `--enable-password` or you'll be prompted

No code modification needed!

### Retry Logic (v3.0)

Automatic retry with exponential backoff:
- **Default**: 3 attempts with 1-10 second wait between retries
- **Configurable**: Enable/disable via settings menu or `--no-retry` flag
- **Requires**: tenacity library (automatically used if installed)
- **Retries on**: Connection timeouts and authentication failures only

### Progress Bars (v3.0)

Visual progress indicators:
- **Rich progress bar**: Colorful, animated (preferred - when Rich installed)
- **tqdm fallback**: Simple text progress bar (when Rich not available)
- **Disable**: Use `--no-progress` flag for non-interactive environments

## Example Workflow

### Example 1: Quick Start with Interactive Mode

1. Launch interactive mode:
```bash
python netmiko_collector.py --interactive
```

2. Configure settings (option 2):
   - Set default device type to `cisco_ios`
   - Enable whitespace stripping
   - Set workers to 10 for faster processing
   - Save settings

3. Run collection (option 1):
   - Provide devices CSV path
   - Provide commands file path
   - Enter credentials
   - Watch as devices are processed in parallel

### Example 2: Command-Line with Minimal CSV

1. Create a minimal devices file (no device_type column):
```bash
cat > devices_simple.csv << EOF
hostname,ip_address
router1,192.168.1.1
router2,192.168.1.2
router3,192.168.1.3
EOF
```

2. Create commands file:
```bash
cat > my_commands.txt << EOF
show version
show ip interface brief
show running-config | include hostname
EOF
```

3. Run with default device type:
```bash
python netmiko_collector.py -d devices_simple.csv -c my_commands.txt \
  --device-type cisco_ios --workers 10 -u admin
```

### Example 3: High-Performance Collection

For large device inventories (50+ devices):

```bash
python netmiko_collector.py \
  -d large_inventory.csv \
  -c commands.txt \
  --device-type cisco_ios \
  --workers 20 \
  --connection-timeout 45 \
  --command-timeout 90 \
  -u admin
```

This configuration processes up to 20 devices simultaneously, significantly reducing total execution time.

### Performance Comparison

**10 devices, 3 commands each:**
- Sequential (old behavior): ~5 minutes
- Parallel with 5 workers: ~1 minute (5x faster)
- Parallel with 10 workers: ~30 seconds (10x faster)

## Example Workflow (Legacy)

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

- **4.0.0** (2025-10-24): 🚀 Modern Typer CLI Framework & UX Enhancements
  - **NEW:** Complete migration from argparse to Typer CLI framework
  - **NEW:** Organized command structure with subcommands (`run`, `edit`, `view`, `config`, `sample`)
  - **NEW:** Rich integration for beautiful help pages with tables and colors
  - **NEW:** Smart file auto-detection in current directory
  - **NEW:** Smart yes/no prompt defaults (press Enter to accept)
  - **NEW:** Simplified autocomplete styling - clean gray/cyan minimal design
  - **NEW:** `config` subcommand group for settings management (show/set/reset)
  - **NEW:** `sample` subcommand group for creating template files
  - **NEW:** `edit` command with auto-detection and create/browse options
  - **NEW:** `view` command for browsing output files
  - **IMPROVED:** Command-line argument handling with type safety via Annotated types
  - **IMPROVED:** Help system with comprehensive `--help` at every command level
  - **IMPROVED:** User experience with fewer keystrokes and smarter defaults
  - **IMPROVED:** Autocomplete dropdown - removed metadata, removed backgrounds
  - **REMOVED:** Old monolithic interactive menu - replaced with subcommand structure
  - **REMOVED:** Password CLI argument (security improvement - use prompts only)
  - Code quality: Modern CLI patterns with Typer best practices
- **3.0.0** (2025-10-24): 🎨 Major UI/UX Overhaul & Production Enhancements
  - **NEW:** Beautiful CLI with Rich library - colored output, tables, and panels
  - **NEW:** Integrated File Manager - edit devices.csv, commands.txt, and view outputs
  - **NEW:** Smart file viewer - HTML in browser, Excel in app, JSON/Markdown with syntax highlighting
  - **NEW:** Sample file creation with templates
  - **NEW:** Multiple output formats - HTML, JSON, Markdown, Excel, CSV
  - **NEW:** Beautiful HTML reports with Bootstrap 5.3 styling and interactive elements
  - **NEW:** Excel output with colored cells and formatted sheets
  - **NEW:** JSON structured output grouped by device
  - **NEW:** Markdown reports for documentation
  - **NEW:** Real-time progress bars with Rich (fallback to tqdm)
  - **NEW:** Automatic retry logic with exponential backoff using tenacity
  - **NEW:** Enable mode support - automatically enter privileged EXEC mode
  - **NEW:** Optional session logging (disabled by default for security)
  - **NEW:** Automatic path expansion for SSH config and key files (~/ support)
  - **NEW:** SSH key file validation before connection attempts
  - **IMPROVED:** Enhanced settings menu with 8 configurable options
  - **IMPROVED:** Better input validation with helper functions
  - **IMPROVED:** Refined whitespace stripping logic
  - **IMPROVED:** Security - password CLI argument removed (use prompt instead)
  - **IMPROVED:** All magic numbers extracted to constants
  - **IMPROVED:** Removed redundant code and wrapper functions
  - **IMPROVED:** Configuration now includes retry, enable mode, and session logging settings
  - **IMPROVED:** Tests fixed - removed importlib.reload anti-pattern
  - **IMPROVED:** CLI arguments validation (workers range check)
  - **IMPROVED:** Summary output with beautiful tables (when Rich available)
  - **IMPROVED:** Better error messages and user feedback
  - Code quality: Production-ready with extensive improvements
- **2.0.0** (2025-10-20): Quality of Life Improvements
  - Added concurrent/parallel device processing with ThreadPoolExecutor
  - Added automatic whitespace stripping from command outputs (configurable)
  - Added default device_type configuration (global setting)
  - Added interactive terminal menu with settings management
  - Added persistent configuration file (~/.netmiko_collector_config.json)
  - Added command-line options for workers, timeouts, and device type
  - Made device_type optional in CSV when default is configured
  - Improved user experience with better prompts and feedback
  - Performance: 5x faster execution on 10+ devices with default settings
- **1.1.0** (2025-10-20): Proxy/Jump Server Support & Code Quality Improvements
  - Added support for SSH config files (global and per-device)
  - Added SSH key authentication support
  - Added proxy/jump server connectivity
  - Fixed pylint warnings (logging format, exception handling)
  - Improved code quality from 8.49/10 to 9.81/10
  - Added .gitignore for better repository management
- **1.0.0** (2025-10-20): Initial release
  - Basic SSH connectivity
  - Command execution
  - CSV output
  - Error handling
  - Logging
