# GitHub Copilot Instructions

## Project Overview

This is a production-ready Python script that uses Netmiko to SSH into multiple Cisco IOS devices, execute commands, and collect outputs into a CSV file. The project focuses on network automation and device management.

### Key Features
- Multi-device SSH connectivity using Netmiko
- Command execution and output collection
- CSV-based device management and results export
- Comprehensive error handling and logging
- Support for SSH proxy/jump servers
- SSH key authentication support

## Code Standards

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Target pylint score of 9.5+ out of 10
- Use type hints for function signatures
- Maximum line length: 100 characters (enforced by black and configured in pyproject.toml)
- Use f-strings for string formatting
- Document all functions with docstrings

### Code Formatting
The project uses **black** and **isort** for automatic code formatting:
- Black enforces consistent code style
- isort organizes imports alphabetically and by type
- Both configured for 100 character line length
- Configuration in `pyproject.toml`

Format code with:
```bash
make format          # Format all Python files
make format-check    # Check formatting without changes
```

### Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods/attributes: prefix with single underscore `_name`

### Error Handling
- Use specific exception types when possible
- Log all exceptions appropriately
- Provide user-friendly error messages
- Handle network-specific exceptions from Netmiko (NetmikoTimeoutException, NetmikoAuthenticationException)

## Project Configuration (pyproject.toml)

The `pyproject.toml` file is the central configuration file for the project:

### Build System
- Uses setuptools for building
- Version: 2.0.0
- Package name: netmiko-collector
- Entry point: `netmiko-collector` command

### Tool Configurations
All development tools are configured in `pyproject.toml`:
- **pytest**: Test discovery, coverage settings, addopts
- **coverage**: Source paths, exclusions, report settings
- **black**: Line length, target Python versions
- **isort**: Profile (black), line length, import grouping
- **pylint**: Max line length, disabled checks, good names
- **mypy**: Type checking strictness, module overrides
- **bandit**: Security scan exclusions and skips

### Dependencies
- Production: netmiko>=4.3.0, paramiko>=3.4.0
- Development: Listed in `[project.optional-dependencies]` section

## Makefile Automation

The `Makefile` provides convenient commands for common development tasks:

### Installation & Setup
```bash
make install          # Install production dependencies
make install-dev      # Install development dependencies
make dev-setup        # Complete development setup (install-dev + pre-commit hooks)
```

### Testing
```bash
make test             # Run tests with verbose output
make test-coverage    # Run tests with coverage report (HTML + terminal)
make test-verbose     # Run tests with extra verbose output
```

### Code Quality
```bash
make lint             # Run all linters (flake8, pylint, mypy)
make lint-pylint      # Run pylint only
make lint-flake8      # Run flake8 only
make lint-mypy        # Run mypy only
make format           # Format code with black and isort
make format-check     # Check formatting without making changes
```

### Security
```bash
make security         # Run all security checks (bandit + safety)
make security-bandit  # Run bandit only
make security-safety  # Run safety dependency check only
```

### Pre-commit
```bash
make pre-commit-install  # Install pre-commit hooks
make pre-commit-run      # Run pre-commit hooks on all files
```

### Maintenance
```bash
make clean            # Clean build artifacts, cache, test files, logs
make clean-logs       # Clean log files only
make build            # Build distribution packages
```

### Combined Operations
```bash
make check            # Run lint, test, and security
make ci               # Run format-check, lint, test-coverage, and security
make all              # Run format, lint, test, and security
```

### Help
```bash
make help             # Show all available targets with descriptions
```

## File Structure

### Core Files
- **netmiko_collector.py**: Main script for device connectivity and command execution
- **test_netmiko_collector.py**: Unit tests using pytest
- **pyproject.toml**: Modern Python project configuration (build system, dependencies, tool configs)
- **Makefile**: Automation for development tasks (test, lint, format, security)
- **requirements.txt**: Production dependencies (netmiko, paramiko)
- **requirements-dev.txt**: Development dependencies (pytest, pylint, black, isort, mypy, bandit, safety)

### Configuration Files
- **.pre-commit-config.yaml**: Pre-commit hooks for automated code quality checks
- **.gitignore**: Files to exclude from version control
- **pyproject.toml**: Tool configurations for pytest, black, isort, pylint, mypy, bandit, coverage

### Documentation
- **README.md**: Comprehensive project documentation
- **CONTRIBUTING.md**: Contribution guidelines and development setup
- **LICENSE**: MIT license file

### Example Files
- **devices.csv**: Sample device inventory
- **devices_minimal.csv**: Minimal device inventory example
- **devices_with_proxy_example.csv**: Example with SSH proxy configuration
- **commands.txt**: Sample command list
- **ssh_config_example.txt**: SSH configuration file example

