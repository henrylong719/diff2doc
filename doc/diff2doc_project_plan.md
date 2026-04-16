# diff2doc

*A CLI Review Aid for AI-Generated Code Diffs*

Product Plan · v1.0 · April 2026

## Overview

| Field | Detail |
|-------|--------|
| Product | diff2doc — CLI tool that turns git diffs into structured review briefs |
| Owner | Engineering (solo build, week 1) |
| Target user | Developers using AI coding assistants who struggle to review large generated diffs |
| v1 timeline | 1 week build + 2 weeks real-world validation |
| v1 success | Feels more useful than raw diff on 80% of real PRs over 2-week trial |
| Status | Planning / pre-build |

## 1. Problem Statement

AI coding assistants generate large volumes of code quickly, but this shifts the bottleneck from writing to reviewing. Developers routinely face 300–1000 line diffs that are technically well-structured but cognitively opaque: it is hard to tell intent from implementation, hard to separate the main change from incidental refactors, and hard to know which parts deserve careful attention. Skimming replaces reviewing, and bugs slip through.

The pain is sharpest for solo developers and small teams without formal review processes — exactly the people most likely to use AI coding in the first place. Existing PR tools (CodeRabbit, PR-Agent, GitHub Copilot PR summaries) focus on automated review, which answers the wrong question. The unmet need is not "review this for me" but "help me see this change clearly so I can review it myself."

## 2. Solution Overview

diff2doc is a local command-line tool that ingests a git diff and outputs a markdown review brief designed for a human reviewer. It groups hunks by logical intent (not file location), expands each hunk with surrounding code context, and produces per-group notes covering intent, approach, cross-file connections, and risks to double-check.

The design principle is that the tool augments the reviewer rather than replaces them. Output is suggestive, not authoritative. The user remains the decision-maker; diff2doc just makes the decision cheaper.

## 3. Goals and Non-Goals

### In scope for v1

- Accept any git range (main...HEAD, HEAD~5..HEAD, --staged, specific commits)
- Produce a markdown review brief with TOC, logically grouped sections, and risk callouts
- Expand diff hunks with enclosing functions/classes and cross-reference callers
- Run locally as a single-user CLI on any git repository
- Support Python via AST and other languages via regex fallback

### Out of scope for v1

- Automated bug detection or style critique
- GitHub App, web UI, or IDE integration
- Multi-repo or team features
- Caching, persistent storage, or history
- Non-git VCS support

## 4. Target Users and Use Cases

The primary user is a developer who uses AI coding tools (Claude Code, Cursor, Copilot) and finds that reviewing generated diffs is the new bottleneck in their workflow. Secondary users are code reviewers on small teams who want a pre-digested view before opening a PR in GitHub.

### Core use cases

- **Pre-PR self-review:** Developer runs diff2doc on their feature branch before opening a PR to catch issues and produce a shareable review brief.
- **Pre-commit check:** Developer runs diff2doc --staged to sanity-check a large AI-generated change before committing.
- **Onboarding to unfamiliar changes:** Reviewer runs diff2doc on a teammate's branch to build a mental model faster than reading raw diff.

## 5. Technical Architecture

Five independent pipeline stages. Each stage is a pure function where possible, which matters because when output quality regresses you need to inspect stages in isolation.

| Stage | Name | Responsibility |
|-------|------|----------------|
| 1 | Diff Extraction | Shells out to git for diff, stat, and log. Returns structured hunks plus commit messages as intent signal. |
| 2 | Context Expansion | Parses hunks, reads current files, pulls enclosing function/class via Python ast or regex fallback. Runs git grep to find callers. |
| 3 | Grouping (LLM) | One Claude call that clusters hunks into 2–6 logical groups by intent. Returns validated JSON. |
| 4 | Explanation (LLM) | Parallel per-group Claude calls producing intent, annotated code, connections, and risks. |
| 5 | Rendering | Assembles markdown with TOC, sections, and incidental-changes appendix. Writes to stdout or file. |

### Tech stack

