"""Stage 1: Extract diff information from git."""

import subprocess


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