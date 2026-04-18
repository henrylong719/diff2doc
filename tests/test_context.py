from diff2doc.context import _find_enclosing_scope, _parse_hunk_start_line


def test_find_enclosing_scope_finds_function() -> None:
    """_find_enclosing_scope returns the function containing the line."""
    source = """\
	class Dog:
		def bark(self):
			print("woof")

		def fetch(self):
			print("fetching")
	"""

    # Line 3 is print("woof"), inside bark
    assert _find_enclosing_scope(source, 3) == "bark"


def test_find_enclosing_scope_returns_none_at_module_level() -> None:
    """_find_enclosing_scope returns None for top-level code."""
    source = """\
        import os

        x = 1
    """
    # Line 3 is x = 1, not inside any function or class
    assert _find_enclosing_scope(source, 3) is None


def test_parse_hunk_start_line_extracts_line_number() -> None:
    """_parse_hunk_start_line pulls the new-file start line from a header."""
    assert _parse_hunk_start_line("@@ -15,3 +15,4 @@ def main():") == 15
    assert _parse_hunk_start_line("@@ -1,5 +1,8 @@") == 1


def test_parse_hunk_start_line_returns_none_for_bad_header() -> None:
    """_parse_hunk_start_line returns None for unparseable headers."""
    assert _parse_hunk_start_line("not a header") is None
    assert _parse_hunk_start_line("") is None
