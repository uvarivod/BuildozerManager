## 1. Data Model Changes

- [x] 1.1 Add `Action.PULL_APK = "pull_apk"` to the Action enum in `src/models/action.py`, keeping `Action.DOWNLOAD` as a deprecated alias

## 2. APK Discovery Service

- [x] 2.1 Create `src/services/apk_service.py` with `APKService` class
- [x] 2.2 Implement `find_latest_apk(profile) -> Path | None` — find newest `*.apk` file under WSL `.buildozer` directory (migrate from WSLService)
- [x] 2.3 Implement `get_package_name(profile) -> str` — parse `package.name` and `package.domain` from `buildozer.spec` in WSL directory
- [x] 2.4 Write unit tests in `tests/test_apk_service.py` for find_latest_apk and get_package_name

## 3. ADB Service Enhancements

- [x] 3.1 Add optional `device_serial: str | None` parameter to `install_apk()` — when provided, prepend `-s <serial>` to the ADB command
- [x] 3.2 Add optional `device_serial: str | None` parameter to `launch_app()` — when provided, prepend `-s <serial>` to the ADB command
- [x] 3.3 Write unit tests in `tests/test_adb_service.py` for install_apk and launch_app (including device serial parameter)

## 4. Action Runner Refactor

- [x] 4.1 In `_run_download()` — rename to `_run_pull_apk()`, return `Path | None` instead of `ActionState`, return the destination APK path on success
- [x] 4.2 In `_run_launch()` — use `APKService.get_package_name()` to extract the package name from buildozer.spec; pass it to `launch_app()` instead of empty string
- [x] 4.3 In `_run_launch()` — reuse the path returned by `_run_pull_apk()` instead of computing `dest_path` independently
- [x] 4.4 In `_run_launch()` — when `list_devices` returns multiple devices, log the list and install/launch on the first device (UI device selection to follow in a separate change)
- [x] 4.5 Wire `Action.PULL_APK` to `_run_pull_apk` in `run_action()` dispatch; keep `Action.DOWNLOAD` mapped to `_run_pull_apk` as well
- [x] 4.6 Update `validate_action()` to accept `PULL_APK` with the same required fields as `DOWNLOAD`

## 5. UI Updates

- [x] 5.1 In `src/kv/actions_screen.kv` — change button text from "Download" to "Pull APK"
- [x] 5.2 In `src/screens/actions_screen.py` — map `'pull_apk'` action string to `Action.PULL_APK`

## 6. Scenario Service Updates

- [x] 6.1 In `src/services/scenario_service.py` — update predefined scenarios to use `Action.PULL_APK` instead of `Action.DOWNLOAD` where applicable
- [x] 6.2 Verify backward compatibility — existing saved scenarios using `Action.DOWNLOAD` still work

## 7. Test Updates

- [x] 7.1 Update `tests/test_action_runner.py` — add test for PULL_APK validation, update DOWNLOAD test references
- [x] 7.2 Add tests for `_run_launch` with package name extraction
