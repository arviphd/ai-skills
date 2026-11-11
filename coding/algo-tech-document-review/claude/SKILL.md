---
name: algo-tech-document-review
description: >-
  Structured multi-pass review of a technical plan, spec, design doc, or mathematical
  formulation — often algorithm/optimization-heavy, often drafted by another agent — to
  validate it for correctness, internal consistency, and gaps BEFORE any code is written. The
  loop: correctness sweeps interleaved with clarifying questions (open decisions, missing
  info) → de-bloat → integrity re-check → round-trip to the author/agent for sign-off → iterate.
  Use whenever the user shares a plan/spec/design/formulation and wants it reviewed, checked for
  gaps or correctness, tightened, or validated before building — e.g. "review this plan", "check
  my spec for gaps", "is this design correct", "my agent generated this, sanity-check it", or
  pasting a design doc expecting scrutiny. The subject is always a DOCUMENT, never source code:
  not for reviewing pull requests or code (ordinary code review), nor a phase/progress
  report during an active build (that is algo-tech-implementation, which this hands off to once
  the doc is validated).
---

# Algo/Tech Document Review

A structured loop for validating a technical document — an implementation plan, a formulation,
a design spec, often drafted by another agent — *before* it drives any code. A wrong or
self-contradictory plan is a bug generator: whoever implements it faithfully implements the
wrong half, and the document is the cheapest place to catch that. The output — a doc that is
correct, consistent, tight, and gap-free, with its author's agreement — feeds
`algo-tech-implementation`.

## The loop

Run these in order — noting Passes 1 and 2 interleave (sweep → ask → re-sweep) — and iterate
the whole thing until it converges.

### Pass 1 — Correctness sweeps (interleaved with Pass 2)

