# Installing the skills

Pick the section for the tool you use. Each skill also has its own page with
anything extra it needs (for example, the answer check needs an API key).

## Claude app (web, desktop, mobile)

1. Download the skill's zip from the
   [latest release](https://github.com/arviphd/ai-skills/releases/tag/skills).
2. In Claude, open **Customize → Skills**, click **+**, choose
   **Create skill → Upload a skill**, and select the zip.
3. Make sure code execution is turned on in **Settings → Capabilities**.

Skills you turn on in the Claude app also load in Claude Code when you sign in
with the same account.

To make a zip yourself from a clone of this repo, zip the skill's `claude/`
folder under the skill's own name (the folder inside the zip must match the
skill name):

```sh
mkdir -p /tmp/skill-zips
cp -R coding/algo-tech-implementation/claude /tmp/skill-zips/algo-tech-implementation
(cd /tmp/skill-zips && zip -r algo-tech-implementation.zip algo-tech-implementation)
```

## Claude Code

Clone the repo, then copy every Claude skill into your personal skills folder.

macOS or Linux:

```sh
git clone https://github.com/arviphd/ai-skills.git
cd ai-skills
for d in */*/claude; do
  name=$(basename "$(dirname "$d")")
  mkdir -p "$HOME/.claude/skills/$name"
  cp -R "$d/." "$HOME/.claude/skills/$name/"
done
```

Windows (PowerShell):

```powershell
git clone https://github.com/arviphd/ai-skills.git
cd ai-skills
Get-ChildItem -Path *\*\claude -Directory | ForEach-Object {
  $dest = Join-Path $HOME ".claude\skills\$($_.Parent.Name)"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item -Recurse -Force -Path (Join-Path $_.FullName '*') -Destination $dest
}
```

To install a single skill, copy just that skill's `claude/` folder to
`~/.claude/skills/<skill-name>/`. For a project-only install, use
`<project>/.claude/skills/<skill-name>/` instead.

## Codex

Clone the repo, then copy every Codex skill into your skills folder.

macOS or Linux:

```sh
git clone https://github.com/arviphd/ai-skills.git
cd ai-skills
for d in */*/codex; do
  [ -f "$d/SKILL.md" ] || continue          # skip the auto-review hook
  name=$(basename "$(dirname "$d")")
  mkdir -p "$HOME/.agents/skills/$name"
  cp -R "$d/." "$HOME/.agents/skills/$name/"
done
```

Windows (PowerShell):

```powershell
git clone https://github.com/arviphd/ai-skills.git
cd ai-skills
Get-ChildItem -Path *\*\codex -Directory |
  Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') } |
  ForEach-Object {
    $dest = Join-Path $HOME ".agents\skills\$($_.Parent.Name)"
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item -Recurse -Force -Path (Join-Path $_.FullName '*') -Destination $dest
  }
```

Codex picks up new skills automatically; restart it if one doesn't appear.
For a project-only install, copy into `<project>/.agents/skills/<skill-name>/`.

The [auto-review hook](coding/auto-review/) is installed separately; its page
has the steps.

## Updating

Pull the latest changes (`git pull`) and run the same copy commands again, or
download and upload the new zip in the Claude app.
