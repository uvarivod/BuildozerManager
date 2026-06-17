## Context

Profile list and editor are separate screens with a dedicated nav button for each. The list screen only shows names — selecting one auto-navigates to the editor. This is two screens doing one job.

## Goals / Non-Goals

**Goals:**
- Single "Profiles" screen with a profile dropdown (Spinner) at the top
- Editor form fills the rest of the screen
- Reduce nav bar from 4 to 3 buttons (Profiles, Actions, Scenarios)
- Auto-save when switching profiles

**Non-Goals:**
- No changes to data models, services, or other screens

## Decisions

1. **Spinner for profile selection** — Kivy `Spinner` widget shows the current profile name and drops down the full list. Simpler than a split layout, no wasted space.
2. **"Add Profile" as Spinner bottom entry** — Add a special `+ New Profile` entry at the end of the Spinner's values list, or use a separate button next to the Spinner. Separate button is cleaner (consistent with Kivy UX patterns).
3. **Auto-save on switch** — Changing the Spinner selection saves the current profile before loading the new one.
4. **Delete button with confirmation** — Delete removes the current profile and selects the next available one.

## Risks / Trade-offs

- [Accidental delete] Mitigation: confirmation popup before delete.
- [Spinner with empty list] Mitigation: disable form fields when no profiles exist; show a prompt to create one.
