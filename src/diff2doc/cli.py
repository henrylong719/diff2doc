"""Command-line interface for diff2doc."""

import typer

from diff2doc.git_diff import get_diff, parse_diff
from diff2doc.renderer import render_markdown

app = typer.Typer(
    name="diff2doc",
    help="Turn git diffs into structured review briefs.",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main(
    git_range: str = typer.Argument(
        default="HEAD",
        help="Git range to diff (e.g. main...HEAD, HEAD~3, --staged).",
    ),
) -> None:
    """Generate a review brief from the current git diff."""
    diff = get_diff(git_range)
    if not diff:
        typer.echo("No changes found.")
        raise typer.Exit()

    result = parse_diff(diff)
    brief = render_markdown(result)
    typer.echo(brief)