Read adversarially. This is not a rubber stamp, and domain confidence is not a reason to skip
verification. For every claim, formula, index, unit, sentinel, boundary condition, and
assumption, ask: is it right, and is it consistent with the rest of the doc? Hunt for **gaps**
(missing cases, unhandled edges), **internal contradictions** (the multi-revision classic: a
stale line a later section already corrected), **unstated dependencies and assumptions**, and
**bug-planting instructions** (a wrong coefficient, an off-by-one, a mis-translated convention,
a sentinel read where it shouldn't be) — full checklist in `references/correctness-passes.md`.

Separate the layers as you go: "the underlying formulation is *assumed* correct" versus "here is
a concrete defect or gap in the doc." And separate **defects from decisions and unknowns** —
some issues are not errors but unstated *choices*, and some are **missing information** only the
author or human can supply (a data convention, an environment fact, a constraint the doc takes
for granted). Queue both as questions — never resolve them silently or fill the gap with an
invented assumption. Defects themselves split the same way: fix the **answer-independent** ones
on the spot; a fix that *hinges* on an open question waits for the answer rather than baking a
guess into the doc. And if an unknown blocks even completing the sweep, ask it immediately.

**The loop: sweep → ask → re-sweep, to convergence.** Ask after the first *full* sweep — not
before it (questions go out as one ranked batch, not a drip) and not after grinding further
(the highest-impact questions gate the fixes themselves; sweeps run on guessed answers converge
on the wrong doc). Concretely:

1. Sweep the whole doc; grade every finding (CRITICAL/HIGH/MEDIUM/LOW). Fix the
   answer-independent CRITICAL/HIGH defects; queue the decisions, unknowns, and
   answer-dependent fixes.
2. **Clarify checkpoint** — run Pass 2 on the queue, then **STOP: end the turn and wait for the
   answers.** Do not proceed to further sweeps or later passes while checkpoint questions are
   open. If the sweep queued nothing, skip the checkpoint and sweep again immediately; don't
   manufacture questions.
3. When the answers come back, apply the deferred fixes, then **re-sweep incrementally**: full
   depth on everything the fixes and answers touched plus whatever references or depends on it,
   and a lighter cross-consistency scan over the rest — the first sweep is the only one that
   must be uniformly deep. If the footprint is large or the dependencies are tangled, fall back
   to a full re-sweep. Each sweep ends with its own checkpoint if it queued anything new.
4. Repeat until a re-sweep surfaces **no new CRITICAL or HIGH** finding and no new questions.
   (The de-bloat pass that follows reads the whole doc anyway, backstopping anything an
   incremental sweep missed.)

Bound it: **cap at ~4 sweeps.** If you're still turning up CRITICAL/HIGH findings at the cap,
stop looping and report that the doc needs deeper rework (a structural problem, not a polish
problem). MEDIUM/LOW items never warrant another sweep — batch them per Edit economy below.

### Pass 2 — Clarify: the question checkpoint

Runs at the end of every sweep that queued anything (and immediately, mid-sweep, for a blocking
unknown) — not once at the end of all sweeping. **A checkpoint is a full stop, not a report
section:** present the questions and end the turn. An "open questions" list at the tail of a
completed review — after de-bloat and sign-off — is the anti-pattern this pass exists to
prevent. Address the checkpoint to the human driving the
review; the drafting author/agent gets its say at the round-trip (Pass 5). The queue holds two
kinds of questions: **decisions** (unstated *choices* that need an owner's call) and **unknowns**
(missing information you cannot derive from the doc — context, conventions, constraints, facts
about the data or target environment). Resolve each batch in a bounded, structured way rather
than an open-ended back-and-forth:

- **Apply the ask-bar first.** A question must earn its hand-back on two counts: the answer is
  *genuinely uncertain* (a real trade-off or a fact you cannot derive) AND it changes what gets
  built or how it's validated. A clear defect with a clear fix is never a question — fix it. A
  "decision" where one option clearly dominates isn't one either — apply the dominant option,
  record it in the decision log, and flag it at the round-trip instead of asking. Never ask to
  appear thorough or to offload a call you can own; the round-trip already gives the author
  veto over everything. If nothing survives the bar, there is no checkpoint — resume sweeping.
- **Queue and rank** the survivors by *impact × uncertainty* — how much the answer changes
  the implementation, times how unresolved it is. Ask at most ~5 per checkpoint; defer the
  tail to the build.
- **Ask one at a time.** For a *decision*, frame it as a small set of mutually-exclusive options
  (2–5) and lead with a **recommended option and one or two sentences of why** — they can
  accept the recommendation or override it. For an *unknown*, there may be nothing to recommend:
  ask crisply for the fact, and say in one line why the answer matters (what it changes
  downstream).
- **Record each resolution in the doc** (a short "Decisions"/"Clarifications" entry with the
  question and the answer) so it isn't relitigated during the build.

### Pass 3 — De-bloat

Multi-revision docs accrete redundancy and, worse, contradictions. Make one pass so that each
fact lives in exactly one canonical place, with pointers (not restatements) elsewhere, and no
section contradicts another. Preserve the author's exact wording where it is load-bearing;
you're removing duplication and drift, not rewriting voice. This is a correctness activity, not
just cosmetics — an internally inconsistent doc plants bugs.

### Pass 4 — Integrity re-check

A focused pass confirming the de-bloat didn't drop or corrupt anything: cross-references still
resolve, no fact was silently lost, numbering/labels are consistent, nothing dangles. Cleanup
is itself a change that can introduce errors — verify it the way you'd verify any edit.

### Pass 5 — Round-trip to the author

Hand back a pointer to the updated doc plus a summary of what you found and changed — not the
full text re-pasted — framed as "here's what I flagged and why; do you agree, and does this
miss anything?" The originating author has context you don't: a rationale behind a line you
trimmed, a constraint you didn't know about. Iterate on their response — accept, push back, or
adjust — and never impose changes unilaterally when an author is in the loop.

### Convergence

When the author/agent is satisfied and nothing CRITICAL or HIGH remains open, the doc is
validated. The deliverable is the tightened doc plus a short record of findings, de-bloat
changes, and decisions taken (see Disciplines) — the single source of truth feeding
`algo-tech-implementation`, which turns it into phased, gated code.

## Edit economy

Never *regenerate* the document. Wholesale rewrites are slow, and every regeneration is a fresh
chance to corrupt something untouched — manufacturing the very transcription drift Pass 4 hunts.

- **Edit in place.** A file gets targeted, surgical edits (the smallest snippet that uniquely
  locates the change). A doc pasted in chat gets findings as *before → after* patches — never
  a rewritten doc echoed back — applied once it's agreed where the canonical copy lives.
- **Batch the cheap fixes.** MEDIUM/LOW items: apply the trivially safe ones alongside the
  sweep that found them, fold the rest into de-bloat, list whatever remains.
- **De-bloat by deletion, not rewrite.** Delete duplicates, leave pointers — canonical text
  survives verbatim. This also scopes Pass 4 to the de-bloat's footprint plus cross-references
  into it, not a full re-verification.
- **One findings report.** Keep a running log; per-sweep output is just new findings plus the
  question batch. The full templated report is assembled once, at the round-trip.
- **Right-size the depth.** A two-page prompt spec may converge in one sweep, one checkpoint,
  and a light tighten. The passes are the checklist; depth scales with size and blast radius.

## Disciplines

- **Adversarial but fair; never rubber-stamp.** A plan that "looks right" hasn't been reviewed —
  re-derive the load-bearing claims yourself. Argue the strongest case for a claim before
  rejecting it; report concrete gaps, not vibes.
- **Fix what you can own; ask what you can't — after one full sweep.** Clear fixes and
  dominated choices are applied and logged; genuine trade-offs and underivable facts become the
  question batch — ranked, capped — at the end of the sweep that found them. Never fix on a
  guessed answer, never drip questions, never hand back bare.
- **Grade every finding** so the go/no-go is unambiguous: CRITICAL (silently corrupts results
  or makes the build infeasible as written) → HIGH (real defect, conflicting requirement, or
  untestable criterion) → MEDIUM (terminology drift, underspecified edge) → LOW (wording).
- **Each fact once; don't corrupt in cleanup.** Passes 3 and 4 are a matched pair — tighten,
  then verify the tightening.
- **Round-trip, don't overwrite.** The author has context. Propose and confirm; iterate.
- **Keep a decision record.** Questions, their resolutions, and dominance-resolved choices go
  somewhere durable in the doc, so nothing is relitigated during the build.

## Files in this skill

- `references/correctness-passes.md` — what to hunt for in an algo/optimization/technical spec.
- `assets/review-findings.template.md` — how to structure findings and the round-trip message.
