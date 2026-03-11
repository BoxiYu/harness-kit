"""harness audit — Generate comprehensive codebase health report."""

from __future__ import annotations

from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def _count_constraints(harness_dir: Path) -> tuple[int, int]:
    """Count total and enabled constraints."""
    constraints_dir = harness_dir / "constraints"
    if not constraints_dir.is_dir():
        return 0, 0
    total = 0
    enabled = 0
    for yml_file in constraints_dir.glob("*.yml"):
        try:
            data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
            if data:
                total += 1
                if data.get("enabled", True):
                    enabled += 1
        except (yaml.YAMLError, OSError):
            total += 1
    return total, enabled


def audit(
    metrics: bool = typer.Option(default=False, help="Show harness health metrics only."),
) -> None:
    """Generate a comprehensive harness health report."""
    root = Path.cwd()
    harness_dir = root / ".harness"

    if not harness_dir.is_dir():
        console.print("[red]No .harness/ directory found. Run 'harness init' first.[/red]")
        raise typer.Exit(1)

    console.print(Panel("[bold]Harness Health Report[/bold]", border_style="blue"))

    # Infrastructure check
    infra_table = Table(title="Infrastructure")
    infra_table.add_column("Component", style="cyan")
    infra_table.add_column("Status")

    components = {
        ".harness/ directory": harness_dir.is_dir(),
        "Constitution": (harness_dir / "memory" / "constitution.md").is_file(),
        "AGENTS.md": (harness_dir / "AGENTS.md").is_file(),
        "Context docs": (harness_dir / "context").is_dir(),
        "Templates": (harness_dir / "templates").is_dir(),
    }

    for name, exists in components.items():
        status = "[green]OK[/green]" if exists else "[red]MISSING[/red]"
        infra_table.add_row(name, status)

    total_constraints, enabled_constraints = _count_constraints(harness_dir)
    infra_table.add_row(
        "Constraints",
        f"[green]{enabled_constraints} active[/green] / {total_constraints} total"
        if total_constraints > 0
        else "[yellow]0 defined[/yellow]",
    )

    # Git hooks
    pre_commit = root / ".git" / "hooks" / "pre-commit"
    infra_table.add_row(
        "Pre-commit hook",
        "[green]INSTALLED[/green]" if pre_commit.is_file() else "[yellow]NOT INSTALLED[/yellow]",
    )

    console.print(infra_table)

    # Constraint detail
    if not metrics:
        constraints_dir = harness_dir / "constraints"
        if constraints_dir.is_dir():
            c_table = Table(title="\nConstraint Inventory")
            c_table.add_column("Name", style="cyan")
            c_table.add_column("Severity")
            c_table.add_column("Enabled")
            c_table.add_column("Has Fix Message")

            for yml_file in sorted(constraints_dir.glob("*.yml")):
                try:
                    data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
                    if not data:
                        continue
                except (yaml.YAMLError, OSError):
                    continue

                severity = data.get("severity", "?")
                sev_style = "red" if severity == "error" else "yellow"
                enabled = data.get("enabled", True)
                has_fix = bool(data.get("fix_message"))

                c_table.add_row(
                    data.get("name", yml_file.stem),
                    f"[{sev_style}]{severity}[/{sev_style}]",
                    "[green]yes[/green]" if enabled else "[dim]no[/dim]",
                    "[green]yes[/green]" if has_fix else "[red]NO[/red]",
                )

            console.print(c_table)

    # Context budget estimate
    context_dir = harness_dir / "context"
    agents_md = harness_dir / "AGENTS.md"
    constitution = harness_dir / "memory" / "constitution.md"

    total_chars = 0
    if agents_md.is_file():
        total_chars += len(agents_md.read_text(encoding="utf-8"))
    if constitution.is_file():
        total_chars += len(constitution.read_text(encoding="utf-8"))
    if context_dir.is_dir():
        for md in context_dir.rglob("*.md"):
            total_chars += len(md.read_text(encoding="utf-8"))

    # Rough token estimate (1 token ≈ 4 chars)
    estimated_tokens = total_chars // 4
    # 200k context window, 40% budget = 80k tokens
    budget = 80_000
    utilization = (estimated_tokens / budget * 100) if budget > 0 else 0

    ctx_table = Table(title="\nContext Budget")
    ctx_table.add_column("Metric", style="cyan")
    ctx_table.add_column("Value")

    ctx_table.add_row("Total harness docs", f"{total_chars:,} chars (~{estimated_tokens:,} tokens)")
    ctx_table.add_row("Budget (40% of 200k)", f"{budget:,} tokens")

    util_style = "green" if utilization < 30 else ("yellow" if utilization < 40 else "red")
    ctx_table.add_row("Utilization", f"[{util_style}]{utilization:.1f}%[/{util_style}]")

    console.print(ctx_table)

    # Recommendations
    recommendations = []
    if not (harness_dir / "memory" / "constitution.md").is_file():
        recommendations.append("Create a constitution: edit .harness/memory/constitution.md")
    if total_constraints == 0:
        recommendations.append("Define constraints: run 'harness constraint add'")
    if not pre_commit.is_file():
        recommendations.append("Install pre-commit hook: re-run 'harness init'")
    if utilization > 40:
        recommendations.append("Context budget exceeded! Reduce docs or split into tiers.")

    if recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")
    else:
        console.print("\n[bold green]Harness looks healthy![/bold green]")
