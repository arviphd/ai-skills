# Phase decomposition

How to slice a feature into phases that each gate cleanly and surface bugs early.

## The governing principle

Order phases so that a bug shows up on the **smallest possible surface area, as early as
possible**. Every phase you add before the logic is a phase in which a whole class of
failure can be attributed and killed in isolation. The cost of a bug is roughly the amount
of code you have to suspect when it appears — phasing shrinks that set.

## The canonical sequence

1. **Scaffolding / wiring — zero logic.**
   Get the feature to compile, parse its config, and dispatch end-to-end through a
   do-nothing stub. Nothing computes yet. What this flushes out: config-key registration
   quirks, dispatch/routing edits, memory-lifecycle setup (allocation and teardown paths,
   including error exits), symbol collisions, build-script edits, guards on shared code
   that the new path must not corrupt. These are the bugs that are murder to attribute
   once real logic is layered on top, so pay them down while the surface is empty.

2. **Smallest verifiable core.**
   The least amount of real logic that produces something checkable. Prefer a piece whose
   output you can count, enumerate, or hand-derive (sizes, shapes, a trivial instance)
   before anything that requires a full solve/run.

3. **Complexity- and feasibility-increasing layers.**
   Add capability in layers, each producing a gate-able artifact. A useful ordering trick:
   start from a *relaxation* (fewer constraints, easy to satisfy, easy to reason about),
   then tighten. Each layer's gate can compare against the looser layer below it (a
   monotonic relationship is a free correctness check).

4. **Output / robustness.**
   The artifacts the feature must emit and the edge/error paths: empty results, failure
   modes, teardown on *every* exit path, schema/format alignment with existing consumers.
   Often much of this got built incrementally in earlier phases — scope this phase to
   what's genuinely left rather than redoing it.

5. **Scale-up and validation — last, behind its own gate.**
   The expensive, environment-dependent, or reference-grade checks: full-size runs,
   performance/benchmark numbers, cross-checks against a trusted implementation. Keep these
   *out* of the correctness phases so an environment problem (a license, a slow run) never
   blocks correctness progress. If some of these need a production toolchain you don't have
   yet, mark them explicitly deferred and gate them separately.

## Sizing a phase

- **Every phase needs a hard, concrete gate.** If you can't write down checkable pass
  criteria, the phase is under-specified — usually because it's too big. Split it.
- **Small enough to hand-verify the crux.** If reviewing the phase would require trusting
  the executor because you can't independently check the key claim, shrink it.
- **One conceptual thing per phase.** "Add per-SKU changeovers" is a phase; "add
  changeovers and family aggregation and the output writer" is three.
- **Prior-phase regression in every gate.** Each gate re-confirms the earlier phases still
  hold (a cheap check that the new layer didn't disturb the old).

## Fixtures: build the cases reality won't hand you

Two fixture types repeatedly earn their keep:

- **Forced-case fixtures.** The normal path — an optimizer, a happy path, a default
  config — actively avoids the transitions and branches most likely to hide a bug (they
  cost money, they're the error path, they're rare). Construct a tiny instance that
  *forces* the case: two things that must share a resource, a limit tight enough to trigger
  the no-result path, an input that must take the branch. Pair it with a fixture proving
  the *adjacent* case is correctly rejected (the "off-by-one is infeasible" probe).

- **Zero-confound anchors.** Find or synthesize the one input where every source of
  *expected* divergence from a trusted reference switches off at once — no approximation,
  no documented bias, no tool difference. On that input the feature must match the
  reference *exactly*, to the digit. This is the strongest correctness statement available
  and worth building deliberately; "roughly agrees" checks never reach it.

Name fixtures so they can't collide with fixtures from other efforts in the same repo, and
record what each one proves (in INVARIANTS or alongside the fixture).

## Anti-patterns

- A phase with no independent gate ("looks right").
- A first phase that already contains real logic (wiring bugs and logic bugs entangle).
- Deferring all validation to a single giant final phase (bugs surface far from their
  cause).
- Letting expensive/environment-dependent checks block correctness phases.
- Phases so large the review step degenerates into trusting the executor's summary.
