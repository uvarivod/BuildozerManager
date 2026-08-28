## Why

Users can produce release AABs with the Build AAB action (`buildozer android release`) but there is no matching pull step to copy the resulting `*.aab` from the WSL `bin/` directory back to the Windows project. The existing Pull APK action only handles `*.apk`. Users must manually locate and copy the AAB via Explorer/WSL, which breaks the scenario chain that expects a one-click build→pull flow for release artifacts.

## What Changes

- Add a new **Pull AAB** action (`Action.PULL_AAB`) mirroring Pull APK but targeting `*.aab` files in `wsl_dir/bin/`.
- Locate the newest matching AAB by `<package.name>-<version>-` (falling back to `<package.name>-`) prefix, using `buildozer.spec` for the expected name — same discovery logic as APK but with `.aab` extension.
- Copy the selected AAB to `sourcedir/bin/` on Windows with the same detailed logging (search path, found file, copy destination, success/replace message).
- Reuse the existing WSL network path (`\\wsl$\<distro>\<dir>\bin`) — no WSL command.
- No new profile fields; validation matches Pull APK (`sourcedir`, `wsl_dir`, `wsl_distro`).
- The new action appears automatically in the scenario editor palette and can be added to scenarios / run separately.

## Capabilities

### New Capabilities

### Modified Capabilities
- `action-execution`: New "Pull AAB" action that locates and copies the built `*.aab` from the WSL `bin/` directory to `sourcedir/bin/`.
- `apk-discovery`: Extend artifact discovery to handle `*.aab` (find latest AAB by `<package.name>-<version>-` / `<package.name>-` prefix).

## Impact

- `src/models/action.py` — new `Action.PULL_AAB` enum member + description entry
- `src/services/apk_service.py` — new `find_latest_aab` method (mirrors `find_latest_apk` with `*.aab` pattern)
- `src/services/action_runner.py` — `validate_action` entry, dispatch branch, and new `_run_pull_aab` handler (mirrors `_run_pull_apk`)
- `src/services/scenario_service.py` — no code change (predefined scenarios unaffected; new action is opt-in)
- `src/screens/scenario_editor_screen.py` / `src/screens/actions_screen.py` — automatically pick up the new enum member (no code change expected)
