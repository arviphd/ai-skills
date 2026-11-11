# Phased build from a validated spec

**Implement a reviewed spec in phases, with readable code you can maintain.**

For anything big or easy to get subtly wrong, this skill has Claude act as the
architect while an executor agent (usually Claude Code) does the coding. The
work is split into ordered phases. Each phase is built, checked at a gate,
reviewed, and committed before the next one starts. The spec, a list of rules
that must never be broken, and a progress log are kept as files, so nothing is
lost when the agent's memory is cleared between phases.

The code is written for a researcher or analyst to maintain, not a
professional developer: plain names that mirror the spec's notation, simple
control flow, and comments that point back to the spec's equations.

Available for: **Claude** ([`claude/`](claude/)). The skill's internal name is
`algo-tech-implementation`. For the Codex equivalent, see
[staged implementation](../staged-agent-implementation/).

## Good for

- Implementing an optimization model, heuristic or decomposition method from a
  written formulation
- Building a multi-step analytics pipeline where each step must be verified
- Large changes to an existing model codebase with many interacting rules

Skip it for small, one-off changes.

## How to use it

Start from a reviewed spec (see
[spec and formulation review](../algo-tech-document-review/)), then:

```text
Let's build docs/allocation_plan.md in phases. Propose the phase breakdown
and write the prompt for Phase 1.
```

After the executor reports back:

```text
Here's the Phase 2 gate report. Review it and tell me if we can go on.
```

## What's included

- `references/`: how to split work into phases and how to review each one
- `assets/`: templates for the spec, the rules file, the progress log and the
  per-phase prompt
