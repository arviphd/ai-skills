---
name: "jev-check"
description: "Score a draft answer with TypeSafe's Jev quality model before sending it, find which claims are weak, and revise. Use when the user asks to check, verify or score a draft answer with Jev, chooses \"Check with Jev\", or types /jev-check."
---

# Jev output check

This calls TypeSafe's Jev API at `api.typesafe.ai`, using the user's API key below. Use it only in the run command; never show it in a reply.

API key: `<YOUR_TYPESAFE_API_KEY>`

If the line above still shows the placeholder `<YOUR_TYPESAFE_API_KEY>`, do not run the check: tell the user to put their TypeSafe API key into this skill's SKILL.md (replacing the placeholder) and re-upload it, then send the answer unchecked.

## 1. Prepare

Do all Jev work in its own folder, `/tmp/jev-check` (create it if needed), never in the user's project or working folder, so no user file is overwritten and nothing is left behind. Every file named below lives in that folder.

Before each check, run `grep -q '^SCRIPT_VERSION = "9"' /tmp/jev-check/jev-check.py`. If it fails (no file, or a copy from another version of this skill), write `jev-check.py` there with the exact contents in "The script" below, overwriting any existing copy. If it succeeds, reuse the file as is.

## 2. Write the inputs

Write the user's request to `request.txt` and your draft answer to `draft.txt`.

`request.txt` is the user's latest message, verbatim. Jev sees nothing else of the conversation, so add a line starting `(Context: ...)` whenever the message relies on earlier turns (for example "proceed", "do it", "fix 1-8") or on facts Jev cannot know. State plainly what the message refers to. If the message quotes someone else's requests (feedback, an email, a ticket), say what the user is actually asking for, for example "(Context: the user asks whether these points are already handled, not for them to be built now.)". Keep it to facts from the conversation; never argue for the draft.

If you used tools for the task, also write `evidence.txt` with their actual output, copied as-is, not summarized:
- commands: each command followed by its output;
- web searches and fetched pages: the URL, then the passages the draft relies on;
- files you read: the file name, then the relevant lines.

Jev scores the draft only against what `evidence.txt` shows, so:
- Never write lines like "applied changes ... ok" or "rendered slide shows X". Jev cannot check a description, only real output.
- Every specific claim in the draft (a changed sentence, a count, a name, a file) must be visible in some pasted output. If none shows it, run a command that does (e.g. dump the changed text from the final file) and paste that.
- Prefer output from the final deliverable over output from intermediate steps.
- For long logs or outputs, paste the lines that matter (found with `grep`, `tail` or similar) rather than the whole thing. Evidence over 30,000 characters loses its middle, and a line lost there cannot support the draft.
- When the draft states a number you worked out (an ETA, a percentage, a total, a difference), run the calculation as a command and paste it with its output. Jev does not do arithmetic, so without the calculation shown it cannot tell a right number from a wrong one and flags both as unsupported.

## 3. Run

```
cd /tmp/jev-check && TYPESAFE_API_KEY="<API key above>" python3 jev-check.py --request request.txt --draft draft.txt --evidence evidence.txt
```

Leave out `--evidence` when no tools were used. It normally takes about a second; if it runs longer than 60 seconds, stop it and report a failure. Evidence over 30,000 characters is trimmed to its start and end before sending.

It prints one JSON line. The script applies the limits itself; act on these fields:
- `verdict`: `pass` or `revise`; `failed` lists the checks over their limit.
- `shaky`: true when the verdict rests on scores Jev could not settle (a yes/no score between 0.3 and 0.7, or clarity with no level at a probability of 0.7). A `revise` is shaky when every failed check is unsettled; a `pass` is shaky when any check is unsettled. `shaky_because` lists those checks.

The other fields are the raw scores; use them only if the user asks for numbers.

## 4. Revise if needed

Revise the draft and run the check once more if `verdict` is `revise`, even when it is shaky.

Before revising, find out what Jev is flagging. Jev returns scores only, never reasons, so do not guess.

