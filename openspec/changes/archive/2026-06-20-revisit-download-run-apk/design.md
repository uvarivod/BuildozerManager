## Context

The current Download and Run APK workflow has critical flaws. The Run action (`_run_launch`) calls `launch_app` with an empty package name `""`, causing `adb shell monkey -p "" ...` to always fail. The Download action merely copies the APK from WSL filesystem — it does not extract any metadata. The Run action independently discovers the latest APK, downloads it redundantly, and attempts to install and launch without ever knowing the package name. There is no device selection when multiple ADB devices are connected.

## Goals / Non-Goals

**Goals:**
- Extract package name (and optionally activity) from the APK or buildozer.spec so launch works correctly
- Allow the user to select which ADB device to install/launch on when multiple are connected
- Rename "Download" to "Pull APK" to accurately describe the action
- Return APK path from Pull APK and reuse it in the Run action to eliminate redundant WSL scans
- Add test coverage for ADB service and APK discovery
- All changes backward compatible at the data model level (profiles, stored scenarios)

**Non-Goals:**
- No change to the ADB device detection mechanism itself
- No network-based APK download (Pull APK remains a WSL-to-Windows copy)
- No in-app APK viewer or installer outside the build pipeline

## Decisions

1. **Extract package name from buildozer.spec** — Rather than parsing the APK binary (which requires aapt/aapt2 or similar tools), read the `package.name` and `package.domain` fields from `buildozer.spec` and combine them as `domain.name`. This avoids external tool dependencies and matches what Buildozer itself does. The spec file is already available via the WSL path.

2. **Search `wsl_dir/bin/` not `.buildozer/bin/`** — Buildozer places output APKs in `wsl_dir/bin/` (the project-level bin directory), not inside `.buildozer/bin/`.

3. **Match APK filename by `<package.name>-<version>-` prefix with fallback** — The APK filename follows the pattern `<package.name>-<version>-<android.archs>-<debug/release>.apk` (multiple archs joined by `_`). First try matching by `<package.name>-<version>-` prefix. If no match, fall back to `<package.name>-` prefix to handle version mismatches. Version is parsed from the spec using method 1 (`version = X.Y.Z`) or method 2 (`version.regex` + `version.filename` reading a source file).

4. **APK discovery as a dedicated service** — Create `APKService` that wraps both finding APKs in WSL and parsing package metadata. This follows the existing service pattern (WSLService, ADBService) and keeps concerns separated rather than bloating WSLService.

5. **Device selection via simple index picker** — When `list_devices` returns >1 device, show a popup in the UI. For programmatic/non-UI scenarios, default to the first device. The ADB service takes a device serial as an optional parameter.

6. **Rename DOWNLOAD to PULL_APK** — Add `Action.PULL_APK = "pull_apk"` alongside `Action.DOWNLOAD` for backward compatibility. The DOWNLOAD value is deprecated but not removed immediately to avoid breaking saved scenarios. The UI uses the new name.

7. **Return APK path from Pull APK** — Change `_run_download` (and its renamed version) to return the destination path on success, allowing the caller to pass it to the install step without re-scanning WSL.

## Risks / Trade-offs

- [Relying on buildozer.spec for package name] → If the spec file is missing or malformed, the launch will fail. Fall back to trying `aapt dump badging` if available on the host, or show a meaningful error.
- [Backward compat for DOWNLOAD action] → Keeping the old enum value adds a small maintenance burden but avoids breaking existing saved scenarios and custom scenarios.
- [No aapt dependency] → Simpler setup but less accurate APK metadata. The package name from buildozer.spec is authoritative since Buildozer itself generated the APK from that spec.
