"""harness init — Bootstrap .harness/ directory in a project."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

HARNESS_DIR = ".harness"
BASE_DIR = Path(__file__).resolve().parents[2] / "harness_cli" / "_base"
# Fallback: when installed via uv, base may be alongside src
REPO_BASE_DIR = Path(__file__).resolve().parents[3] / "base"

AI_AGENTS = {
    "claude": {
        "context_file": "CLAUDE.md",
        "commands_dir": ".claude/commands",
    },
    "copilot": {
        "context_file": ".github/copilot-instructions.md",
        "commands_dir": None,
    },
    "cursor": {
        "context_file": ".cursorrules",
        "commands_dir": None,
    },
    "gemini": {
        "context_file": "GEMINI.md",
        "commands_dir": None,
    },
    "codex": {
        "context_file": "AGENTS.md",
        "commands_dir": None,
    },
}


def _find_base_dir() -> Path:
    """Locate the base template directory."""
    # Installed via wheel: _base is bundled inside the package
    if BASE_DIR.is_dir():
        return BASE_DIR
    # Development: base/ is at repo root
    if REPO_BASE_DIR.is_dir():
        return REPO_BASE_DIR
    # Walk up from this file looking for base/
    current = Path(__file__).resolve().parent
    for _ in range(8):
        candidate = current / "base"
        if candidate.is_dir():
            return candidate
        current = current.parent
    typer.echo("Error: Could not locate base template directory.", err=True)
    raise typer.Exit(1)


def _copy_tree(src: Path, dst: Path) -> list[str]:
    """Recursively copy a directory tree, returning list of created files."""
    created = []
    for item in sorted(src.rglob("*")):
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copy2(item, target)
                created.append(str(rel))
    return created


def _replace_placeholders(path: Path, project_name: str) -> None:
    """Replace template placeholders in markdown files."""
    today = date.today().isoformat()
    for md_file in path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        original = content
        content = content.replace("[PROJECT_NAME]", project_name)
        content = content.replace("[DATE]", today)
        if content != original:
            md_file.write_text(content, encoding="utf-8")


def _setup_agent_context(project_dir: Path, ai: str, project_name: str) -> None:
    """Generate agent-specific context files."""
    agent_config = AI_AGENTS.get(ai)
    if not agent_config:
        console.print(f"[yellow]Warning: Unknown AI agent '{ai}'. Skipping agent setup.[/yellow]")
        return

    context_file = project_dir / agent_config["context_file"]
    context_file.parent.mkdir(parents=True, exist_ok=True)

    if not context_file.exists():
        context_content = f"""# {project_name}

## Harness Engineering

This project uses harness-kit for constraint enforcement and quality management.

### Before Writing Code

1. Read `.harness/AGENTS.md` for project rules and architecture.
2. Check `.harness/constraints/` for active constraints.
3. Load domain docs from `.harness/context/` only when needed.

### Before Submitting Code

1. Run `harness lint` — all constraints must pass.
2. Run tests and type-checks.
3. If `harness lint` reports a violation, read the fix message and apply it.
4. If you edit the same file 3+ times for the same issue, stop and re-think.

### Key Commands

```bash
harness lint                    # Check all constraints
harness lint --fix-instructions # Agent-friendly output
harness gc --report             # Check for entropy
harness audit                   # Full health report
harness constraint list         # Show active constraints
```

### Architecture

