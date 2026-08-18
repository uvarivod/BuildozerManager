## Context

The app builds Android APKs/AABs via Buildozer inside WSL. There is currently no way to sign release builds. The user must sign manually in the WSL terminal using `jarsigner` and `zipalign`. Profiles today store build settings (`sourcedir`, `spec_path`, `adb_path`, `wsl_dir`, `wsl_distro`, patches, exclusions) persisted as JSON in `data/profiles.json` via `ProfileStore`. Actions are modeled as an `Action` enum dispatched by `ActionRunner.run_action`, with per-action validation in `ActionRunner.validate_action`. WSL commands are executed via `wsl.exe --distribution <distro> --exec ...`. The profile editor screen builds its UI from `profile_editor_screen.kv` plus inline widgets.

## Goals / Non-Goals

**Goals:**
- Add certificate path + password fields to the profile (password stored base64-encoded, never plaintext).
- Add a "Check jarsigner and zipalign" button in the profile editor that verifies both tools run in WSL, with an inline success marker or a failure popup.
- Add a new "Signing Android App" action that: creates `signing_android_app/` in the WSL build dir, copies the built AAB from `bin/` plus the certificate into it, runs `jarsigner` with SHA1withRSA/SHA1 and the cert password, runs `zipalign -p 4` producing `<name>-signed.aab`, and copies the signed file back to `bin/`.
- Wire the action through the existing action chain UI and runner.

**Non-Goals:**
- Re-signing with APK Signature Scheme (apksigner) or Play App Signing upload keys.
- Signing APKs (only AAB flow as requested).
- Any changes to the existing Build/Pull/Run flows.
- Auto-detecting or managing the keystore beyond a file path + password.

## Decisions

### D1. Persist certificate fields as new Profile dataclass fields
Add `cert_path: str = ""` and `cert_password: str = ""` to `Profile`. `ProfileStore` reads/writes them like the other fields. `Validate`: password round-trips base64.

Rationale: keeps the existing store/schema pattern (whitelist `_PROFILE_FIELDS`) with minimal churn. Alternative (separate secrets store) rejected — out of scope, the base64 encoding is the requested level of protection, not OS-grade secret storage.

### D2. Password encoded as base64utf8 at the storage layer only
The UI and action runner work with the plaintext value; `ProfileStore.save_all` encodes `cert_password` via `base64.b64encode(value.encode("utf-8")).decode("ascii")`, and `load_all` decodes it back. Old/plaintext values encountered on load are migrated by decoding; values that fail to decode are treated as plaintext.

Rationale: isolates encoding in one place (storage service), matching the requirement "saves in data with base64 encoded". Alternative of encoding in the UI was rejected to avoid leaking the encoding concern into widgets.

### D3. Tool check implemented as a synchronous WSL command with inline marker
The Check button runs one WSL command: `wsl.exe --distribution <distro> --exec bash -c "command -v jarsigner && jarsigner -help >/dev/null && command -v zipalign && zipalign -h >/dev/null"`. On success, set a `signing_check_ok` marker near the button (e.g., a label "✓ jarsigner & zipalign OK"); on failure or empty wsl fields, show the failure popup with the requested exact text.

Rationale: `command -v` + a trivial `-h`/`-help` invocation verifies both presence and executability. Using WSL directly mirrors how ADB Check works locally. Alternative (parsing `/usr/bin/which` output only) rejected because it can report a path for a non-executable stub.

### D4. Signing action as a new Action enum member + WSLService method
Add `Action.SIGN_APK` with description "Sign Android App (AAB)". The flow lives in a new `WSLService.sign_apk(...)` method that shells out to `bash -c` running the whole flow, streaming output through the same log-callback pattern used by `exec_buildozer`. `ActionRunner` gains `_run_sign_apk` and `validate_action` gains `cert_path`, `cert_password`, `wsl_dir`, `wsl_distro` for `SIGN_APK`.

Rationale: keeps WSL command handling centralized in `WSLService`; a single `bash -c` script keeps the 6 steps atomic in WSL (matching the reference flow exactly) and streams logs line-by-line. Alternative — separate subprocess per step — rejected: more moving parts, easier to leave partial state, and slower.

Flow script (projected; exact quoting finalized during implementation):
1. `mkdir -p signing_android_app`
2. `cp <bin>/*.aab signing_android_app/`
3. `cp <cert_path> signing_android_app/`
4. `cd signing_android_app && jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore <cert_basename> -keypass <password> <*.aab> app`
   - uses the *copied* keystore basename inside the directory (matching "Copy there certificate file"). The keystore may live on any filesystem — WSL, Windows, or the Windows repo — so referencing the copy keeps paths predictable inside WSL regardless of the source location. We therefore always `cp <cert_path>` first and then refer to the copied basename.
5. `zipalign -p 4 <name>-release.aab <name>-signed.aab` (suffix mapping `-release` → `-signed`)
6. `cp signing_android_app/*-signed.aab <bin>/`

Log messages report each step's success/failure and the final copied signed file. A `SignatureFileNotFoundException` state check needs to fail gracefully (see D5).

### D5. Intermediate error handling inside the bash script
If AAB not found, jarsigner missing, or jarsigner/zipalign fails, the script prints a distinguishable marker line (`SIGNING_ERROR: <detail>`) and exits nonzero; `WSLService` surfaces it and `ActionRunner` reports `FAILED`. No partial return codes are treated as success.

Rationale: preserves the observable behavior from the specs (stop with Failed) without needing brittle log text parsing.

### D6. WSL-run check mirrors ADB check UX
The Check button requires non-empty `wsl_dir` and `wsl_distro`; otherwise it errors with a message listing missing fields (spec scenario). The success marker lives next to the button and is cleared on profile reload / field edits.

## Risks / Trade-offs

- **Keystore password in command line** → visible in `ps` inside WSL and in logs. Mitigation: password comes from the profile (base64 at rest only), never logged; note in help text that WSL is single-user in practice. A future enhancement could use a tempfile/env var, out of scope here.
- **`-keypass` vs `-storepass`** → for keystores where both are the same password the reference flow works as given; signing fails if storepass differs. Mitigation: log the jarsigner stderr verbatim so the user sees the correct error; documented as a known limitation.
- **Hardcoded `-release.aab` naming** → the built AAB must contain `-release` for the zipalign rename. Mitigation: script falls back to using the found AAB's actual basename and derives the signed name by replacing `-release` if present, else appending `-signed`; logged so the user sees actual names.
- **No cancellation support mid-signing** → signing is fast (<1 min typically); the bash script is run to completion. Acceptable trade-off for this flow.
- **jarsigner SHA1 deprecation warnings** → expected; tools still run. Logged but not treated as failure (matches the provided command).

## Migration Plan

- No schema migration needed: `Profiles` dataclass gets defaults, and store load tolerates missing keys (existing JSON unaffected). Old profiles load with `cert_path=""`, `cert_password=""`.
- Existing buildozer.spec/wsl dirs untouched.
- Rollback: revert the Profile fields plus the new action; nothing else changes.

## Open Questions

- None outstanding. Decisions: the Check button validates only the jarsigner/zipalign tools (not the certificate path — path existence is left to the signing action), and the signing script always copies the certificate into `signing_android_app/` first, then references the copied basename, since the keystore may reside on any filesystem (WSL, Windows, or the Windows repo).