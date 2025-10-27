# Netmiko Device Command Collector

A production-ready Python CLI tool for collecting command outputs from network devices using SSH. Built with modern Typer framework and beautiful Rich UI.

## Features

- **Modern CLI** with Typer framework and Rich formatting
- **Concurrent processing** - configurable worker threads (1-20)
- **Multiple output formats** - CSV, JSON, HTML, Markdown, Excel
- **Smart defaults** - auto-detection, intelligent prompts
- **Retry logic** - automatic retry with exponential backoff
- **SSH features** - proxy/jump server support, key authentication
- **Enable mode** - automatic privileged EXEC mode entry
- **Persistent config** - saved to `~/.netmiko_collector_config.json`

## Requirements

- Python 3.7+
- Netmiko (network automation)
- Typer (CLI framework)
- Rich (terminal formatting - recommended)
- SSH access to target devices

Optional: tqdm, tenacity, openpyxl, prompt_toolkit

## Quick Setup

1. Clone the repository:
```bash
git clone https://github.com/lammesen/netmiko-script.git
cd netmiko-script
```

2. Create and activate virtual environment:
```bash
python -m venv venv

# Windows Command Prompt
venv\Scripts\activate.bat

# PowerShell
.\venv\Scripts\Activate.ps1

# Linux/macOS/Git Bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# View all commands
python netmiko_collector.py --help

# Create sample files
python netmiko_collector.py sample devices
python netmiko_collector.py sample commands

# Run collection (interactive with auto-detection)
python netmiko_collector.py run

# Run with specific files
python netmiko_collector.py run -d devices.csv -c commands.txt

# Multiple output formats
python netmiko_collector.py run -d devices.csv -c commands.txt -f json html excel
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `run` | Execute command collection on devices |
| `edit` | Edit devices or commands files |
| `view` | View output files interactively |
| `config show/set/reset` | Manage configuration settings |
| `sample` | Create sample template files |

## Input Files

### Devices File (CSV)

Minimal format:
```csv
hostname,ip_address
router1,192.168.1.1
switch1,192.168.1.2
```

Full format with optional columns:
```csv
hostname,ip_address,device_type,ssh_config_file,use_keys,key_file
router1,192.168.1.1,cisco_ios,~/.ssh/config,true,~/.ssh/id_rsa
```

### Commands File (TXT)

One command per line:
```
show version
show ip interface brief
show running-config | include hostname
```

Lines starting with `#` are comments and will be ignored.

## Output Formats

- **CSV** - Traditional spreadsheet format
- **JSON** - Structured data with metadata
- **HTML** - Interactive Bootstrap report
- **Markdown** - GitHub-compatible documentation
- **Excel** - Formatted spreadsheet with summary

## Common Usage Examples

```bash
# High-performance collection with 15 workers
python netmiko_collector.py run -d devices.csv -c commands.txt -w 15

# With enable mode
python netmiko_collector.py run -d devices.csv -c commands.txt --enable-mode

# All formats at once
python netmiko_collector.py run -d devices.csv -c commands.txt -f all

# Configure settings
python netmiko_collector.py config set

# View generated outputs
python netmiko_collector.py view
```

## Configuration

Settings are saved to `~/.netmiko_collector_config.json`:
- Default device type
- Max workers (1-20)
- Connection/command timeouts
- Whitespace stripping
- Enable mode
- Session logging
- Retry on failure

Update via: `python netmiko_collector.py config set`

## Proxy/Jump Server

Use SSH config file for proxy connections:

```bash
# ~/.ssh/config
Host jumphost
    HostName 10.0.0.1
    User jumpuser
    IdentityFile ~/.ssh/jump_key

Host router1
    HostName 192.168.1.1
    ProxyCommand ssh -W %h:%p jumphost
```

Then reference in devices.csv:
```csv
hostname,ip_address,ssh_config_file,use_keys,key_file
router1,router1,~/.ssh/config,true,~/.ssh/id_rsa
```

## Output

Results include:
- Timestamped output files in selected format(s)
- Application log: `netmiko_collector.log`
- Session logs: `session_<hostname>_<timestamp>.log` (if enabled)

## Security

### Security Policy

For information on reporting security vulnerabilities, see [SECURITY.md](SECURITY.md).

**Supported Versions:**
- 3.x.x ✅ (Current - Full support)
- 2.x.x ✅ (Security updates)
- < 2.0 ❌ (Not supported)

### Built-in Security Features

