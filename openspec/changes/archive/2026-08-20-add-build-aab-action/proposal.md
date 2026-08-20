## Why

Users currently can only produce debug APK builds through the Build action (`buildozer android debug`). Releasing an AAB (`buildozer android release`) for Play Store submission requires manual terminal work outside the app. This change adds a dedicated Build AAB action that mirrors the existing Build action but runs the release build command, so an AAB can be produced with one click.

## What Changes

- Add a new **Build AAB** action (`Action.BUILD_AAB`) to the action system.
- The action runs `buildozer android release` (instead of the default `buildozer android debug` used by Build) in the profile's WSL working directory.
- The action reuses the existing buildozer execution pipeline (PATH setup, `cd` into the WSL build dir, live output parsing, cancellation, and progress logging) unchanged.
- The new action appears automatically in the scenario editor action palette and can be added to scenarios / run separately like any other action.
- No new profile fields are required; validation matches the existing Build action (`sourcedir`, `wsl_dir`, `wsl_distro`).

## Capabilities

### New Capabilities

### Modified Capabilities
- `action-execution`: New "Build AAB" action that runs `buildozer android release` in the WSL working directory with the same pipeline, validation, and status reporting as the existing Build action.

## Impact

- `src/models/action.py` — new `Action.BUILD_AAB` enum member + description entry
- `src/services/action_runner.py` — dispatch for `BUILD_AAB` in `run_action`, `validate_action` entry, and new `_run_build_aab` handler reusing the build pipeline
- `src/services/wsl_service.py` — reuse existing `exec_buildozer`, passing `command="buildozer android release"` (no structural changes expected)
- `src/screens/scenario_editor_screen.py` — automatically picks up the new enum member (no code change expected)
- `src/screens/actions_screen.py` / `action_card.py` — automatically rendered via the generic action card (no code change expected)