"""Stage 4: Generate per-group explanations using an LLM."""

import anthropic

from diff2doc.models import DiffResult, FileDiff

EXPLAIN_PROMPT = """\
You are a code review assistant. Below is a diff for a single file: {file_path}
Explain what this change does, covering:
- The intent: what is the developer trying to accomplish?
- The approach: how are they doing it?
- Risks: what should a reviewer double-check?
 
Keep your explanation concise and direct.
 
<diff>
{diff_text}
</diff>"""

DEFAULT_MODEL = "claude-sonnet-4-20250514"

MIN_CHANGED_LINES = 4


def _count_changed_lines(file_diff: FileDiff) -> int:
    """Count the number of added or removed lines in a file diff."""
    count = 0
    for hunk in file_diff.hunks:
        for line in hunk.content.splitlines():
            if line.startswith("+") or line.startswith("-"):
                count += 1

    return count


def _extract_text(message: anthropic.types.Message) -> str:
    """Return the concatenated text content from an Anthropic message."""

    text_parts = [
        getattr(block, "text", "")
        for block in message.content
        if getattr(block, "type", None) == "text"
    ]
    if not text_parts:
        raise RuntimeError("Anthropic returned no text content.")
    return "\n".join(text_parts)


def explain_groups(diff_result: DiffResult) -> DiffResult:
    """Send the diff to Claude and get an explanation.

    Args:
        diff_result: The parsed diff data.

    Returns:
        The same DiffResult with the explanation field filled in.

    Raises:
        RuntimeError: If the API call fails.
    """

    client = anthropic.Anthropic()

    for file_diff in diff_result.files:
        if _count_changed_lines(file_diff) < MIN_CHANGED_LINES:
            continue

        hunks_text = "\n".join(
            f"{hunk.header}\n{hunk.content}" for hunk in file_diff.hunks
        )

        prompt = EXPLAIN_PROMPT.format(
            file_path=file_diff.path,
            diff_text=hunks_text,
        )

        try:
            message = client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

        except anthropic.APIConnectionError:
            raise RuntimeError("Could not connect to the Anthropic API.")
        except anthropic.AuthenticationError:
            raise RuntimeError(
                "Invalid API key. Set ANTHROPIC_API_KEY in your environment."
            )
        except anthropic.RateLimitError:
            raise RuntimeError("Rate limited by the Anthropic API. Try again shortly.")

        file_diff.explanation = _extract_text(message)

    return diff_result