- **Language:** Python 3.11+ (built-in ast, mature Anthropic SDK)
- **CLI framework:** typer
- **Terminal UX:** rich for progress and formatted output
- **LLM:** Claude Sonnet as default (configurable via DIFF2DOC_MODEL env var)
- **Validation:** pydantic for stage 3 JSON schema
- **Config:** ~/.diff2doc/config.toml (API key, model, context lines, ignore list)

## 6. Milestones and Timeline

One week build, two weeks validation. Each day has a concrete, demoable deliverable.

| When | Milestone | Deliverable |
|------|-----------|-------------|
| Day 1 | Skeleton | Repo, pyproject.toml, typer CLI, stages 1+5 wired with no-op middle. Command runs end-to-end. |
| Day 2 | First LLM call | Monolithic stage 4 explaining whole diff with no grouping. Prompts externalized to files. |
| Day 3 | Context expansion | Stage 2 with Python AST and regex fallback. Re-run day-2 fixtures and note quality delta. |
| Day 4 | Grouping + parallelism | Stage 3 with pydantic-validated JSON. Stage 4 runs per-group in parallel via ThreadPoolExecutor. |
| Day 5 | Polish | --dry-run, --verbose with token/cost output, error messages, ignore list, README. |
| Days 6–12 | Real-world validation | Daily use on actual PRs. No new features. Log every failure mode for v2 planning. |
| Day 13 | v1 review | Decide: ship, iterate, or pivot based on the 80% usefulness bar. |

## 7. Success Metrics

### Primary metric

Subjective usefulness: across a 2-week trial on real PRs, the generated review brief feels more useful than the raw diff on ≥80% of invocations. Tracked via a daily log kept by the builder during validation.

### Secondary metrics

- **Latency:** End-to-end runtime under 30 seconds for diffs up to 500 lines.
- **Cost:** Median cost per run under $0.10 on default model.
- **Reliability:** Graceful handling of all common failure modes (empty diff, not-a-repo, rate limit, context overflow).
- **Adoption signal:** Builder runs it voluntarily — without a reminder — on ≥70% of their own PRs during validation.

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Context window overflow on large diffs | High | Process groups separately; warn and truncate with a note if a single group exceeds limit. |
| Generated file noise (lockfiles, migrations) | Medium | Ship default ignore list in config; easy to extend per-repo. |
| LLM hallucinates cross-file connections | Medium | Stage 2 context expansion grounds the model; phrase prompts so output is suggestive, not authoritative. |
| Cost creep from frequent runs | Low | Print token + cost estimate after every run; prominent --dry-run; default to cheaper model. |
| Prompt drift during iteration | Medium | Maintain golden set of 5–10 diffs; re-run whenever prompts change meaningfully. |
| Quality bar not met after 2 weeks | Medium | Kill criterion built in — pivot to different framing (e.g. IDE-integrated, review-focused) or shelve. |

## 9. Open Questions

- Should commit messages be trusted as intent signal, or are they too unreliable in AI-assisted workflows?
- Is grouping by intent worth the extra LLM call, or does a single well-prompted call suffice on typical diffs?
- How should diff2doc handle binary files, renames, and deletions — ignore, summarize, or full treatment?
- Should the tool expose a --style flag (terse / thorough / teaching) or pick one opinionated voice?

## 10. Post-v1 Candidates

Decide after validation, not before. Candidates are listed without priority because the validation notes will determine the right order.

- GitHub Action that posts the review brief as a PR comment
- VS Code extension triggered from the source control panel
- Multi-language AST support via tree-sitter
- Caching layer keyed on diff hash for free re-runs
- HTML renderer with syntax highlighting and collapsible sections
- Team config with shared ignore lists and prompt overrides

## 11. Definition of Done

v1 ships when, on a real feature branch run against diff2doc itself, the command completes in under 30 seconds, produces a markdown review brief the builder reads end-to-end without skipping, and feels more useful than git diff alone. This bar must hold on ≥80% of real PRs across the 2-week validation period. If it does, v1 is done and v2 planning begins from the validation log. If it doesn't, the project is paused and reframed before any further investment.
