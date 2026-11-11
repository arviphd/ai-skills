# INVARIANTS — {Feature}
Cross-phase rules. Violating any is a defect regardless of phase. Re-read before every phase.
Number them; reference the numbers in phase prompts. Append new hazards as they surface —
this file growing over the build is the method working.

## CORRECTNESS
<!-- Laws the model/logic must obey in every phase. Each: the rule, and *why* (so a
     future re-prime doesn't "simplify" it away). Record any spec-vs-implementation
     correction here the moment it's found, with the wrong version flagged. -->
1. {rule — and the reason it holds / the trap it avoids}
2. {…}

## WIRING
<!-- Config, dispatch, memory-lifecycle, and shared-code rules. The plumbing that, if
     wrong, fails in ways that are hard to attribute. -->
6. {rule}
7. {…}

## WIRING LANDMINES FOUND MID-BUILD (additive — keep honouring)
<!-- Hazards discovered during a phase: symbol collisions, ordering dependencies,
     parser quirks, platform/tool sentinels. Symptom + resolution, so the next /clear
     can't reintroduce them. Tag with the phase found. -->
W1. {symptom → resolution}
W2. {…}

## DELIBERATE DEPARTURES (matches {reference}; differs from the {spec} on purpose)
<!-- Places where the implementation intentionally diverges from the spec or the
     reference, with the reason. These are the "expected divergences" the reviewer must
     know before calling a number a regression. -->
10. {departure — and why it's intentional}

## FIXTURES
<!-- Purpose-built test instances: what each one is and what it proves. Name them so they
     can't collide with fixtures from other work in the same repo. -->
13. {fixture name = what it forces / anchors, and the expected result}
