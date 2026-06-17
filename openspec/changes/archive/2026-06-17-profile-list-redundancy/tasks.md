## 1. Remove old screens

- [x] 1.1 Delete `src/screens/profile_list_screen.py`
- [x] 1.2 Delete `src/screens/profile_editor_screen.py`
- [x] 1.3 Delete `src/kv/profile_list_screen.kv`
- [x] 1.4 Delete `src/kv/profile_editor_screen.kv`

## 2. Create merged ProfilesScreen

- [x] 2.1 Create `src/screens/profiles_screen.py` with Spinner for profile selection + editor form fields
- [x] 2.2 Create `src/kv/profiles_screen.kv` with Spinner at top, form fields below in a ScrollView
- [x] 2.3 Implement profile selection from Spinner → populate form fields
- [x] 2.4 Implement auto-save current profile when Spinner selection changes
- [x] 2.5 Implement "New Profile" button → creates profile, selects it, clears form for editing
- [x] 2.6 Implement "Delete" button with confirmation popup
- [x] 2.7 Preserve auto-detect for buildozer.spec and ADB path

## 3. Update app wiring

- [x] 3.1 Update `app.py` to import `ProfilesScreen` instead of old screens, remove old KV loads
- [x] 3.2 Update `kv/main.kv` to use `ProfilesScreen` and remove "Editor" nav button
- [x] 3.3 Verify active profile selection propagates to ActionsScreen