### CI/CD Workflows (`.github/workflows/`)
- `pylint.yml`: Code quality checks with pylint
- `python-package.yml`: Tests and linting with pytest and flake8
- `security.yml`: Security scanning with Bandit and Safety

## Dependencies

### Required Libraries (requirements.txt)
- **netmiko** (>=4.3.0): SSH connectivity to network devices
- **paramiko** (>=3.4.0): Low-level SSH implementation

### Development Dependencies (requirements-dev.txt)
- **Testing**: pytest (>=7.0.0), pytest-cov (>=4.0.0), pytest-mock (>=3.10.0)
- **Code Quality**: pylint (>=2.15.0), flake8 (>=5.0.0)
- **Code Formatting**: black (>=22.0.0), isort (>=5.10.0)
- **Type Checking**: mypy (>=0.990)
- **Security**: bandit (>=1.7.0), safety (>=2.3.0)
- **Pre-commit**: pre-commit (>=2.20.0)
- **Documentation**: sphinx (>=5.0.0), sphinx-rtd-theme (>=1.0.0)

### Installation

Quick start with make:
```bash
# Install production dependencies only
make install

# Install all development dependencies (recommended)
make install-dev

# Complete development setup (install + pre-commit hooks)
make dev-setup
```

Manual installation:
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Testing Guidelines

### Framework
- Use **pytest** for all unit tests
- Tests are located in `test_netmiko_collector.py`
- Run tests with: `pytest -v`

### Test Structure
- Organize tests in classes (e.g., `TestLoadDevices`, `TestLoadCommands`)
- Use descriptive test method names: `test_<functionality>_<scenario>`
- Use temporary files for file I/O testing
- Clean up test resources in `finally` blocks

### Coverage Expectations
- Test all public functions
- Test both success and error paths
- Test edge cases (empty files, missing fields, invalid data)
- Mock external dependencies (network connections)

### Running Tests
```bash
# Using make (recommended)
make test                    # Run tests with verbose output
make test-coverage          # Run tests with coverage report
make test-verbose           # Run tests with extra verbose output

# Using pytest directly
pytest -v                    # Run all tests
pytest test_netmiko_collector.py::TestLoadDevices -v  # Run specific test class
pytest --cov=netmiko_collector --cov-report=html       # Run with coverage
```

### Test Configuration
Tests are configured in `pyproject.toml` with:
- Coverage reporting enabled by default
- HTML coverage reports generated in `htmlcov/`
- Minimum coverage tracking for code quality

## Linting and Code Quality

### Overview
The project uses multiple tools for code quality, all configured in `pyproject.toml`:
- **pylint**: Comprehensive code analysis (target score: 9.5+)
- **flake8**: Style guide enforcement
- **black**: Automatic code formatting (line length: 100)
- **isort**: Import statement sorting
- **mypy**: Static type checking
- **bandit**: Security issue detection

### Running Linters

Using make (recommended):
```bash
make lint              # Run all linters (flake8, pylint, mypy)
make lint-pylint       # Run pylint only
make lint-flake8       # Run flake8 only
make lint-mypy         # Run mypy only
make format            # Format code with black and isort
make format-check      # Check formatting without changes
```

Using tools directly:
```bash
# Pylint (target score: 9.5+)
pylint netmiko_collector.py test_netmiko_collector.py --fail-under=9.5

# Flake8 (line length: 100)
flake8 netmiko_collector.py test_netmiko_collector.py --max-line-length=100 --extend-ignore=E203,W503

# Black (format code)
black --line-length=100 netmiko_collector.py test_netmiko_collector.py

# isort (sort imports)
isort --profile black --line-length=100 netmiko_collector.py test_netmiko_collector.py

# mypy (type checking)
mypy netmiko_collector.py --ignore-missing-imports
```

### Pylint Configuration
- Target score: 9.5+ out of 10
- Line length: 100 characters
- Configuration in `pyproject.toml`
- Known acceptable warnings:
  - R0914 (too-many-locals) in main function - acceptable for CLI scripts
  - R0912 (too-many-branches) in main function - acceptable for error handling
  - W0718 (broad-exception-caught) - acceptable for top-level error handling

### Black Configuration
- Line length: 100 characters
- Target Python versions: 3.7, 3.8, 3.9, 3.10, 3.11
- Configuration in `pyproject.toml`

### isort Configuration
- Profile: black (compatible with black formatter)
- Line length: 100 characters
- Configuration in `pyproject.toml`

## CI/CD Workflows

### Automated Checks
The project has three GitHub Actions workflows:

1. **Python Package Workflow** (`python-package.yml`)
   - Triggers: Push to main, pull requests
   - Python versions: 3.9, 3.10, 3.11
   - Steps:
     - Install dependencies
     - Lint with flake8 (syntax errors and undefined names)
     - Run pytest with full test suite

