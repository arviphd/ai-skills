# Simplify

**Tidy working code without changing what it does.**

Agent-written code often works but is longer and more tangled than it needs
to be. This skill makes small, local clean-ups (clearer names, simpler logic,
less duplication) while keeping every result, output format and error
behaviour exactly the same. It then runs the checks the project already has.
When in doubt it leaves the code alone rather than risk a change.

Available for: **Codex** ([`codex/`](codex/))

## Good for

- Cleaning up a long pandas or SQL-generating script after it works
- Making a notebook's helper functions readable for a colleague
- A final tidy-up after a feature is built

It is not for adding features, fixing bugs, or large restructuring.

## How to use it

```text
Use $simplify on clean_sales.py and its tests. The output CSV must stay
exactly the same.
```

Without a target, it works on the code changed in the current task. The
[auto-review hook](../auto-review/) can run it automatically after every
coding turn.
