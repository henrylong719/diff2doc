"""Stage 2: Expand diff hunks with surrounding code context."""

from diff2doc.models import DiffResult


def expand_context(diff_result: DiffResult) -> DiffResult:
    """Add surrounding code context to each hunk.

    In the full implementation this will parse source files to find
    enclosing functions/classes and callers. For now it passes data
    through unchanged.

    Args:
        diff_result: The parsed diff data.

    Returns:
        The same DiffResult, eventually enriched with context.
    """
    return diff_result
