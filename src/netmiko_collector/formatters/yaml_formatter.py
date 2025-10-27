"""YAML formatter for command execution results."""

from typing import List

from ..models import ExecutionResult
from .base import BaseFormatter


class YAMLFormatter(BaseFormatter):
    """Format execution results as YAML."""

    def format(self, results: List[ExecutionResult]) -> str:
        """Format execution results as YAML.
        
        Args:
            results: List of ExecutionResult objects
            
        Returns:
            YAML formatted string
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML output. "
                "Install with: pip install pyyaml"
            )
        
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
        
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
