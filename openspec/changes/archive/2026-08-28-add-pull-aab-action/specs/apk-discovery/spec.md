## ADDED Requirements

### Requirement: System can find the AAB in WSL matching buildozer.spec
The system SHALL locate the AAB by searching `wsl_dir/bin/` for `*.aab` files whose stem starts with `<package.name>-<version>-`. The search is performed via the Windows network path (`\\wsl$\<distro>\<dir>\bin`), not via a WSL command. The version is parsed from `buildozer.spec` (method 1: `version = X.Y.Z` line, or method 2: `version.regex` + `version.filename`). If no match with version, falls back to `<package.name>-` prefix. Among matching files, the newest by modification time is selected. The expected filename format is `<package.name>-<version>-<android.archs>-<release>.aab`.

#### Scenario: Find AAB matching spec with version
- **WHEN** a release build has completed with `package.name = myapp` and `version = 1.1.0`
- **THEN** the system searches `wsl_dir/bin/` for `*.aab` files with stem starting with `myapp-1.1.0-`
- **THEN** the system picks the newest matching file

#### Scenario: Find AAB with version fallback
- **WHEN** `buildozer.spec` has `version = 1.1.0` but no AAB matches `myapp-1.1.0-` prefix
- **THEN** the system falls back to matching files with stem starting with `myapp-`
- **THEN** the system picks the newest matching file

#### Scenario: No AAB found
- **WHEN** no `*.aab` files matching the spec exist in `wsl_dir/bin/`
- **THEN** the system returns an empty result
