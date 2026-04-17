"""Tests for the render markdown."""

from diff2doc.models import DiffResult, FileDiff, Hunk
from diff2doc.renderer import render_markdown


def test_render_markdown_basic() -> None:
    """render_markdown produces markdown with heading, file path, and hunk."""
    diff_result = DiffResult(
        files=[
            FileDiff(
                path="src/cli.py",
                hunks=[
                    Hunk(
                        header="@@ -15,3 +15,4 @@ def main()",
                        content="     diff = get_diff()\n+    print(diff)\n     return",
                    )
                ],
            )
        ],
        raw_diff="not used in rendering",
    )

    output = render_markdown(diff_result)

    assert "# Review Brief" in output
    assert "## src/cli.py" in output
    assert "### Hunk 1" in output
    assert "+    print(diff)" in output
