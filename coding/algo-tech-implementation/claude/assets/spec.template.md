# {Feature} — Implementation Spec

The single source of truth for *what* is being built. Reviewed and de-bloated before phase 0.
Everything (INVARIANTS, phase prompts) points back here. When a fact changes, change it here —
in exactly one place — and re-point, don't restate.

## Context
{What this is, where it slots into the existing system, and the one-line goal. Link the
entry point / dispatch / data the feature reuses.}

### Decisions locked with the user
<!-- The choices already made, each with its rationale, so they don't get relitigated
     mid-build. Flag any deliberate departure from a reference/prior art and why. -->
- {decision — rationale}
- {…}

### Key facts established during exploration
<!-- Ground truth about the existing code/data the implementation depends on: units,
     indexing conventions, where things live, sparsity, sentinels. The stuff that, if
     assumed wrong, plants a bug. Cite file:line where possible. -->
- {fact — citation}

### Tractability / risk
<!-- The main thing likely to be hard (scale, performance, a dense structure). Size it,
     and note the mitigation baked into the plan. -->
- {risk — size — mitigation}

## Approach
{The build, in enough detail that each piece maps to a phase. Describe variables/state,
the core logic/constraints, the objective/output, and how it's driven. Point to reference
code to mirror rather than re-deriving conventions.}

## Verification
<!-- The checks that prove it works, numbered so phases can reference them. Include the
     zero-confound anchor (the input where the feature must match a reference exactly) and
     the forced-case fixtures. -->
1. {check}
2. {…}

## Wiring edits
<!-- Every touch-point outside the feature's own file: config registration, dispatch,
     build script, shared writers/guards. This is where cross-cutting landmines live —
     be exhaustive. -->
- {file:location — edit}

## Addendum / open decisions
<!-- Anything deliberately deferred, with the options and the (recorded) decision, so a
     later reader knows it was a choice, not an oversight. -->
