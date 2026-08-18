## Why

Users cannot sign their release AAB with a keystore from within the app. Signing currently requires manual WSL terminal work: running `jarsigner` and `zipalign` by hand, locating the built AAB, and copying signed output back. This change adds a dedicated, automated Signing Android App action plus per-profile certificate configuration, so the whole signing flow is one click.

## What Changes

- Add 2 new fields to the profile editor:
  1. **Path to certificate** — path to the certificate/keystore file
  2. **Password for certificate** — stored in `data/profiles.json` as base64-encoded (not plaintext)
- Add a **Check jarsigner and zipalign** button in the profile editor next to those fields:
  - Runs `jarsigner` and `zipalign` successfully inside Ubuntu (WSL)
  - On success, shows a marker (e.g. a check indicator) near the button that the check passed
  - On failure, shows a popup:
    - `<jarsigner>,<zipalign> Not Found`
    - `<jarsigner>,<zipalign> should be installed in WSL and added to PATH.`
    - `This is required for Signing Android App Action only`
- Add a new **Signing Android App** action with this flow:
  1. Create `signing_android_app` directory in the WSL Build Directory
  2. Copy the built `*.aab` file from WSL Build Directory/`bin` into it
  3. Copy the certificate file into it
  4. Run `jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore <certificate file> -keypass <Password for certificate> <copied *.aab> app`
  5. Run `zipalign -p 4 <aabfilename>-release.aab <aabfilename>-signed.aab`
  6. Copy signed files back to WSL Build Directory/`bin`
- Extend the `Action` enum with the new signing action and add a description.

## Capabilities

### New Capabilities
- `signing-tool-check`: Verification that `jarsigner` and `zipalign` are installed and on PATH in the WSL distribution, triggered from the profile editor.

### Modified Capabilities
- `profile-management`: Per-profile certificate path and base64-encoded password fields, plus the Check jarsigner/zipalign button in the profile editor.
- `action-execution`: New "Signing Android App" action that signs and aligns the built AAB inside WSL.

## Impact

- `src/models/profile.py` — two new dataclass fields (`cert_path`, `cert_password`) with base64 encoding
- `src/models/action.py` — new `Action.SIGN_APK` enum member + description
- `src/services/storage_service.py` — persist/load new profile fields (base64 encoding of password)
- `src/services/wsl_service.py` — new methods to create signing dir, copy AAB/cert, run `jarsigner`/`zipalign`, copy signed AAB back to `bin`
- `src/screens/profile_editor_screen.py` — two new fields + Check button (success marker / failure popup)
- `src/screens/actions_screen.py` / `action_runner.py` — wiring the new action into the chain and execution
- `src/services/action_runner.py` — new handler for the signing action flow