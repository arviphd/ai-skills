# Auto-review hook

**Get a review automatically after every coding turn.**

This is a small script that Codex runs at the start and end of each turn. If
the agent changed code during the turn, it asks Codex for one review pass that
checks correctness first and then runs [simplify](../simplify/). If only
documentation changed, it stays quiet.

Available for: **Codex** ([`codex/`](codex/)). It is a Codex lifecycle hook,
not a skill.

## Good for

- Making sure every change to your analysis or model code gets a second look,
  without having to ask for it each time

## Install

Requirements: macOS, Python 3, Git, and a Codex version that supports hooks.

```sh
mkdir -p "$HOME/.codex/hooks"
cp coding/auto-review/codex/auto-review.py "$HOME/.codex/hooks/auto-review.py"
cp coding/auto-review/codex/hooks.json "$HOME/.codex/hooks.json"
```

`hooks.json` is a complete example configuration and the last command
replaces any existing one. If you already use other hooks, merge its
`UserPromptSubmit` and `Stop` entries into your file by hand instead.

Then open `/hooks` in Codex and trust the new hook definition; Codex skips
hooks you haven't trusted. Install the [simplify](../simplify/) skill too,
since the review uses it.

## How it behaves

- At the start of a turn it records a small snapshot of the repository's Git
  state; at the end it compares.
- It only asks for a review when it is sure source or executable code changed,
  and it ignores documentation-only changes.
- If anything goes wrong inside the hook, it lets Codex finish normally rather
  than blocking.

## Settings

Optional environment variables:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `CODEX_AUTO_REVIEW_MAX_CANDIDATES` | `50` | Most changed paths considered in one turn |
| `CODEX_AUTO_REVIEW_MAX_FILE_BYTES` | `26214400` | Largest file the hook will inspect |
| `CODEX_AUTO_REVIEW_MAX_DISPLAY_PATHS` | `40` | Most changed paths listed in the review request |
| `CODEX_AUTO_REVIEW_STATE_TTL_DAYS` | `7` | Age after which old hook state is deleted |
| `CODEX_AUTO_REVIEW_STATE_DIR` | `~/Library/Caches/CodexAutoReview/state` | Where the hook keeps its temporary state |
