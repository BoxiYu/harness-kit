"""harness check — Verify harness infrastructure is properly set up."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def check() -> None:
    """Check that harness-kit infrastructure is properly set up."""
    project_dir = Path.cwd()
    harness_dir = project_dir / ".harness"

    table = Table(title="Harness Infrastructure Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Path")

    all_ok = True

    checks = [
        (".harness/", harness_dir.is_dir()),
        (".harness/memory/constitution.md", (harness_dir / "memory" / "constitution.md").is_file()),
        (".harness/constraints/", (harness_dir / "constraints").is_dir()),
        (".harness/templates/", (harness_dir / "templates").is_dir()),
        (".harness/context/", (harness_dir / "context").is_dir()),
        (".harness/AGENTS.md", (harness_dir / "AGENTS.md").is_file()),
    ]

    # Count constraints
    constraints_dir = harness_dir / "constraints"
    constraint_count = 0
    if constraints_dir.is_dir():
        constraint_count = len(list(constraints_dir.glob("*.yml")))

    # Check git hooks
    git_hooks_dir = project_dir / ".git" / "hooks"
    pre_commit_hook = git_hooks_dir / "pre-commit"
    has_hook = pre_commit_hook.is_file()

    for path_str, exists in checks:
        status = "[green]OK[/green]" if exists else "[red]MISSING[/red]"
        if not exists:
            all_ok = False
        table.add_row(path_str, status, str(project_dir / path_str))

    table.add_row(
        "Constraints defined",
        f"[green]{constraint_count}[/green]" if constraint_count > 0 else "[yellow]0[/yellow]",
        str(constraints_dir) if constraints_dir.is_dir() else "—",
    )

    table.add_row(
        "Pre-commit hook",
        "[green]INSTALLED[/green]" if has_hook else "[yellow]NOT INSTALLED[/yellow]",
        str(pre_commit_hook) if has_hook else "—",
    )

    console.print(table)

    if all_ok:
        console.print("\n[bold green]All checks passed.[/bold green]")
    else:
        console.print(
            "\n[bold yellow]Some components are missing.[/bold yellow] "
            "Run [cyan]harness init[/cyan] to set up."
        )
        raise typer.Exit(1)
