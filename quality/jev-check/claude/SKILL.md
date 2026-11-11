---
name: "jev-check"
description: "Run the Jev quality check on a draft answer before sending it. Use when the user chooses \"Check with Jev\" or types /jev-check."
---

# Jev output check (Claude cloud workspace)

This calls TypeSafe's Jev API at `api.typesafe.ai`, using the user's API key below. Use it only in the run command; never show it in a reply.

API key: `<YOUR_TYPESAFE_API_KEY>`

If the line above still shows the placeholder `<YOUR_TYPESAFE_API_KEY>`, do not run the check: tell the user to put their TypeSafe API key into this skill's SKILL.md (replacing the placeholder) and re-upload it, then send the answer unchecked.

## 1. Prepare

Do all Jev work in its own folder, `/tmp/jev-check` (create it if needed), never in the user's project or working folder, so no user file is overwritten and nothing is left behind. Every file named below lives in that folder.

Before each check, run `grep -q '^SCRIPT_VERSION = "6"' /tmp/jev-check/jev-check.py`. If it fails (no file, or a copy from another version of this skill), write `jev-check.py` there with the exact contents in "The script" below, overwriting any existing copy. If it succeeds, reuse the file as is.

## 2. Write the inputs

Write the user's request to `request.txt` and your draft answer to `draft.txt`.

`request.txt` is the user's latest message, verbatim. Jev sees nothing else of the conversation, so add a line starting `(Context: ...)` whenever the message relies on earlier turns (for example "proceed", "do it", "fix 1-8") or on facts Jev cannot know. State plainly what the message refers to. Keep it to facts from the conversation; never argue for the draft.

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

Leave out `--evidence` when no tools were used. It normally takes about a second; if it runs longer than 60 seconds, stop it and report a failure. It prints one JSON line with `addresses_request`, `contradicted_by_evidence`, `hidden_errors`, `unsupported_claims` (each 0 to 1), `clarity` (0 to 2), `clarity_confusing` (0 to 1: the probability that the draft is confusing) and `missing_caveat` (0 to 1: the draft leaves out a warning the user needs to act safely or correctly). `contradicted_by_evidence` and `hidden_errors` are only checked against tool output, so both are null when no evidence was given; ignore them then. When no evidence was given, `unsupported_claims` is the higher of two separate checks, shown in `unsupported_parts`: `wrong_or_invented` (states something that looks wrong or made up) and `unshown_work` (claims work was done or verified without showing it). Evidence longer than 30,000 characters is trimmed to its start and end before sending.

## 4. Revise if needed

Revise the draft and run the check once more if any of these hold:
- `addresses_request` < 0.7
- `contradicted_by_evidence` > 0.5 or `hidden_errors` > 0.5 (skip either one when it is null)
- `unsupported_claims` > 0.7
- `clarity` < 1.5 or `clarity_confusing` > 0.3
- `missing_caveat` > 0.7

Before revising, find out what Jev is flagging. Jev returns scores only, never reasons, so do not guess.