**Diagnose.**
1. Write `claims.txt`: one specific, standalone claim from the draft per line (about 8-20). If `hidden_errors`, `missing_caveat` or `addresses_request` failed, also add 3-6 lines of the form `caveat: that <something the user may need to know>`, naming possible omissions: limitations, approximations, things left unfixed, things the evidence cannot verify.
2. Run the step 3 command with `--claims claims.txt` added (with or without `--evidence`, matching step 3). It prints one JSON line per item, worst first: `{"claim", "contradicted", "unsupported", "wrong_or_invented", "cannot_check"}` for claims when evidence was given, `{"claim", "wrong_or_invented", "cannot_check"}` for claims when it was not, and `{"caveat", "omitted"}` for caveats. `cannot_check` is high when a claim cannot be checked from general knowledge (too recent, too specific or private), which is different from looking wrong. When evidence was given, the script also picks out the output lines that look like errors, warnings, failures, skips or limits, and adds `{"evidence_line", "left_out"}` for each: how likely it is that the draft leaves out that line when the user should be told. You can add your own `evidence: <exact output line>` lines to `claims.txt` too. Each item also has `unsure`: the names of its scores that fall between 0.3 and 0.7 (empty when Jev was clear-cut on it).
3. Act on every score over 0.5:
   - `unsupported`: this only matters for claims about the work itself (something run, found, changed or verified). For those, add the real output that shows it to `evidence.txt`; if you cannot, soften or drop the claim. A general-knowledge claim (not about the work) that scores `unsupported` high but `wrong_or_invented` at or below 0.5 is fine: keep it.
   - `contradicted`: re-check the claim. If it is wrong, correct the draft. If the evidence just does not show the relevant part, add the output that does.
   - `wrong_or_invented` with `cannot_check` at or below 0.5: Jev thinks the claim is wrong. Re-check it and correct it if it is wrong; if it is right, add how you know it (for example, run a command that shows it and switch to checking with `--evidence`), or soften or drop it.
   - `wrong_or_invented` with `cannot_check` over 0.5: Jev cannot verify the claim (too recent, specific or private); that is not the same as wrong. If you have a source (a fetched page, a file, a command), add it to `evidence.txt` and check again with `--evidence`. If not, keep the claim if you are confident, and make it a review point in step 5 so the user confirms it.
   - `left_out` on an `evidence_line` over 0.5: the draft leaves out that part of the output. Mention it in the draft.
   - `omitted`: if the caveat is real and the user should know it, add it to the draft.

A claim counts as failing if `contradicted` is over 0.5, if `wrong_or_invented` is over 0.5 while `cannot_check` is at or below 0.5, or if it is about the work and `unsupported` is over 0.5. A claim Jev cannot check is not failing; it becomes a review point. A caveat fails if `omitted` is over 0.5, and an evidence line fails if `left_out` is over 0.5.

**Follow-up round (at most one).** Put only the failing items into `followup.txt` and run with `--claims followup.txt`. Each follow-up must rest on something new: added output in `evidence.txt` or a corrected or added sentence in the draft. Never reword a claim or caveat just to get a better score.

**Final check.** Run the step 3 command once more.
- If `verdict` is `pass` and it is not shaky, send.
- If `verdict` is `pass` but it is shaky, find where: run the diagnose step (claims and 2-4 likely caveats) once, without revising. The items whose scores fall between 0.3 and 0.7, or above 0.5, are the review points for step 5. Then send.
- If it still fails but no diagnosed item is failing any more, the overall question is not pointing at anything concrete. Send the answer, say that every claim and caveat passes on its own, and do not revise further.
- If some item still fails, send the revised answer anyway and name, in plain words, what is still flagged.

## 5. Send

Send the final answer with a short Jev note for a busy human, who only needs to know what to look at:
- Not shaky: one line, for example "Jev check: passed, no concerns." or "Jev check: passed after 1 revision, no concerns." Nothing more.
- Shaky, or still failing after revision: one line saying so, then at most 3 review points, worst first. Each point quotes the sentence from the answer (or names the missing point) and says in plain words what is doubtful and what the user should check, for example:
  - a claim nothing shows: "Nothing I ran shows the export finished; I took that from the notification."
  - a claim Jev doubted: "Jev wasn't sure '2 h 38 min' is right: the calculation gives 2:37:30, so it's rounded."
  - a claim Jev can't verify: "Jev can't verify the 2026 price (too recent for it); please confirm it."
  - a part of the output left out: "The output also says 'Exit code 137', which the answer doesn't mention."
  - a missing point: "Worth adding: the range assumes the remaining tasks run as fast as recent ones."
  - clarity: "Jev couldn't decide whether this is clear enough; skim it."
- Whenever there are review points, end with this line: "Note: Jev only checks the points Claude puts to it. It cannot find other problems on its own, and it does not judge whether the advice itself is good."
- No scores, no check names, no JSON. Give numbers only if the user asks.

