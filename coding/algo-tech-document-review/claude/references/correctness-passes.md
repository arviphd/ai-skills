# Correctness passes — what to hunt for

A checklist for the adversarial correctness pass over a technical/algorithm/optimization
document. Not exhaustive; a prompt for the categories of error that hide in specs and plant
bugs downstream.

## Conventions and units

- **Units.** Every quantity has units; every coefficient combines them. A cost that's
  per-hour used as per-unit, a rate multiplied where it shouldn't be — these read fine in
  prose and produce nonsense in code. Check that each product of terms has the units the
  result claims.
- **Indexing conventions.** 0-indexed vs 1-indexed, inclusive vs exclusive ranges, and any
  translation between a formulation's math (often 1-indexed) and the target code (often
  0-indexed). Off-by-one in a boundary or initial condition is the archetypal spec bug.
- **Sentinels and special values.** Values that mean "absent/infeasible/infinite" (a `9999`,
  a `-1`, a `±inf`). Where does the doc read one that should have been excluded? Where does a
  diagonal/identity/no-op case need to be hardcoded rather than read from data that may carry
  a sentinel?

## Completeness

- **Edge and boundary cases.** First/last element, empty set, single element, the horizon
  end, the zero case. Does the doc's logic hold there, or only in the interior?
- **Every case handled.** For each branch/type/mode the doc introduces, is the complementary
  case specified? (If it handles X, does it say what happens for not-X?)
- **Feasibility.** Is there always a valid choice available where the doc requires one? A
  constraint that becomes infeasible in a corner (e.g. at a boundary because a required
  enabling element was pruned) is a real defect.

## Consistency

- **Internal contradictions.** The multi-revision classic: one section states a rule, a later
  section (added in a revision) states its opposite, and both survive. Read cross-section, not
  just top-to-bottom.
- **Cross-references resolve.** Every "see section N", "as in X", "per the Y rule" points at
  something that exists and says what the reference implies.
- **Notation is stable.** The same symbol means the same thing throughout; a renamed variable
  is renamed everywhere.

## Correctness of the logic itself

- **Coefficients and directions.** Signs, inequality directions, which variable scales which
  term. A relaxation that's meant to bound from below actually does.
- **Reductions and equivalences.** Where the doc claims two forms coincide (a general form
  reducing to a special case), does the reduction actually hold — and is it worth flagging as
  a test anchor?
- **Assumptions made explicit.** Anything the logic relies on that isn't stated (an ordering,
  a non-negativity, a uniqueness). Name it so it becomes a checkable precondition.

## Defect vs. decision vs. unknown

Some "issues" aren't errors — they're unstated choices with real trade-offs (a modelling
relaxation, an approximation, a scope boundary, a default). For each, don't silently resolve
it: surface it to the human as a decision, with the options, a recommendation, and what each
side trades off. Record the resolution in the doc so it reads as a choice, not an oversight.
Apply the dominance test first, though: if one option clearly wins — no genuine trade-off —
it isn't a decision worth a hand-back. Apply it, log it, and flag it at the round-trip. A
question exists to extract something only the human has (a preference among real alternatives,
a fact you can't derive), never to demonstrate diligence or to offload a call the review can
own.

Others are **unknowns** — information the doc neither states nor lets you derive (which solver
build, whether the input data can carry sentinels, which indexing convention the downstream
code uses, what the data's actual scale is). Ask; don't assume. An assumption invented during
review reads exactly like a fact by the time it reaches the implementer — and it's the kind of
bug no correctness sweep will catch, because the doc will be internally consistent around it.
If an unknown blocks verification of a load-bearing claim, ask early rather than sweeping on a
guess.

## Downstream-impact framing

When you flag something, say what it costs if left: "this plants a feasibility bug at the
horizon end," "this makes the benchmark non-comparable," "this is cosmetic." Severity guides
where the author spends attention. Distinguish blocking defects (must fix before build) from
hardening (fold in) from questions (decisions the human picks; unknowns the human supplies).