**Diagnose.**
1. Write `claims.txt`: one specific, standalone claim from the draft per line (about 8-20). If `hidden_errors`, `missing_caveat` or `addresses_request` failed, also add 3-6 lines of the form `caveat: that <something the user may need to know>`, naming possible omissions: limitations, approximations, things left unfixed, things the evidence cannot verify.
2. Run the step 3 command with `--claims claims.txt` added (with or without `--evidence`, matching step 3). It prints one JSON line per item, worst first: `{"claim", "contradicted", "unsupported", "wrong_or_invented"}` for claims when evidence was given, `{"claim", "wrong_or_invented"}` for claims when it was not, and `{"caveat", "omitted"}` for caveats. A last line, `{"unbacked_handling": ..., "probabilities": {...}}`, says how the draft as a whole treats things it cannot back up: `all_backed`, `left_out`, `flagged_unknown`, `hedged` or `stated_as_fact` (the most likely one is named; all five probabilities are listed). It only guides the fix below; it never decides pass or fail.
3. Act on every score over 0.5:
   - `unsupported`: this only matters for claims about the work itself (something run, found, changed or verified). For those, add the real output that shows it to `evidence.txt`; if you cannot, soften or drop the claim. A general-knowledge claim (not about the work) that scores `unsupported` high but `wrong_or_invented` at or below 0.5 is fine: keep it.
   - `contradicted`: re-check the claim. If it is wrong, correct the draft. If the evidence just does not show the relevant part, add the output that does.
   - `wrong_or_invented`: re-check the claim. Correct it if it is wrong; if it is right but Jev cannot tell, add how you know it (for example, run a command that shows it and switch to checking with `--evidence`), or soften or drop it.
   - `omitted`: if the caveat is real and the user should know it, add it to the draft.
   - Use `unbacked_handling` to choose how to fix claims you cannot back up. If it is `hedged` or `stated_as_fact`, do not just reword: either show what backs the claim, or say plainly that you could not check it, or remove it. Never turn a hedge into a firmer statement without new evidence.

A claim counts as failing if `contradicted` or `wrong_or_invented` is over 0.5, or if it is about the work and `unsupported` is over 0.5. A caveat fails if `omitted` is over 0.5.

**Follow-up round (at most one).** Put only the failing items into `followup.txt` and run with `--claims followup.txt`. Each follow-up must rest on something new: added output in `evidence.txt` or a corrected or added sentence in the draft. Never reword a claim or caveat just to get a better score.

**Final check.** Run the step 3 command once more.
- If it passes, send.
- If it still fails but no diagnosed item is failing any more, the overall question is not pointing at anything concrete. Send the answer, report the overall scores and that every claim and caveat passes on its own, and do not revise further.
- If some item still fails, send the revised answer anyway, say which scores are below the bar, and name the items still flagged.

## 5. Send

Send the final answer with a one-line note of the Jev scores.

If the script fails, say so with its error message and send the answer unchecked. Two failures have a known cause:
- A proxy or connection error (for example `403`, `Tunnel connection failed`, `connection refused`): `api.typesafe.ai` isn't allowed yet. Tell the user to add it under Settings > Capabilities on claude.ai, then start a new chat.
- `HTTP 401` from TypeSafe: the API key in this skill is wrong or expired. Tell the user to update it in this skill's SKILL.md and re-upload it.

## The script

