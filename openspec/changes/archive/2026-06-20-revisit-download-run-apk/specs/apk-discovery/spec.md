# APK Discovery

## Purpose

Locate the built APK file in the WSL `.buildozer/bin/` directory by matching the expected filename from `buildozer.spec`, and extract package metadata needed for installation and launch.

## Requirements

### Requirement: System can find the APK in WSL matching buildozer.spec
The system SHALL locate the APK by searching `wsl_dir/bin/` (the Buildozer output directory, not `.buildozer/bin/`) for `*.apk` files whose stem starts with `<package.name>-<version>-`. The version is parsed from `buildozer.spec` (method 1: `version = X.Y.Z` line, or method 2: `version.regex` + `version.filename`). If no match with version, falls back to `<package.name>-` prefix. Among matching files, the newest by modification time is selected. The expected filename format is `<package.name>-<version>-<android.archs>-<debug/release>.apk`, where multiple archs are joined by `_`.

#### Scenario: Find APK matching spec with version
- **WHEN** a buildozer build has completed with `package.name = myapp` and `version = 1.1.0`
- **THEN** the system searches `wsl_dir/bin/` for `*.apk` files with stem starting with `myapp-1.1.0-`
- **THEN** the system picks the newest matching file

#### Scenario: Find APK with version fallback
- **WHEN** `buildozer.spec` has `version = 1.1.0` but no APK matches `myapp-1.1.0-` prefix
- **THEN** the system falls back to matching files with stem starting with `myapp-`
- **THEN** the system picks the newest matching file

#### Scenario: No APK found
- **WHEN** no `*.apk` files matching the spec exist in `wsl_dir/bin/`
- **THEN** the system returns an empty result

### Requirement: System can extract package name from local buildozer.spec
The system SHALL read the `buildozer.spec` file from the local source directory (`sourcedir/buildozer.spec`) to extract `package.name` and `package.domain` and combine them as `domain.name` to form the Android package name. The spec is read from the local filesystem, not from WSL.

#### Scenario: Extract package name from local spec
- **WHEN** `sourcedir/buildozer.spec` contains `package.name = myapp` and `package.domain = com.example`
- **THEN** the system returns `com.example.myapp` as the package name

#### Scenario: Spec file missing or malformed
- **WHEN** `sourcedir/buildozer.spec` is missing or the package fields are not found
- **THEN** the system returns an empty string and logs a warning
