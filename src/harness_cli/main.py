import typer

from harness_cli.commands.init import init
from harness_cli.commands.check import check
from harness_cli.commands.constraint import constraint_app
from harness_cli.commands.lint import lint
from harness_cli.commands.gc import gc
from harness_cli.commands.audit import audit
from harness_cli.commands.loop import loop_app

app = typer.Typer(
    name="harness",
    help="harness-kit: Constraints, feedback loops, and lifecycle systems for AI coding agents.",
    no_args_is_help=True,
)

app.command()(init)
app.command()(check)
app.add_typer(constraint_app, name="constraint", help="Manage architectural constraints.")
app.add_typer(loop_app, name="loop", help="Doom loop detection for AI agents.")
app.command()(lint)
app.command()(gc)
app.command()(audit)
