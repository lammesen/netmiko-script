# Code Map

## Document Information
- **Last Updated**: 2025-10-27
- **Code Version**: 2.0.0 (pyproject.toml)
- **Main File**: netmiko_collector.py (2,837 lines)
- **Test Files**: 3 files (test_netmiko_collector.py, test_autocomplete.py, test_yes_no_defaults.py)

---

## Repository Tree Structure

```
netmiko-script/
├── .github/                           # GitHub configuration
│   ├── copilot-instructions.md        # GitHub Copilot instructions
│   ├── dependabot.yml                 # Dependency update automation
│   ├── labeler.yml                    # PR auto-labeling rules
│   └── workflows/                     # CI/CD pipelines (13 workflows)
│       ├── bandit.yml                 # Security scanning (Bandit)
│       ├── claude.yml                 # Claude AI integration
│       ├── codeql.yml                 # Security analysis (CodeQL)
│       ├── dependency-review.yml      # Dependency vulnerability check
│       ├── docs.yml                   # Documentation build
│       ├── formatting.yml             # Code formatting check
│       ├── label.yml                  # Issue/PR labeling
│       ├── pre-commit.yml             # Pre-commit hook validation
│       ├── pylint.yml                 # Code quality (pylint)
│       ├── python-package.yml         # Main test pipeline
│       ├── release.yml                # Release automation
│       ├── security.yml               # Security audit (pip-audit)
│       └── type-check.yml             # Type checking (mypy)
│
├── docs/                              # Documentation directory
│   ├── OVERVIEW.md                    # Project overview (this audit)
│   ├── CODEMAP.md                     # Code structure (this file)
│   └── rfcs/                          # Request for comments
│
├── examples/                          # Example usage (empty, to be added)
├── infra/                             # Infrastructure configs (empty)
├── scripts/                           # Utility scripts (empty)
├── tools/                             # Development tools (empty)
│
├── Core Application Files
├── netmiko_collector.py               # Main application (2,837 lines)
├── test_netmiko_collector.py          # Core unit tests (322 lines)
├── test_autocomplete.py               # Autocomplete tests (70 lines)
├── test_yes_no_defaults.py            # Input validation tests (80 lines)
│
├── Configuration & Build
├── pyproject.toml                     # Python project configuration
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── Makefile                           # Build automation (24 targets)
├── .pre-commit-config.yaml            # Pre-commit hook config
├── .gitignore                         # Git ignore patterns
├── .editorconfig                      # (Missing - to be added)
│
├── Documentation
├── README.md                          # Main user documentation (362 lines)
├── CONTRIBUTING.md                    # Contribution guidelines (244 lines)
├── SECURITY.md                        # Security policy (239 lines)
├── CHANGELOG.md                       # Version history (111 lines)
├── LICENSE                            # MIT License
├── ASSUMPTIONS.md                     # Project assumptions (NEW)
├── WORKLOG.md                         # Development log (NEW)
│
├── Example Files
├── devices.csv                        # Sample device inventory
├── devices_minimal.csv                # Minimal device example
├── devices_with_proxy_example.csv     # Proxy/jump server example
├── commands.txt                       # Sample command list
└── ssh_config_example.txt             # SSH configuration example
```

---

## Main Application Structure: netmiko_collector.py

### Overview
The main application is a **monolithic single-file** implementation (2,837 lines) using the Typer CLI framework. While functional, this structure presents maintenance and testing challenges.

### File Organization (Line Numbers)

#### 1. Imports & Setup (Lines 1-62)
```python
- Standard library imports (csv, logging, sys, etc.)
- Third-party imports (typer, netmiko, rich, etc.)
- Windows UTF-8 console setup
- Constants definition
  - TRUTHY_VALUES
  - Worker limits (MIN_WORKERS, MAX_WORKERS)
  - Retry configuration (MAX_RETRY_ATTEMPTS, etc.)
  - DEFAULT_CONFIG dictionary
  - CONFIG_FILE path
```

**Dependencies Used**:
- csv, io, json, logging, sys, pathlib (stdlib)
- datetime, getpass, typing (stdlib)
- concurrent.futures (ThreadPoolExecutor)
- typer, typing_extensions (CLI framework)

