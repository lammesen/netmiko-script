"""Base formatter interface for output generation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from ..models import ExecutionResult


class BaseFormatter(ABC):
    """Abstract base class for all output formatters.
    
    All formatters must implement the format() method which takes
    a list of ExecutionResult objects and returns formatted output.
    """

    @abstractmethod
    def format(self, results: List[ExecutionResult]) -> str:
        """Format execution results into output string.
        
        Args:
            results: List of ExecutionResult objects to format
            
        Returns:
            Formatted output as string
        """
        pass

    def write_to_file(self, results: List[ExecutionResult], filepath: Path) -> None:
        """Write formatted results to a file.
        
        Args:
            results: List of ExecutionResult objects to format
            filepath: Path to output file
        """
        output = self.format(results)
        filepath.write_text(output, encoding="utf-8")
