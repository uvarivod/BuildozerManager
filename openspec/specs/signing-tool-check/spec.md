# Signing Tool Check

## Purpose

Verify that `jarsigner` and `zipalign` are available inside the configured WSL distribution before signing Android App bundles. (TBD)

## Requirements

### Requirement: User can check jarsigner and zipalign availability
The system SHALL provide a "Check jarsigner and zipalign" button in the profile editor, near the certificate fields, that verifies both tools run successfully inside the configured WSL distribution.

#### Scenario: Check succeeds
- **WHEN** the user clicks "Check jarsigner and zipalign" and both `jarsigner` and `zipalign` run successfully in WSL
- **THEN** a success marker is shown near the button indicating the check passed

#### Scenario: Check fails
- **WHEN** the user clicks "Check jarsigner and zipalign" and either `jarsigner` or `zipalign` does not run successfully in WSL
- **THEN** a popup is shown with the message:
  `<jarsigner>,<zipalign> Not Found
  <jarsigner>,<zipalign> should be installed in WSL and added to PATH.
  This is required for Signing Android App Action only`

#### Scenario: Check skipped when WSL settings missing
- **WHEN** the profile has empty wsl_dir or wsl_distro
- **THEN** the check is rejected with a message listing the missing fields
