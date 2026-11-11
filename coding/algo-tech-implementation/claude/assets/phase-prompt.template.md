<!--
Per-phase executor prompt template (for Claude Code or similar).
Fill the {braces}. Paste after /clear (or into a fresh executor session).
The prompt must be self-sufficient: it plus the on-disk files are all the executor has.
Keep it scoped to ONE phase and end with a hard stop so the review loop stays intact.
-->

{FEATURE} Phase {N} = {one-line goal — what this phase adds}. {One line on what it does NOT touch.}

Re-prime by reading: {SPEC}.md (sections: {the relevant ones}), INVARIANTS_{feature}.md (esp. #{live invariants this phase}), PROGRESS_{feature}.md ({any carry-forward note from the last phase}).

Do:
1. {Scoped step, phrased in terms of the spec — point to spec sections, don't restate them.}
2. {…}
3. {…}

Do NOT: {what is explicitly out of scope this phase — the next phase's work, anything that would tempt scope creep}.

Honor INVARIANTS {#…} {and any wiring landmines W# that apply}. Keep {#… — the correctness invariants that must stay intact} intact.

Sign-off gate ({instance / config to run}):
- {Concrete, checkable pass criterion 1 — ideally something you can independently re-derive.}
- {Criterion 2 …}
- {A crux check: force the case the normal path would dodge, or match a zero-confound reference exactly.}
- {Prior-phase regression still holds — name the specific number/behavior.}

Finish: update PROGRESS_{feature}.md (Phase {N} status, files touched, gate result, the key numbers). If you found a new cross-phase hazard, append it to INVARIANTS_{feature}.md (numbered, with symptom + resolution). Then STOP — do not start Phase {N+1}. Report {the specific outputs you want to review} for review.
