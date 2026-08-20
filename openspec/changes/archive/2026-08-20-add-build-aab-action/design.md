## Context

The app executes a fixed set of build pipeline actions (`Action` enum in `src/models/action.py`), dispatched through `ActionRunner.run_action` (`src/services/action_runner.py`). The Build action (`_run_build`) delegates to `WSLService.exec_buildozer` (`src/services/wsl_service.py`), which builds a shell command `export PATH=$PATH:~/.local/bin/; cd <dir> && <command>` and streams parsed output back. `exec_buildozer` already accepts a `command` parameter defaulting to `"buildozer android debug"` — so a release build only requires passing `"buildozer android release"`.

The scenario editor auto-discovers actions by iterating `for action in Action:` (`src/screens/scenario_editor_screen.py:373`), and the actions screen renders any action generically via `ActionCard`, so a new enum member surfaces in the UI without additional screen changes.

## Goals / Non-Goals

**Goals:**
- Add a Build AAB action that runs `buildozer android release` in the WSL working directory.
- Reuse the existing buildozer execution pipeline (PATH setup, output parsing, progress logging, cancellation) unchanged.
- Match the existing Build action's validation profile (`sourcedir`, `wsl_dir`, `wsl_distro`).

**Non-Goals:**
- No changes to the signing flow, APK pull, or any other action.
- No new profile fields or UI screens.
- No changes to `WSLService.exec_buildozer`'s behavior.

## Decisions

**1. New `Action.BUILD_AAB` enum member over a parameterized existing action.**
Future-proofing: the enum is the source of truth for the action palette and per-action descriptions. A dedicated member keeps naming/validation/dispatch explicit and matches how `SIGN_APK` was added.

**2. Reuse `exec_buildozer` with `command="buildozer android release"`.**
The release command differs only by the buildozer subcommand. Rather than duplicating the WSL execution logic, call the existing method with the explicit command. The custom `command` parameter already exists and defaults to the debug build, so no signature changes are required.

**3. `_run_build_aab` mirrors `_run_build`.**
It performs the same steps: check WSL running → warn if `buildozer.spec` missing in WSL → run `exec_buildozer(order=...)` → check cancellation → map result to `SUCCESS`/`FAILED`/`CANCELLED`. This keeps behavior per-action consistent and testable.

**4. Validation reuses the Build action's required fields.**
A release build needs the same profile inputs as a debug build, so `validate_action` maps `BUILD_AAB` to `["sourcedir", "wsl_dir", "wsl_distro"]`.

**5. No UI changes required.**
The scenario editor (`for action in Action:`), actions screen (`_build_action_chain` generic card logic), and scenario orchestration (`ScenarioService`) all handle new enum members automatically. Only the description dictionary needs a new entry.

## Risks / Trade-offs

- [Release builds can fail for many reasons (keystore, resource issues, longer build times)] → Mitigation: the existing parsed-output logging shows buildozer's failure line and the action returns `FAILED`; users see the same diagnostics as the debug build.
- [Enum iteration order places the new chip in the palette wherever `BUILD_AAB` is declared] → Mitigation: place the member near `BUILD` so the palette remains logical; this is cosmetic only.
- [Scenarios persisted to disk store raw enum names] → Mitigation: existing scenarios are unaffected (no removal or rename of existing members); new member is additive, and `Enum` name serialization stays stable across reloads.