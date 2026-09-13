#!/usr/bin/env python3
"""Move Google Antigravity into VS Code's Gemini secondary-sidebar tab."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path


EXTENSION_ID = "google.google-antigravity"
OLD_CONTAINER = "antigravity-sidebar"
NEW_CONTAINER = "gemini-secondary-sidebar"
OLD_WORKBENCH_ID = f"workbench.view.extension.{OLD_CONTAINER}"
NEW_WORKBENCH_ID = f"workbench.view.extension.{NEW_CONTAINER}"
VIEW_ID = "antigravity.panel"


class CustomizationError(RuntimeError):
    pass


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CustomizationError(f"Cannot read valid JSON from {path}: {exc}") from exc


def write_json(path: Path, value) -> None:
    temporary = path.with_name(f".{path.name}.gemini.tmp")
    temporary.write_text(
        json.dumps(value, indent="\t", ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def default_user_dir() -> Path:
    return Path.home() / "Library/Application Support/Code/User"


def extension_root() -> Path:
    return Path.home() / ".vscode/extensions"


def discover_extension(explicit: Path | None) -> Path:
    if explicit:
        candidate = explicit.expanduser().resolve()
        if not (candidate / "package.json").is_file():
            raise CustomizationError(f"No package.json in extension directory: {candidate}")
        return candidate

    root = extension_root()
    registry = root / "extensions.json"
    if registry.is_file():
        entries = load_json(registry)
        matches = [
            entry
            for entry in entries
            if entry.get("identifier", {}).get("id", "").lower() == EXTENSION_ID
        ]
        if len(matches) == 1:
            location = matches[0].get("location", {})
            raw_path = location.get("fsPath") or location.get("path")
            if raw_path:
                candidate = Path(raw_path).expanduser().resolve()
                if (candidate / "package.json").is_file():
                    return candidate
        elif len(matches) > 1:
            raise CustomizationError(f"Multiple active {EXTENSION_ID} registry entries found")

    candidates = []
    for candidate in root.glob("google.google-antigravity-*"):
        package = candidate / "package.json"
        if package.is_file():
            manifest = load_json(package)
            if manifest.get("publisher") == "google" and manifest.get("name") == "google-antigravity":
                candidates.append((version_key(str(manifest.get("version", "0"))), candidate))
    if not candidates:
        raise CustomizationError("Google Antigravity is not installed in ~/.vscode/extensions")
    return max(candidates, key=lambda item: item[0])[1].resolve()


def version_key(version: str):
    parts = re.split(r"[.-]", version)
    return tuple((0, int(part)) if part.isdigit() else (1, part) for part in parts)


def manifest_status(manifest: dict) -> tuple[bool, str]:
    contributes = manifest.get("contributes", {})
    containers = contributes.get("viewsContainers", {})
    views = contributes.get("views", {})
    target_containers = containers.get("secondarySidebar", [])
    target = [item for item in target_containers if item.get("id") == NEW_CONTAINER]
    target_views = views.get(NEW_CONTAINER, [])
    ok = (
        len(target) == 1
        and target[0].get("title") == "Gemini"
        and any(view.get("id") == VIEW_ID and view.get("name") == "Gemini" for view in target_views)
        and not any(item.get("id") == OLD_CONTAINER for item in containers.get("activitybar", []))
        and OLD_CONTAINER not in views
    )
    return ok, "manifest uses Gemini secondarySidebar" if ok else "manifest is not customized"


def patch_manifest(path: Path) -> bool:
    manifest = load_json(path)
    already_done, _ = manifest_status(manifest)
    if already_done:
        return False

    contributes = manifest.setdefault("contributes", {})
    containers = contributes.setdefault("viewsContainers", {})
    views = contributes.setdefault("views", {})

    old_containers = [item for item in containers.get("activitybar", []) if item.get("id") == OLD_CONTAINER]
    old_views = views.get(OLD_CONTAINER)
    if len(old_containers) != 1 or not isinstance(old_views, list):
        raise CustomizationError(
            "Antigravity's manifest structure changed; expected one activitybar "
            f"container named {OLD_CONTAINER!r} and its views"
        )
    if not any(view.get("id") == VIEW_ID for view in old_views):
        raise CustomizationError(f"Expected webview {VIEW_ID!r} is missing from the manifest")
    if any(item.get("id") == NEW_CONTAINER for item in containers.get("secondarySidebar", [])):
        raise CustomizationError(f"Target container {NEW_CONTAINER!r} already exists unexpectedly")
    if NEW_CONTAINER in views:
        raise CustomizationError(f"Target views key {NEW_CONTAINER!r} already exists unexpectedly")

    containers["activitybar"] = [
        item for item in containers.get("activitybar", []) if item.get("id") != OLD_CONTAINER
    ]
    if not containers["activitybar"]:
        del containers["activitybar"]

    target_container = dict(old_containers[0])
    target_container.update({"id": NEW_CONTAINER, "title": "Gemini"})
    containers.setdefault("secondarySidebar", []).append(target_container)

    target_views = []
    for view in old_views:
        updated = dict(view)
        if updated.get("id") == VIEW_ID:
            updated["name"] = "Gemini"
        target_views.append(updated)
    del views[OLD_CONTAINER]
    views[NEW_CONTAINER] = target_views

    valid, message = manifest_status(manifest)
    if not valid:
        raise CustomizationError(f"Post-transform manifest validation failed: {message}")
    write_json(path, manifest)
    return True


def desktop_naming_block(source: str) -> re.Match[str] | None:
    return re.search(r"const desktopNaming\s*=\s*\{(?P<body>.{0,2000}?)\n\s*\};", source, re.DOTALL)


def runtime_status(source: str) -> tuple[bool, str]:
    block = desktop_naming_block(source)
    if not block:
        return False, "desktopNaming block not found"
    locations = re.findall(r"viewLocation:\s*'([^']+)'", block.group("body"))
    ok = locations == ["auxiliarybar"]
    return ok, "runtime uses auxiliarybar" if ok else f"runtime locations: {locations!r}"


def patch_runtime(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    already_done, _ = runtime_status(source)
    if already_done:
        return False

    block = desktop_naming_block(source)
    if not block:
        raise CustomizationError("Antigravity's desktopNaming block was not found")
    old_body = block.group("body")
    if len(re.findall(r"viewLocation:\s*'sidebar'", old_body)) != 1:
        raise CustomizationError("Expected exactly one sidebar viewLocation in desktopNaming")
    new_body = re.sub(
        r"viewLocation:\s*'sidebar'",
        "viewLocation: 'auxiliarybar'",
        old_body,
        count=1,
    )
    patched = source[: block.start("body")] + new_body + source[block.end("body") :]
    valid, message = runtime_status(patched)
    if not valid:
        raise CustomizationError(f"Post-transform runtime validation failed: {message}")

    temporary = path.with_name(f".{path.name}.gemini.tmp")
    temporary.write_text(patched, encoding="utf-8")
    temporary.replace(path)
    return True


def read_json_state(connection: sqlite3.Connection, key: str):
    row = connection.execute("SELECT CAST(value AS TEXT) FROM ItemTable WHERE key = ?", (key,)).fetchone()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except json.JSONDecodeError as exc:
        raise CustomizationError(f"VS Code state key {key!r} is not valid JSON") from exc


def write_json_state(connection: sqlite3.Connection, key: str, value) -> None:
    connection.execute(
        "UPDATE ItemTable SET value = ? WHERE key = ?",
        (json.dumps(value, separators=(",", ":")), key),
    )


def update_layout(database: Path, extension_dir: Path) -> None:
    if not database.is_file():
        raise CustomizationError(f"VS Code global state database not found: {database}")
    with sqlite3.connect(database, timeout=15) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "DELETE FROM ItemTable WHERE key = ?",
            (f"{OLD_WORKBENCH_ID}.state.hidden",),
        )

        marker_key = "__$__targetStorageMarker"
        marker = read_json_state(connection, marker_key)
        if isinstance(marker, dict):
            marker.pop(f"{OLD_WORKBENCH_ID}.state.hidden", None)
            write_json_state(connection, marker_key, marker)

        for key in ("workbench.activity.pinnedViewlets2", "workbench.activity.placeholderViewlets"):
            entries = read_json_state(connection, key)
            if isinstance(entries, list):
                write_json_state(
                    connection,
                    key,
                    [item for item in entries if item.get("id") != OLD_WORKBENCH_ID],
                )

        pinned_key = "workbench.auxiliarybar.pinnedPanels"
        pinned = read_json_state(connection, pinned_key)
        if not isinstance(pinned, list):
            raise CustomizationError(f"VS Code state key {pinned_key!r} is missing or malformed")
        pinned = [item for item in pinned if item.get("id") not in (OLD_WORKBENCH_ID, NEW_WORKBENCH_ID)]
        pinned.append({"id": NEW_WORKBENCH_ID, "pinned": True, "visible": False, "order": 100})
        write_json_state(connection, pinned_key, pinned)

        placeholder_key = "workbench.auxiliarybar.placeholderPanels"
        placeholders = read_json_state(connection, placeholder_key)
        if not isinstance(placeholders, list):
            raise CustomizationError(f"VS Code state key {placeholder_key!r} is missing or malformed")
        placeholders = [
            item for item in placeholders if item.get("id") not in (OLD_WORKBENCH_ID, NEW_WORKBENCH_ID)
        ]
        placeholders.append(
            {
                "id": NEW_WORKBENCH_ID,
                "iconUrl": {"$mid": 1, "path": str(extension_dir / "img/logo.svg"), "scheme": "file"},
                "name": "Gemini",
                "isBuiltin": False,
                "views": [{}],
            }
        )
        write_json_state(connection, placeholder_key, placeholders)
        connection.commit()


def layout_status(database: Path) -> tuple[bool, str]:
    if not database.is_file():
        return False, f"state database not found: {database}"
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
        pinned = read_json_state(connection, "workbench.auxiliarybar.pinnedPanels")
        placeholders = read_json_state(connection, "workbench.auxiliarybar.placeholderPanels")
        activity_pins = read_json_state(connection, "workbench.activity.pinnedViewlets2") or []
        activity_placeholders = read_json_state(connection, "workbench.activity.placeholderViewlets") or []
    target_pins = [item for item in pinned or [] if item.get("id") == NEW_WORKBENCH_ID]
    target_placeholders = [item for item in placeholders or [] if item.get("id") == NEW_WORKBENCH_ID]
    old_entries = [
        item
        for item in [*activity_pins, *activity_placeholders]
        if item.get("id") == OLD_WORKBENCH_ID
    ]
    ok = len(target_pins) == 1 and len(target_placeholders) == 1 and not old_entries
    return ok, "layout pins Gemini in auxiliary bar" if ok else "layout state needs repair"


def backup_dir_for(version: str, backup_root: Path | None = None) -> Path:
    timestamp = dt.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    root = backup_root or (
        Path.home()
        / "Library/Application Support/codex-customizations/antigravity-gemini-sidebar/backups"
    )
    return root.expanduser().resolve() / f"{version}-{timestamp}"


def clear_scan_caches(user_dir: Path, extension_dir: Path, backup_dir: Path) -> int:
    code_root = user_dir.parent
    cache_root = code_root / "CachedProfilesData"
    moved = 0
    for cache in cache_root.glob("*/extensions.user.cache"):
        destination = backup_dir / f"{cache.parent.name}.extensions.user.cache"
        shutil.move(str(cache), destination)
        moved += 1
    registry = extension_dir.parent / "extensions.json"
    if registry.exists():
        registry.touch()
    return moved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without changing files")
    parser.add_argument("--skip-layout", action="store_true", help="do not update VS Code state or caches")
    parser.add_argument("--extension-dir", type=Path, help="explicit Antigravity extension directory")
    parser.add_argument(
        "--user-data-dir",
        type=Path,
        default=default_user_dir(),
        help="VS Code User directory (default: %(default)s)",
    )
    parser.add_argument("--backup-root", type=Path, help="override the backup parent directory")
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    extension_dir = discover_extension(args.extension_dir)
    package_path = extension_dir / "package.json"
    runtime_path = extension_dir / "extension.js"
    manifest = load_json(package_path)
    version = str(manifest.get("version", "unknown"))
    database = args.user_data_dir.expanduser().resolve() / "globalStorage/state.vscdb"

    if args.check:
        manifest_ok, manifest_message = manifest_status(manifest)
        runtime_ok, runtime_message = runtime_status(runtime_path.read_text(encoding="utf-8"))
        checks = [(manifest_ok, manifest_message), (runtime_ok, runtime_message)]
        if not args.skip_layout:
            checks.append(layout_status(database))
        print(f"Extension: {extension_dir} (version {version})")
        for ok, message in checks:
            print(f"[{'OK' if ok else 'FAIL'}] {message}")
        if all(ok for ok, _ in checks):
            print("Gemini customization: OK")
            return 0
        print("Gemini customization: NOT READY", file=sys.stderr)
        return 1

    backup_dir = backup_dir_for(version, args.backup_root)
    backup_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(package_path, backup_dir / "package.json")
    shutil.copy2(runtime_path, backup_dir / "extension.js")
    if not args.skip_layout and database.is_file():
        with sqlite3.connect(database) as source, sqlite3.connect(backup_dir / "global-state.vscdb") as target:
            source.backup(target)

    try:
        manifest_changed = patch_manifest(package_path)
        runtime_changed = patch_runtime(runtime_path)
        if not args.skip_layout:
            update_layout(database, extension_dir)
            moved_caches = clear_scan_caches(
                args.user_data_dir.expanduser().resolve(), extension_dir, backup_dir
            )
        else:
            moved_caches = 0
    except Exception:
        shutil.copy2(backup_dir / "package.json", package_path)
        shutil.copy2(backup_dir / "extension.js", runtime_path)
        database_backup = backup_dir / "global-state.vscdb"
        if database_backup.is_file():
            with sqlite3.connect(database_backup) as source, sqlite3.connect(database) as target:
                source.backup(target)
        raise

    print(f"Extension: {extension_dir} (version {version})")
    print(f"Backup: {backup_dir}")
    print(f"Manifest: {'updated' if manifest_changed else 'already customized'}")
    print(f"Runtime: {'updated' if runtime_changed else 'already customized'}")
    if not args.skip_layout:
        print(f"Layout: updated; scan caches moved: {moved_caches}")
    print("Fully quit VS Code with Cmd+Q, reopen it, then run this script with --check.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except CustomizationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
