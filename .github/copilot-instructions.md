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
- Maximum line length: 100 characters (as per project convention)
- Use f-strings for string formatting
- Document all functions with docstrings

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

## File Structure

- **netmiko_collector.py**: Main script for device connectivity and command execution
- **test_netmiko_collector.py**: Unit tests using pytest
- **requirements.txt**: Python dependencies (netmiko, paramiko)
- **devices.csv**: Device inventory (not in repo - user-provided)
- **commands.txt**: Command list (not in repo - user-provided)
- **.github/workflows/**: CI/CD workflows
  - `pylint.yml`: Code quality checks
  - `python-package.yml`: Tests and linting

## Dependencies

### Required Libraries
- **netmiko** (>=4.3.0): SSH connectivity to network devices
- **paramiko** (>=3.4.0): Low-level SSH implementation

### Development Dependencies
- **pytest**: Testing framework
- **pylint**: Code quality checker
- **flake8**: Additional linting (used in CI)

Install all dependencies:
```bash
pip install -r requirements.txt
pip install pytest pylint flake8
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
# Run all tests
pytest -v

# Run specific test class
pytest test_netmiko_collector.py::TestLoadDevices -v

# Run with coverage
pytest --cov=netmiko_collector --cov-report=html
```

## Linting and Code Quality

### Pylint
- Target score: 9.5+ out of 10
- Configuration: Default pylint settings
- Known acceptable warnings:
  - R0914 (too-many-locals) in main function - acceptable for CLI scripts
  - R0912 (too-many-branches) in main function - acceptable for error handling
  - W0718 (broad-exception-caught) - acceptable for top-level error handling

Run pylint:
```bash
pylint netmiko_collector.py test_netmiko_collector.py
```

### Flake8
- Maximum complexity: 10
- Maximum line length: 127 (CI setting)
- Stop build on: E9, F63, F7, F82 errors

Run flake8:
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## CI/CD Workflows

### Automated Checks
- **Python Package Workflow** (on push to main, PRs):
  - Tests on Python 3.9, 3.10, 3.11
  - Flake8 linting
  - Pytest execution
  
- **Pylint Workflow** (on all pushes):
  - Code quality checks on Python 3.8, 3.9, 3.10
  - Requires pylint score to pass

### Before Committing
1. Run tests: `pytest -v`
2. Run pylint: `pylint netmiko_collector.py test_netmiko_collector.py`
3. Run flake8: `flake8 .`
4. Ensure all checks pass

## Common Development Tasks

### Adding New Features
1. Update the main script (`netmiko_collector.py`)
2. Add corresponding unit tests (`test_netmiko_collector.py`)
3. Update README.md if user-facing changes
4. Run tests and linting
5. Ensure documentation is current

### Modifying Device Connection Logic
- Located in `connect_and_execute()` function
- Update connection parameters in device_params dictionary
- Consider SSH config file and key authentication options
- Update error handling for new scenarios
- Add tests for new connection types

### Adding Command Processing Features
- Modify `load_commands()` for input processing
- Update command execution in main loop
- Consider timeout and error handling
- Update CSV output structure if needed

## Security Considerations

### Sensitive Data
- **Never commit credentials** to version control
- Use `.gitignore` to exclude:
  - `*.log` (log files may contain sensitive data)
  - `output_*.csv` (may contain device configurations)
  - `session_*.log` (contains SSH session data)
  - Device and command files with real data

### SSH Security
- Support SSH key authentication
- Use SSH config files for proxy/jump servers
- Avoid password flags in CLI (use interactive prompts)
- Session logs should be reviewed before sharing

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
2. **Test thoroughly**: Network code can fail in many ways, test error paths
3. **Consider backward compatibility**: Users may have existing device and command files
4. **Document user-facing changes**: Update README.md with new features or changed behavior
5. **Maintain code quality**: Keep pylint score above 9.5/10
6. **Security first**: Never expose credentials, avoid insecure practices

## Python Version Support

- **Minimum**: Python 3.7 (for type hints and modern features)
- **Tested**: Python 3.8, 3.9, 3.10, 3.11
- **Recommended**: Python 3.9+ for best compatibility with dependencies

## Additional Resources

- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [Paramiko Documentation](https://www.paramiko.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
