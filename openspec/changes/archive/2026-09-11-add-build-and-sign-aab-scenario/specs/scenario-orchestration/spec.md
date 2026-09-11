## MODIFIED Requirements

### Requirement: System provides precisely two predefined scenarios
The system SHALL include exactly three built-in scenarios: "Full Clean build", "Rebuild", and "Build and Sign AAB".

#### Scenario: Full Clean build
- **WHEN** the user selects "Full Clean build"
- **THEN** the system runs CLEAN (delete everything in WSL working directory including `.buildozer`)
- **THEN** the system runs SYNC_SRC (copy fresh source preserving exclusions)
- **THEN** the system runs BUILD (buildozer build)
- **THEN** the system runs PATCH (apply all active patches)
- **THEN** the system runs BUILD again (rebuild with patches applied)
- **THEN** the system runs PULL_APK (copy APK from WSL to local sourcedir/bin)
- **THEN** the system runs RUN (install APK via ADB and launch on device)

#### Scenario: Rebuild
- **WHEN** the user selects "Rebuild"
- **THEN** the system runs SYNC_SRC (copy fresh source preserving exclusions)
- **THEN** the system runs BUILD (buildozer build)
- **THEN** the system runs PULL_APK (copy APK from WSL to local sourcedir/bin)
- **THEN** the system runs RUN (install APK via ADB and launch on device)

#### Scenario: Build and Sign AAB
- **WHEN** the user selects "Build and Sign AAB"
- **THEN** the system runs BUILD_AAB (buildozer android release)
- **THEN** the system runs SIGN_APK (sign and zipalign the AAB with the configured keystore)
- **THEN** the system runs PULL_AAB (copy signed AAB from WSL bin to local sourcedir/bin)

### Requirement: Predefined scenarios are not editable
Predefined scenarios ("Full Clean build", "Rebuild", "Build and Sign AAB") SHALL NOT be editable or deletable via the Scenario Editor. Their action sequences, names, and descriptions SHALL be fixed.

#### Scenario: Opening predefined scenario shows read-only
- **WHEN** the user selects a predefined scenario in the Scenario Editor
- **THEN** all editing controls are disabled
- **THEN** name and description fields are read-only
- **THEN** the delete button is hidden
