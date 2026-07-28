## MODIFIED Requirements

### Requirement: Each screen has a context-sensitive help button
The system SHALL display a help button (?) on each screen's top bar that opens a popup explaining the screen's purpose and controls. The popup SHALL be created using `show_info_dialog()` from the dialog helper module.

#### Scenario: Help popup on Actions screen
- **WHEN** the user clicks the help button on the Actions screen
- **THEN** a popup opens with text explaining: profile selection, scenario selection, action chain display, running scenarios/actions, and the log panel
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

#### Scenario: Help popup on Profile Editor screen
- **WHEN** the user clicks the help button on the Profile Editor screen
- **THEN** a popup opens explaining the profile editing fields and how to save/delete a profile
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

#### Scenario: Help popup on Scenario Builder screen
- **WHEN** the user clicks the help button on the Scenario Builder screen
- **THEN** a popup opens explaining how to create, edit, and manage scenarios and their action sequences
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

#### Scenario: Help popup on Settings screen
- **WHEN** the user clicks the help button on the Settings screen
- **THEN** a popup opens explaining the settings fields (log path, max log size)
- **THEN** the popup uses consistent dark theme styling from the dialog helper module

### Requirement: Log panel help explains SHIFT+click selection
The system SHALL provide a help popup specifically for the log panel that explains how to select text using SHIFT+click range selection. The popup SHALL be created using `show_info_dialog()` from the dialog helper module.

#### Scenario: Log selection help popup
- **WHEN** the user clicks the help button near the log panel
- **THEN** a popup opens with text: "To select log text, click to set an anchor, then SHIFT+click a different line to select all text between. Plain-click resets the anchor."
- **THEN** the popup uses consistent dark theme styling from the dialog helper module
