"""CSV formatter for command execution results."""

import csv
from io import StringIO
from typing import List

from ..models import ExecutionResult
from .base import BaseFormatter


class CSVFormatter(BaseFormatter):
    """Format execution results as CSV.
    
    Outputs results with columns: hostname, command, status, output, error, duration
    """

    def format(self, results: List[ExecutionResult]) -> str:
        """Format execution results as CSV.
        
        Args:
            results: List of ExecutionResult objects
            
        Returns:
            CSV formatted string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "hostname",
            "command",
            "status",
            "output",
            "error",
            "duration_ms"
        ])
        
        # Write data rows
        for result in results:
            writer.writerow([
                result.hostname,
                result.command.text,
                result.status.value,
                result.output or "",
                result.error or "",
                int(result.duration * 1000) if result.duration is not None else ""
            ])
        
        return output.getvalue()
