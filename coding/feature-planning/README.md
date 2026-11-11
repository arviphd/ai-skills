# Feature planning

**Think a project through with the agent before any code is written.**

Agents like to jump straight into building. This skill makes Codex slow down:
it first assesses the idea against your actual code and data, talks through
the important design choices with you, and only writes a plan when you ask for
one. It then reviews that plan for correctness and for scope creep, so the plan
you end up with does what you agreed and nothing more.

Available for: **Codex** ([`codex/`](codex/))

## Good for

- Deciding how a forecasting or reporting pipeline should be structured before building it
- Working out what a new model feature or data source would change in an existing project
- Turning a rough idea into a plan another person (or agent) can implement

## How to use it

Start by asking for an assessment, not a plan:

```text
Use $feature-planning to assess adding weekly seasonality to our demand
forecast. Discuss the options and trade-offs with me first; don't write the
plan yet.
```

Once the important choices are settled:

```text
Write the plan now and save it as docs/plans/seasonality.md.
```

The skill keeps every decision you agreed on, produces one plan file, and runs
focused review passes on it until it settles.

## Next step

Build the plan with [staged implementation](../staged-agent-implementation/),
or have it challenged first with [peer review](../peer-review/).
