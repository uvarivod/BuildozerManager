## MODIFIED Requirements

### Requirement: User can select the active profile
The system SHALL maintain a single active profile whose settings are used for all actions. The user SHALL select the active profile from a dropdown (Spinner) at the top of the Profiles screen.

#### Scenario: Select profile from dropdown
- **WHEN** the user opens the profile dropdown and clicks a profile name
- **THEN** that profile becomes active and its settings are displayed in the form below

### Requirement: User can create a new profile
The system SHALL provide a "New Profile" button on the Profiles screen. Clicking it creates a new profile with default settings and selects it for editing.

#### Scenario: Create new profile
- **WHEN** the user clicks "New Profile"
- **THEN** a new profile named "New Profile" (or "New Profile N" if taken) is created and selected in the dropdown

### Requirement: User can delete a profile
The system SHALL allow deletion of the currently selected profile with a confirmation prompt.

#### Scenario: Delete current profile
- **WHEN** the user clicks "Delete" in the Profiles screen and confirms
- **THEN** the profile is permanently removed and the next profile (or first) is selected

## REMOVED Requirements

### Requirement: User can create a new profile with a custom name at creation time
**Reason**: Names can be edited in the form after creation
**Migration**: Use the "New Profile" button then edit the name field in the form

### Requirement: Excluded files/folders configured per profile
**Reason**: Functionality preserved — moved to delta spec format
**Migration**: Functionality is identical, just displayed in a different layout
