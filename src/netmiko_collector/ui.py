"""Rich UI components for beautiful terminal output."""

from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

from .models import ExecutionResult, ExecutionStatus


console = Console()


def create_progress_bar(total: int, description: str = "Processing devices") -> Progress:
    """
    Create a Rich progress bar for tracking device execution.

    Args:
        total: Total number of devices to process
        description: Description to display

    Returns:
        Progress: Configured Rich Progress object
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def create_results_table(results: List[ExecutionResult]) -> Table:
    """
    Create a Rich table displaying execution results.

    Args:
        results: List of execution results

    Returns:
        Table: Formatted Rich Table
    """
    table = Table(title="Execution Results", show_header=True, header_style="bold magenta")
    table.add_column("Device", style="cyan", no_wrap=True)
    table.add_column("Status", style="white")
    table.add_column("Duration", justify="right", style="green")
    table.add_column("Commands", justify="right", style="blue")

    for result in results:
        status_style = {
            ExecutionStatus.SUCCESS: "[green]✓ Success[/green]",
            ExecutionStatus.FAILED: "[red]✗ Failed[/red]",
            ExecutionStatus.TIMEOUT: "[yellow]⏱ Timeout[/yellow]",
            ExecutionStatus.AUTH_FAILED: "[red]🔒 Auth Failed[/red]",
        }.get(result.status, "[white]Unknown[/white]")

        duration = f"{result.duration:.2f}s" if result.duration else "N/A"
        commands_count = str(len(result.outputs)) if result.outputs else "0"

        table.add_row(result.hostname, status_style, duration, commands_count)

    return table


def create_panel(content: str, title: str, style: str = "blue") -> Panel:
    """
    Create a styled Rich panel.

    Args:
        content: Content to display in panel
        title: Panel title
        style: Panel border style color

    Returns:
        Panel: Configured Rich Panel
    """
    return Panel(content, title=title, border_style=style)


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[bold red]ERROR:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[bold green]SUCCESS:[/bold green] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[bold yellow]WARNING:[/bold yellow] {message}")


def create_device_summary(results: List[ExecutionResult]) -> str:
    """
    Create a summary of device execution results.

    Args:
        results: List of execution results

    Returns:
        str: Formatted summary text
    """
    total = len(results)
    success = sum(1 for r in results if r.status == ExecutionStatus.SUCCESS)
    failed = sum(1 for r in results if r.status == ExecutionStatus.FAILED)
    timeout = sum(1 for r in results if r.status == ExecutionStatus.TIMEOUT)
    auth_failed = sum(1 for r in results if r.status == ExecutionStatus.AUTH_FAILED)

    summary_lines = [
        f"Total Devices: {total}",
        f"[green]✓ Success: {success}[/green]",
        f"[red]✗ Failed: {failed}[/red]",
        f"[yellow]⏱ Timeout: {timeout}[/yellow]",
        f"[red]🔒 Auth Failed: {auth_failed}[/red]",
    ]

    return "\n".join(summary_lines)
