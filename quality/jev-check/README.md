# Answer check (Jev)

**Check an answer before Claude sends it.**

Before Claude gives you its final answer, this skill has the draft scored by
Jev, a quality-checking model from [TypeSafe](https://typesafe.ai). Jev looks
at whether the draft answers what you asked, makes claims the evidence
doesn't support, contradicts the output of the tools Claude used, or leaves
out a warning you need. If any score is weak, Claude breaks the draft into
individual claims, finds the ones Jev flags, fixes them, and checks again.
The answer arrives with a one-line summary of its scores.

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

To be asked every time, add a line like this to your Claude preferences or
memory:

```text
Before giving the final answer for a task, ask whether to check it with Jev
first, with the options "Check with Jev" and "Send as is".
```

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
