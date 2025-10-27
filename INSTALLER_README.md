# Netmiko Collector - Windows Installer

## For Users: Installing the Application

### System Requirements
- Windows 7/8/10/11 (64-bit)
- No Python installation required
- Administrator privileges (for PATH modification)

### Installation Steps

1. **Download the installer**
   - Get `netmiko-collector-2.0.0-setup.exe`

2. **Run the installer**
   - Double-click the installer
   - Click "Yes" if User Account Control prompts

3. **Follow the wizard**
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\Netmiko Collector`)
   - ✅ **Check "Add to PATH"** (recommended - allows running from anywhere)
   - Choose additional options (desktop shortcut, etc.)
   - Click "Install"

4. **Verify installation**
   - Open Command Prompt (cmd) or PowerShell
   - Type: `netmiko-collector --version`
   - You should see: `netmiko-collector version 2.0.0`

### Quick Start

After installation, you can use netmiko-collector from any command prompt:

```batch
# View help
netmiko-collector --help

# Run with your device and command files
netmiko-collector -d devices.csv -c commands.txt

# Specify output format
netmiko-collector -d devices.csv -c commands.txt -f json
```

### Uninstallation

**Method 1: Windows Settings**
1. Open Windows Settings
2. Go to "Apps" or "Apps & features"
3. Find "Netmiko Collector"
4. Click "Uninstall"

**Method 2: Start Menu**
1. Open Start Menu
2. Find "Netmiko Collector" folder
3. Click "Uninstall Netmiko Collector"

The uninstaller will:
- Remove all installed files
- Remove PATH entry
- Remove Start Menu shortcuts
- Remove Desktop shortcut (if created)

### Troubleshooting

#### "Command not found" error

If you get `'netmiko-collector' is not recognized...`:

1. **Restart your command prompt** after installation
2. Verify PATH was added:
   ```batch
   echo %PATH%
   ```
   Should contain `C:\Program Files\Netmiko Collector`

3. **Manual PATH fix** (if needed):
   - Open System Properties → Environment Variables
   - Add `C:\Program Files\Netmiko Collector` to PATH
   - Restart command prompt

#### Antivirus warnings

Some antivirus software may flag the executable:
- This is a false positive (common with PyInstaller executables)
- The application is safe and contains no malware
- You can verify the source code at: https://github.com/lammesen/netmiko-script

#### Permission errors

If you get permission errors during installation:
- Run the installer as Administrator
- Right-click installer → "Run as administrator"

### Portable Usage (Without Installation)

Don't want to install? You can use the standalone executable:

1. Extract `netmiko-collector.exe` from the installer (or get it separately)
2. Place it in any folder
3. Run it directly or add that folder to your PATH manually

## For Developers: Building the Installer

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build instructions.

### Quick Build

```batch
# Build everything (executable + installer)
build_complete.bat

# Or just the executable
build_installer.bat
```

## Support

- **Documentation**: [README.md](README.md)
- **Issues**: https://github.com/lammesen/netmiko-script/issues
- **Source Code**: https://github.com/lammesen/netmiko-script

## License

MIT License - See [LICENSE](LICENSE) file
