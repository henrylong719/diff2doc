"""Command-line interface for diff2doc."""

import typer

from diff2doc.context import expand_context
from diff2doc.explanation import explain_groups
from diff2doc.git_diff import get_diff, parse_diff
from diff2doc.grouping import group_hunks
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
        help="Git range to diff (e.g. main...HEAD, HEAD~3).",
    ),
    staged: bool = typer.Option(False, help="Diff staged changes."),
) -> None:
    """Generate a review brief from the current git diff."""
    try:
        if staged:
            diff = get_diff("--staged")
        else:
            diff = get_diff(git_range)

        if not diff:
            typer.echo("No changes found.")
            raise typer.Exit()

        result = parse_diff(diff)
        result = expand_context(result)
        result = group_hunks(result)
        result = explain_groups(result)
        brief = render_markdown(result)
        typer.echo(brief)
    except typer.Exit:
        raise
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
