"""harness loop — Doom loop detection for AI coding agents."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from harness_cli.engine.loop_detector import LoopDetector

console = Console()

loop_app = typer.Typer(no_args_is_help=True)


@loop_app.command("record")
def loop_record(
    file: str = typer.Argument(help="File path that was edited."),
    context: str = typer.Option(default="", help="Brief description of the edit."),
    threshold: int = typer.Option(default=3, help="Number of edits before triggering loop alert."),
    window: int = typer.Option(default=300, help="Time window in seconds."),
) -> None:
    """Record a file edit and check for doom loops.

    This is the primary command for AI agents. Call it after every file edit.
    If a loop is detected, the output ADVISES the agent to re-think,
    but does NOT block execution (exit 0). This avoids breaking normal
    iterative development (TDD, incremental fixes, multi-part edits).
    """
    root = Path.cwd()
    detector = LoopDetector.load(root, edit_threshold=threshold, time_window=window)
    detector.record_edit(file, context=context)
    result = detector.check(file)
    detector.save()

    if result.is_loop:
        # Advisory, not blocking — agent can choose to continue or re-think
        console.print(f"\n[bold yellow]{result.intervention_message}[/bold yellow]")
    elif result.edit_count >= 2:
        remaining = threshold - result.edit_count
        console.print(
            f"[yellow]Note: {file} edited {result.edit_count} times "
            f"in the last {window // 60}min. "
            f"{remaining} more edit(s) before loop advisory.[/yellow]"
        )
    else:
        console.print(f"[dim]Recorded edit: {file}[/dim]")


@loop_app.command("status")
def loop_status(
    threshold: int = typer.Option(default=3, help="Number of edits before triggering."),
    window: int = typer.Option(default=300, help="Time window in seconds."),
) -> None:
    """Show current edit frequency for all recently edited files."""
    root = Path.cwd()
    detector = LoopDetector.load(root, edit_threshold=threshold, time_window=window)
    results = detector.check_all()

    if not results:
        console.print("[dim]No recent file edits recorded.[/dim]")
        return

    table = Table(title="Recent Edit Activity")
    table.add_column("File", style="cyan")
    table.add_column("Edits", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Status")

    for r in results:
        if r.is_loop:
            status = "[bold red]LOOP DETECTED[/bold red]"
        elif r.edit_count >= threshold - 1:
            status = "[yellow]WARNING[/yellow]"
        else:
            status = "[green]OK[/green]"

        table.add_row(
            r.file,
            str(r.edit_count),
            str(threshold),
            status,
        )

    console.print(table)


@loop_app.command("clear")
def loop_clear(
    file: str = typer.Option(default="", help="Clear history for a specific file. Omit to clear all."),
) -> None:
    """Clear edit history (use after resolving a loop)."""
    root = Path.cwd()
    detector = LoopDetector.load(root)

    if file:
        detector.clear(file)
        console.print(f"[green]Cleared edit history for {file}[/green]")
    else:
        detector.clear()
        console.print("[green]Cleared all edit history.[/green]")

    detector.save()