**Authentication & Authorization:**
- ✅ SSH key authentication with validation
- ✅ Interactive password prompts (no CLI password arguments)
- ✅ Enable mode password handling
- ✅ SSH config file support with path validation
- ✅ No hardcoded credentials anywhere in codebase

**Network Security:**
- ✅ Connection timeouts (configurable, default 30s)
- ✅ Command timeouts (configurable, default 60s)
- ✅ Retry logic with exponential backoff
- ✅ Thread pool limits (1-20 workers) to prevent resource exhaustion
- ✅ No insecure fallbacks or deprecated algorithms

**Code Security:**
- ✅ Pre-commit hooks with security scanning
- ✅ Bandit security linter in CI/CD
- ✅ CodeQL static analysis (weekly)
- ✅ pip-audit dependency scanning
- ✅ Input validation on all user inputs
- ✅ No eval(), exec(), or dangerous functions

**Secrets Protection:**
- ✅ Pre-commit hook detects private keys
- ✅ Comprehensive .gitignore for credentials
- ✅ No credential logging
- ✅ Secure password handling with getpass()

**Automated Security Scans:**
- Bandit (Python security) - every push/PR + weekly
- CodeQL (semantic analysis) - weekly
- pip-audit (dependencies) - every push/PR + weekly
- Dependency Review - every PR

### Security Best Practices

**Credential Management:**

DO:
- ✅ Use SSH key authentication when possible
- ✅ Use interactive password prompts (default behavior)
- ✅ Store SSH keys with 600 permissions (`chmod 600 ~/.ssh/id_rsa`)
- ✅ Use SSH key passphrases for additional security
- ✅ Rotate credentials regularly
- ✅ Use strong, unique passwords per device
- ✅ Consider credential management systems (Vault, AWS Secrets Manager)

DON'T:
- ❌ Never commit credentials to version control
- ❌ Never use password CLI arguments (removed for security)
- ❌ Never share credentials via email or insecure channels
- ❌ Never store passwords in plain text files
- ❌ Never commit device inventory files with production IPs/credentials

**File Security:**
- Store device/command CSV files outside version control
- Use restrictive file permissions: `chmod 600` on sensitive files
- Keep SSH private keys in `~/.ssh/` directory
- Review and validate command files before execution
- Use encrypted storage for sensitive device inventories

**Network Security:**
- Use jump hosts/bastion servers for production environments
- Implement network segmentation
- Use SSH config files for complex topologies
- Limit concurrent connections (`--max-workers`) appropriately
- Enable session logging only when required for compliance

**Dependency Security:**
```bash
# Check for vulnerabilities
pip-audit

# Update dependencies safely
pip install --upgrade -r requirements.txt

# Run all security checks
pre-commit run --all-files
```

### Security Considerations

**Command Execution Risk:**
- Commands are read from text files - treat command files as trusted sources
- Implement file integrity monitoring for command files in production
- Review command files before execution
- All commands execute with timeout protection
- No automatic privilege escalation (enable mode must be explicit)

**File Path Security:**
- Validate file permissions before use
- Use absolute paths when possible
- Store sensitive files in secure locations with proper ACLs

### Enterprise/Compliance

For regulated environments (HIPAA, PCI-DSS, SOC 2):

**Audit Logging:**
- Enable session logging when required
- Store logs in centralized, secure location
- Implement log retention policies
- Monitor logs for suspicious activity

**Access Control:**
- Implement role-based access control
- Use privileged access management (PAM) solutions
- Document and follow access procedures
- Restrict credential storage access

**Data Protection:**
- Command outputs may contain sensitive configurations
- Encrypt output files at rest
- Use secure file transfer methods
- Follow data classification policies

See [SECURITY.md](SECURITY.md) for comprehensive security information.

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- `python netmiko_collector.py --help` - Built-in help

## Troubleshooting

**Connection issues:**
- Verify device IP addresses and network connectivity
- Check SSH is enabled on devices
- Review `netmiko_collector.log` for errors

**Authentication issues:**
- Verify credentials
- Check if enable password is required
- Review device AAA configuration

**Command execution issues:**
- Verify command syntax for device type
- Check user privilege level
- Increase timeout values if needed

## Performance

**Example - 10 devices, 3 commands each:**
- Sequential: ~5 minutes
- 5 workers: ~1 minute (5x faster)
- 10 workers: ~30 seconds (10x faster)

## License

MIT License - See LICENSE file

## Support

For issues or questions:
1. Check troubleshooting section
2. Review documentation
3. Open an issue on GitHub

---

**Version:** 4.0.0 | **Powered by:** Netmiko, Typer, Rich
