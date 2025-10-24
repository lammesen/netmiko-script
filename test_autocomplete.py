#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the enhanced autocomplete styling with modern appearance."""

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import prompt_toolkit components
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

# Clean and simple autocomplete styling
CUSTOM_STYLE = Style.from_dict({
    # Autocomplete dropdown - minimal and clean
    'completion-menu.completion': '#888888',  # Gray text for unselected items
    'completion-menu.completion.current': '#00aaff bold',  # Bright cyan for selected (no background)

    # Scrollbar - subtle appearance
    'scrollbar.background': 'bg:#2a2a2a',
    'scrollbar.button': 'bg:#00aaff',

    # Prompt styling
    'prompt': 'cyan bold',
    'input': '#ffffff',  # White input text
})

# Sample commands for autocomplete
commands = [
    "show version",
    "show running-config",
    "show ip interface brief",
    "show ip route",
    "show interfaces",
    "show vlan brief",
    "show cdp neighbors",
    "show mac address-table",
    "show arp",
    "show inventory",
    "configure terminal",
    "interface gigabitethernet",
    "interface vlan",
    "router ospf",
    "router bgp",
    "access-list",
    "ip route",
    "hostname",
]

print("=" * 70)
print("🎨 ENHANCED AUTOCOMPLETE STYLING TEST")
print("=" * 70)
print()
print("✨ Features to test:")
print("  ▶ Clean, minimal dropdown design")
print("  ▶ Bright cyan highlight for selected item (no background)")
print("  ▶ Gray text for unselected suggestions")
print("  ▶ Subtle scrollbar appearance")
print("  ▶ Simple and easy to read")
print()
print("📝 Instructions:")
print("  1. Start typing: 'show' or 'config'")
print("  2. Press Tab or start typing to see autocomplete")
print("  3. Use ↑/↓ arrows to navigate suggestions")
print("  4. Notice the clean, minimal styling")
print("  5. Press Ctrl+C to exit")
print()

# Create clean completer - simple and minimal
completer = FuzzyCompleter(
    WordCompleter(
        commands,
        ignore_case=True,
        sentence=True
    )
)

try:
    while True:
        result = prompt(
            HTML('<cyan><b>Router</b></cyan> <b>&gt;</b> '),
            completer=completer,
            complete_while_typing=True,
            style=CUSTOM_STYLE,
            complete_in_thread=True,
            mouse_support=True,
            refresh_interval=0.5
        )

        if result.strip():
            print(f"✅ You entered: {result}")
        print()

except KeyboardInterrupt:
    print("\n\n✅ Test completed!")
    print("Did you notice the enhanced styling? 🎨")
