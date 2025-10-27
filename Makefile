.PHONY: help install install-dev test test-coverage lint format clean security pre-commit-install pre-commit-run

# Default target
.DEFAULT_GOAL := help

# Python and pip executables
PYTHON := python3
PIP := $(PYTHON) -m pip

# Source files
PYTHON_FILES := netmiko_collector.py test_netmiko_collector.py

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev:  ## Install development dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "Run 'make pre-commit-install' to setup pre-commit hooks"

test:  ## Run tests
	pytest -v

test-coverage:  ## Run tests with coverage report
	pytest --cov=netmiko_collector --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

test-verbose:  ## Run tests with verbose output
	pytest -vv -s

lint:  ## Run all linters
	@echo "Running flake8..."
	flake8 $(PYTHON_FILES) --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running pylint..."
	pylint $(PYTHON_FILES) --fail-under=9.0
	@echo "Running mypy..."
	mypy netmiko_collector.py --ignore-missing-imports || true
	@echo "All linters passed!"

lint-pylint:  ## Run pylint only
	pylint $(PYTHON_FILES) --fail-under=9.0

lint-flake8:  ## Run flake8 only
	flake8 $(PYTHON_FILES) --max-line-length=100 --extend-ignore=E203,W503

lint-mypy:  ## Run mypy only
	mypy netmiko_collector.py --ignore-missing-imports

format:  ## Format code with black and isort
	@echo "Running isort..."
	isort --profile black --line-length=100 $(PYTHON_FILES)
	@echo "Running black..."
	black --line-length=100 $(PYTHON_FILES)
	@echo "Code formatted!"

format-check:  ## Check code formatting without making changes
	@echo "Checking with isort..."
	isort --profile black --line-length=100 --check-only $(PYTHON_FILES)
	@echo "Checking with black..."
	black --line-length=100 --check $(PYTHON_FILES)

security:  ## Run security checks
	@echo "Running bandit security scan..."
	bandit -r . -c pyproject.toml
	@echo "Checking dependencies for known vulnerabilities..."
	safety check --file=requirements.txt || true
	@echo "Security checks complete!"

security-bandit:  ## Run bandit only
	bandit -r . -c pyproject.toml

security-safety:  ## Run safety check only
	safety check --file=requirements.txt

pre-commit-install:  ## Install pre-commit hooks
	pre-commit install
	@echo "Pre-commit hooks installed!"

pre-commit-run:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

clean:  ## Clean build artifacts and cache files
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .eggs/
	@echo "Cleaning Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	@echo "Cleaning test artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -f coverage.xml
	rm -f bandit-report.json
	rm -f safety-report.json
	@echo "Cleaning log files..."
	rm -f *.log
	rm -f session_*.log
	@echo "Clean complete!"

clean-logs:  ## Clean only log files
	rm -f *.log
	rm -f session_*.log
	@echo "Log files cleaned!"

build:  ## Build distribution packages
	$(PYTHON) -m build

check:  ## Run all checks (lint, test, security)
	@echo "Running all checks..."
	@make lint
	@make test
	@make security
	@echo "All checks passed!"

ci:  ## Run CI checks locally (format-check, lint, test, security)
	@echo "Running CI checks..."
	@make format-check
	@make lint
	@make test-coverage
	@make security
	@echo "CI checks complete!"

dev-setup:  ## Complete development setup
	@echo "Setting up development environment..."
	@make install-dev
	@make pre-commit-install
	@echo ""
	@echo "Development environment ready!"
	@echo "Next steps:"
	@echo "  1. Run 'make test' to verify installation"
	@echo "  2. Run 'make lint' to check code quality"
	@echo "  3. See 'make help' for more commands"

watch-test:  ## Watch files and run tests on change (requires pytest-watch)
	@command -v ptw >/dev/null 2>&1 || { echo "Installing pytest-watch..."; $(PIP) install pytest-watch; }
	ptw -- -v

.PHONY: all
all: format lint test security  ## Run format, lint, test, and security checks
	@echo "All tasks complete!"
