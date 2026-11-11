---
name: algo-tech-implementation
description: >-
  Methodology for building a substantial, high-risk, or multi-phase code feature from an
  already-validated spec as reviewed, gated phases driven through an executor agent (e.g. Claude
  Code), on a feature branch, with durable on-disk state (spec + invariants + progress) that
  survives context clears. The ritual: branch first → per phase, execute one scoped phase, gate
  it, review it, commit code+docs, then /clear before the next → merge to main after a final
  integration gate. Use whenever the user wants to plan or run a multi-phase/staged build, drive
  Claude Code through a phased rollout, set up a phase-by-phase review loop, review a PHASE or
  PROGRESS report from an active build and decide go/no-go, or write the next phase's prompt —
  e.g. "do this in phases", "stage this build", "here's the Phase 3 gate report". For
  substantial or risky work only — skip small one-shot changes. Reviewing a PRE-build plan/spec
  not yet validated is algo-tech-document-review, not this; this takes over once that spec is
  signed off.
---

# Algo/Tech Implementation

Land a big or bug-prone feature safely from a validated spec: decompose it into ordered phases,
drive an executor agent (usually Claude Code, in the repo) through them one at a time on a
feature branch, and gate each phase on independent review. Durable state lives on disk so the
executor's context can be cleared between phases without losing anything. Two roles: **you (the
architect)** own the phase plan, the reviews, and the go/no-go calls; **the executor** does one
scoped phase per prompt and stops at a gate. This skill is written for the architect.

## Preconditions

Start from a **validated spec** — `algo-tech-document-review` produces exactly this; phasing an
unreviewed plan means the executor faithfully implements the wrong half. Use the method only for
changes big enough that one-shotting is risky (a new subsystem, a cross-cutting refactor, many
interacting invariants); for a small self-contained change, skip the ceremony.

## The durable files

The validated **spec** (`<feature>_plan.md`) is the source of truth. Before the first executor
phase, create two more files (templates in `assets/`) — the memory that survives a `/clear`:

- **INVARIANTS** (`INVARIANTS_<feature>.md`) — numbered cross-phase rules: correctness laws,
  wiring hazards, deliberate spec departures. Landmines found mid-build get appended here so
  the next `/clear` carries them forward; reference the numbers in prompts.
- **PROGRESS** (`PROGRESS_<feature>.md`) — phase checklist plus, per phase, what was built,
  files touched, gate result, new invariants. The executor appends; you read it to review.

Commit code and these files together, in lockstep, or a re-prime reads state that doesn't
match the tree.

## The ritual

```
0. Setup: create a feature branch — never build multi-phase work on main; the
   branch is what lets you abandon or rewrite a phase without contaminating it.
   Executor verifies the folder structure the spec assumes (src/module dirs,
   output/log paths, test-fixture data dirs); if anything is missing, it lists
   exactly what it would create and gets the user's OK BEFORE creating anything
   — never silently scaffold directories.
1. Write the phase plan from the validated spec.
2. Per phase:
     a. /clear (or a fresh executor session)
     b. paste the phase prompt — it re-primes from spec + INVARIANTS + PROGRESS
     c. executor does ONE scoped phase, stops at its sign-off gate
     d. executor reports (terminal PHASE REPORT block; PROGRESS updated on disk)
     e. YOU review — verify the crux independently, record new landmines in
        INVARIANTS, decide go/no-go
     f. COMMIT (code + durable docs together; build phases — experiments follow
        "Commit discipline")  ── then ──  /clear → next phase
3. Final integration gate (end-to-end on the production toolchain).
4. Merge to main.
```

Merge only after the integration gate: if correctness phases ran on a stand-in (a different
solver, a mock, a dev path), the feature must run end-to-end on the *production* toolchain at
least once before merging — compile-checked ≠ run. Exception: a fully opt-in feature whose
shared-file edits are proven inert for existing code may merge early, when branch longevity
against active work becomes the bigger cost.

## Commit discipline

- **Build phases**: commit-on-green — the gate passes, your review clears it, commit code + the
  durable docs in one commit, then `/clear`. Each commit is a known-good revertible checkpoint;
  don't stack phases as uncommitted working-tree changes.
- **Experiments / probes**: the executor runs, gates, reports — and **stops uncommitted**, with
  a diff summary (files touched, line counts). Commit / revert / discard is the architect's call
  *after* seeing the verdict; a negative result usually means revert the code, keep the finding.
- **Read-only diagnostics**: usually discard the probe code entirely — the finding is the
  artifact.

