# Repository Overview

## Document Information
- **Last Updated**: 2025-10-27
- **Repository**: https://github.com/lammesen/netmiko-script
- **Current Branch**: main
- **License**: MIT

---

## Mission Statement

Netmiko Device Command Collector is a production-ready Python CLI tool designed to enable network engineers and administrators to efficiently execute commands across multiple Cisco network devices via SSH. The tool emphasizes security, concurrent processing, and flexible output formats to support network automation, audit, and documentation workflows.

**Core Value Proposition**: Transform manual, time-consuming device-by-device command execution into automated, parallelized batch operations with comprehensive output options.

---

## Users & Stakeholders

### Primary Users
1. **Network Engineers**: Execute show commands across device fleets for troubleshooting and documentation
2. **Network Administrators**: Collect configuration data for compliance and backup
3. **DevOps Engineers**: Automate network device auditing and monitoring
4. **Security Teams**: Gather security-related configurations and logs

### Use Cases
- **Network Audits**: Collect configuration and status from multiple devices
- **Troubleshooting**: Gather diagnostic information across affected devices
- **Documentation**: Generate network inventory and configuration reports
- **Compliance**: Audit device configurations against security policies
- **Change Validation**: Verify configuration changes across environment
- **Capacity Planning**: Collect utilization and performance metrics

---

## High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Netmiko Collector CLI                   │
│                     (netmiko_collector.py)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   Input       │    │  Processing   │    │   Output      │
│   Layer       │    │   Engine      │    │   Layer       │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
  CSV Devices          ThreadPoolExecutor     CSV/JSON/HTML
  TXT Commands         Concurrent SSH         Markdown/Excel
  SSH Config           Retry Logic            Session Logs
  User Prompts         Error Handling         Application Logs
                       Netmiko Integration
```

### Component Layers

#### 1. Input Layer
- **Device Inventory**: CSV file parser (hostname, IP, type, SSH config, keys)
- **Command List**: Text file parser (supports comments, validation)
- **Configuration**: JSON config file + CLI arguments + interactive prompts
- **Credentials**: Interactive password prompts (getpass), SSH key files

#### 2. Processing Engine
- **Connection Management**: Netmiko ConnectHandler with timeout handling
- **Concurrency**: ThreadPoolExecutor (1-20 configurable workers)
- **Retry Logic**: Exponential backoff for transient failures (3 attempts max)
- **Progress Tracking**: Rich progress bars and status indicators
- **Error Handling**: Per-device error capture without stopping batch

#### 3. Output Layer
- **Structured Data**: CSV, JSON, Excel formats
- **Human Readable**: HTML reports, Markdown documentation
- **Logging**: Application logs, per-device session logs
- **Console Output**: Rich-formatted tables and status updates

---

## Key Flows

### 1. Basic Command Collection Flow

```
User Invocation
      │
      ▼
Parse CLI Arguments
      │
      ▼
Load Configuration ──────► Load Devices CSV
      │                          │
      ▼                          ▼
Load Commands TXT          Validate Device Data
      │                          │
      ▼                          ▼
Prompt for Credentials     Establish SSH Connections
      │                     (ThreadPoolExecutor)
      │                          │
      ▼                          ▼
Execute Commands ────────► Collect Outputs
  (per device)                   │
      │                          ▼
      ▼                    Format Results
Save Outputs                     │
  (CSV/JSON/etc)                 ▼
      │                    Display Summary
      ▼
Generate Reports
      │
      ▼
    Done
```

### 2. Concurrent Processing Flow

```
Device Queue: [Device1, Device2, ..., DeviceN]
                        │
                        ▼
              ThreadPoolExecutor
              (max_workers = 5)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    Worker 1        Worker 2        Worker 3
        │               │               │
    Device 1        Device 2        Device 3
        │               │               │
    SSH Connect     SSH Connect     SSH Connect
        │               │               │
    Send Cmd 1      Send Cmd 1      Send Cmd 1
    Send Cmd 2      Send Cmd 2      Send Cmd 2
        │               │               │
    Collect         Collect         Collect
        │               │               │
        └───────────────┴───────────────┘
                        │
                        ▼
              Aggregate Results
                        │
                        ▼
               Write Outputs
```

### 3. Error Handling & Retry Flow

```
Attempt Connection
        │
        ▼
   ┌─Success?─┐
   │          │
  Yes        No
   │          │
   │          ▼
   │    Log Error
   │          │
   │    ┌─Retry Enabled?─┐
   │    │                │
   │   Yes              No
   │    │                │
   │    ▼                ▼
   │  Wait (backoff)   Mark Failed
   │    │                │
   │    ▼                │
   │  Retry              │
   │    │                │
   │    └────────────────┘
   │                     │
   ▼                     ▼
Execute Commands    Continue to
        │           Next Device
        ▼
  Return Results