2. **Pylint Workflow** (`pylint.yml`)
   - Triggers: All pushes and pull requests
   - Python versions: 3.8, 3.9, 3.10
   - Steps:
     - Install dependencies
     - Run pylint with fail-under score of 9.5

3. **Security Workflow** (`security.yml`)
   - Triggers: Push to main, pull requests, weekly on Mondays
   - Python version: 3.11
   - Jobs:
     - **Bandit**: Scans code for security issues, uploads JSON report
     - **Safety**: Checks dependencies for vulnerabilities, uploads JSON report

### Local CI Simulation
Run all CI checks locally before pushing:
```bash
make ci              # Run format-check, lint, test-coverage, security
make check           # Run lint, test, security (no format check)
make all             # Run format, lint, test, security
```

### Before Committing
Recommended workflow:
```bash
# 1. Format code
make format

# 2. Run all checks
make ci

# 3. If pre-commit hooks are installed, they'll run on commit
git add .
git commit -m "Your message"

# 4. Push to trigger CI workflows
git push
```

## Common Development Tasks

### Quick Reference Commands
```bash
# Setup
make dev-setup              # One-time setup: install deps + pre-commit hooks

# Development cycle
make format                 # Format code before committing
make test                   # Run tests
make lint                   # Check code quality
make ci                     # Run all CI checks locally

# Specific checks
make lint-pylint            # Just pylint
make test-coverage          # Tests with coverage report
make security               # Security scans

# Cleanup
make clean                  # Remove all generated files
make clean-logs             # Remove log files only
```

### Adding New Features
1. Create a feature branch
2. Update the main script (`netmiko_collector.py`)
3. Add corresponding unit tests (`test_netmiko_collector.py`)
4. Format code: `make format`
5. Run tests: `make test`
6. Run linters: `make lint`
7. Update README.md if user-facing changes
8. Update CONTRIBUTING.md if development process changes
9. Commit and push (pre-commit hooks will run automatically)
10. Create pull request

### Modifying Device Connection Logic
- Located in `connect_and_execute()` function
- Update connection parameters in device_params dictionary
- Consider SSH config file and key authentication options
- Update error handling for new scenarios
- Add tests for new connection types
- Run security scan: `make security-bandit`

### Adding Command Processing Features
- Modify `load_commands()` for input processing
- Update command execution in main loop
- Consider timeout and error handling
- Update CSV output structure if needed
- Add unit tests for new functionality
- Run full test suite: `make test-coverage`

### Updating Dependencies
When adding or updating dependencies:
```bash
# Add to requirements.txt (production) or requirements-dev.txt (development)
pip install <package>
pip freeze | grep <package> >> requirements.txt

# Check for security vulnerabilities
make security-safety

# Update pre-commit hooks if needed
pre-commit autoupdate
```

### Code Review Checklist
Before submitting a PR, ensure:
- [ ] Code is formatted: `make format-check` passes
- [ ] All tests pass: `make test` passes
- [ ] Linters pass: `make lint` passes (pylint score ≥ 9.5)
- [ ] Security checks pass: `make security` passes
- [ ] Pre-commit hooks pass: `pre-commit run --all-files` passes
- [ ] Documentation updated if needed
- [ ] Type hints added to new functions
- [ ] No secrets or credentials in code

## Security

### Security Tools
The project includes comprehensive security scanning:
- **Bandit**: Identifies common security issues in Python code
- **Safety**: Checks dependencies for known vulnerabilities
- **Pre-commit hooks**: Prevents committing secrets and sensitive data

### Running Security Scans

Using make:
```bash
make security          # Run all security checks (bandit + safety)
make security-bandit   # Run bandit only
make security-safety   # Run safety check only
```

Using tools directly:
```bash
# Bandit security scan
bandit -r . -c pyproject.toml

# Safety dependency check
safety check --file=requirements.txt
```

### Bandit Configuration
- Configuration in `pyproject.toml`
- Excludes test files by default
- Skips B101 (assert_used) and B601 (paramiko_calls)
- Generates JSON reports in CI

### Security Workflow
- Runs on push to main, pull requests, and weekly schedule
- Generates security reports as artifacts
- Scans both code (Bandit) and dependencies (Safety)

### Security Best Practices
- **Never commit credentials** to version control
- Use `.gitignore` to exclude:
  - `*.log` (log files may contain sensitive data)
  - `output_*.csv` (may contain device configurations)
  - `session_*.log` (contains SSH session data)
  - Device and command files with real data
- Use SSH key authentication
- Use SSH config files for proxy/jump servers
- Avoid password flags in CLI (use interactive prompts)
- Review session logs before sharing

