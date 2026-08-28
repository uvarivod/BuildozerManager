## ADDED Requirements

### Requirement: User can execute the Pull AAB action
The system SHALL provide a "Pull AAB" action that locates the built `*.aab` in the WSL `bin/` directory (project-level `bin`, not `.buildozer/bin/`) by matching the expected filename derived from `buildozer.spec` and copies it to `sourcedir/bin/` on Windows. The search is performed via the Windows network path (`\\wsl$\<distro>\<dir>\bin`), not via a WSL command. The action SHALL log the search path, whether a match was found, and the copy result, consistent with the existing Pull APK behavior but for `*.aab`.

#### Scenario: Pull AAB after release build
- **WHEN** the user runs Pull AAB after a successful Build AAB
- **THEN** the system reads `buildozer.spec` to derive the expected AAB name (package name + version)
- **THEN** the system searches `wsl_dir/bin/` for matching `*.aab` files
- **THEN** the system logs which AAB was selected
- **THEN** the system copies it to `sourcedir/bin/`
- **THEN** the system logs the copied AAB filename, source WSL path, and destination path

#### Scenario: No buildozer.spec found
- **WHEN** the `buildozer.spec` file does not exist in the local sourcedir
- **THEN** the system logs an error: "buildozer.spec not found"
- **THEN** the action stops immediately with status Failed

#### Scenario: No matching AAB found
- **WHEN** no AAB file matching the spec name is found in `wsl_dir/bin/`
- **THEN** the system logs the search path and expected filename pattern
- **THEN** the system returns an empty result and sets action status to Failed

#### Scenario: Pull AAB fails validation if paths are empty
- **WHEN** the profile has empty sourcedir, wsl_dir, or wsl_distro
- **THEN** the action is rejected with a message listing missing fields

#### Scenario: Pull AAB is available in the scenario editor
- **WHEN** the user opens the scenario editor
- **THEN** a Pull AAB action chip is available in the action palette (labeled "Pull_AAB")
- **THEN** adding it to a scenario inserts `Action.PULL_AAB` into the action sequence
