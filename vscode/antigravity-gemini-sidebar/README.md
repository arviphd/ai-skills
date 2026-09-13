# Antigravity as a Gemini secondary-sidebar tab

This customization moves the Google Antigravity webview from VS Code's
Activity Bar to the secondary sidebar—the right-side tab strip that also holds
Chat, Codex, and Claude Code—and labels it **Gemini**.

Antigravity is a Marketplace extension. Installing or automatically updating
it replaces its installation directory, so this customization must be applied
again after an update. The script discovers the active installed version; it
does not contain or redistribute Antigravity source code.

## Requirements

- macOS
- Visual Studio Code installed in the standard location
- Google Antigravity already installed
- Python 3

## Apply

Save your work first. The script can run while VS Code is open, but you must
fully quit VS Code with **Cmd+Q** and reopen it afterward. `Developer: Reload
Window` may retain the old extension scan in the shared process.

```sh
python3 vscode/antigravity-gemini-sidebar/apply.py
```

The script:

1. Finds the active `google.google-antigravity` installation using
   `~/.vscode/extensions/extensions.json`.
2. Creates a timestamped backup under
   `~/Library/Application Support/codex-customizations/antigravity-gemini-sidebar/backups/`.
3. Changes the view container from `activitybar` to `secondarySidebar`, gives
   the container the unique ID `gemini-secondary-sidebar`, and labels it
   `Gemini`.
4. Changes Antigravity's internal default view location from `sidebar` to
   `auxiliarybar`, so its focus and close commands operate on the correct UI.
5. Removes obsolete Activity Bar layout records, pins Gemini in the secondary
   sidebar, and moves stale user-extension scan caches into the backup.

The operation is idempotent. Running it again on an already customized version
does not add duplicate layout entries.

## Verify

After fully quitting and reopening VS Code:

```sh
python3 vscode/antigravity-gemini-sidebar/apply.py --check
```

Successful verification ends with `Gemini customization: OK`.

## Nonstandard locations

Override discovery when needed:

```sh
python3 vscode/antigravity-gemini-sidebar/apply.py \
  --extension-dir /path/to/google.google-antigravity-1.3.0 \
  --user-data-dir "/path/to/Code/User"
```

Use `--skip-layout` to change only the extension files and leave VS Code's
saved layout database and scan caches untouched.

## Reverting

The simplest clean revert is to uninstall and reinstall Antigravity from the
Marketplace. That restores Google's files. VS Code will reconcile the view
container on the next full restart.

The timestamped backup also contains the original `package.json`,
`extension.js`, and (when layout changes are enabled) a safe SQLite backup of
the global state database. Treat the database backup as recovery material, not
as a routine restore: replacing a live database can discard newer unrelated UI
state.

## Maintenance note

The script deliberately fails instead of guessing if a future Antigravity
release changes the relevant manifest or runtime structure. Update the guarded
transform and its validation for the new release rather than performing an
unbounded text replacement.
