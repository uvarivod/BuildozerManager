## Context

The old `WSLService.clean_wsl_dir()` method used `profile.delete_exclusions` (default `[".buildozer"]`) to decide what to keep during cleanup. This conflated two different concerns: (1) preserving the buildozer cache, and (2) letting users retain arbitrary files. The standalone "Clean" button was confusing because its behavior depended on the exclusion list, and `buildozer clean` (the buildozer command) had the same name.

## Goals / Non-Goals

**Goals:**
- Replace `clean_wsl_dir()` with two unambiguous methods: `sync_src()` and `clean_wsl_project()`
- Add `SYNC_SRC` as a standalone Action with its own UI button
- Keep `delete_exclusions` on Profile for user's custom retain items only
- `sync_src()` always preserves `.buildozer` (hardcoded) + user's `delete_exclusions`
- `clean_wsl_project()` ignores all exclusions
- Add `buildozer clean` step to "Clean Build" scenario
- Remove the `.buildozer` protection popup
- All actions exposed as standalone UI buttons for development transparency

**Non-Goals:**
- Not changing how source copying works (SyncSRC reuses existing copy logic)
- Not changing the scenario builder UI (separate feature)
- Not changing Patch, Pull APK, or Run actions

## Decisions

1. **Two separate WSLService methods instead of one parameterized method**
   - `sync_src()`: delete (preserve .buildozer + user exclusions) → copy source — used by both standalone SYNC_SRC action and internally by BUILD
   - `clean_wsl_project()`: delete everything — used by both standalone CLEAN action and internally by Clean Build scenarios

2. **Hardcoded `.buildozer` + user's `delete_exclusions` in SyncSRC**
   - `.buildozer` is always preserved (hardcoded) so build cache is never accidentally lost
   - `delete_exclusions` (default `[]`) lets users retain custom files across syncs
   - CleanWSLProject ignores all exclusions — true nuke

3. **`delete_exclusions` kept on Profile with default `[]`**
   - The old default was `[".buildozer"]` which made it look like a buildozer-specific setting
   - Now it's purely for user's custom items (e.g., "node_modules", "big_downloads")
   - `sync_src` merges `{".buildozer"} | set(profile.delete_exclusions)`

4. **`buildozer clean` added to Clean Build scenario**
   - Since CleanWSLProject deletes `.buildozer`, running `buildozer clean` afterwards is harmless but semantically correct

5. **All actions exposed as standalone buttons**
   - SYNC_SRC, CLEAN, BUILD, PATCH, PULL_APK, RUN all have buttons
   - Useful for development/testing — each primitive can be invoked independently
   - The scenario system still provides the composed workflows

## Risks / Trade-offs

- **[Risk] Existing saved profiles have `delete_exclusions: [".buildozer"]`** → `ProfileStore.load_all()` filters unknown fields via `_PROFILE_FIELDS` set. Loading a profile with `.buildozer` in the list is harmless — `sync_src` already hardcodes it.
- **[Risk] User removes `.buildozer` from their `delete_exclusions` thinking it will be deleted** → `.buildozer` is always preserved by `sync_src` regardless of the list. No risk.
- **[Risk] Custom scenarios that use CLEAN action** → CLEAN still maps to CleanWSLProject. Custom scenarios continue to work unchanged.
