<!--
Template for presenting document-review findings and the round-trip message to the author/agent.
Structure findings by what the author must DO with each, not just by location. Lead with the
blocking items. Keep each item concrete: what's wrong, where, why it matters, the fix.

Tag every finding with a severity. Heuristics:
  CRITICAL — would silently corrupt results or make the build infeasible if implemented as written
             (wrong coefficient, mis-translated convention, a case that becomes infeasible).
  HIGH     — a real defect or conflicting requirement; an acceptance/verification criterion that
             is untestable or unquantified.
  MEDIUM   — terminology drift, an underspecified edge case, a missing non-critical case.
  LOW      — wording, minor redundancy, style.
Nothing CRITICAL or HIGH may stay open at convergence.
-->

# Review of {document} — findings

## Correctness-critical (fix before building)
<!-- Defects that would plant a bug if implemented as written. Each is CRITICAL or HIGH. -->
- **[CRITICAL] {short title}** — {what's wrong and where}. {Why it matters / what it costs downstream.}
  {The fix.}
- **[HIGH] {title}** — {what's wrong and where}. {Cost.} {Fix.}
- ...

## Hardening (fold in)
<!-- Real improvements that aren't blocking: missing edge handling, a caveat to document,
     a tractability note. Typically MEDIUM or LOW. -->
- **[MEDIUM] {title}** — {issue} → {suggested change}.
- **[LOW] {title}** — {issue} → {suggested change}.
- ...

## Open questions (author/human answers — not defects)
<!-- Only items past the ask-bar: genuinely uncertain AND build-affecting. Dominated choices
     go in the round-trip's resolved list below, not here. Rank by impact × uncertainty,
     resolve via the Clarify checkpoint, record answers.
     Decisions: unstated choices with trade-offs — give options + a recommendation.
     Unknowns: missing information you can't derive — ask for the fact + why it matters. -->
- **[DECISION] {choice}** — Option A: {…, trades off …}. Option B: {…, trades off …}.
  Recommendation: {A/B} because {…}.
- **[UNKNOWN] {question}** — {what fact is missing}. Matters because: {what it changes downstream}.
- ...

## De-bloat summary (if a de-bloat pass was made)
<!-- What redundancy/contradiction was removed, so the author can see the doc wasn't gutted. -->
- Collapsed {N} restatements of {topic} to one canonical home in {section}; pointers elsewhere.
- Removed stale line in {section} that contradicted {section} (the corrected version kept).
- Integrity re-check: cross-references resolve, numbering consistent, no fact dropped.

---

# Round-trip message to the author/agent

> I reviewed {document} and made {N} correctness fixes, a de-bloat pass, and an integrity
> check. Summary of what I changed and why:
> - {change 1 — reason}
> - {change 2 — reason}
>
> Choices I resolved during review (one option clearly dominated; applied and logged — veto
> welcome): {list}.
>
> Open questions (decisions and unknowns) I did NOT resolve (your call): {list}.
>
> Please confirm: do you agree with these changes, and does the revised doc miss anything —
> any gap, constraint, or rationale I removed that should stay? Once you're satisfied and no
> open gaps remain, the doc is validated and ready to implement.