#### 2. Device Command Database (Lines 63-200)
```python
DEVICE_COMMANDS: Dict[str, Dict[str, List[str]]]
  ├── cisco_ios
  │   ├── show: List[str]           # 50+ show commands
  │   ├── config: List[str]         # Configuration commands
  │   └── troubleshooting: List[str] # Diagnostic commands
  ├── cisco_nxos
  │   └── (similar structure)
  ├── cisco_asa
  │   └── (similar structure)
  └── (other device types)
```

**Purpose**: Pre-defined command sets for auto-completion and quick command generation.

#### 3. Logging Configuration (Lines 201-300)
```python
- File handler setup (netmiko_collector.log)
- Console handler with Rich formatting (optional)
- Log level configuration (INFO by default)
- Format: "%(asctime)s - %(levelname)s - %(message)s"
```

#### 4. Rich Console Setup (Lines 301-350)
```python
- Console object initialization
- Conditional Rich import (graceful degradation)
- Global console instance for formatted output
```

#### 5. Utility Functions (Lines 351-600)

| Function | Lines | Purpose |
|----------|-------|---------|
| `print_banner()` | 374-381 | Print styled banner text |
| `print_success()` | 384-389 | Print success message (green) |
| `print_error()` | 392-397 | Print error message (red) |
| `print_warning()` | 400-405 | Print warning message (yellow) |
| `print_info()` | 408-413 | Print info message (blue) |
| `get_positive_int_input()` | 416-443 | Validate positive integer input |
| `expand_path()` | 446-479 | Expand user paths (~, env vars) |
| `select_from_menu()` | 480-600 | Interactive menu selection |

**Key Design Pattern**: Rich UI wrapper functions for consistent formatting.

#### 6. File Operations (Lines 601-857)

| Function | Lines | Purpose |
|----------|-------|---------|
| `open_file_in_editor()` | 603-649 | Open file in system editor |
| `get_commands_for_device_type()` | 652-694 | Retrieve command templates |
| `edit_commands_with_autocomplete()` | 697-855 | Interactive command editor |

**Features**:
- Cross-platform editor detection (EDITOR env var, notepad, vi)
- Command autocomplete with device-type awareness
- Template-based command generation

#### 7. Output Management (Lines 858-1025)

| Function | Lines | Purpose |
|----------|-------|---------|
| `list_output_files()` | 858-876 | Find output files by pattern |
| `view_output_file()` | 879-955 | Display output with pagination |
| `get_or_create_file()` | 958-1023 | File selection/creation wizard |

**Features**:
- Pattern-based file discovery
- Platform-specific file opening (Windows: os.startfile)
- Interactive file selection menu

#### 8. File Management UI (Lines 1026-1173)

| Function | Lines | Purpose |
|----------|-------|---------|
| `show_file_manager_menu()` | 1026-1173 | File operations menu |

**Operations**:
- Create new files
- Edit existing files
- View files
- Delete files
- List files

#### 9. Configuration Management (Lines 1174-1338)

| Function | Lines | Purpose |
|----------|-------|---------|
| `load_config()` | 1176-1193 | Load JSON config file |
| `save_config()` | 1195-1207 | Save config to JSON |
| `show_settings_menu()` | 1210-1338 | Interactive config editor |

**Configuration Storage**:
- Location: `~/.netmiko_collector_config.json`
- Format: JSON
- Fallback: DEFAULT_CONFIG dictionary

**Configurable Settings**:
- default_device_type
- strip_whitespace
- max_workers (1-20)
- connection_timeout
- command_timeout
- enable_session_logging
- enable_mode
- retry_on_failure

#### 10. Device Loading (Lines 1339-1435)

| Function | Lines | Purpose |
|----------|-------|---------|
| `load_devices()` | 1341-1433 | Parse device CSV file |

**CSV Schema** (flexible):
- **Required**: hostname, ip_address
- **Optional**: device_type, ssh_config_file, use_keys, key_file, port, enable_password

**Features**:
- Flexible column mapping
- Path expansion (~, environment variables)
- Validation and error reporting
- Default value injection

#### 11. Command Loading (Lines 1436-1466)

| Function | Lines | Purpose |
|----------|-------|---------|
| `load_commands()` | 1436-1464 | Parse command text file |

