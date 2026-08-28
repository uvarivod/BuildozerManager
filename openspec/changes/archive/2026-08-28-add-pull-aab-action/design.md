## Context

The app builds Android artifacts in WSL and copies them back to the Windows project via the Pull APK action (`src/services/action_runner.py:_run_pull_apk`). That handler delegates discovery to `APKService.find_latest_apk` (`src/services/apk_service.py`), which searches `\\wsl$\<distro>\<dir>\bin` for `*.apk` whose stems match `<package.name>-<version>-` (falling back to `<package.name>-`), then copies the newest match to `sourcedir/bin/`. The Build AAB action now produces `*.aab` in the same `bin/` directory, but there is no pull step for it — users must copy the AAB manually, breaking the scenario chain for release builds. Discovery, logging, and copy are all local filesystem operations (WSL network path), not WSL commands.

## Goals / Non-Goals

**Goals:**
- Add a Pull AAB action that locates and copies the built `*.aab` from the WSL `bin/` directory to `sourcedir/bin/` with the same discovery rules and logging as Pull APK.
- Keep the action available in the scenario editor palette and runnable separately, consistent with Pull APK.

**Non-Goals:**
- No changes to the signing flow, Run, or any other action.
- No new profile fields or UI screens.
- No change to predefined scenarios (new action is opt-in).

## Decisions

**1. New `Action.PULL_AAB` enum member alongside `PULL_APK`.**
Keeps naming/dispatch/validation explicit and matches how `BUILD_AAB` and `PULL_APK` are modeled. The scenario editor iterates `Action` and surfaces the new chip automatically; `_action_label` in `scenario_editor_screen.py` already preserves the `AAB` acronym.

**2. `APKService.find_latest_aab` as a sibling to `find_latest_apk`.**
Extract the common prefix logic (`get_short_name` + `get_version` + prefix matching + newest-by-mtime) into a small helper `_find_latest_by_ext(profile, ext)` shared by `find_latest_apk(ext="apk")` and `find_latest_aab(ext="aab")`. This avoids duplicating the version/prefix fallback and keeps the rglob/filter identical except for the glob pattern (`*.aab` vs `*.apk`). A single generalized method is simpler than a separate service.

**3. `_run_pull_aab` mirrors `_run_pull_apk`.**
Steps: verify `buildozer.spec` exists locally → log the WSL `bin` search path → call `find_latest_aab` → handle not-found (log "Missed" + folder contents) → copy to `sourcedir/bin/` with replace/success message. Same error messages and log levels so users see consistent diagnostics. Validation reuses Pull APK's required fields (`sourcedir`, `wsl_dir`, `wsl_distro`).

**4. No `WSLService` change.**
Discovery and copy use the Windows network path `\\wsl$\<distro>` already, so no WSL command or `WSLService` modification is needed — only `APKService` and `ActionRunner`.

## Risks / Trade-offs

- [No AAB produced yet] → Mitigation: handler logs search path and folder contents on miss, returns `FAILED`; same UX as Pull APK when no artifact exists.
- [Multiple AABs match the prefix] → Mitigation: pick newest by mtime, same rule as APK; deterministic for versioned builds.
- [Small duplication if helper not extracted cleanly] → Mitigation: centralize `_find_latest_by_ext` so APK/AAB stay consistent in the future.

## Migration Plan

No data migration. Existing scenarios/persistence are unaffected (new enum member is additive). Users add Pull AAB to scenarios manually. Rollback: remove enum member and handler; scenarios containing it will show the missing-action guard already in the scenario editor.

## Open Questions

- None.
