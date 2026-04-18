"""Stage 2: Expand diff hunks with surrounding code context."""

import ast
from pathlib import Path
from textwrap import dedent

from diff2doc.models import DiffResult


def _find_enclosing_scope(source: str, line_number: int) -> str | None:
    """Find the name of the function or class containing a line number.

    Args:
        source: The full Python source code of the file.
        line_number: The line to look up.

    Returns:
        The name of the enclosing function or class, or None if the
        line is at module level.
    """
    tree = ast.parse(dedent(source))
    best_match: str | None = None
    smallest_range = float("inf")

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            continue

        if node.end_lineno is None:
            continue

        if node.lineno <= line_number <= node.end_lineno:
            node_range = node.end_lineno - node.lineno
            if node_range < smallest_range:
                smallest_range = node_range
                best_match = node.name

    return best_match


def _parse_hunk_start_line(header: str) -> int | None:
    """Extract the starting line number from a hunk header.

    The header format is: @@ -old_start,old_count +new_start,new_count @@
    We want new_start since we read the current version of the file.

    Args:
        header: The @@ line from a diff hunk.

    Returns:
        The starting line number, or None if parsing fails.
    """
    # "@@ -15,3 +15,4 @@ def main()" -> find "+15,4" -> take "15"
    parts = header.split("+")
    if len(parts) < 2:
        return None
    number_part = parts[1].split(",")[0]
    try:
        return int(number_part)
    except ValueError:
        return None


def expand_context(diff_result: DiffResult) -> DiffResult:
    """Add surrounding code context to each hunk.

    For Python files, finds the enclosing function or class for each
    hunk using the ast module. Non-Python files are skipped.

    Args:
        diff_result: The parsed diff data.

    Returns:
        The same DiffResult with enclosing_scope filled in where possible.
    """
    for file_diff in diff_result.files:
        if not file_diff.path.endswith(".py"):
            continue

        try:
            source = Path(file_diff.path).read_text()
        except FileNotFoundError:
            continue

        for hunk in file_diff.hunks:
            start_line = _parse_hunk_start_line(hunk.header)
            if start_line is None:
                continue

            hunk.enclosing_scope = _find_enclosing_scope(source, start_line)

    return diff_result
