# Answer check (Jev)

**Check an answer before Claude sends it.**

Before Claude gives you its final answer, this skill has the draft checked by
Jev, a quality-checking model from [TypeSafe](https://typesafe.ai). Jev looks
at whether the draft answers what you asked, makes claims the evidence
doesn't support, contradicts the output of the tools Claude used, or leaves
out a warning you need. If the draft doesn't pass, Claude breaks it into
individual claims, finds the ones Jev flags, fixes them, and checks again.

The answer arrives with a short note in plain words. Usually that's one line,
such as "Jev check: passed, no concerns." When Jev wasn't sure, the note lists
up to three points worth checking yourself, for example a figure Jev couldn't
verify or a warning in the tool output that the answer left out.

Jev only checks the points Claude puts to it. It doesn't find other problems
on its own, and it doesn't judge whether the advice itself is good.

Available for: **Claude** ([`claude/`](claude/))

## Good for

- Summaries of analysis results that will go to a manager or client
- Answers that report numbers, counts or "it works" after Claude ran tools
- Any answer where an unsupported claim would be costly

## How to use it

Ask for it:

```text
Check your draft with Jev before you send it.
```

To be asked every time, add this to your `CLAUDE.md` (for Claude Code) or to
your Claude preferences:

```markdown
## Jev output check (applies to every session)

Before giving the user a final answer that makes claims (numbers, findings, explanations of why something happened, or recommendations), ask whether they want it checked by Jev first. Use AskUserQuestion with the options "Check with Jev" and "Send as is". Do not ask when the answer only reports mechanical results that tests, CI, git or a command's output already show (committed, pushed, PR opened, checks passed, deployed), for short conversational replies (greetings, yes/no confirmations, one-line clarifying questions), or when the user has said "no Jev check" for this session.

If they choose "Check with Jev", invoke the `jev-check` skill and follow it.
```

Claude then skips the question for routine status updates and small talk, and
you can turn it off for a session by saying "no Jev check".

## Setup

1. **Get a TypeSafe API key** from the
   [TypeSafe console](https://console.typesafe.ai/settings/keys). Usage is
   billed by TypeSafe, at a few cents per million input tokens.
2. **Add your key to the skill.** In `claude/SKILL.md`, replace
   `<YOUR_TYPESAFE_API_KEY>` with your key. If you use the zip from the
   release, unzip it, edit `jev-check/SKILL.md`, and zip the `jev-check`
   folder again. Keep the edited copy private and never commit it to a public
   repo. Until the key is filled in, the skill tells you it's missing and
   doesn't run the check.
3. **Let Claude reach the API.** In the Claude app, add `api.typesafe.ai` to
   the allowed domains under **Settings → Capabilities**, then start a new
   chat.
4. Upload or install the skill as described in [INSTALL.md](../../INSTALL.md).

## What gets sent to TypeSafe

Each check sends your latest request, Claude's draft answer, and, when Claude
used tools, the relevant tool output (commands and their results, passages
from pages or files it read). Long tool output is trimmed to 30,000
characters. Don't use the check on material you aren't allowed to share with a
third-party service.
