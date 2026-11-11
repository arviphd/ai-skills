# Review discipline

How to review a phase report so the gate means something. The executor will report "PASS."
Your job is to make that word earn its place.

## The Iron Law: evidence before claims

No status is real until you've seen the evidence for it *in this review*. The executor's "PASS"
is a claim, not proof; the solver's exit code, the recomputed objective, the validator's issue
count are proof. Confidence — yours or the executor's — is not evidence. Before accepting a phase
as done, name the command or check that proves each claim and confirm you've actually seen its
output this pass. The rationalizations are subtle because they sound reasonable:

| Rationalization | Reality |
|---|---|
| "The executor reported success." | Verify independently — read the diff / rerun the check yourself. |
| "Recompute matched last phase, so it's fine now." | Re-read *this* phase's recompute==UB with the delta magnitude. |
| "Requirements met — the gate passed." | Gate criteria are a checklist; walk it line by line, don't extrapolate from one green. |
| "The objective looks right." | "Looks right" is not the zero-confound anchor. Hit the anchor. |
| "Tiny change, no need to re-run." | Small diffs flip signs and bounds. Re-run. |
| "I'm confident." | Confidence isn't evidence. Point at the output. |

Different wording doesn't exempt a claim — "seems converged," "should be fine," and "done" all
demand the same evidence.

## The core move: verify the crux independently

Each phase has one thing that most needs to be true — the claim that, if wrong, makes the
phase worthless. Find it and prove it *yourself*, from first principles, not by re-reading
the executor's explanation.

- If it's a count, re-derive the count with your own formula and check it against theirs.
- If it's a tricky sequencing/timing/indexing behavior, hand-trace one concrete case
  end to end.
- If it's an equivalence, confirm the two things match *exactly* (bit-identical) where
  theory says they must, not merely "close."
- If it's an arithmetic identity (a recomputed value equalling a reported one), check the
  delta magnitude — `1e-10` is floating-point noise; `1e-3` is a real discrepancy wearing
  a small number.

An independent re-derivation that agrees is worth far more than a careful reading of a
claim. When it disagrees, you've caught something the gate would have waved through.

## Force what the normal path dodges

The most dangerous unverified code is the branch the happy path avoids. Optimizers skip
costly transitions; defaults skip error handling; typical inputs skip edge cases. A gate
that only ran the normal path has *vacuously* passed the assertions guarding those
branches. Before signing off, ask: which branch did this phase build that the test run
never actually exercised? Then force it with a fixture (see
`phase-decomposition.md` → Fixtures), or explicitly carry it forward as "built but
unexercised" to be closed in a later phase — and track that debt.

## Know your expected divergences

Before you call a changed number a regression, enumerate the effects that can *legitimately*
move it and which direction each pushes:

- **Documented modelling choices / biases** (a deliberate relaxation, an approximation)
  shift results a known way — a shift in that direction is expected, not a bug.
- **Discretization / quantization** rounds things; finer settings should improve
  monotonically, and a violation may be a quantization artifact rather than a defect —
  investigate before concluding.
- **A different tool or a longer run** can return a *better* result (a tighter incumbent,
  a closed gap). A value improving between phases can mean the earlier one was
  unconverged, not that something broke.

If two of your effects push opposite ways, "the numbers roughly agree" tells you little —
lean on the zero-confound anchor instead, where all of them are switched off.

## Separate the layers before touching code

When something fails, locate the layer first:

- **Environment / infrastructure** — a license expiry, a leaked token, a missing
  dependency, a full disk. Not a code bug. Diagnose and unblock the environment; do not
  churn source.
- **Tool-specific behavior** — a solver returning a sentinel, an API's off-by-one, a
  platform quirk. Fix at the boundary, and check whether the house convention (how the
  existing code already handles this tool) covers it before inventing a new approach.
- **Genuine code defect** — reproduce it, minimize it, fix it, and add an invariant so it
  can't silently return.

Conflating these wastes effort: patching correct code to work around an expired license,
or "fixing" a tool quirk in a way that diverges from how the rest of the codebase handles
it.

## When a phase fails: root cause before fix

A failed gate is a signal to investigate, not to patch. No fix until you can name the root
cause — a change that "makes the gate green" without explaining *why* it was red usually moves
the bug rather than removing it. This discipline matters most exactly when it's tempting to skip:
under time pressure, when a one-line fix looks obvious, or when two earlier fixes already didn't
hold. The order:

1. **Locate the layer** (above) — environment, tool-specific, or genuine code defect. A
   surprising fraction of "failures" are the first two and need no code change at all.
2. **Reproduce it minimally** — the smallest input/config that triggers it. A fixture that
   forces the failing case is worth building; it doubles as the regression guard.
3. **Explain the mechanism** in a sentence or two ("the no-incumbent best-bound is an off-basis
   sentinel"), and check it against how the rest of the codebase handles the same situation
   before inventing a new approach.
4. **Only then fix**, and record the hazard in INVARIANTS so a later `/clear` can't reintroduce
   it.

A wrong premise from you (the architect) is a common root cause. If the executor's investigation
contradicts your diagnosis, its evidence wins — an executor that root-causes past a bad prompt is
doing exactly the right thing, and following the prompt's wrong premise would have churned working
code.

## Correctness vs performance

Results (objectives, outputs, validation) are usually independent of which tool/solver/
backend produced them, so they're safe to verify anywhere, including on a stand-in.
Performance (timing, node counts, resource use) is *not* portable — hold those numbers for
the production toolchain and never let stand-in performance figures into a report that
implies production behavior.

## The go/no-go checklist

Before greenlighting the next phase:

- [ ] I re-derived the phase's crux independently and it agrees.
- [ ] Every branch this phase built was actually exercised — or the unexercised ones are
      tracked as explicit debt.
- [ ] Changed numbers are explained by a known effect (or investigated until they are).
- [ ] The gate's prior-phase regression still holds.
- [ ] Any new hazard is recorded in INVARIANTS, numbered, with symptom + resolution.
- [ ] Failures were attributed to the right layer (env / tool / code) and root-caused —
      mechanism named, not symptom-patched.
- [ ] Code and the three durable docs are committed together.

## Tone of review

Be the reviewer you'd want: precise, independent, and willing to say "this is correct and
here's my independent confirmation" as readily as "this is wrong." When the executor
corrects a wrong premise you gave it, say so plainly — that's the loop working, and
rewarding it keeps the executor investigating rather than complying. Own your own misses
without over-apologizing; accountability keeps the review trustworthy.
