"""JSON formatter for command execution results."""

import json
from typing import List

from ..models import ExecutionResult
from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """Format execution results as JSON."""

    def __init__(self, indent: int = 2):
        """Initialize JSON formatter.
        
        Args:
            indent: Number of spaces for indentation (default: 2)
        """
        self.indent = indent

    def format(self, results: List[ExecutionResult]) -> str:
        """Format execution results as JSON.
        
        Args:
            results: List of ExecutionResult objects
            
        Returns:
            JSON formatted string
        """
        data = []
        for result in results:
            data.append({
                "hostname": result.hostname,
                "command": result.command.text,
                "status": result.status.value,
                "output": result.output,
                "error": result.error,
                "duration_ms": int(result.duration * 1000) if result.duration is not None else None,
                "timestamp": result.timestamp.isoformat() if result.timestamp else None
            })
        
        return json.dumps(data, indent=self.indent, ensure_ascii=False)
