"""harness lint — Run constraint checks against the codebase."""

from __future__ import annotations

import re
from pathlib import Path

import typer
import yaml
from pathspec import PathSpec
from rich.console import Console

console = Console()


def _load_constraints() -> list[dict]:
    constraints_dir = Path.cwd() / ".harness" / "constraints"
    if not constraints_dir.is_dir():
        return []
    constraints = []
    for yml_file in sorted(constraints_dir.glob("*.yml")):
        try:
            data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
            if data and data.get("enabled", True):
                data["_file"] = yml_file.name
                constraints.append(data)
        except (yaml.YAMLError, OSError):
            pass
    return constraints


def _match_files(patterns: list[str], root: Path) -> list[Path]:
    """Find files matching glob patterns (supports ! negation)."""
    include = [p for p in patterns if not p.startswith("!")]
    exclude = [p[1:] for p in patterns if p.startswith("!")]

    include_spec = PathSpec.from_lines("gitignore", include) if include else None
    exclude_spec = PathSpec.from_lines("gitignore", exclude) if exclude else None

    matched = []
    for f in root.rglob("*"):
        if not f.is_file():
            continue
        rel = str(f.relative_to(root))
        if include_spec and include_spec.match_file(rel):
            if exclude_spec and exclude_spec.match_file(rel):
                continue
            matched.append(f)
    return sorted(matched)


def _check_naming_rules(constraint: dict, root: Path) -> list[dict]:
    """Check naming convention rules."""
    violations = []
    rules = constraint.get("rules", [])

    for rule in rules:
        patterns = rule.get("file_patterns", [])
        files = _match_files(patterns, root)
        check = rule.get("check", {})
        check_type = check.get("type", "")

        for f in files:
            if check_type == "filename":
                pattern = check.get("pattern", "")
                if pattern and not re.match(pattern, f.name):
                    violations.append({
                        "constraint": constraint.get("name", "unnamed"),
                        "rule": rule.get("name", ""),
                        "file": str(f.relative_to(root)),
                        "line": 0,
                        "message": rule.get("fix_message", "").format(
                            file=str(f.relative_to(root)),
                            filename=f.name,
                            suggested_name=re.sub(r"([A-Z])", r"_\1", f.stem).lower().lstrip("_") + f.suffix,
                        ),
                    })
            elif check_type == "regex":
                # Regex checks look for lines that SHOULD match (positive pattern)
                # This is informational — full AST checks would be in Phase 2
                pass

    return violations


def _check_layer_rules(constraint: dict, root: Path) -> list[dict]:
    """Check dependency layer violations by analyzing imports."""
    violations = []
    layers = constraint.get("layers", [])
    if not layers:
        return violations

    # Build layer lookup: pattern -> (layer_name, layer_index)
    layer_lookup: dict[str, tuple[str, int]] = {}
    for layer in layers:
        for pattern in layer.get("patterns", []):
            layer_lookup[pattern] = (layer["name"], layer["index"])

    # Map each source file to its layer
    def _file_layer(rel_path: str) -> tuple[str, int] | None:
        for pattern, (name, idx) in layer_lookup.items():
            spec = PathSpec.from_lines("gitignore", [pattern])
            if spec.match_file(rel_path):
                return (name, idx)
        return None

    # Scan Python imports
    import_re = re.compile(r"^\s*(?:from|import)\s+([\w.]+)")
    src_dir = root / "src"
    if not src_dir.is_dir():
        return violations

    for f in src_dir.rglob("*.py"):
        rel = str(f.relative_to(root))
        source_layer = _file_layer(rel)
        if source_layer is None:
            continue

        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue

        for line_num, line in enumerate(lines, 1):
            m = import_re.match(line)
            if not m:
                continue
            imported_module = m.group(1)
            # Convert module path to file path guess
            imported_path = "src/" + imported_module.replace(".", "/")
            for ext in ["", ".py", "/__init__.py"]:
                candidate = imported_path + ext
                target_layer = _file_layer(candidate)
                if target_layer:
                    break
            else:
                continue

            source_name, source_idx = source_layer
            target_name, target_idx = target_layer

            if target_idx > source_idx:
                fix_msg = constraint.get("fix_message", "Layer violation.")
                violations.append({
                    "constraint": constraint.get("name", "unnamed"),
                    "rule": "layer-direction",
                    "file": rel,
                    "line": line_num,
                    "message": fix_msg.format(
                        file=rel,
                        line=line_num,
                        source_layer=source_name,
                        source_index=source_idx,
                        target_layer=target_name,
                        target_index=target_idx,
                        import_statement=line.strip(),
                    ),
                })

    return violations


def lint(
    fix_instructions: bool = typer.Option(
        default=False,
        help="Output in agent-friendly format with fix instructions.",
    ),
    layer: bool = typer.Option(
        default=False,
        help="Only run dependency layer checks.",
    ),
    naming: bool = typer.Option(
        default=False,
        help="Only run naming convention checks.",
    ),
) -> None:
    """Run all constraint checks against the codebase."""
    root = Path.cwd()
    harness_dir = root / ".harness"

    if not harness_dir.is_dir():
        console.print("[red]No .harness/ directory found. Run 'harness init' first.[/red]")
        raise typer.Exit(1)

    constraints = _load_constraints()
    if not constraints:
        console.print("[yellow]No constraints found in .harness/constraints/[/yellow]")
        return

    all_violations: list[dict] = []
    checked_count = 0

    for c in constraints:
        cname = c.get("name", "unnamed")

        # Filter by flags
        if layer and cname != "dependency-layers":
            continue
        if naming and cname != "naming-conventions":
            continue

        checked_count += 1

        if cname == "dependency-layers":
            all_violations.extend(_check_layer_rules(c, root))
        elif cname == "naming-conventions":
            all_violations.extend(_check_naming_rules(c, root))
        # Other constraint types can be added here

    # Report
    if not all_violations:
        console.print(
            f"[bold green]All checks passed.[/bold green] "
            f"({checked_count} constraint(s) checked)"
        )
        return

    console.print(f"\n[bold red]{len(all_violations)} violation(s) found:[/bold red]\n")

    for v in all_violations:
        if fix_instructions:
            # Agent-friendly format: just print the fix message directly
            console.print(v["message"])
            console.print()
        else:
            location = v["file"]
            if v.get("line"):
                location += f":{v['line']}"
            console.print(f"  [red]VIOLATION[/red] \\[{v['constraint']}] at [cyan]{location}[/cyan]")

    if not fix_instructions:
        console.print(
            f"\nRun [cyan]harness lint --fix-instructions[/cyan] for detailed remediation guidance."
        )

    # Check for doom loops on violated files
    try:
        from harness_cli.engine.loop_detector import LoopDetector
        detector = LoopDetector.load(root)
        violated_files = set(v["file"] for v in all_violations)
        loops_found = False
        for vf in sorted(violated_files):
            result = detector.check(vf)
            if result.edit_count >= 2:
                if result.is_loop:
                    console.print(f"\n[bold red]{result.intervention_message}[/bold red]")
                    loops_found = True
                else:
                    remaining = detector.edit_threshold - result.edit_count
                    console.print(
                        f"\n[yellow]Note: {vf} has been edited {result.edit_count} time(s) recently. "
                        f"{remaining} more before loop alert.[/yellow]"
                    )
    except Exception:
        pass  # loop detector is optional, don't break lint

    raise typer.Exit(1)