**Features**:
- One command per line
- Comment support (lines starting with #)
- Whitespace handling
- Empty line filtering

#### 12. SSH Connection & Execution (Lines 1467-1746)

| Function | Lines | Purpose |
|----------|-------|---------|
| `connect_and_execute()` | 1467-1650 | Main SSH connection handler |
| `connect_with_retry()` | 1653-1744 | Retry wrapper with backoff |

**Connection Flow**:
1. Build device parameters dictionary
2. Apply SSH config file if specified
3. Establish SSH connection (Netmiko)
4. Enter enable mode if required
5. Execute commands sequentially
6. Collect outputs
7. Disconnect gracefully
8. Return results dictionary

**Error Handling**:
- NetmikoTimeoutException
- NetmikoAuthenticationException
- Generic exceptions
- Per-command error tracking
- Connection cleanup in finally block

**Session Logging**:
- Optional per-device session logs
- Filename: `session_{hostname}_{timestamp}.log`
- Contains raw SSH session data

#### 13. Parallel Processing Engine (Lines 1747-1934)

| Function | Lines | Purpose |
|----------|-------|---------|
| `process_devices_parallel()` | 1747-1932 | Concurrent device processing |

**Architecture**:
```
ThreadPoolExecutor
    ├── max_workers: configurable (1-20)
    ├── submit(): connect_with_retry per device
    ├── as_completed(): Process results as they finish
    └── Progress tracking: Rich progress bar or tqdm
```

**Features**:
- Configurable worker pool size
- Progress bar with device count
- Per-device error handling
- Result aggregation
- Non-blocking execution

**Performance**:
- Sequential: ~30s per device
- 5 workers: ~6s per device (5x faster)
- 10 workers: ~3s per device (10x faster)

#### 14. Output Formatters (Lines 1935-2398)

| Function | Lines | Format | Features |
|----------|-------|--------|----------|
| `save_to_csv()` | 1935-1955 | CSV | Standard spreadsheet format |
| `save_to_json()` | 1957-2000 | JSON | Metadata + structured data |
| `save_to_markdown()` | 2002-2062 | Markdown | GitHub-compatible |
| `save_to_html()` | 2065-2279 | HTML | Bootstrap-styled report |
| `save_to_excel()` | 2282-2396 | Excel | Multi-sheet workbook |
| `save_results()` | 2399-2447 | Dispatcher | Calls format-specific savers |

**JSON Structure**:
```json
{
  "metadata": {
    "timestamp": "ISO-8601",
    "device_count": int,
    "command_count": int,
    "format_version": "1.0"
  },
  "results": [
    {
      "hostname": str,
      "ip_address": str,
      "device_type": str,
      "timestamp": str,
      "command": str,
      "output": str,
      "success": bool,
      "error": str | null
    }
  ]
}
```

**HTML Features**:
- Bootstrap 5 styling
- Collapsible output sections
- Device filtering
- Command search
- Responsive design
- Copy-to-clipboard

**Excel Structure**:
- **Summary Sheet**: Device/command counts, status overview
- **Results Sheet**: Full data table
- **Statistics Sheet**: Success rates, timing info
- Auto-formatted headers, frozen panes

#### 15. CLI Commands (Lines 2448-2834)

##### Main Run Command (Lines 2450-2605)
```python
@app.command()
def run_collection(
    devices_file: str,
    commands_file: str,
    username: Optional[str] = None,
    ssh_config_file: Optional[str] = None,
    global_ssh_config: Optional[str] = None,
    global_use_keys: bool = False,
    global_key_file: Optional[str] = None,
    enable_mode: bool = False,
    enable_password: Optional[str] = None,
    max_workers: int = 5,
    output_formats: List[str] = ["csv"],
    output_file: str = None,
) -> None:
```

**Flow**:
1. Load configuration
2. Auto-detect/prompt for device/command files
3. Load devices and commands
4. Prompt for credentials (interactive)
5. Process devices in parallel
6. Save results in requested formats
7. Display summary

##### Edit Command (Lines 2607-2665)
```python
@app.command()
def edit_files(
    file_type: str = typer.Argument(..., help="'devices' or 'commands'")
) -> None:
```

**Purpose**: Edit device/command files with autocomplete support.

##### View Command (Lines 2667-2704)
```python
@app.command()
def view_outputs() -> None:
```

**Purpose**: Interactively view generated output files.

##### Config Commands (Lines 2706-2786)

| Command | Lines | Purpose |
|---------|-------|---------|
| `config_show()` | 2706-2717 | Display current configuration |
| `config_set()` | 2719-2770 | Interactive configuration editor |
| `config_reset()` | 2772-2784 | Reset to default configuration |

##### Sample Commands (Lines 2788-2834)

| Command | Lines | Purpose |
|---------|-------|---------|
| `sample_devices()` | 2788-2810 | Generate sample devices.csv |
| `sample_commands()` | 2812-2832 | Generate sample commands.txt |

**Purpose**: Quick start templates for new users.

#### 16. Application Entry Point (Lines 2835-2837)
```python
if __name__ == "__main__":
    app()
```

**Framework**: Typer CLI app instance.

---

## Test Files Structure

### test_netmiko_collector.py (322 lines)

**Test Classes & Coverage**:

| Class | Methods | Coverage | Purpose |
|-------|---------|----------|---------|
| `TestLoadDevices` | 5 | Core CSV parsing |
| `TestLoadCommands` | 5 | Command file parsing |
| `TestExpandPath` | 3 | Path expansion logic |
| `TestConfigFunctions` | 3 | Config save/load |

**Total Tests**: 16 passing

**Key Tests**:
- CSV parsing with various formats
- Missing required columns
- Path expansion (~, env vars)
- Command file parsing
- Comment handling
- Configuration persistence

**Mocking Strategy**:
- File I/O operations mocked with tempfile
- No actual SSH connections (unit tests only)
- Configuration file mocking

**Coverage**: 20% overall (most UI and SSH code not covered)

### test_autocomplete.py (70 lines)

**Purpose**: Test command autocomplete functionality

**Test Cases**:
- Device type command retrieval
- Template-based command generation
- Autocomplete data structure validation

### test_yes_no_defaults.py (80 lines)

**Purpose**: Test user input validation and defaults

**Test Cases**:
- Boolean input parsing (yes/no/true/false)
- Default value handling
- Invalid input rejection

---

## Module Responsibilities (Current Monolith)

| Concern | Lines | Responsibility | Issues |
|---------|-------|----------------|--------|
| **Configuration** | ~200 | Config load/save, defaults | Mixed with UI |
| **Device Management** | ~150 | CSV parsing, validation | Tightly coupled |
| **Command Management** | ~100 | Command loading, templates | Limited reusability |
| **SSH Operations** | ~300 | Connection, execution, retry | Hard to test |
| **Concurrency** | ~200 | ThreadPool management | Mixed with logic |
| **Output Formatting** | ~600 | 5 format generators | Good separation |
| **CLI Interface** | ~400 | Typer commands, menus | Mixed concerns |
| **Utilities** | ~200 | Path, printing, validation | Reusable |
| **Logging** | ~100 | Setup, formatting | Good practice |

**Total Lines**: 2,837 (including comments, docstrings, whitespace)

---

## Dependency Graph

```
CLI Layer (Typer)
    │
    ├─► Configuration Manager
    │       └─► JSON File I/O
    │
    ├─► Device Loader
    │       ├─► CSV Parser
    │       └─► Path Expander
    │
    ├─► Command Loader
    │       └─► Text Parser
    │
    ├─► SSH Executor
    │       ├─► Netmiko (ConnectHandler)
    │       ├─► Retry Logic (Tenacity)
    │       └─► Session Logger
    │
    ├─► Parallel Processor
    │       ├─► ThreadPoolExecutor
    │       ├─► Progress Bar (Rich/tqdm)
    │       └─► Result Aggregator
    │
    └─► Output Formatters
            ├─► CSV Writer
            ├─► JSON Writer
            ├─► Markdown Generator
            ├─► HTML Generator
            └─► Excel Writer (openpyxl)
```

---

## Code Quality Metrics

### Current Status

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Total Lines** | 2,837 | <2,000 | 🔴 Too large |
| **Functions** | 39 | - | ✅ Good granularity |
| **Classes** | 0 | 5-10 | 🔴 Needs OOP |
| **Cyclomatic Complexity** | High | <10/fn | 🟡 Some high |
| **Test Coverage** | 20% | >80% | 🔴 Too low |
| **Pylint Score** | 9.22/10 | >9.0 | ✅ Good |
| **Type Hints** | Partial | Full | 🟡 38 mypy errors |
| **Documentation** | Good | - | ✅ Well documented |

### Complexity Hotspots

**High Complexity Functions** (>20 cyclomatic complexity):
1. `connect_and_execute()` - 280 lines, complex error handling
2. `process_devices_parallel()` - 180 lines, concurrency logic
3. `show_settings_menu()` - 130 lines, nested UI logic
4. `save_to_html()` - 200 lines, template generation
5. `run_collection()` - 150 lines, orchestration logic

**Recommendation**: These functions are prime candidates for refactoring into smaller, testable units.

---

## Recommended Refactoring Structure

### Proposed Module Breakdown

```python
src/netmiko_collector/
    ├── __init__.py
    ├── __main__.py              # Entry point
    │
    ├── cli.py                   # Typer CLI commands (300 lines)
    │   ├── run_command()
    │   ├── edit_command()
    │   ├── view_command()
    │   ├── config_command()
    │   └── sample_command()
    │
    ├── config.py                # Configuration (150 lines)
    │   ├── class Config
    │   ├── load_config()
    │   ├── save_config()
    │   └── DEFAULT_CONFIG
    │
    ├── devices.py               # Device management (200 lines)
    │   ├── class Device
    │   ├── load_devices()
    │   ├── validate_device()
    │   └── DeviceInventory
    │
    ├── commands.py              # Command management (150 lines)
    │   ├── class Command
    │   ├── load_commands()
    │   ├── DEVICE_COMMANDS
    │   └── CommandList
    │
    ├── ssh.py                   # SSH operations (300 lines)
    │   ├── class SSHConnection
    │   ├── connect()
    │   ├── execute_command()
    │   ├── disconnect()
    │   └── SSHResult
    │
    ├── executor.py              # Parallel execution (250 lines)
    │   ├── class ParallelExecutor
    │   ├── process_devices()
    │   ├── handle_device()
    │   └── aggregate_results()
    │
    ├── formatters/              # Output formatting (600 lines)
    │   ├── __init__.py
    │   ├── base.py             # Abstract Formatter
    │   ├── csv_formatter.py
    │   ├── json_formatter.py
    │   ├── markdown_formatter.py
    │   ├── html_formatter.py
    │   └── excel_formatter.py
    │
    ├── ui.py                    # UI utilities (200 lines)
    │   ├── print_banner()
    │   ├── print_success/error/warning/info()
    │   ├── select_from_menu()
    │   └── get_positive_int_input()
    │
    └── utils.py                 # General utilities (150 lines)
        ├── expand_path()
        ├── open_file_in_editor()
        └── file operations
```

**Benefits**:
- Single Responsibility Principle
- Easier testing (unit test per module)
- Better code reusability
- Clearer dependencies
- Improved maintainability
- Easier onboarding for contributors

---

## Testing Structure

### Current Tests
```
tests/ (currently in root)
    ├── test_netmiko_collector.py    # 16 tests, 20% coverage
    ├── test_autocomplete.py          # Autocomplete tests
    └── test_yes_no_defaults.py       # Input validation
```

### Recommended Test Structure
```
tests/
    ├── __init__.py
    ├── conftest.py                   # Shared fixtures
    │
    ├── unit/                         # Fast, isolated tests
    │   ├── test_config.py
    │   ├── test_devices.py
    │   ├── test_commands.py
    │   ├── test_ssh.py
    │   ├── test_executor.py
    │   ├── test_formatters.py
    │   ├── test_ui.py
    │   └── test_utils.py
    │
    ├── integration/                  # Component integration
    │   ├── test_device_loading.py
    │   ├── test_command_execution.py
    │   └── test_output_generation.py
    │
    ├── e2e/                          # End-to-end tests
    │   └── test_full_workflow.py
    │
    └── fixtures/                     # Test data
        ├── devices/
        │   ├── valid.csv
        │   ├── invalid.csv
        │   └── minimal.csv
        ├── commands/
        │   ├── basic.txt
        │   └── advanced.txt
        └── outputs/
            └── expected_results.json
```

---

## CI/CD Pipeline Architecture

### Current Workflows (13 total)

```
GitHub Actions Workflows:
    ├── python-package.yml         # Main test pipeline (matrix: 3.9, 3.10, 3.11)
    ├── pylint.yml                 # Code quality check (target: 9.5/10)
    ├── type-check.yml             # mypy type checking
    ├── formatting.yml             # black + isort formatting
    ├── pre-commit.yml             # Pre-commit hooks validation
    │
    ├── bandit.yml                 # Security scanning (Python)
    ├── codeql.yml                 # Semantic analysis (weekly)
    ├── security.yml               # pip-audit dependency scan
    ├── dependency-review.yml      # PR dependency check
    │
    ├── docs.yml                   # Documentation build
    ├── release.yml                # Automated releases
    ├── label.yml                  # Auto-labeling
    └── claude.yml                 # AI integration
```

**Triggers**:
- Push to main: Most workflows
- Pull requests: All quality checks
- Weekly schedule: CodeQL, security scans
- Manual: Release workflow

---

## Known Technical Debt

### High Priority 🔴

1. **Monolithic Structure**: 2,837-line single file
   - **Impact**: Hard to maintain, test, and extend
   - **Effort**: High (RFC required)
   - **Risk**: Breaking changes

2. **Low Test Coverage**: 20%
   - **Impact**: Unsafe refactoring, hidden bugs
   - **Effort**: Medium (incremental improvement)
   - **Risk**: Low (additive only)

3. **Type Checking Issues**: 38 mypy errors
   - **Impact**: Potential runtime errors
   - **Effort**: Medium (add type hints)
   - **Risk**: Low (fixes, not changes)

### Medium Priority 🟡

4. **Version Number Inconsistency**: 2.0.0 vs 3.0.0 vs 4.0.0
   - **Impact**: Confusion
   - **Effort**: Low (update files)
   - **Risk**: Low

5. **No Devcontainer**: Development environment not reproducible
   - **Impact**: Setup friction
   - **Effort**: Low (create devcontainer.json)
   - **Risk**: None

6. **Missing .editorconfig**: Code style not enforced in editors
   - **Impact**: Inconsistent formatting
   - **Effort**: Low (create file)
   - **Risk**: None

### Low Priority 🟢

7. **No Examples Directory**: Missing usage examples
   - **Impact**: Harder onboarding
   - **Effort**: Low (create examples)
   - **Risk**: None

8. **No Tools Directory**: Missing development utilities
   - **Impact**: Manual processes
   - **Effort**: Low (create tools)
   - **Risk**: None

---

## Next Steps for Refactoring

### Phase 1: Preparation (Non-Breaking)
1. Increase test coverage to >50% before refactoring
2. Add comprehensive type hints
3. Create refactoring RFC with stakeholder input
4. Add integration tests for critical paths
5. Document all public APIs

### Phase 2: Module Extraction (Gradual)
1. Extract utilities (expand_path, file operations)
2. Extract formatters (already well-separated)
3. Extract configuration management
4. Extract device/command loading
5. Extract SSH operations
6. Extract executor logic

### Phase 3: Integration (Careful)
1. Create new module structure
2. Copy tests alongside modules
3. Update imports progressively
4. Maintain backward compatibility
5. Deprecate old interfaces

### Phase 4: Cleanup (Final)
1. Remove deprecated code
2. Update documentation
3. Publish major version
4. Update examples

---

## Complexity Analysis

### Cyclomatic Complexity (Top 10 Functions)

| Function | Lines | Complexity | Status |
|----------|-------|------------|--------|
| `connect_and_execute()` | 280 | ~25 | 🔴 Refactor |
| `process_devices_parallel()` | 180 | ~20 | 🔴 Refactor |
| `show_settings_menu()` | 130 | ~18 | 🟡 Simplify |
| `save_to_html()` | 200 | ~15 | 🟡 Template |
| `run_collection()` | 150 | ~15 | 🟡 Orchestrate |
| `load_devices()` | 95 | ~12 | ✅ Acceptable |
| `save_to_excel()` | 110 | ~12 | ✅ Acceptable |
| `edit_commands_with_autocomplete()` | 155 | ~11 | ✅ Acceptable |
| `connect_with_retry()` | 90 | ~10 | ✅ Acceptable |
| `save_to_json()` | 45 | ~8 | ✅ Good |

**Recommendation**: Functions with complexity >15 should be refactored into smaller functions or classes.

---

## Documentation Coverage

| Area | Current | Needed | Priority |
|------|---------|--------|----------|
| **User Docs** | ✅ Good | Refresh | Low |
| **Architecture** | ❌ None | OVERVIEW.md | ✅ Done |
| **Code Map** | ❌ None | CODEMAP.md | ✅ Done |
| **API Docs** | 🟡 Partial | Sphinx docs | Medium |
| **Operations** | ❌ None | OPERATIONS.md | High |
| **Examples** | 🟡 Basic | More examples | Medium |
| **Upgrade Guide** | ❌ None | UPGRADE_GUIDE.md | Low |
| **RFCs** | ❌ None | RFC process | High |

---

*Last updated: 2025-10-27*
*Document version: 1.0*
