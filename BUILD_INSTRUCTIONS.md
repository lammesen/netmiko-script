# Building netmiko-collector Installer

This document explains how to build a standalone Windows installer for netmiko-collector.

## Overview

The build process creates:
1. **Standalone executable** (`netmiko-collector.exe`) - No Python required
2. **Windows installer** (`.exe`) - Installs the application and adds it to PATH

## Prerequisites

### Required
- Python 3.11+ installed
- PyInstaller (installed automatically by build script)

### Optional (for installer creation)
- [Inno Setup 6](https://jrsoftware.org/isdl.php) - Creates professional Windows installer

## Quick Start

### Option 1: Build Executable Only

```batch
build_installer.bat
```

This creates a standalone executable at `dist\netmiko-collector.exe` that can be run without Python.

### Option 2: Build Complete Installer (Recommended)

```batch
build_complete.bat
```

This creates both:
- Standalone executable: `dist\netmiko-collector.exe`
- Windows installer: `installer_output\netmiko-collector-2.0.0-setup.exe`

## Manual Build Steps

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Build Executable

```bash
python -m PyInstaller netmiko-collector.spec --clean
```

The executable will be created in the `dist` folder.

### Step 3: Test Executable

```bash
cd dist
netmiko-collector.exe --version
netmiko-collector.exe --help
```

### Step 4: Create Installer (Optional)

If you have Inno Setup installed:

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

The installer will be created in the `installer_output` folder.

## What the Installer Does

The Windows installer (`netmiko-collector-2.0.0-setup.exe`):

✅ **Installation**
- Installs netmiko-collector.exe to `C:\Program Files\Netmiko Collector\`
- Creates Start Menu shortcuts
- Optionally creates Desktop shortcut

✅ **PATH Integration**
- Automatically adds installation directory to system PATH
- Allows running `netmiko-collector` from any command prompt
- Can be disabled during installation

✅ **Uninstallation**
- Clean uninstall via Windows Control Panel
- Removes PATH entry automatically
- Removes all installed files

## Distribution

### For End Users

Distribute the installer: `installer_output\netmiko-collector-2.0.0-setup.exe`

**Installation steps for users:**
1. Run the installer
2. Accept the license agreement
3. Choose installation directory (default: `C:\Program Files\Netmiko Collector`)
4. Select "Add to PATH" option (recommended)
5. Complete installation
6. Open command prompt and type: `netmiko-collector --help`

### For Portable Use

Distribute just the executable: `dist\netmiko-collector.exe`

Users can:
- Run it directly without installation
- Copy it to any folder
- Manually add to their PATH if desired

## File Structure

```
netmiko-script/
├── netmiko-collector.spec      # PyInstaller configuration
├── installer.iss                # Inno Setup script
├── build_installer.bat          # Build executable only
├── build_complete.bat           # Build everything
├── BUILD_INSTRUCTIONS.md        # This file
│
├── dist/                        # Build output
│   └── netmiko-collector.exe    # Standalone executable
│
└── installer_output/            # Installer output
    └── netmiko-collector-2.0.0-setup.exe
```

## Troubleshooting

### PyInstaller Issues

**Error: Module not found**
- Check `hiddenimports` in `netmiko-collector.spec`
- Add missing modules to the list

**Executable too large**
- Edit `.spec` file and add unwanted modules to `excludes`
- Current size: ~50-100 MB (includes all dependencies)

**Runtime errors**
- Test in a clean environment without Python
- Check for missing data files in `.spec` `datas` section

### Inno Setup Issues

**Compiler not found**
- Download from: https://jrsoftware.org/isdl.php
- Install to default location
- Update path in `build_complete.bat` if needed

**PATH modification doesn't work**
- Run installer as Administrator
- Check the "Add to PATH" option during installation

### Testing

**Test the standalone executable:**
```batch
cd dist
netmiko-collector.exe --version
netmiko-collector.exe --help
```

**Test the installer:**
1. Run the installer
2. Open a NEW command prompt
3. Type: `netmiko-collector --version`
4. Test uninstall via Control Panel

## Build Configuration

### PyInstaller Options (netmiko-collector.spec)

- **One-file mode**: Creates single .exe (slower startup)
- **Console application**: Shows terminal window
- **UPX compression**: Reduces file size
- **Hidden imports**: Ensures all dependencies are included

### Inno Setup Options (installer.iss)

- **Admin privileges**: Required for PATH modification
- **LZMA compression**: Best compression ratio
- **Modern wizard style**: Clean, professional UI
- **Uninstaller**: Automatic cleanup

## CI/CD Integration

To automate builds in GitHub Actions:

```yaml
- name: Build with PyInstaller
  run: python -m PyInstaller netmiko-collector.spec --clean

- name: Upload artifact
  uses: actions/upload-artifact@v3
  with:
    name: netmiko-collector-windows
    path: dist/netmiko-collector.exe
```

## Version Updates

When releasing a new version:

1. Update version in `pyproject.toml`
2. Update version in `installer.iss` (#define MyAppVersion)
3. Run build script
4. Test installer
5. Upload to GitHub Releases

## Support

For issues or questions:
- GitHub Issues: https://github.com/lammesen/netmiko-script/issues
- Documentation: See README.md

## License

MIT License - See LICENSE file