```

---

## Code Map

### Current Structure (Monolithic)

```
netmiko-script/
├── netmiko_collector.py      # 2,837 lines - ENTIRE APPLICATION
│   ├── Constants & Config     # Lines 1-62
│   ├── Logging Setup          # Lines 63-150
│   ├── Command Database       # Lines 64-200
│   ├── Helper Functions       # Lines 201-500
│   ├── Device Operations      # Lines 501-1000
│   ├── File I/O               # Lines 1001-1400
│   ├── CLI Commands           # Lines 1401-2400
│   ├── Output Generators      # Lines 2401-2800
│   └── Main Entry Point       # Lines 2801-2837
│
├── test_netmiko_collector.py # 322 lines - Unit tests
├── test_autocomplete.py       # 70 lines - Autocomplete tests
├── test_yes_no_defaults.py    # 80 lines - Input validation tests
│
├── pyproject.toml             # Project configuration
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── Makefile                   # Build automation
│
├── README.md                  # User documentation
├── CONTRIBUTING.md            # Contributor guide
├── SECURITY.md                # Security policy
├── CHANGELOG.md               # Version history
├── LICENSE                    # MIT License
│
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .gitignore                 # Git exclusions
│
├── devices.csv                # Example device inventory
├── commands.txt               # Example command list
└── .github/                   # GitHub configuration
    └── workflows/             # 13 CI/CD pipelines
```

### Recommended Future Structure

```
netmiko-script/
├── src/
│   └── netmiko_collector/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py             # Typer CLI interface
│       ├── config.py          # Configuration management
│       ├── device.py          # Device models
│       ├── ssh.py             # SSH connection handling
│       ├── executor.py        # Concurrent execution
│       ├── commands.py        # Command management
│       ├── outputs.py         # Output formatters
│       └── utils.py           # Helper functions
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_device.py
│   ├── test_ssh.py
│   ├── test_executor.py
│   ├── test_commands.py
│   ├── test_outputs.py
│   └── fixtures/              # Test data
│
├── docs/
│   ├── OVERVIEW.md            # This file
│   ├── CODEMAP.md             # Detailed code structure
│   ├── DEPENDENCIES.md        # Dependency inventory
│   ├── OPERATIONS.md          # Operational guide
│   ├── UPGRADE_GUIDE.md       # Migration instructions
│   ├── CONFIG.md              # Configuration reference
│   ├── BACKLOG.md             # Feature backlog
│   ├── backlog.json           # Structured backlog
│   ├── IMPROVEMENT_PLAN.md    # Enhancement roadmap
│   ├── NEXT_STEPS.md          # Future work
│   ├── sbom.json              # Software bill of materials
│   └── rfcs/                  # Request for comments
│       └── RFC-0001-...md
│
├── examples/
│   ├── basic/                 # Simple usage examples
│   ├── advanced/              # Complex scenarios
│   └── templates/             # Reusable templates
│
├── scripts/
│   ├── setup_dev.sh           # Development setup
│   └── generate_docs.py       # Documentation generation
│
├── tools/
│   └── migration/             # Migration utilities
│
├── .devcontainer/             # VS Code devcontainer
│   └── devcontainer.json
│
├── .editorconfig              # Editor configuration
└── (existing root files)
```

---

## Dependencies

### Runtime Dependencies
- **netmiko** (≥4.3.0): SSH automation library for network devices
- **paramiko** (≥3.4.0): Low-level SSH protocol implementation
- **typer** (≥0.9.0): Modern CLI framework
- **rich** (≥13.0.0): Terminal formatting and styling
- **tqdm** (≥4.65.0): Progress bars
- **tenacity** (≥8.2.0): Retry logic with exponential backoff
- **openpyxl** (≥3.1.0): Excel file generation
- **prompt_toolkit** (≥3.0.0): Interactive prompts

### Development Dependencies
- **pytest** (≥7.0.0): Testing framework
- **pytest-cov** (≥4.0.0): Coverage reporting
- **pylint** (≥2.15.0): Code linter
- **flake8** (≥5.0.0): Style checker
- **black** (≥22.0.0): Code formatter
- **isort** (≥5.10.0): Import sorter
- **mypy** (≥0.990): Type checker
- **bandit** (≥1.7.0): Security scanner
- **pre-commit** (≥2.20.0): Git hooks framework

See [DEPENDENCIES.md](./DEPENDENCIES.md) for detailed dependency analysis.

---

## Build & Run Instructions

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git
- SSH access to target devices

### Quick Start

```bash
# Clone repository
git clone https://github.com/lammesen/netmiko-script.git
cd netmiko-script

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
make install

# Verify installation
python netmiko_collector.py --help
```

### Development Setup

```bash
# Install development dependencies
make install-dev

# Install pre-commit hooks
make pre-commit-install

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Run all checks
make ci
```

### Running the Application

```bash
# Interactive mode (recommended for first use)
python netmiko_collector.py run

