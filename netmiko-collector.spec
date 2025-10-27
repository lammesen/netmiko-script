# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for netmiko-collector
Builds a standalone executable with all dependencies bundled.
"""

import sys
from pathlib import Path

block_cipher = None

# Get the source directory
src_path = str(Path('.') / 'src')

a = Analysis(
    ['run_netmiko_collector.py'],
    pathex=[src_path, '.'],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'netmiko',
        'paramiko',
        'typer',
        'rich',
        'click',
        'openpyxl',
        'tenacity',
        'tqdm',
        'prompt_toolkit',
        'netmiko_collector',
        'netmiko_collector.cli',
        'netmiko_collector.commands',
        'netmiko_collector.config',
        'netmiko_collector.devices',
        'netmiko_collector.executor',
        'netmiko_collector.models',
        'netmiko_collector.ssh',
        'netmiko_collector.ui',
        'netmiko_collector.utils',
        'netmiko_collector.formatters',
        'netmiko_collector.formatters.base',
        'netmiko_collector.formatters.csv_formatter',
        'netmiko_collector.formatters.html_formatter',
        'netmiko_collector.formatters.json_formatter',
        'netmiko_collector.formatters.xlsx_formatter',
        'netmiko_collector.formatters.yaml_formatter',
        # Netmiko drivers
        'netmiko.cisco',
        'netmiko.cisco.cisco_ios',
        'netmiko.cisco.cisco_xe',
        'netmiko.cisco.cisco_xr',
        'netmiko.cisco.cisco_nxos',
        'netmiko.cisco.cisco_asa',
        'netmiko.arista',
        'netmiko.juniper',
        'netmiko.hp',
        # TextFSM templates
        'ntc_templates',
        'textfsm',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pytest',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='netmiko-collector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)
