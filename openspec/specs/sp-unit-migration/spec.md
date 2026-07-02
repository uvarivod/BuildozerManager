# SP Unit Migration

## Purpose

TBD

## Requirements

### Requirement: All font sizes use `sp` units
The system SHALL use `sp` (scale-independent pixels) for all font size declarations across KV files and Python code to ensure proper DPI scaling.

#### Scenario: KV font sizes use sp
- **GIVEN** all KV layout files in `src/kv/`
- **WHEN** any `font_size` property is declared
- **THEN** its value SHALL be in `sp` units (e.g., `font_size: "11sp"`)
- **AND** NOT use bare integers (e.g., `font_size: 11`), `dp` units, or `px` units

#### Scenario: Python font sizes use sp
- **GIVEN** all Python files in `src/`
- **WHEN** `font_size` is passed as a keyword argument to any widget constructor
- **THEN** its value SHALL be a string ending in `"sp"` (e.g., `font_size="11sp"`)
- **AND** NOT use bare integers or `dp` strings

### Requirement: Dynamic font sizes in Python are also migrated
The system SHALL ensure that font sizes set programmatically (not just in KV) use `sp` units.

#### Scenario: Programmatic font sizes
- **WHEN** a font size is set via `widget.font_size = value` in Python
- **THEN** the value SHALL be a string with `sp` suffix or use `kivy.metrics.sp()` function

### Requirement: All layout dimension values in Python use `dp` units with proper import
The system SHALL use `dp()` from `kivy.metrics` for all programmatic layout dimension values (padding, spacing, size, height) in Python files, and the `dp` function SHALL be imported at the top of each file that uses it.

#### Scenario: Python layout dimensions use dp function
- **WHEN** a layout dimension (e.g., `padding`, `spacing`, `size`, `height`) is set via a function call in a Python file
- **THEN** the keyword arguments SHALL use the `dp()` function from `kivy.metrics`
- **AND** the file SHALL import `dp` via `from kivy.metrics import dp`
