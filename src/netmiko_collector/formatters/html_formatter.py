"""HTML formatter for command execution results."""

from datetime import datetime
from typing import List

from ..models import ExecutionResult, ExecutionStatus
from .base import BaseFormatter


class HTMLFormatter(BaseFormatter):
    """Format execution results as HTML table."""

    def format(self, results: List[ExecutionResult]) -> str:
        """Format execution results as HTML.
        
        Args:
            results: List of ExecutionResult objects
            
        Returns:
            HTML formatted string
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <title>Network Command Execution Results</title>",
            "  <style>",
            "    body { font-family: Arial, sans-serif; margin: 20px; }",
            "    table { border-collapse: collapse; width: 100%; }",
            "    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "    th { background-color: #4CAF50; color: white; }",
            "    tr:nth-child(even) { background-color: #f2f2f2; }",
            "    .success { color: green; }",
            "    .failed { color: red; }",
            "    .pending { color: orange; }",
            "    pre { white-space: pre-wrap; word-wrap: break-word; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>Network Command Execution Results</h1>",
            f"  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            f"  <p>Total Results: {len(results)}</p>",
            "  <table>",
            "    <tr>",
            "      <th>Hostname</th>",
            "      <th>Command</th>",
            "      <th>Status</th>",
            "      <th>Output</th>",
            "      <th>Error</th>",
            "      <th>Duration (ms)</th>",
            "    </tr>",
        ]
        
        for result in results:
            status_class = {
                ExecutionStatus.SUCCESS: "success",
                ExecutionStatus.FAILED: "failed",
                ExecutionStatus.PENDING: "pending"
            }.get(result.status, "")
            
            duration = int(result.duration * 1000) if result.duration is not None else "N/A"
            
            html_parts.extend([
                "    <tr>",
                f"      <td>{self._escape_html(result.hostname)}</td>",
                f"      <td><code>{self._escape_html(result.command.text)}</code></td>",
                f"      <td class='{status_class}'>{result.status.value}</td>",
                f"      <td><pre>{self._escape_html(result.output or '')}</pre></td>",
                f"      <td><pre>{self._escape_html(result.error or '')}</pre></td>",
                f"      <td>{duration}</td>",
                "    </tr>",
            ])
        
        html_parts.extend([
            "  </table>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))