# With specific files
python netmiko_collector.py run -d devices.csv -c commands.txt

# Concurrent processing
python netmiko_collector.py run -d devices.csv -c commands.txt -w 10

# Multiple output formats
python netmiko_collector.py run -d devices.csv -c commands.txt -f json html excel

# Show all commands
python netmiko_collector.py --help
```

---

## Known Issues & Limitations

### Current Known Issues

1. **Version Number Inconsistency**
   - pyproject.toml: 2.0.0
   - Code comments: 3.0.0
   - README: 4.0.0
   - **Impact**: Confusion about current version
   - **Workaround**: Standardize on single version

2. **Low Test Coverage**
   - Current: 20% (893/1117 statements uncovered)
   - **Impact**: Difficult to refactor safely
   - **Goal**: Increase to >80%

3. **Monolithic Architecture**
   - Single 2,837-line file
   - **Impact**: Hard to maintain, test, and extend
   - **Planned**: Modular refactoring

4. **Type Checking Errors**
   - 38 mypy errors (non-blocking)
   - **Impact**: Potential runtime errors
   - **Planned**: Add comprehensive type hints

### Limitations

1. **Device Support**: Primarily tested with Cisco IOS devices
2. **Concurrency**: Maximum 20 workers (configurable limit)
3. **Platform**: Best tested on Windows 11
4. **Output Size**: Very large outputs may impact memory usage
5. **SSH Only**: No Telnet or other protocol support

---

## Risk Areas

### Security Risks 🔴 HIGH PRIORITY
- **Credential Handling**: SSH passwords and keys must be protected
- **Command Injection**: Commands are read from files (treat as trusted)
- **Session Logging**: May contain sensitive configuration data
- **Output Files**: May expose network topology and credentials
- **Dependency Vulnerabilities**: Regular security updates required

**Mitigations**:
- No password CLI arguments (interactive only)
- Pre-commit secret scanning
- Bandit, CodeQL, pip-audit in CI
- Comprehensive .gitignore for sensitive files
- SSH key authentication support

### Operational Risks 🟡 MEDIUM PRIORITY
- **Network Disruption**: Concurrent connections could overwhelm devices
- **Credential Lockout**: Failed auth attempts could trigger lockouts
- **Data Loss**: Output file overwrites without backup
- **Timeout Issues**: Long-running commands may timeout

**Mitigations**:
- Configurable worker limits
- Connection timeouts
- Retry logic with exponential backoff
- Timestamped output files

### Development Risks 🟢 LOW PRIORITY
- **Breaking Changes**: Refactoring could break existing workflows
- **Dependency Updates**: New versions may introduce bugs
- **Test Coverage**: Low coverage increases regression risk

**Mitigations**:
- RFC process for breaking changes
- Semantic versioning
- Dependabot for dependency updates
- Increase test coverage

---

## Performance Characteristics

### Baseline Performance
- **Sequential Processing**: ~30 seconds per device
- **Concurrent (5 workers)**: ~6 seconds per device (5x faster)
- **Concurrent (10 workers)**: ~3 seconds per device (10x faster)

### Scalability
- **Tested**: Up to 100 devices
- **Recommended**: 1-50 devices per batch
- **Memory**: ~50MB base + ~1MB per device
- **Network**: Limited by SSH connection overhead

### Optimization Opportunities
1. Connection pooling for multiple command runs
2. Caching SSH config parsing
3. Async I/O instead of threading
4. Compiled Python (Cython/PyPy)
5. Output streaming for large datasets

---

## Change History

See [CHANGELOG.md](../CHANGELOG.md) for detailed version history.

**Recent Major Changes**:
- v2.0.0: Typer CLI framework integration
- v1.x: Thread pool concurrent processing
- v1.0: Initial release with basic functionality

---

## Next Steps

See [NEXT_STEPS.md](./NEXT_STEPS.md) for detailed future roadmap.

**Immediate Priorities**:
1. Create comprehensive backlog (Phase 1)
2. Modular architecture refactoring (Phase 2)
3. Increase test coverage to >80% (Phase 3)
4. Add devcontainer for reproducible development
5. Standardize version numbering

---

## Resources

### Internal Documentation
- [CODEMAP.md](./CODEMAP.md) - Detailed code structure
- [DEPENDENCIES.md](./DEPENDENCIES.md) - Dependency analysis
- [OPERATIONS.md](./OPERATIONS.md) - Operational procedures
- [BACKLOG.md](./BACKLOG.md) - Feature backlog
- [SECURITY.md](../SECURITY.md) - Security policy

### External Resources
- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)

---

## Contact & Support

- **Repository**: https://github.com/lammesen/netmiko-script
- **Issues**: https://github.com/lammesen/netmiko-script/issues
- **Maintainer**: @lammesen

---

*Last updated: 2025-10-27*
*Document version: 1.0*
