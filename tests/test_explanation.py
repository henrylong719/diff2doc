"""Tests for explanation stage."""

from unittest.mock import MagicMock, patch

from diff2doc.explanation import _count_changed_lines, explain_groups
from diff2doc.models import DiffResult, FileDiff, Hunk


def test_count_changed_lines_counts_additions_and_removals() -> None:
    """_count_changed_lines counts lines starting with + or -."""
    file_diff = FileDiff(
        path="src/cli.py",
        hunks=[
            Hunk(
                header="@@ -1,5 +1,5 @@",
                content="-    old line\n+    new line\n     unchanged\n+    added",
            )
        ],
    )

    assert _count_changed_lines(file_diff) == 3


def test_count_changed_lines_returns_zero_for_context_only() -> None:
    """_count_changed_lines returns 0 when there are no changes."""
    file_diff = FileDiff(
        path="src/cli.py",
        hunks=[
            Hunk(
                header="@@ -1,3 +1,3 @@",
                content="     context line\n     another context line",
            )
        ],
    )

    assert _count_changed_lines(file_diff) == 0


@patch("diff2doc.explanation.anthropic.Anthropic")
def test_explain_groups_fills_explanation(mock_anthropic_class: MagicMock) -> None:
    """explain_groups calls the API and fills in each file's explanation."""
    # Set up the fake response
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "This adds logging."

    mock_message = MagicMock()
    mock_message.content = [mock_block]

    # Wire up: Anthropic() -> client -> client.messages.create() -> message
    mock_client = mock_anthropic_class.return_value
    mock_client.messages.create.return_value = mock_message

    # Need at least MIN_CHANGED_LINES (4) changed lines
    diff_result = DiffResult(
        files=[
            FileDiff(
                path="src/cli.py",
                hunks=[
                    Hunk(
                        header="@@ -1,5 +1,8 @@",
                        content=(
                            "+    line one\n"
                            "+    line two\n"
                            "+    line three\n"
                            "+    line four"
                        ),
                    )
                ],
            )
        ],
        raw_diff="some diff text",
    )
    result = explain_groups(diff_result)

    assert result.files[0].explanation == "This adds logging."
    mock_client.messages.create.assert_called_once()


@patch("diff2doc.explanation.anthropic.Anthropic")
def test_explain_groups_skips_trivial_files(mock_anthropic_class: MagicMock) -> None:
    """explain_groups calls the API and fills in the explanation field."""
    # Set up the fake response
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "This adds a print statement."

    mock_message = MagicMock()
    mock_message.content = [mock_block]

    # Wire up: Anthropic() -> client -> client.messages.create() -> message
    mock_client = mock_anthropic_class.return_value
    mock_client.messages.create.return_value = mock_message

    # Run the function
    diff_result = DiffResult(
        files=[
            FileDiff(
                path="src/cli.py",
                hunks=[
                    Hunk(
                        header="@@ -1,3 +1,4 @@",
                        content="+    one small change",
                    )
                ],
            )
        ],
        raw_diff="some diff text",
    )
    result = explain_groups(diff_result)

    # No API call should have been made
    mock_client = mock_anthropic_class.return_value
    mock_client.messages.create.create.assert_not_called()

    # Explanation should remain empty
    assert result.files[0].explanation == ""