The principle: **separate the finding from the code.** A reverted experiment still gets its
PROGRESS writeup; the knowledge is committed even when the code is not.

## Decomposing into phases

Order phases to surface bugs on the smallest surface area, earliest: (1) scaffolding/wiring
with no logic — isolates config/dispatch/memory landmines; (2) the smallest verifiable core,
then complexity-increasing layers, each with a gate-able artifact; (3) output/robustness;
(4) scale-up and validation last. Each phase must be independently verifiable with a hard gate
and small enough to check its crux by hand. Full heuristics in
`references/phase-decomposition.md`.

## The per-phase prompt

Same shape every time (template in `assets/phase-prompt.template.md`): **goal** → **re-prime**
(spec sections, INVARIANTS #n, PROGRESS) → **do** (scoped; point to spec sections, don't
restate them) → **do NOT** (out of scope this phase) → **honor INVARIANTS #…** → **code style**
(standing line) → **self-review before running** → **sign-off gate** (concrete pass criteria +
a prior-phase regression check) → **finish** (update PROGRESS, append new invariants, an
explicit COMMIT POLICY line per "Commit discipline", **STOP — do not start the next phase**,
end with the PHASE REPORT block).

Two delivery rules, both about copy-paste fidelity:

- **Prompts out**: emit every finished executor prompt (phase, fix, re-prime) inside a single
  fenced code block, verbatim and self-contained — commentary goes outside the block, never
  interleaved. If the body itself contains a fenced block, use a four-backtick outer fence.
- **Reports back**: every prompt requires the executor to END its final message with a
  self-contained PHASE REPORT in a fenced block (skeleton in the template) that the user relays
  to the architect verbatim. Updating PROGRESS on disk is NOT a substitute — an executor that
  writes the file and ends with "done" leaves the architect blind.

## Executor self-review before running (mandatory when a phase writes real code)

Executors reliably introduce bugs when they write a non-trivial amount of code in one pass, and
the bug fires *during the run* — so the results are contaminated before you ever review.
Therefore: **before running any experiment, solve, or measurement, the executor performs an
independent code review of its own diff — and reports it — as a gate the run may not precede.**
Put this instruction in every phase prompt that writes more than a trivial change.

## Code style: plain code for a non-professional maintainer

The maintainer is a researcher, not a professional developer — the executor writes for that
reader. Names are plain full words (`total_dispatch_cost`) or an exact mirror of the spec's
math notation (`z_ils`, `tau_cell`) — never a third scheme. Control flow is simple and
explicit: no clever one-liners, dense comprehensions, macro tricks, or indirection where a
plain if/loop works; a little repetition beats an abstraction layer. Small single-purpose
functions; no new libraries or frameworks without asking. Comments explain *why* and map code
blocks to the spec's section and constraint numbers. Match the existing codebase's conventions.
Hard boundary: simplicity never overrides correctness or numerical determinism (floating-point
operation order, cut/callback ordering, counter placement) — flag the conflict instead of
resolving it silently. The template carries this as a standing line.

## Reviewing a phase (the crux)

Never take "PASS" on trust. Name the one thing that most needs to be true and verify it
*independently*: re-derive the number, hand-trace the tricky case. Force the case the normal
path dodges (a fixture that makes the happy path take the branch it avoids). Anchor on a
zero-confound case that must match a trusted reference exactly. Distinguish expected divergence
(a documented bias, quantization, a better incumbent) from genuine regression, and separate
environment/tool problems from code problems before touching source. When a gate fails,
root-cause before patching — name the mechanism, don't just turn the gate green. Full checklist
(plus the evidence-before-claims Iron Law) in `references/review-discipline.md`.

## Capturing landmines

Every non-obvious hazard a phase surfaces — a spec-vs-code inconsistency, an indexing
translation, a symbol collision, an ordering dependency, a fixture clash — is appended to
INVARIANTS immediately, numbered, with symptom and resolution. That's what stops a later
`/clear` from reintroducing a bug you already paid for.

## Honest correction

A prompt is a hypothesis, not an order. When the executor investigates a wrong premise you
handed it and corrects you instead of implementing the mistake, that is the system working —
acknowledge it plainly and update the shared understanding.

## Files in this skill

- `assets/INVARIANTS.template.md`, `assets/PROGRESS.template.md`,
  `assets/phase-prompt.template.md` — the durable-file and prompt templates.
- `assets/spec.template.md` — spec skeleton for when one isn't arriving validated from
  `algo-tech-document-review`.
- `references/phase-decomposition.md` — slicing a feature into gated phases.
- `references/review-discipline.md` — reviewing a phase report without trusting it.