```python
#!/usr/bin/env python3
"""jev-check.py — score a draft answer with TypeSafe's Jev model.

Usage:
  python3 jev-check.py --request r.txt --draft d.txt [--evidence e.txt]
  python3 jev-check.py --request r.txt --draft d.txt [--evidence e.txt] --claims c.txt
    (breakdown: one JSON line per item, worst first. Lines in c.txt are claims;
     lines starting "caveat:" are checked as possible omissions from the draft.
     Claims are always checked for looking wrong or invented, and with evidence also
     for being contradicted or unsupported by it. A final line reports how the draft
     handles things it cannot back up; it is guidance only, not a pass/fail score)

API key: $TYPESAFE_API_KEY, or a line TYPESAFE_API_KEY=... in ~/.claude/jev.env.
With --no-key, no Authorization header is sent: use this in Claude cloud sessions
where a network secret for api.typesafe.ai makes the proxy attach the key.

Output (stdout, one JSON line):
  {"model": "...", "addresses_request": 0.93, "contradicted_by_evidence": 0.04,
   "hidden_errors": 0.08, "unsupported_claims": 0.12, "clarity": 1.71,
   "clarity_confusing": 0.02, "missing_caveat": 0.1}
contradicted_by_evidence and hidden_errors are null when no evidence file is given.
Without evidence, unsupported_claims is the higher of two checks, listed in
"unsupported_parts": wrong_or_invented and unshown_work.
Evidence over 30,000 characters is trimmed to its first and last 15,000.

Exit codes: 0 ok, 1 bad input or missing key, 2 API/network error.
Standard library only.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_VERSION = "6"  # bump whenever this script changes; the skill rewrites older copies
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
    if key:
        return key
    env_file = Path.home() / ".claude" / "jev.env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            m = re.match(r'^\s*TYPESAFE_API_KEY\s*=\s*"?([^"\s]+)"?\s*$', line)
            if m:
                key = m.group(1)
    if not key:
        fail("API key missing: set TYPESAFE_API_KEY or add it to ~/.claude/jev.env", 1)
    return key


MAX_EVIDENCE = 30000


def trim_evidence(text):
    """Keep the start and end of long logs, where commands and final results usually are."""
    if len(text) <= MAX_EVIDENCE:
        return text
    half = MAX_EVIDENCE // 2
    return text[:half] + "\n...[middle of log omitted]...\n" + text[-half:]


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
        else:
            questions[k + "_wrong"] = noul(
                f'Does this claim from the draft look wrong or made up: "{c}"',
                "The claim looks wrong or made up",
                "The claim looks correct and well founded")
        if kind != "caveat" and evidence is not None:
            questions[k + "_contradicted"] = noul(
                f'Does the evidence contradict this claim from the draft: "{c}"',
                "The evidence contradicts it",
                "The evidence is consistent with it or says nothing about it")
            questions[k + "_unsupported"] = noul(
                f'Is this claim from the draft unsupported by the evidence: "{c}"',
                "Nothing in the evidence supports it",
                "The evidence supports it")
    questions["unbacked_handling"] = {
        "type": "choice",
        "instructions": "How does draft_answer handle things it cannot back up, meaning "
                        "things not shown in evidence (when evidence is given) and not "
                        "well-established general knowledge?",
        "criteria": {
            "all_backed": "Everything it states is shown in the evidence or is "
                          "well-established knowledge",
            "left_out": "It leaves out what it cannot back up and does not mention it",
            "flagged_unknown": "It says plainly that it does not know or could not check "
                               "something",
            "hedged": "It states something it cannot back up but softens it, for example "
                      "with probably, roughly or may",
            "stated_as_fact": "It states something it cannot back up as plain fact",
        },
    }
    return {"model": MODEL, "state": state, "questions": questions}


def main():
    ap = argparse.ArgumentParser(description="Score a draft answer with Jev.")
    ap.add_argument("--request", required=True, help="file with the user's request")
    ap.add_argument("--draft", required=True, help="file with the draft answer")
    ap.add_argument("--evidence", help="file with commands and their output")
    ap.add_argument("--claims", help="file with one draft claim per line: per-claim breakdown")
    ap.add_argument("--endpoint", default=ENDPOINT, help=argparse.SUPPRESS)
    ap.add_argument("--no-key", action="store_true",
                    help="send no key; a proxy (network secret) attaches it")
    ap.add_argument("--timeout", type=float, default=45, help="seconds (default 45)")
    args = ap.parse_args()

    key = None if args.no_key else load_key()
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
            else:
                claims.append(("claim", line))
        body = build_claims_body(request, draft, evidence, claims)
    else:
        body = build_body(request, draft, evidence)
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
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
            elif evidence is None:
                rows.append({"claim": c, "wrong_or_invented": get(k + "_wrong", "noul", 3)})
            else:
                rows.append({"claim": c,
                             "contradicted": get(k + "_contradicted", "noul", 3),
                             "unsupported": get(k + "_unsupported", "noul", 3),
                             "wrong_or_invented": get(k + "_wrong", "noul", 3)})
        rows.sort(key=lambda r: max(v for v in r.values() if isinstance(v, float)),
                  reverse=True)
        for r in rows:
            print(json.dumps(r))
        h = answers.get("unbacked_handling") or {}
        probs = h.get("probabilities") or {}
        if not probs:
            fail("response is missing answer 'unbacked_handling'", 2)
        print(json.dumps({"unbacked_handling": max(probs, key=probs.get),
                          "probabilities": {k: round(float(v), 3) for k, v in probs.items()}}))
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
    print(json.dumps(out))


if __name__ == "__main__":
    main()
```