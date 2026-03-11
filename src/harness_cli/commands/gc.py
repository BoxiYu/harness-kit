"""harness gc — Garbage collection for codebase entropy."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _check_doc_freshness(harness_dir: Path, root: Path) -> list[dict]:
    """Check if documentation is stale relative to code changes."""
    issues = []
    context_dir = harness_dir / "context"
    if not context_dir.is_dir():
        return issues

    for doc in context_dir.rglob("*.md"):
        doc_mtime = doc.stat().st_mtime
        doc_age_days = (datetime.now().timestamp() - doc_mtime) / 86400

        # Flag docs older than 30 days as potentially stale
        if doc_age_days > 30:
            issues.append({
                "type": "doc-freshness",
                "file": str(doc.relative_to(root)),
                "detail": f"Last modified {int(doc_age_days)} days ago",
                "severity": "warning",
            })

    return issues


def _check_orphaned_files(root: Path) -> list[dict]:
    """Simple heuristic check for potentially orphaned files."""
    issues = []
    src_dir = root / "src"
    if not src_dir.is_dir():
        return issues

    for py_file in src_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
        # Check if the file is empty (besides comments/whitespace)
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        if len(lines) == 0:
            issues.append({
                "type": "stale-artifact",
                "file": str(py_file.relative_to(root)),
                "detail": "Empty file (no code besides comments)",
                "severity": "warning",
            })

    return issues


def _check_constraint_consistency(harness_dir: Path, root: Path) -> list[dict]:
    """Check if constraint files are well-formed."""
    import yaml

    issues = []
    constraints_dir = harness_dir / "constraints"
    if not constraints_dir.is_dir():
        return issues

    required_fields = ["name", "description", "severity"]

    for yml_file in constraints_dir.glob("*.yml"):
        try:
            data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
        except (yaml.YAMLError, OSError) as e:
            issues.append({
                "type": "constraint-consistency",
                "file": str(yml_file.relative_to(root)),
                "detail": f"Failed to parse: {e}",
                "severity": "error",
            })
            continue

        if not data:
            issues.append({
                "type": "constraint-consistency",
                "file": str(yml_file.relative_to(root)),
                "detail": "Empty constraint file",
                "severity": "warning",
            })
            continue

        for field in required_fields:
            if field not in data:
                issues.append({
                    "type": "constraint-consistency",
                    "file": str(yml_file.relative_to(root)),
                    "detail": f"Missing required field: {field}",
                    "severity": "error",
                })

        if not data.get("fix_message"):
            issues.append({
                "type": "constraint-consistency",
                "file": str(yml_file.relative_to(root)),
                "detail": "Missing fix_message — agents won't know how to remediate violations",
                "severity": "warning",
            })

    return issues


def gc(
    docs: bool = typer.Option(default=False, help="Only check documentation freshness."),
    patterns: bool = typer.Option(default=False, help="Only check pattern drift."),
    report: bool = typer.Option(default=False, help="Generate report without fixing."),
) -> None:
    """Run garbage collection checks on the codebase."""
    root = Path.cwd()
    harness_dir = root / ".harness"

    if not harness_dir.is_dir():
        console.print("[red]No .harness/ directory found. Run 'harness init' first.[/red]")
        raise typer.Exit(1)

    all_issues: list[dict] = []

    if not patterns:
        console.print("[dim]Checking documentation freshness...[/dim]")
        all_issues.extend(_check_doc_freshness(harness_dir, root))

    if not docs:
        console.print("[dim]Checking for stale artifacts...[/dim]")
        all_issues.extend(_check_orphaned_files(root))

    console.print("[dim]Checking constraint consistency...[/dim]")
    all_issues.extend(_check_constraint_consistency(harness_dir, root))

    # Report
    if not all_issues:
        console.print("\n[bold green]No entropy issues found. Codebase is clean.[/bold green]")
        return

    table = Table(title="Garbage Collection Report")
    table.add_column("Type", style="cyan")
    table.add_column("File")
    table.add_column("Severity")
    table.add_column("Detail")

    error_count = 0
    warning_count = 0

    for issue in all_issues:
        severity = issue["severity"]
        if severity == "error":
            severity_display = "[red]error[/red]"
            error_count += 1
        else:
            severity_display = "[yellow]warning[/yellow]"
            warning_count += 1

        table.add_row(
            issue["type"],
            issue["file"],
            severity_display,
            issue["detail"],
        )

    console.print(table)
    console.print(f"\n[bold]{error_count} error(s), {warning_count} warning(s)[/bold]")

    if error_count > 0:
        raise typer.Exit(1)