## Pre-commit Hooks

### Overview
Pre-commit hooks automatically check code quality before commits. Configuration is in `.pre-commit-config.yaml`.

### Installation
```bash
# Using make
make pre-commit-install

# Using pre-commit directly
pre-commit install
```

### What Gets Checked
Pre-commit runs these checks automatically:
- **File checks**: trailing whitespace, end-of-file fixer, large files, merge conflicts
- **Python formatting**: black (100 char line length)
- **Import sorting**: isort (black profile)
- **Linting**: flake8 (excludes test files from some checks)
- **Security**: bandit (excludes test files)
- **Type checking**: mypy (excludes test files)
- **Docstring style**: pydocstyle (excludes test files)
- **Dependency vulnerabilities**: safety check

### Running Pre-commit Hooks
```bash
# Run on all files
make pre-commit-run
# or
pre-commit run --all-files

# Hooks run automatically on git commit
git commit -m "Your commit message"

# Skip hooks (not recommended)
git commit --no-verify -m "Your commit message"
```

### Updating Hooks
```bash
# Update to latest versions
pre-commit autoupdate
```

## Logging

### Application Logging
- File: `netmiko_collector.log`
- Level: INFO
- Format: `%(asctime)s - %(levelname)s - %(message)s`
- Logs to both file and stdout

### Session Logging
- Per-device session logs: `session_<hostname>_<timestamp>.log`
- Contains raw SSH session data
- Automatically created by Netmiko
- Useful for troubleshooting connectivity issues

## Usage Patterns

### Basic Execution
```bash
python netmiko_collector.py -d devices.csv -c commands.txt
```

### With Options
```bash
# Specify username
python netmiko_collector.py -d devices.csv -c commands.txt -u admin

# Use SSH config
python netmiko_collector.py -d devices.csv -c commands.txt -s ~/.ssh/config

# Custom output file
python netmiko_collector.py -d devices.csv -c commands.txt -o results.csv
```

## Making Changes

When making changes to this repository:

1. **Understand the scope**: This is a single-script CLI tool, keep it simple
2. **Follow the development workflow**:
   - Format code: `make format`
   - Run tests: `make test`
   - Run linters: `make lint`
   - Run security checks: `make security`
   - Or run all: `make ci`
3. **Test thoroughly**: Network code can fail in many ways, test error paths
4. **Use pre-commit hooks**: They catch issues before commit
5. **Consider backward compatibility**: Users may have existing device and command files
6. **Document user-facing changes**: Update README.md with new features or changed behavior
7. **Maintain code quality**: Keep pylint score above 9.5/10
8. **Security first**: Never expose credentials, avoid insecure practices
9. **Keep it consistent**: Use black for formatting, follow existing patterns

### Development Workflow
```bash
# 1. Create a branch
git checkout -b feature/your-feature

# 2. Make your changes
# Edit files...

# 3. Format code
make format

# 4. Run checks locally
make ci

# 5. Commit (pre-commit hooks will run)
git add .
git commit -m "Description of changes"

# 6. Push and create PR
git push origin feature/your-feature
```

## Python Version Support

- **Minimum**: Python 3.7 (for type hints and modern features)
- **Tested**: Python 3.8, 3.9, 3.10, 3.11
- **Recommended**: Python 3.9+ for best compatibility with dependencies

## Additional Resources

### Project Documentation
- [README.md](../README.md) - Comprehensive project documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Detailed contribution guidelines
- [pyproject.toml](../pyproject.toml) - Tool configurations and project metadata

### External Documentation
- [Netmiko Documentation](https://github.com/ktbyers/netmiko) - SSH library for network devices
- [Paramiko Documentation](https://www.paramiko.org/) - Low-level SSH implementation
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/) - Python coding standards
- [Black Documentation](https://black.readthedocs.io/) - Code formatter
- [isort Documentation](https://pycqa.github.io/isort/) - Import sorter
- [mypy Documentation](https://mypy.readthedocs.io/) - Static type checker
- [Bandit Documentation](https://bandit.readthedocs.io/) - Security scanner
- [Pre-commit Documentation](https://pre-commit.com/) - Git hook framework

### Development Tools
- **pytest**: Unit testing framework with coverage support
- **pylint**: Comprehensive Python linter
- **flake8**: PEP 8 style checker
- **black**: Opinionated code formatter (no configuration needed)
- **isort**: Import statement organizer
- **mypy**: Static type checker for Python
- **bandit**: Security linter for Python code
- **safety**: Checks Python dependencies for known security vulnerabilities
- **pre-commit**: Manages and runs pre-commit hooks

### CI/CD
- GitHub Actions workflows in `.github/workflows/`
- All checks run automatically on push and PR
- Security scans run weekly
