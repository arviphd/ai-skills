# Peer review

**Get a second, independent opinion from another AI.**

One agent reviewing its own work tends to miss the same things twice. This
skill sets up a structured review between two agents: Codex reviews and makes
focused fixes, while a second reviewer (Claude, Gemini, or another Codex agent)
challenges the work without editing it. They go back and forth until both
agree the work is right, or until they report a clear disagreement for you to
settle.

Available for: **Codex** ([`codex/`](codex/)), with Claude, Gemini or Codex as
the second reviewer.

## Good for

- Checking a SQL query, notebook or analysis script before results go out
- Challenging a model write-up, methodology note or plan document
- High-stakes milestones in a larger build

## How to use it

With another Codex agent as the reviewer:

```text
Use $peer-review Codex to review analysis/attribution_model.py. Fix confirmed
problems, but don't change what the analysis is meant to do.
```

With Claude or Gemini as the reviewer:

```text
Use $peer-review Claude to review docs/methodology.md.
```

## Requirements

- Claude or Gemini as reviewer needs that tool installed and available
  alongside Codex.
- When the reviewer can't talk to Codex directly, the two exchange findings
  through a shared Markdown file that records every finding and approval, so
  the review survives across turns. It's a working file, so keep it out of
  your project's git history (for example, add `*_Review_Handoff*.md` to
  `.gitignore`).
