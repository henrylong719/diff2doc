# diff2doc

> Turn git diffs into structured review briefs for humans.

**diff2doc** is a command-line tool for developers who use AI coding assistants
and find that reviewing the resulting diffs has become the new bottleneck. It
reads a git diff, groups the changes by logical intent, expands each hunk with
surrounding code context, and produces a markdown review brief that highlights
what changed, why, and what a careful reviewer should pay attention to.

It doesn't review your code for you. It helps you review it yourself — faster
and more reliably.

## Why

AI coding tools generate large volumes of code quickly, but this shifts the
bottleneck from writing to reviewing. A 500-line diff is cognitively expensive
to review well, and "skimming and hoping" is how bugs slip through. diff2doc
makes the reviewer's job easier by doing the grunt work of grouping, context
expansion, and risk-spotting — leaving the actual judgment to you.

## Status

Early development. Not yet on PyPI.
