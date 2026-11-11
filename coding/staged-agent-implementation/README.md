# Staged implementation

**Build something substantial one checked stage at a time.**

Instead of writing a whole pipeline in one go, Codex splits an agreed plan
into stages and builds one stage at a time. Each stage goes to a fresh helper
agent, gets checked against the plan, and is recorded in a short progress file.
Then Codex stops and waits for your go-ahead before the next stage. You stay in
control, and problems surface while they are still small.

Available for: **Codex** ([`codex/`](codex/)). For the Claude equivalent, see
[phased build](../algo-tech-implementation/).

## Good for

- Building a model end to end: data preparation, features, training, evaluation
- Adding a large piece to an existing analysis codebase without breaking it
- Any change big enough that you'd want to review it in pieces

Small, self-contained changes don't need this; just ask for them directly.

## How to use it

```text
Use $staged-agent-implementation to build docs/plans/churn_model.md one stage
at a time. Show me the stage breakdown and wait for my approval before Stage 1.
```

After reviewing each stage:

```text
Proceed with Stage 2.
```

The plan should already be agreed, for example with
[feature planning](../feature-planning/). This skill builds the plan; it
doesn't redesign it.
