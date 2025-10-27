#!/usr/bin/env python
"""
Entry point for netmiko-collector standalone executable.
This wrapper ensures proper imports when running as a PyInstaller bundle.
"""

import sys
import os

# Add the source directory to Python path for proper imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    bundle_dir = sys._MEIPASS
else:
    # Running as normal Python script
    bundle_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(bundle_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

# Import and run the CLI
from netmiko_collector.cli import app

if __name__ == '__main__':
    app()
