"""Stage 1: Extract diff information from git."""

import subprocess

from diff2doc.models import DiffResult, FileDiff, Hunk


def get_diff(git_range: str = "HEAD") -> str:
    """Run git diff and return the output as a string.

    Args:
        git_range: The git range to diff. Defaults to "HEAD",
            which shows unstaged changes against the last commit.

    Returns:
        The raw diff output from git.

    Raises:
        RuntimeError: If the git command fails.
    """
    result = subprocess.run(
        ["git", "diff", git_range],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip()}")

    return result.stdout


def _extract_path(diff_git_line: str) -> str:
    """Extract the file path from a 'diff --git' line."""
    return diff_git_line.split()[-1].removeprefix("b/")


def parse_diff(raw_diff: str) -> DiffResult:
    """Parse a raw git diff string into structured data.

    Args:
        raw_diff: The complete output of a git diff command.

    Returns:
        A DiffResult containing parsed files and hunks.
    """
    files: list[FileDiff] = []
    lines = raw_diff.splitlines()

    current_file_path: str | None = None
    current_hunks: list[Hunk] = []
    current_hunk_header: str | None = None
    current_hunk_lines: list[str] = []

    for line in lines:
        if line.startswith("diff --git"):
            # save the previous hunk if one exists
            if current_hunk_header is not None:
                current_hunks.append(
                    Hunk(
                        header=current_hunk_header,
                        content="\n".join(current_hunk_lines),
                    )
                )
            # save the previous file if one exists
            if current_file_path is not None:
                files.append(FileDiff(path=current_file_path, hunks=current_hunks))

            # start a new file
            current_file_path = _extract_path(line)
            current_hunks = []
            current_hunk_header = None
            current_hunk_lines = []

        elif line.startswith("@@"):
            # save the previous hunk if one exists
            if current_hunk_header is not None:
                current_hunks.append(
                    Hunk(
                        header=current_hunk_header,
                        content="\n".join(current_hunk_lines),
                    )
                )
            # start a new hunk
            current_hunk_header = line
            current_hunk_lines = []

        else:
            current_hunk_lines.append(line)

    # save the final hunk and file
    if current_hunk_header is not None:
        current_hunks.append(
            Hunk(
                header=current_hunk_header,
                content="\n".join(current_hunk_lines),
            )
        )
    if current_file_path is not None:
        files.append(
            FileDiff(
                path=current_file_path,
                hunks=current_hunks,
            )
        )

    return DiffResult(files=files, raw_diff=raw_diff)
