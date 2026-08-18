## 1. Profile Model & Storage

- [x] 1.1 Add `cert_path: str = ""` and `cert_password: str = ""` fields to `Profile` dataclass in `src/models/profile.py`
- [x] 1.2 Add `cert_path`, `cert_password` to `_PROFILE_FIELDS` whitelist in `src/services/storage_service.py`
- [x] 1.3 Encode `cert_password` as UTF-8 base64 (via `base64.b64encode`) when persisting in `ProfileStore.save_all`
- [x] 1.4 Decode `cert_password` from base64 (tolerating plaintext/migrated values) in `ProfileStore.load_all`
- [x] 1.5 Add unit tests for base64 round-trip + plaintext migration in `tests/test_storage_service.py`

## 2. WSL Service: Tool Check & Signing

- [x] 2.1 Add `WSLService.check_signing_tools(profile)` that runs `command -v jarsigner && jarsigner -help >/dev/null && command -v zipalign && zipalign -h >/dev/null` in WSL and returns success + error detail; guard on empty `wsl_dir`/`wsl_distro`
- [x] 2.2 Add `WSLService.sign_apk(profile, log_callback, cancel_check)` implementing the signing flow (create `signing_android_app/`, copy `bin/*.aab` + cert, run `jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore <cert> -keypass <password> <aab>.aab app`, run `zipalign -p 4 <name>-release.aab <name>-signed.aab`, copy `*-signed.aab` back to `bin/`) via a single `bash -c` with streamed/parsed logging
- [x] 2.3 Ensure `sign_apk` derives the signed filename by replacing `-release` with `-signed` (fallback: append `-signed`) and logs a recognizable `SIGNING_ERROR:` marker line plus nonzero exit on any step failure
- [x] 2.4 Add unit tests for filename derivation and tool-check success/failure in `tests/test_wsl_service.py`

## 3. New Action Enum & Runner

- [x] 3.1 Add `Action.SIGN_APK` to `src/models/action.py` with description "Sign Android App (AAB)"
- [x] 3.2 Add `SIGN_APK: ["cert_path", "cert_password", "wsl_dir", "wsl_distro"]` to `ActionRunner.validate_action`
- [x] 3.3 Add `_run_sign_apk` in `src/services/action_runner.py` that checks WSL is running, calls `_wsl.sign_apk`, logs each step, and maps result to SUCCESS/FAILED/CANCELLED
- [x] 3.4 Register `SIGN_APK` dispatch in `run_action` to call `_run_sign_apk`
- [x] 3.5 Add tests for validation + runner dispatch in `tests/test_action_runner.py`

## 4. Profile Editor UI: Fields & Check Button

- [x] 4.1 Add `cert_path_input` and `cert_password_input` ObjectProperties and .kv widgets (text + password fields) with a Browse button for the certificate file (`_browse_cert_path`) in the profile editor
- [x] 4.2 Load/save/clear the new fields in `profile_editor_screen.py` (`load_profile`, `clear_fields`, `_build_profile`)
- [x] 4.3 Add a "Check jarsigner and zipalign" button calling `_check_signing_tools` using `WSLService.check_signing_tools`
- [x] 4.4 Show success marker label near the button on check pass; on failure or missing wsl fields show the failure popup with the exact message:
  `<jarsigner>,<zipalign> Not Found
  <jarsigner>,<zipalign> should be installed in WSL and added to PATH.
  This is required for Signing Android App Action only`
- [x] 4.5 Update profile editor help text to document the cert fields and check button
- [x] 4.6 Add/update UI tests in `tests/test_profile_editor_screen.py` covering populate, save, browse, and check success/failure

## 5. Action Chain UI Wiring

- [x] 5.1 Register `SIGN_APK` in the action chain/action cards UI (actions_screen / action_card or scenario definition) so it appears and can run
- [x] 5.2 Update any action-name lookup/description tables to include `SIGN_APK`
- [x] 5.3 Add tests verifying the action appears in the chain and dispatches through the runner

## 6. Verification

- [x] 6.1 Run full test suite (`python -m pytest`) and fix regressions
- [x] 6.2 Manually verify profile save/load preserves base64 password and cert path fields
- [x] 6.3 Manually verify Check button success marker and failure popup text
- [x] 6.4 Manually verify Signing Android App action end-to-end in WSL (signed AAB appears in `bin/`)

