"""
Command-line interface for netmiko-collector.

This module provides the main CLI entry point using Typer for command-line
argument parsing and Rich for beautiful console output.
"""

from pathlib import Path
from typing import Optional
import sys

try:
    import typer
    from rich.console import Console
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("Please install with: pip install typer rich")
    sys.exit(1)

from . import __version__
from .config import Config
from .devices import load_devices_from_csv
from .commands import load_commands_from_file
from .executor import execute_on_devices
from .formatters import get_formatter
from .ui import (
    create_progress_bar,
    create_device_summary,
    print_error,
    print_success,
    print_warning,
)

app = typer.Typer(
    name="netmiko-collector",
    help="Network device automation tool for batch command execution via SSH",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        typer.echo(f"netmiko-collector version {__version__}")
        raise typer.Exit()


@app.command()
def main(
    devices_file: Path = typer.Option(
        ...,
        "--devices",
        "-d",
        help="CSV file containing device information",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    commands_file: Path = typer.Option(
        ...,
        "--commands",
        "-c",
        help="Text file containing commands to execute",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output_file: Path = typer.Option(
        "output.csv",
        "--output",
        "-o",
        help="Output file path",
    ),
    output_format: str = typer.Option(
        "csv",
        "--format",
        "-f",
        help="Output format (csv, json, yaml, html, xlsx)",
    ),
    username: Optional[str] = typer.Option(
        None,
        "--username",
        "-u",
        help="Username for device authentication (overrides CSV)",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Password for device authentication (overrides CSV)",
        hide_input=True,
    ),
    ssh_key: Optional[Path] = typer.Option(
        None,
        "--ssh-key",
        "-k",
        help="Path to SSH private key file",
        exists=True,
    ),
    ssh_config: Optional[Path] = typer.Option(
        None,
        "--ssh-config",
        "-s",
        help="Path to SSH config file",
        exists=True,
    ),
    workers: int = typer.Option(
        10,
        "--workers",
        "-w",
        help="Number of concurrent workers",
        min=1,
        max=100,
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    Execute commands on network devices via SSH and collect outputs.
    
    This tool connects to multiple network devices concurrently, executes
    specified commands, and collects the outputs into a structured format.
    """
    try:
        # Load devices from CSV
        print_warning(f"Loading devices from {devices_file}...")
        devices = load_devices_from_csv(devices_file)
        console.print(f"✓ Loaded {len(devices)} device(s)", style="green")
        
        # Load commands from file
        print_warning(f"Loading commands from {commands_file}...")
        commands = load_commands_from_file(commands_file)
        console.print(f"✓ Loaded {len(commands)} command(s)", style="green")
        
        # Create configuration
        config = Config(
            devices_file=devices_file,
            commands_file=commands_file,
            output_file=output_file,
            output_format=output_format,
            username=username,
            password=password,
            ssh_key_file=ssh_key,
            ssh_config_file=ssh_config,
            max_workers=workers,
        )
        
        # Execute commands on devices
        console.print("\n[bold cyan]Executing commands on devices...[/bold cyan]")
        
        results = []
        progress_bar = create_progress_bar(len(devices))
        
        with progress_bar as progress:
            task = progress.add_task("Processing devices", total=len(devices))
            
            def progress_callback(result):
                """Update progress bar on each completed device."""
                results.append(result)
                progress.update(task, advance=1)
            
            # Execute on all devices
            stats = execute_on_devices(
                devices=devices,
                commands=commands,
                max_workers=config.max_workers,
                progress_callback=progress_callback,
            )
        
        # Display summary
        console.print()
        summary_panel = create_device_summary(stats)
        console.print(summary_panel)
        
        # Generate output file
        if results:
            print_warning(f"\nGenerating {output_format.upper()} output...")
            formatter = get_formatter(output_format)
            output_content = formatter.format(results)
            
            output_file.write_text(output_content)
            print_success(f"✓ Output written to: {output_file}")
        else:
            print_warning("No results to write")
        
        # Exit with appropriate code
        if stats.failed > 0:
            console.print(
                f"\n[yellow]Warning: {stats.failed} device(s) failed[/yellow]"
            )
            raise typer.Exit(code=1)
        else:
            console.print("\n[green]✓ All devices completed successfully[/green]")
            raise typer.Exit(code=0)
            
    except FileNotFoundError as e:
        print_error(f"File not found: {e}")
        raise typer.Exit(code=2)
    except ValueError as e:
        print_error(f"Invalid input: {e}")
        raise typer.Exit(code=3)
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        raise typer.Exit(code=130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
