"""Stage 4: Generate per-group explanations using an LLM."""

from typing import Any, cast

import anthropic

from diff2doc.models import DiffResult

EXPLAIN_PROMPT = """\
You are a code review assistant. Below is a git diff.
Explain what this change does, covering:
- The intent: what is the developer trying to accomplish?
- The approach: how are they doing it?
- Risks: what should a reviewer double-check?

Keep your explanation concise and direct.

<diff>
{diff_text}
</diff>"""

DEFAULT_MODEL = "claude-sonnet-4-20250514"


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
    prompt = EXPLAIN_PROMPT.format(diff_text=diff_result.raw_diff)

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

    diff_result.explanation = _extract_text(message)

    return diff_result
