"""Stage 3: Group diff hunks by logical intent using an LLM."""

from diff2doc.models import DiffResult


def group_hunks(diff_result: DiffResult) -> DiffResult:
    """Cluster hunks into logical groups by intent.

    In the full implementation this will make an LLM call to group
    related hunks together. For now it passes data through unchanged.

    Args:
        diff_result: The parsed diff data with context.

    Returns:
        The same DiffResult, eventually with hunks grouped by intent.
    """
    return diff_result
