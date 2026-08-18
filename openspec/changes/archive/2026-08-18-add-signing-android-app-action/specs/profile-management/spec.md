## MODIFIED Requirements

### Requirement: Profile stores all build settings
Each profile SHALL store: name, sourcedir, buildozer spec path, adb path, excluded files/folders, WSL Build Directory, WSL Distribution name, patch list, and delete_exclusions list (items preserved during SyncSRC). In addition, each profile SHALL store the certificate path (`cert_path`) and the certificate password (`cert_password`). The password SHALL be persisted base64-encoded, never in plaintext.

#### Scenario: Edit profile settings
- **WHEN** the user selects a profile and modifies any setting field, or clicks Browse to select a source directory, buildozer.spec, ADB path, or WSL Build Directory via the file chooser
- **THEN** the change is reflected in the UI immediately and persisted on save

#### Scenario: Certificate fields persisted securely
- **WHEN** the user saves a profile with a certificate path and certificate password set
- **THEN** the profile stores the certificate path as plaintext and the password base64-encoded
- **THEN** on load, the password is decoded from base64 for use by the Signing Android App action

#### Scenario: Browse for source directory
- **WHEN** the user clicks "Browse" next to the Source Directory field
- **THEN** a directory chooser dialog opens pre-populated with the current path (if any)
- **THEN** selecting a directory fills the text input with the chosen path
- **THEN** if the chosen directory contains `buildozer.spec`, a confirmation popup asks "We found buildozer.spec in the folder you chose. Do you want to use it?"
- **THEN** if the user clicks "Yes", the buildozer spec path field is populated with the path to that file
- **THEN** if the user clicks "No", the popup closes with no further action

### Requirement: User can browse for certificate file
The system SHALL provide a Browse button next to the Path to certificate field that opens a file chooser dialog for selecting the certificate/keystore file.

#### Scenario: Browse for certificate file
- **WHEN** the user clicks "Browse" next to the Path to certificate field
- **THEN** a file chooser dialog opens pre-populated with the current path (if any) or the source directory path
- **THEN** selecting a certificate/keystore file fills the text input with its full path

### Requirement: User can enter certificate password
The system SHALL provide a password input field for the certificate password in the profile editor. The password SHALL be base64-encoded when persisted.

#### Scenario: Enter certificate password
- **WHEN** the user types a certificate password and saves the profile
- **THEN** the password is stored base64-encoded in the profile data
- **THEN** the field displays the saved value masked or as-is on reload