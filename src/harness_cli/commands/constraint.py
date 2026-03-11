"""harness constraint — Manage architectural constraints."""

from __future__ import annotations

from pathlib import Path
from datetime import date

import typer
import yaml
from rich.console import Console
from rich.table import Table

console = Console()

constraint_app = typer.Typer(no_args_is_help=True)


def _get_constraints_dir() -> Path:
    return Path.cwd() / ".harness" / "constraints"


def _load_constraints() -> list[dict]:
    """Load all YAML constraint files."""
    constraints_dir = _get_constraints_dir()
    if not constraints_dir.is_dir():
        return []
    constraints = []
    for yml_file in sorted(constraints_dir.glob("*.yml")):
        try:
            data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
            if data:
                data["_file"] = yml_file.name
                constraints.append(data)
        except (yaml.YAMLError, OSError) as e:
            console.print(f"[yellow]Warning: Failed to parse {yml_file.name}: {e}[/yellow]")
    return constraints


@constraint_app.command("list")
def constraint_list() -> None:
    """List all active constraints."""
    constraints = _load_constraints()
    if not constraints:
        console.print("[yellow]No constraints found in .harness/constraints/[/yellow]")
        console.print("Run [cyan]harness constraint add[/cyan] to create one.")
        return

    table = Table(title="Active Constraints")
    table.add_column("Name", style="cyan")
    table.add_column("Severity")
    table.add_column("Enabled")
    table.add_column("File")
    table.add_column("Description")

    for c in constraints:
        severity = c.get("severity", "unknown")
        severity_style = "red" if severity == "error" else "yellow"
        enabled = c.get("enabled", True)
        table.add_row(
            c.get("name", "unnamed"),
            f"[{severity_style}]{severity}[/{severity_style}]",
            "[green]yes[/green]" if enabled else "[dim]no[/dim]",
            c.get("_file", "?"),
            c.get("description", ""),
        )

    console.print(table)


@constraint_app.command("add")
def constraint_add(
    name: str = typer.Option(..., help="Constraint short ID (e.g., 'api-auth')"),
    rule: str = typer.Option(..., help="One-line rule description"),
    fix: str = typer.Option(..., help="Fix instruction for AI agents"),
    severity: str = typer.Option(default="error", help="Severity: error or warning"),
    patterns: str = typer.Option(default="src/**/*.py", help="Comma-separated file patterns"),
) -> None:
    """Add a new constraint."""
    constraints_dir = _get_constraints_dir()
    constraints_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename from name
    filename = name.replace(" ", "-").lower() + ".yml"
    filepath = constraints_dir / filename

    if filepath.exists():
        console.print(f"[yellow]Constraint file {filename} already exists. Use --force or edit directly.[/yellow]")
        raise typer.Exit(1)

    file_patterns = [p.strip() for p in patterns.split(",")]

    constraint_data = {
        "name": name,
        "description": rule,
        "severity": severity,
        "enabled": True,
        "created": date.today().isoformat(),
        "file_patterns": file_patterns,
        "check": {
            "type": "custom",
            "rule": rule,
        },
        "fix_message": (
            f"VIOLATION [{name}] at {{file}}:{{line}}\n"
            f"  Rule: {rule}\n"
            f"  Fix: {fix}\n"
        ),
    }

    filepath.write_text(
        yaml.dump(constraint_data, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    console.print(f"[green]Created constraint:[/green] [cyan]{filename}[/cyan]")
    console.print(f"  Name: {name}")
    console.print(f"  Rule: {rule}")
    console.print(f"  Fix:  {fix}")
    console.print(f"\nEdit [cyan].harness/constraints/{filename}[/cyan] to refine the check logic.")


@constraint_app.command("check")
def constraint_check() -> None:
    """Run all constraint checks against the codebase (alias for harness lint)."""
    from harness_cli.commands.lint import lint
    lint(fix_instructions=True, layer=False, naming=False)
