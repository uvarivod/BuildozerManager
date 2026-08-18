## ADDED Requirements

### Requirement: User can execute the Signing Android App action
The system SHALL provide a "Signing Android App" action that signs and zipaligns the built release AAB inside WSL using the profile's certificate and returns the signed file to the WSL bin directory.

#### Scenario: Signing flow executes
- **WHEN** the user runs the Signing Android App action with a valid profile (certificate path, cert password, wsl_dir, wsl_distro)
- **THEN** the system creates a `signing_android_app` directory in the WSL Build Directory
- **THEN** the system copies the built `*.aab` file from the WSL Build Directory `bin` folder into it
- **THEN** the system copies the certificate file into it
- **THEN** the system runs `jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore <certificate file> -keypass <Password for certificate> <copied *.aab file> app`
- **THEN** the system runs `zipalign -p 4 <aabfilename>-release.aab <aabfilename>-signed.aab`
- **THEN** the system copies the signed files back to the WSL Build Directory `bin` folder

#### Scenario: Signing fails validation if certificate fields empty
- **WHEN** the profile has empty cert_path or cert_password
- **THEN** the action is rejected with a message listing missing fields

#### Scenario: No AAB found stops signing
- **WHEN** no `*.aab` file is found in the WSL Build Directory `bin` folder
- **THEN** the system logs the search path
- **THEN** the action stops immediately with status Failed

#### Scenario: jarsigner or zipalign missing stops signing
- **WHEN** `jarsigner` or `zipalign` is not installed in WSL
- **THEN** the system logs the tool error output
- **THEN** the action stops with status Failed

#### Scenario: WSL not running stops signing
- **WHEN** WSL is not running and the user starts the Signing Android App action
- **THEN** the system shows an error message: "WSL is not running"
- **THEN** the action is not executed

### Requirement: Signed AAB artifacts are named consistently
The Signing Android App action SHALL generate the signed file name based on the source AAB file name, replacing the `-release` suffix with `-signed` (e.g., `<name>-release.aab` → `<name>-signed.aab`).

#### Scenario: Signed file naming
- **WHEN** the built file is `MyApp-release.aab`
- **THEN** the signed output is `MyApp-signed.aab`
- **THEN** the signed file is copied to the WSL Build Directory `bin` folder