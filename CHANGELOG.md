# Changelog

All notable changes to the Netmiko Device Command Collector will be documented in this file.

## [4.0.0] - 2025-10-24 - Modern Typer CLI Framework & UX Enhancements

### Added
- Complete migration from argparse to Typer CLI framework
- Organized command structure with subcommands (`run`, `edit`, `view`, `config`, `sample`)
- Rich integration for beautiful help pages with tables and colors
- Smart file auto-detection in current directory
- Smart yes/no prompt defaults (press Enter to accept)
- Simplified autocomplete styling - clean gray/cyan minimal design
- `config` subcommand group for settings management (show/set/reset)
- `sample` subcommand group for creating template files
- `edit` command with auto-detection and create/browse options
- `view` command for browsing output files

### Improved
- Command-line argument handling with type safety via Annotated types
- Help system with comprehensive `--help` at every command level
- User experience with fewer keystrokes and smarter defaults
- Autocomplete dropdown - removed metadata, removed backgrounds
- Code quality: Modern CLI patterns with Typer best practices

### Removed
- Old monolithic interactive menu - replaced with subcommand structure
- Password CLI argument (security improvement - use prompts only)

## [3.0.0] - 2025-10-24 - UI/UX Overhaul & Production Enhancements

### Added
- Beautiful CLI with Rich library - colored output, tables, and panels
- Integrated File Manager - edit devices.csv, commands.txt, and view outputs
- Smart file viewer - HTML in browser, Excel in app, JSON/Markdown with syntax highlighting
- Sample file creation with templates
- Multiple output formats - HTML, JSON, Markdown, Excel, CSV
- Beautiful HTML reports with Bootstrap 5.3 styling and interactive elements
- Excel output with colored cells and formatted sheets
- JSON structured output grouped by device
- Markdown reports for documentation
- Real-time progress bars with Rich (fallback to tqdm)
- Automatic retry logic with exponential backoff using tenacity
- Enable mode support - automatically enter privileged EXEC mode
- Optional session logging (disabled by default for security)
- Automatic path expansion for SSH config and key files (~/ support)
- SSH key file validation before connection attempts

### Improved
- Enhanced settings menu with 8 configurable options
- Better input validation with helper functions
- Refined whitespace stripping logic
- Security - password CLI argument removed (use prompt instead)
- All magic numbers extracted to constants
- Configuration now includes retry, enable mode, and session logging settings
- Tests fixed - removed importlib.reload anti-pattern
- CLI arguments validation (workers range check)
- Summary output with beautiful tables (when Rich available)
- Better error messages and user feedback
- Removed redundant code and wrapper functions

## [2.0.0] - 2025-10-20 - Quality of Life Improvements

### Added
- Concurrent/parallel device processing with ThreadPoolExecutor
- Automatic whitespace stripping from command outputs (configurable)
- Default device_type configuration (global setting)
- Interactive terminal menu with settings management
- Persistent configuration file (~/.netmiko_collector_config.json)
- Command-line options for workers, timeouts, and device type
- Made device_type optional in CSV when default is configured

### Improved
- User experience with better prompts and feedback
- Performance: 5x faster execution on 10+ devices with default settings

## [1.1.0] - 2025-10-20 - Proxy/Jump Server Support & Code Quality

### Added
- Support for SSH config files (global and per-device)
- SSH key authentication support
- Proxy/jump server connectivity

### Fixed
- Pylint warnings (logging format, exception handling)

### Improved
- Code quality from 8.49/10 to 9.81/10
- Added .gitignore for better repository management

## [1.0.0] - 2025-10-20 - Initial Release

### Added
- Basic SSH connectivity
- Command execution on network devices
- CSV output format
- Comprehensive error handling
- Application logging
