# Contributing to Netmiko Collector

Thank you for considering contributing to Netmiko Collector! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and professional in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- pip (Python package installer)

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/lammesen/netmiko-script.git
cd netmiko-script
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Making Changes

### Branch Naming Convention

Use descriptive branch names:
- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation changes
- `refactor/description` - for code refactoring

### Coding Standards

We follow strict coding standards to maintain code quality:

#### Python Style (PEP 8)
- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_SNAKE_CASE for constants

#### Type Hints
- Add type hints to all function signatures
- Use `typing` module for complex types
```python
from typing import List, Dict, Optional

def example_function(param: str, optional_param: Optional[int] = None) -> List[str]:
    """Function with type hints."""
    pass
```

#### Documentation
- All functions must have docstrings following Google/NumPy style
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description of the function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

#### Error Handling
- Use specific exception types
- Always log exceptions appropriately
- Provide user-friendly error messages

## Testing

### Running Tests

Run all tests:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=netmiko_collector --cov-report=html --cov-report=term-missing
```

Run specific test class:
```bash
pytest test_netmiko_collector.py::TestLoadDevices -v
```

### Writing Tests

- Place tests in `test_netmiko_collector.py`
- Organize tests in classes by functionality
- Use descriptive test names: `test_<function>_<scenario>`
- Mock external dependencies (network connections, file I/O)
- Clean up resources in `finally` blocks or use pytest fixtures
- Test both success and failure paths
- Test edge cases

Example test:
```python
def test_load_devices_valid(self):
    """Test loading valid devices CSV."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("hostname,ip_address,device_type\n")
        f.write("router1,192.168.1.1,cisco_ios\n")
        temp_file = f.name

    try:
        devices = load_devices(temp_file)
        assert len(devices) == 1
        assert devices[0]["hostname"] == "router1"
    finally:
        os.unlink(temp_file)
```

## Code Quality

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit. To run manually:
```bash
pre-commit run --all-files
```

### Linting

#### Pylint
Target score: 9.5+ out of 10
```bash
pylint netmiko_collector.py test_netmiko_collector.py
```

#### Flake8
```bash
flake8 . --max-line-length=100 --exclude=venv,build,dist
```

#### Black (Code Formatter)
```bash
black --line-length=100 .
```

#### isort (Import Sorter)
```bash
isort --profile black --line-length=100 .
```

### Type Checking

Run mypy for static type checking:
```bash
mypy netmiko_collector.py --ignore-missing-imports
```

### Security Scanning

Run bandit for security checks:
```bash
bandit -r . -c pyproject.toml
```

Check dependencies for vulnerabilities:
```bash
safety check --file=requirements.txt
```

### Using the Makefile

Common tasks are available via make:
```bash
make help          # Show available commands
make install       # Install dependencies
make test          # Run tests
make lint          # Run all linters
make format        # Format code
make security      # Run security checks
make clean         # Clean build artifacts
```

## Submitting Changes

### Pull Request Process

1. Ensure all tests pass
2. Ensure code meets quality standards (pylint >= 9.5)
3. Update documentation if needed
4. Add or update tests for your changes
5. Commit your changes with clear, descriptive messages
6. Push to your fork
7. Submit a pull request

### Commit Message Format

Use clear, descriptive commit messages:

```
type: Short description (50 chars or less)

Longer explanation if necessary. Wrap at 72 characters.
Explain what and why, not how.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
- Reference issues and pull requests
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: Add support for multiple SSH config files

fix: Resolve connection timeout handling issue

docs: Update README with new configuration options

test: Add tests for parallel device processing
```

### Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows PEP 8 and project style guidelines
- [ ] All tests pass (`pytest -v`)
- [ ] Pylint score is >= 9.5
- [ ] Code is formatted with Black
- [ ] Imports are sorted with isort
- [ ] Type hints are added to new functions
- [ ] Docstrings are added to new functions
- [ ] Tests are added for new functionality
- [ ] Documentation is updated if needed
- [ ] Pre-commit hooks pass
- [ ] No security vulnerabilities introduced
- [ ] Commit messages are clear and descriptive

## Reporting Bugs

### Before Submitting a Bug Report

- Check if the bug has already been reported
- Ensure you're using the latest version
- Verify the issue is reproducible

### Submitting a Bug Report

Include:
1. **Description**: Clear and concise description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - Netmiko version
   - Network device types
6. **Logs**: Relevant log files (sanitize sensitive data!)
7. **Additional Context**: Screenshots, configuration files, etc.

## Suggesting Enhancements

### Before Submitting an Enhancement

- Check if the enhancement has already been suggested
- Ensure it aligns with project goals
- Consider if it would be useful to most users

### Submitting an Enhancement Suggestion

Include:
1. **Use Case**: Describe the problem or use case
2. **Proposed Solution**: Describe your proposed solution
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Examples, mockups, etc.

## Development Workflow

### Typical Workflow

1. Create a new branch from `main`
```bash
git checkout -b feature/my-new-feature
```

2. Make your changes
3. Run tests and linters
```bash
make test
make lint
```

4. Commit your changes
```bash
git add .
git commit -m "feat: Add new feature"
```

5. Push to your fork
```bash
git push origin feature/my-new-feature
```

6. Create a pull request on GitHub

### Keeping Your Fork Updated

```bash
# Add upstream remote
git remote add upstream https://github.com/lammesen/netmiko-script.git

# Fetch and merge updates
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## Questions?

If you have questions:
- Check the [README.md](README.md) for basic information
- Review existing issues and pull requests
- Open a new issue with your question

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Netmiko Collector!
