# Spec and formulation review

**Catch errors in a plan, spec or mathematical formulation before it becomes code.**

A wrong plan is a bug generator: whoever implements it faithfully builds the
mistake. This skill has Claude review the document itself, adversarially and
in several passes. It checks every formula, index, unit, boundary condition
and assumption, looks for gaps and self-contradictions, and asks you about
anything that is a decision or missing information rather than guessing. It
then trims the document, re-checks it, and sends it back to the author for
sign-off.

Available for: **Claude** ([`claude/`](claude/)). The skill's internal name is
`algo-tech-document-review`.

## Good for

- LP/MIP and other optimization formulations: indices, constraints, units,
  coefficients, boundary conditions
- Specs for forecasting, pricing, allocation or scheduling models
- Plans another AI agent drafted that you want sanity-checked before building
- Methodology documents where one inconsistency would invalidate the results

It reviews documents only, not code.

## How to use it

Share the document and ask for a review; Claude recognises the request:

```text
Review this facility-location formulation before we implement it. Check every
index, constraint and unit, and ask me about anything that's ambiguous.
```

```text
My agent drafted this plan for the inventory allocation model. Sanity-check it
for gaps and contradictions.
```

Claude stops to ask its questions in one batch after the first full pass, so
expect a short back-and-forth before the final version.

## Next step

Once the document is signed off, build it with the
[phased build](../algo-tech-implementation/) skill.
