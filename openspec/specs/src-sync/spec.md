# Sync SRC

## Purpose

Provide the Sync SRC operation that replaces source files in the WSL project directory while always preserving the `.buildozer` build cache (hardcoded) and any user-configured Retain During Sync items.

## Requirements

### Requirement: System provides SyncSRC operation
The system SHALL provide a SyncSRC operation that replaces source files in the WSL project directory while always preserving the `.buildozer` directory and the profile's Retain During Sync list.

#### Scenario: SyncSRC preserves .buildozer
- **WHEN** the SyncSRC operation runs on a WSL project directory that contains source files and a `.buildozer` directory
- **THEN** the `.buildozer` directory and all its contents are preserved intact
- **THEN** all other files in the WSL project directory are deleted
- **THEN** fresh source files are copied from the local sourcedir to the WSL project directory

#### Scenario: SyncSRC with no WSL directory
- **WHEN** the SyncSRC operation runs and the WSL project directory does not exist
- **THEN** the operation creates the WSL project directory
- **THEN** source files are copied from the local sourcedir

### Requirement: System provides CleanWSLProject operation
The system SHALL provide a CleanWSLProject operation that deletes everything in the WSL project directory including `.buildozer`, ignoring all exclusions.

#### Scenario: CleanWSLProject removes everything
- **WHEN** the CleanWSLProject operation runs on a WSL project directory that contains files and a `.buildozer` directory
- **THEN** all files including `.buildozer` are deleted
- **THEN** the operation logs each deleted item
