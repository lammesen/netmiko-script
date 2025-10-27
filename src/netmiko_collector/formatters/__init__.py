"""Output formatters for command execution results.

This package provides formatters for various output formats including
CSV, JSON, YAML, HTML, and XLSX.
"""

from .base import BaseFormatter
from .csv_formatter import CSVFormatter
from .json_formatter import JSONFormatter
from .yaml_formatter import YAMLFormatter
from .html_formatter import HTMLFormatter
from .xlsx_formatter import XLSXFormatter


def get_formatter(format_name: str) -> BaseFormatter:
    """
    Get a formatter instance by format name.
    
    Args:
        format_name: Name of the format (csv, json, yaml, html, xlsx)
        
    Returns:
        Formatter instance
        
    Raises:
        ValueError: If format name is not recognized
    """
    formatters = {
        "csv": CSVFormatter,
        "json": JSONFormatter,
        "yaml": YAMLFormatter,
        "html": HTMLFormatter,
        "xlsx": XLSXFormatter,
    }
    
    format_lower = format_name.lower()
    if format_lower not in formatters:
        valid_formats = ", ".join(formatters.keys())
        raise ValueError(
            f"Unknown format: {format_name}. Valid formats: {valid_formats}"
        )
    
    return formatters[format_lower]()


__all__ = [
    "BaseFormatter",
    "CSVFormatter",
    "JSONFormatter",
    "YAMLFormatter",
    "HTMLFormatter",
    "XLSXFormatter",
    "get_formatter",
]
