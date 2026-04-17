"""Tests for the git diff extraction stage."""

from subprocess import CompletedProcess
from unittest.mock import MagicMock, patch

import pytest

from diff2doc.git_diff import get_diff, parse_diff


@patch("diff2doc.git_diff.subprocess.run")
def test_get_diff_returns_stdout_on_success(mock_run: MagicMock) -> None:
    """get_diff returns the raw stdout when git exits successfully."""

    mock_run.return_value = CompletedProcess(
        args=["git", "diff", "HEAD"],
        returncode=0,
        stdout="fake diff output\n",
        stderr="",
    )

    result = get_diff("HEAD")

    assert result == "fake diff output\n"
    mock_run.assert_called_once_with(
        ["git", "diff", "HEAD"], capture_output=True, text=True
    )


@patch("diff2doc.git_diff.subprocess.run")
def test_get_diff_raises_on_git_failure(mock_run: MagicMock) -> None:
    """get_diff raises RuntimeError when git exits with a non-zero code."""
    mock_run.return_value = CompletedProcess(
        args=["git", "diff", "HEAD"],
        returncode=128,
        stdout="",
        stderr="fatal: not a git repository",
    )

    with pytest.raises(RuntimeError, match="not a git repository"):
        get_diff("HEAD")


SIMPLE_DIFF = """\
diff --git a/src/cli.py b/src/cli.py
index abc123..def456 100644
--- a/src/cli.py
+++ b/src/cli.py
@@ -15,3 +15,4 @@ def main():
     diff = get_diff()
+    print(diff)
     return"""


def test_parse_diff_one_file_one_hunk() -> None:
    """parse_diff correctly parses a diff with one file and one hunk."""
    result = parse_diff(SIMPLE_DIFF)

    assert len(result.files) == 1
    assert result.files[0].path == "src/cli.py"
    assert len(result.files[0].hunks) == 1
    assert result.files[0].hunks[0].header.startswith("@@")


TWO_FILE_DIFF = """\
diff --git a/src/cli.py b/src/cli.py
index abc123..def456 100644
--- a/src/cli.py
+++ b/src/cli.py
@@ -15,3 +15,4 @@ def main():
     diff = get_diff()
+    print(diff)
     return
@@ -25,2 +26,3 @@ def helper():
     x = 1
+    y = 2
     return x
diff --git a/src/models.py b/src/models.py
index 111222..333444 100644
--- a/src/models.py
+++ b/src/models.py
@@ -1,3 +1,4 @@
+from dataclasses import dataclass
 
 class Hunk:
     pass"""


def test_parse_diff_two_files_multiple_hunks() -> None:
    """parse_diff handles multiple files and multiple hunks per file."""
    result = parse_diff(TWO_FILE_DIFF)

    assert len(result.files) == 2

    # first file: cli.py with two hunks
    assert result.files[0].path == "src/cli.py"
    assert len(result.files[0].hunks) == 2

    # second file: models.py with one hunk
    assert result.files[1].path == "src/models.py"
    assert len(result.files[1].hunks) == 1


def test_parse_diff_empty_string() -> None:
    """parse_diff returns an empty DiffResult for an empty diff."""
    result = parse_diff("")

    assert len(result.files) == 0
    assert result.raw_diff == ""
