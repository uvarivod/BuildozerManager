## Why

The Download and Run APK workflow is broken — the Run action passes an empty package name to ADB, making app launch always fail. Additionally, the Download action name is misleading (it copies from WSL, not a network download), there is no device selection when multiple ADB devices are connected, and the system never extracts package metadata from the APK or buildozer.spec.

## What Changes

- Fix the Run action to extract the package name from the buildozer.spec (or APK) and pass it to ADB launch
- Add device selection when multiple ADB devices are detected
- Rename "Download" action to "Pull APK" for clarity
- Return the APK path from the Download action and reuse it in Run to avoid redundant WSL lookups
- Add a dedicated APK discovery service to centralize finding and parsing APK metadata
- Add comprehensive tests for ADB service and APK discovery

## Capabilities

### New Capabilities
- `apk-discovery`: Finding APK files in WSL `.buildozer` and extracting package name, version, and activity from APK metadata

### Modified Capabilities
- `adb-integration`: Launch requirement updated to use package name extracted from APK/buildozer.spec; add device selection requirement for multi-device scenarios
- `action-execution`: Download action renamed to Pull APK; Download returns the APK path for downstream use; Run action passes package name to launch

## Impact

- `src/services/action_runner.py`: Fix empty package name bug, restructure Download/Run data flow, rename Download action
- `src/services/adb_service.py`: Add device selection support, possibly package name extraction helper
- `src/services/wsl_service.py`: May need APK metadata extraction
- `src/models/action.py`: Rename DOWNLOAD enum value (or add PULL alternatve)
- `src/screens/actions_screen.py`, `src/kv/actions_screen.kv`: UI button label change
- `src/services/scenario_service.py`: Update scenario action references
- `tests/test_adb_service.py`: New test file for ADB service
- `tests/test_wsl_service.py`: Add tests for find_apk_in_wsl
