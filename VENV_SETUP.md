# Virtual Environment Setup Guide

This guide explains how to use the Python virtual environment for the Netmiko Device Command Collector.

## What's Been Set Up

A Python 3.14.0 virtual environment has been created with all required and optional dependencies installed:

### Installed Packages
- ✅ **typer** (0.20.0) - Modern CLI framework
- ✅ **click** (8.3.0) - CLI toolkit (required by typer)
- ✅ **netmiko** (4.6.0) - Network device automation
- ✅ **paramiko** (4.0.0) - SSH protocol implementation
- ✅ **rich** (14.2.0) - Beautiful terminal formatting
- ✅ **tqdm** (4.67.1) - Progress bars
- ✅ **tenacity** (9.1.2) - Retry logic
- ✅ **openpyxl** - Excel output support
- ✅ **prompt_toolkit** - Interactive autocomplete
- Plus all their dependencies

## How to Activate the Environment

### Windows Command Prompt
```cmd
activate_venv.bat
```

Or manually:
```cmd
venv\Scripts\activate.bat
```

### PowerShell
```powershell
.\activate_venv.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
```

**Note:** If you get a PowerShell execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Git Bash / Linux / macOS
```bash
source venv/Scripts/activate
```

## Using the Script

Once activated, you'll see `(venv)` in your prompt. The script uses a modern Typer CLI with subcommands:

### View All Commands
```bash
python netmiko_collector.py --help
```

### Quick Start - Run Collection
```bash
# Interactive mode with auto-detection
python netmiko_collector.py run

# With specific files
python netmiko_collector.py run -d devices.csv -c commands.txt
```

### Create Sample Files
```bash
python netmiko_collector.py sample devices
python netmiko_collector.py sample commands
```

### Edit Files
```bash
python netmiko_collector.py edit devices
python netmiko_collector.py edit commands
```

### View Output Files
```bash
python netmiko_collector.py view
```

### Manage Configuration
```bash
python netmiko_collector.py config show
python netmiko_collector.py config set
python netmiko_collector.py config reset
```

### Run Tests
```bash
pip install -r requirements-dev.txt
pytest test_netmiko_collector.py -v
```

## Deactivating the Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Troubleshooting

### "Python not found" error
Make sure you're in the project directory:
```cmd
cd C:\Users\t979259\Desktop\Claude\netmiko-script
```

### Dependencies not working
Reinstall dependencies:
```bash
venv\Scripts\python.exe -m pip install -r requirements.txt --upgrade
```

### Virtual environment corrupted
Delete and recreate:
```bash
rmdir /s /q venv
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Environment Info

- **Python Version:** 3.14.0
- **Location:** `C:\Users\t979259\Desktop\Claude\netmiko-script\venv`
- **Platform:** Windows (win32)

## Quick Reference

| Command | Description |
|---------|-------------|
| `activate_venv.bat` | Activate environment (CMD) |
| `.\activate_venv.ps1` | Activate environment (PowerShell) |
| `deactivate` | Deactivate environment |
| `python netmiko_collector.py --help` | Show all available commands |
| `python netmiko_collector.py run` | Run collection (interactive) |
| `python netmiko_collector.py edit devices` | Edit devices file |
| `python netmiko_collector.py config show` | Show configuration |
| `python -m pip list` | List installed packages |
| `python -m pip freeze` | Export requirements |

## Next Steps

1. ✅ Virtual environment created
2. ✅ Dependencies installed
3. ✅ Script verified
4. 📝 Create your `devices.csv` file (see README.md)
5. 📝 Create your `commands.txt` file
6. 🚀 Run the script!

For full documentation, see [README.md](README.md)