If the script fails, say so with its error message and send the answer unchecked. Two failures have a known cause:
- A proxy or connection error (for example `403`, `Tunnel connection failed`, `connection refused`): `api.typesafe.ai` isn't allowed yet. Tell the user to add it under Settings > Capabilities on claude.ai, then start a new chat.
- `HTTP 401` from TypeSafe: the API key in this skill is wrong or expired. Tell the user to update it in this skill's SKILL.md and re-upload it.

## The script

```python
#!/usr/bin/env python3
"""jev-check.py: score a draft answer with TypeSafe's Jev model (see the jev-check skill).
Key from $TYPESAFE_API_KEY. Exit codes: 0 ok, 1 bad input or missing key, 2 API/network error."""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_VERSION = "9"  # bump whenever this script changes; the skill rewrites older copies
ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"


def fail(msg, code):
    print(f"jev-check: {msg}", file=sys.stderr)
    sys.exit(code)


def read_text(path, label):
    p = Path(path)
    if not p.is_file():
        fail(f"{label} not found: {path}", 1)
    text = p.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        fail(f"{label} is empty: {path}", 1)
    return text


def load_key():
    key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not key:
        fail("API key missing: set TYPESAFE_API_KEY", 1)
    return key


MAX_EVIDENCE = 30000


def trim_evidence(text):
    """Keep the start and end of long logs, where commands and final results usually are."""
    if len(text) <= MAX_EVIDENCE:
        return text
    half = MAX_EVIDENCE // 2
    return text[:half] + "\n...[middle of log omitted]...\n" + text[-half:]


UNSURE_LOW, UNSURE_HIGH = 0.3, 0.7

ALERT = re.compile(r"error|warn|fail|exception|traceback|killed|timed? ?out|denied|not found|"
                   r"exit (code )?[1-9]|skipp|refus|abort|gap|limit", re.I)
MAX_EVIDENCE_LINES = 8


def alert_lines(evidence):
    """Output lines that look like errors, warnings, failures, skips or limits."""
    seen, picked = set(), []
    for line in evidence.splitlines():
        line = line.strip()
        if not line or line.startswith("$") or not ALERT.search(line) or line in seen:
            continue
        seen.add(line)
        picked.append(line[:300])
        if len(picked) == MAX_EVIDENCE_LINES:
            break
    return picked


def is_unsure(value):
    return value is not None and UNSURE_LOW <= value <= UNSURE_HIGH


def noul(instructions, yes, no):
    return {"type": "noul", "instructions": instructions,
            "criteria": {"true": yes, "false": no}}


def build_body(request, draft, evidence):
    state = {"user_request": request, "draft_answer": draft}
    questions = {
        "addresses_request": noul(
            "Does draft_answer fully address what user_request asks for?",
            "Every part of the request is answered or explicitly handled",
            "Part of the request is ignored, missed, or answered off-target"),
        "wrong_or_invented": noul(
            "Does draft_answer state something as fact that looks wrong or made up?",
            "It states as fact something that looks wrong or made up",
            "Every fact it states looks correct and well founded"),
        "unshown_work": noul(
            "Does draft_answer claim that work was done or verified without showing it?",
            "It says something was done, run, tested or checked, with nothing shown to back it",
            "It claims no work, or shows what backs each claim of work"),
        "missing_caveat": noul(
            "Does draft_answer leave out a warning or caveat the user needs in order to act "
            "on it safely or correctly?",
            "Acting on the draft as written could cause harm, data loss or a wrong result "
            "that a missing warning would have prevented",
            "The draft includes the warnings the user needs, or none are needed"),
        "clarity": {
            "type": "score",
            "instructions": "How clear and easy to act on is draft_answer for the user?",
            "criteria": [
                "Confusing, disorganized or hard to act on",
                "Understandable but could be clearer or better organized",
                "Clear, well organized and easy to act on",
            ],
        },
    }
    if evidence is not None:
        state["evidence"] = evidence
        del questions["wrong_or_invented"], questions["unshown_work"]
        questions["unsupported_claims"] = noul(
            "Does draft_answer claim something that evidence (the commands that ran and "
            "their outputs) does not back up, such as a result, a number, or \"it works\" "
            "that no output shows?",
            "It claims a result, number or success that no output shows",
            "Every result, number or success it claims is shown in the evidence")
        questions["contradicted_by_evidence"] = noul(
            "Does evidence contradict anything draft_answer says, such as the draft "
            "reporting success where an output shows an error, a failed exit code, or a "
            "different value?",
            "At least one statement in the draft is contradicted by the evidence",
            "The draft is consistent with the evidence")
        questions["hidden_errors"] = noul(
            "Does evidence show an error, warning, or failure that matters to "
            "user_request but that draft_answer does not mention?",
            "The evidence shows a relevant error, warning or failure the draft leaves out",
            "The draft mentions every relevant error, warning or failure in the evidence")
    return {"model": MODEL, "state": state, "questions": questions}


def build_claims_body(request, draft, evidence, items):
    state = {"user_request": request, "draft_answer": draft}
    if evidence is not None:
        state["evidence"] = evidence
    questions = {}
    for i, (kind, c) in enumerate(items, 1):
        k = f"c{i:02d}"
        if kind == "caveat":
            questions[k + "_omitted"] = noul(
                f"Does draft_answer fail to tell the user {c}, when the user should be told?",
                "The draft omits or understates this and the user should know",
                "The draft states it plainly, or the user does not need to be told")
        elif kind == "evidence":
            questions[k + "_left_out"] = noul(
                f'Does draft_answer leave out this part of the output, when the user should '
                f'be told about it: "{c}"',
                "The draft does not mention it, and the user should know",
                "The draft mentions it, or it does not matter to the user")
        else:
            questions[k + "_wrong"] = noul(
                f'Does this claim from the draft look wrong or made up: "{c}"',
                "The claim looks wrong or made up",
                "The claim looks correct and well founded")
            questions[k + "_cannot_check"] = noul(
                f"Is this claim from the draft something that cannot be checked from "
                f"well-established general knowledge, for example a recent price, version, "
                f"release or date, or a detail of the user's own systems: \"{c}\"",
                "It cannot be checked from general knowledge: it is too recent, too specific "
                "or private",
                "It can be checked from well-established general knowledge")
        if kind == "claim" and evidence is not None:
            questions[k + "_contradicted"] = noul(
                f'Does the evidence contradict this claim from the draft: "{c}"',
                "The evidence contradicts it",
                "The evidence is consistent with it or says nothing about it")
            questions[k + "_unsupported"] = noul(
                f'Is this claim from the draft unsupported by the evidence: "{c}"',
                "Nothing in the evidence supports it",
                "The evidence supports it")
    return {"model": MODEL, "state": state, "questions": questions}


def main():
    ap = argparse.ArgumentParser(description="Score a draft answer with Jev.")
    ap.add_argument("--request", required=True, help="file with the user's request")
    ap.add_argument("--draft", required=True, help="file with the draft answer")
    ap.add_argument("--evidence", help="file with commands and their output")
    ap.add_argument("--claims", help="file with one draft claim per line: per-claim breakdown")
    ap.add_argument("--endpoint", default=ENDPOINT, help=argparse.SUPPRESS)
    ap.add_argument("--timeout", type=float, default=45, help="seconds (default 45)")
    args = ap.parse_args()

    key = load_key()
    request = read_text(args.request, "request file")
    draft = read_text(args.draft, "draft file")
    evidence = trim_evidence(read_text(args.evidence, "evidence file")) if args.evidence else None

    claims = None
    if args.claims:
        claims = []
        for line in read_text(args.claims, "claims file").splitlines():
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith("caveat:"):
                claims.append(("caveat", line[7:].strip()))
            elif line.lower().startswith("evidence:"):
                if evidence is not None:
                    claims.append(("evidence", line[9:].strip()))
            else:
                claims.append(("claim", line))
        if evidence is not None:
            given = {c for kind, c in claims if kind == "evidence"}
            claims += [("evidence", l) for l in alert_lines(evidence) if l not in given]
        body = build_claims_body(request, draft, evidence, claims)
    else:
        body = build_body(request, draft, evidence)
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8",
               "Authorization": f"Bearer {key}"}
    req = urllib.request.Request(args.endpoint, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            resp = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        fail(f"API call failed: HTTP {e.code} {e.reason} {body}", 2)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        fail(f"API call failed: {getattr(e, 'reason', e)}", 2)
    except json.JSONDecodeError:
        fail("API returned a response that is not JSON", 2)

    answers = resp.get("answers")
    if not isinstance(answers, dict):
        fail(f"unexpected response: {json.dumps(resp)[:500]}", 2)

    def get(name, field, digits):
        a = answers.get(name) or {}
        if a.get(field) is None:
            fail(f"response is missing answer '{name}'", 2)
        return round(float(a[field]), digits)

    if claims is not None:
        rows = []
        for i, (kind, c) in enumerate(claims, 1):
            k = f"c{i:02d}"
            if kind == "caveat":
                rows.append({"caveat": c, "omitted": get(k + "_omitted", "noul", 3)})
            elif kind == "evidence":
                rows.append({"evidence_line": c, "left_out": get(k + "_left_out", "noul", 3)})
            elif evidence is None:
                rows.append({"claim": c, "wrong_or_invented": get(k + "_wrong", "noul", 3),
                             "cannot_check": get(k + "_cannot_check", "noul", 3)})
            else:
                rows.append({"claim": c,
                             "contradicted": get(k + "_contradicted", "noul", 3),
                             "unsupported": get(k + "_unsupported", "noul", 3),
                             "wrong_or_invented": get(k + "_wrong", "noul", 3),
                             "cannot_check": get(k + "_cannot_check", "noul", 3)})
        for r in rows:
            r["unsure"] = [k for k, v in r.items() if isinstance(v, float) and is_unsure(v)]
        rows.sort(key=lambda r: max(v for k, v in r.items()
                                    if isinstance(v, float) and k != "cannot_check"),
                  reverse=True)
        for r in rows:
            print(json.dumps(r))
        return

    out = {
        "model": resp.get("model"),
        "addresses_request": get("addresses_request", "noul", 3),
        "contradicted_by_evidence":
            get("contradicted_by_evidence", "noul", 3) if evidence is not None else None,
        "hidden_errors":
            get("hidden_errors", "noul", 3) if evidence is not None else None,
        "unsupported_claims": None,
        "clarity": get("clarity", "score", 2),
        "clarity_confusing": None,
        "missing_caveat": get("missing_caveat", "noul", 3),
    }
    if evidence is not None:
        out["unsupported_claims"] = get("unsupported_claims", "noul", 3)
    else:
        parts = {"wrong_or_invented": get("wrong_or_invented", "noul", 3),
                 "unshown_work": get("unshown_work", "noul", 3)}
        out["unsupported_claims"] = max(parts.values())
        out["unsupported_parts"] = parts
    probs = (answers.get("clarity") or {}).get("probabilities") or {}
    if "0" not in probs:
        fail("response is missing clarity probabilities", 2)
    out["clarity_confusing"] = round(float(probs["0"]), 3)
    unsure = []
    checked = dict(out)
    checked.update(out.get("unsupported_parts") or {})
    for k in ("addresses_request", "contradicted_by_evidence", "hidden_errors",
              "unsupported_claims", "wrong_or_invented", "unshown_work", "missing_caveat"):
        if k in checked and is_unsure(checked[k]):
            if k == "unsupported_claims" and "unsupported_parts" in out:
                continue  # its parts are listed instead
            unsure.append({"check": k, "value": checked[k]})
    if max(float(v) for v in probs.values()) < UNSURE_HIGH:
        unsure.append({"check": "clarity", "value": out["clarity"]})
    out["unsure"] = unsure

    # Apply the skill's limits (step 4) so the verdict and its shakiness come from code.
    failed = []
    if out["addresses_request"] < 0.7:
        failed.append("addresses_request")
    for k in ("contradicted_by_evidence", "hidden_errors"):
        if out[k] is not None and out[k] > 0.5:
            failed.append(k)
    if out["unsupported_claims"] > 0.7:
        failed.append("unsupported_claims")
    if out["clarity"] < 1.5 or out["clarity_confusing"] > 0.3:
        failed.append("clarity")
    if out["missing_caveat"] > 0.7:
        failed.append("missing_caveat")
    unsettled = {u["check"] for u in unsure}
    if unsettled & {"wrong_or_invented", "unshown_work"}:
        # only the part over the limit decides unsupported_claims
        if out["unsupported_claims"] in [u["value"] for u in unsure]:
            unsettled.add("unsupported_claims")
    out["verdict"] = "revise" if failed else "pass"
    out["failed"] = failed
    if failed:
        shaky_checks = failed if all(c in unsettled for c in failed) else []
    else:
        shaky_checks = sorted(unsettled)
    out["shaky"] = bool(shaky_checks)
    out["shaky_because"] = [
        u for u in unsure
        if u["check"] in shaky_checks
        or (u["check"] in ("wrong_or_invented", "unshown_work") and "unsupported_claims" in shaky_checks
            and u["value"] == out["unsupported_claims"])
    ]
    print(json.dumps(out))


if __name__ == "__main__":
    main()
```