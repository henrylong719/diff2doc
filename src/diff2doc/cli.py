"""Command-line interface for diff2doc."""

import typer

from diff2doc.git_diff import get_diff

app = typer.Typer(
    name="diff2doc",
    help="Turn git diffs into structured review briefs.",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main() -> None:
    """Generate a review brief from the current git diff."""
    diff = get_diff()
    if not diff:
        typer.echo("No changes found.")
        raise typer.Exit()

    typer.echo(diff)
