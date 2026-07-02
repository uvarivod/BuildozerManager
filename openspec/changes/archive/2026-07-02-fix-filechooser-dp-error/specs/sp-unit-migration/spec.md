## ADDED Requirements

### Requirement: All layout dimension values in Python use `dp` units with proper import
The system SHALL use `dp()` from `kivy.metrics` for all programmatic layout dimension values (padding, spacing, size, height) in Python files, and the `dp` function SHALL be imported at the top of each file that uses it.

#### Scenario: Python layout dimensions use dp function
- **WHEN** a layout dimension (e.g., `padding`, `spacing`, `size`, `height`) is set via a function call in a Python file
- **THEN** the keyword arguments SHALL use the `dp()` function from `kivy.metrics`
- **AND** the file SHALL import `dp` via `from kivy.metrics import dp`
