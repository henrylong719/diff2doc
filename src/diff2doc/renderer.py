"""Render parsed diff data as markdown review output."""

from diff2doc.models import DiffResult


def render_markdown(diff_result: DiffResult) -> str:
    """Render a DiffResult as a markdown review brief.

    Args:
        diff_result: The parsed diff data to render.

    Returns:
        A markdown-formatted string.
    """
    lines: list[str] = []
    lines.append("# Review Brief")
    lines.append("")

    for file_diff in diff_result.files:
        lines.append(f"## {file_diff.path}")
        lines.append("")

        if file_diff.explanation:
            lines.append(file_diff.explanation)
            lines.append("")

        for hunk_number, hunk in enumerate(file_diff.hunks, start=1):
            lines.append(f"### Hunk {hunk_number}")
            lines.append("```")
            lines.append(hunk.header)
            lines.append(hunk.content)
            lines.append("```")
            lines.append("")

    return "\n".join(lines)