See `.harness/context/ARCHITECTURE.md` for the dependency layer model.
"""
        context_file.write_text(context_content, encoding="utf-8")
        console.print(f"  Created [cyan]{agent_config['context_file']}[/cyan]")

    # Create slash commands for Claude
    if ai == "claude" and agent_config.get("commands_dir"):
        commands_dir = project_dir / agent_config["commands_dir"]
        commands_dir.mkdir(parents=True, exist_ok=True)

        commands = {
            "harness-lint.md": (
                "Run harness lint to check all architectural constraints. "
                "Report violations with their fix messages. "
                "Apply fixes for any violations found. "
                "Re-run until all constraints pass."
            ),
            "harness-gc.md": (
                "Run harness gc --report to check for entropy in the codebase. "
                "Review the garbage collection report. "
                "Flag any documentation freshness issues, pattern drift, or constraint bypasses. "
                "Propose fixes for the most critical issues."
            ),
            "harness-audit.md": (
                "Run harness audit to generate a full health report. "
                "Summarize the key findings: constraint violations, feedback loop health, "
                "entropy indicators. Recommend the top 3 actions to improve codebase health."
            ),
        }

        for filename, content in commands.items():
            cmd_file = commands_dir / filename
            if not cmd_file.exists():
                cmd_file.write_text(content, encoding="utf-8")
                console.print(f"  Created [cyan]{agent_config['commands_dir']}/{filename}[/cyan]")


def _setup_git_hooks(project_dir: Path) -> None:
    """Install pre-commit hook that runs harness lint."""
    git_dir = project_dir / ".git"
    if not git_dir.is_dir():
        return

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    pre_commit = hooks_dir / "pre-commit"
    if not pre_commit.exists():
        pre_commit.write_text(
            "#!/bin/sh\n"
            "# harness-kit pre-commit hook\n"
            "# 1. Run constraint checks\n"
            "# 2. Record edits for doom loop detection\n\n"
            "if command -v harness >/dev/null 2>&1; then\n"
            "    # Check constraints first\n"
            "    harness lint --fix-instructions\n"
            "    LINT_EXIT=$?\n"
            "    if [ $LINT_EXIT -ne 0 ]; then\n"
            "        # Record each staged file as an edit (for loop detection)\n"
            '        for f in $(git diff --cached --name-only); do\n'
            '            harness loop record "$f" --context "pre-commit: lint failed" 2>/dev/null\n'
            "        done\n"
            "        exit $LINT_EXIT\n"
            "    fi\n"
            "fi\n",
            encoding="utf-8",
        )
        pre_commit.chmod(0o755)
        console.print("  Installed [cyan]pre-commit hook[/cyan]")


def init(
    project_name: str = typer.Argument(
        default=".",
        help="Project name or '.' for current directory.",
    ),
    ai: str = typer.Option(
        default="",
        help="AI agent: claude, copilot, cursor, gemini, codex.",
    ),
    no_git: bool = typer.Option(
        default=False,
        help="Skip git initialization.",
    ),
    force: bool = typer.Option(
        default=False,
        help="Force overwrite in non-empty directories.",
    ),
    here: bool = typer.Option(
        default=False,
        help="Initialize in the current directory.",
    ),
) -> None:
    """Initialize harness-kit in a project directory."""

    if here or project_name == ".":
        project_dir = Path.cwd()
        resolved_name = project_dir.name
    else:
        project_dir = Path.cwd() / project_name
        resolved_name = project_name

    harness_path = project_dir / HARNESS_DIR

    # Check existing
    if harness_path.is_dir() and not force:
        console.print(
            f"[yellow].harness/ already exists in {project_dir}. Use --force to overwrite.[/yellow]"
        )
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold green]Initializing harness-kit[/bold green] in [cyan]{project_dir}[/cyan]",
            title="harness-kit",
            border_style="green",
        )
    )

    # Create project dir if needed
    project_dir.mkdir(parents=True, exist_ok=True)

    # Copy base templates
    base_dir = _find_base_dir()
    console.print("\n[bold]Setting up .harness/ directory...[/bold]")
    created = _copy_tree(base_dir, harness_path)
    for f in created:
        console.print(f"  Created [cyan].harness/{f}[/cyan]")

    # Replace placeholders
    _replace_placeholders(harness_path, resolved_name)

    # Git init
    if not no_git and not (project_dir / ".git").is_dir():
        import subprocess

        try:
            subprocess.run(
                ["git", "init"],
                cwd=project_dir,
                capture_output=True,
                check=True,
            )
            console.print("\n  Initialized [cyan]git repository[/cyan]")
        except (subprocess.CalledProcessError, FileNotFoundError):
            console.print("[yellow]  Warning: git init failed. Skipping.[/yellow]")

    # Git hooks
    _setup_git_hooks(project_dir)

    # Agent setup
    if ai:
        console.print(f"\n[bold]Configuring for AI agent: {ai}[/bold]")
        _setup_agent_context(project_dir, ai, resolved_name)

    # Summary
    console.print(
        Panel(
            "[bold green]harness-kit initialized![/bold green]\n\n"
            "Next steps:\n"
            "  1. Edit [cyan].harness/memory/constitution.md[/cyan] with your project principles\n"
            "  2. Customize constraints in [cyan].harness/constraints/[/cyan]\n"
            "  3. Fill in [cyan].harness/context/ARCHITECTURE.md[/cyan]\n"
            "  4. Run [cyan]harness check[/cyan] to verify setup\n"
            "  5. Run [cyan]harness lint[/cyan] to test constraint enforcement",
            title="Done",
            border_style="green",
        )
    )
