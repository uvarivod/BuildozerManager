## 1. Project Setup

- [x] 1.1 Create virtual environment and install kivy
- [x] 1.2 Create project directory structure (screens/, services/, models/, patches/, kv/)
- [x] 1.3 Create `main.py` entry point with App class and basic ScreenManager
- [x] 1.4 Create `requirements.txt` with kivy dependency

## 2. Data Models

- [x] 2.1 Create `models/profile.py` with Profile dataclass (name, sourcedir, spec_path, adb_path, excluded_files, wsl_dir, wsl_distro, patches, delete_exclusions)
- [x] 2.2 Create `models/patch.py` with Patch dataclass (name, description, enabled) and PatchRegistry
- [x] 2.3 Create `models/action.py` with Action enum (CLEAN, BUILD, PATCH, DOWNLOAD, RUN) and ActionState enum (IDLE, RUNNING, SUCCESS, FAILED, CANCELLED)
- [x] 2.4 Create `models/scenario.py` with Scenario dataclass (name, action_sequence list, stop_on_failure bool) and ScenarioRun dataclass (start_time, duration, per_action_status)
- [x] 2.5 Create `models/__init__.py` exporting all models

## 3. Persistent Storage Service

- [x] 3.1 Create `services/storage_service.py` with JSON read/write helpers (indented, sorted keys)
- [x] 3.2 Implement `ProfileStore` class: load/save/delete/list profiles from `~/.buildozer-manager/profiles.json`
- [x] 3.3 Implement `SettingsStore` class: load/save global settings from `~/.buildozer-manager/settings.json`
- [x] 3.4 Implement `ScenarioStore` class: load/save custom scenarios from `~/.buildozer-manager/scenarios.json`
- [x] 3.5 Create directory and default files on first run if missing

## 4. Profile Management UI

- [x] 4.1 Create `screens/profile_list_screen.py` with RecycleView listing profiles
- [x] 4.2 Create `kv/profile_list_screen.kv` with list layout, add/delete buttons
- [x] 4.3 Create `screens/profile_editor_screen.py` with form fields for all profile settings
- [x] 4.4 Create `kv/profile_editor_screen.kv` with labeled text inputs, checkboxes for patches, list management for exclusions
- [x] 4.5 Implement profile selection → active profile updates all downstream screens
- [x] 4.6 Implement auto-detect for buildozer.spec (scan sourcedir) and ADB path (check PATH)

## 5. Log Service and UI

- [x] 5.1 Create `services/log_service.py` with singleton LogService (thread-safe, level-based logging, timestamping)
- [x] 5.2 Implement `LogEvent` dataclass (timestamp, level, message, source)
- [x] 5.3 Create `screens/log_panel.py` with ScrollView + Label for log display
- [x] 5.4 Create `kv/log_panel.kv` with color-coded markup, auto-scroll, clear button, save button
- [x] 5.5 Implement save-to-file via Kivy FileChooseDialog
- [x] 5.6 Integrate LogService with Kivy Clock for non-blocking UI updates

## 6. WSL Integration Service

- [x] 6.1 Create `services/wsl_service.py` with WSLService class
- [x] 6.2 Implement `check_wsl_running()` → verify distribution is accessible
- [x] 6.3 Implement `copy_source_to_wsl(profile, callback)` → copy files from sourcedir to WSL working dir, respecting exclusion patterns, with progress callback
- [x] 6.4 Implement `clean_wsl_dir(profile, callback)` → delete files in WSL working dir, respecting deletion exclusion list
- [x] 6.5 Implement `exec_buildozer(profile, command, log_callback)` → run buildozer in WSL with real-time output streaming
- [x] 6.6 Implement `find_apk_in_wsl(profile)` → locate built APK in `.buildozer` directory
- [x] 6.7 Use `pathlib` + `\\wsl$\\` UNC paths for file operations; `wsl.exe --distribution` for commands

## 7. ADB Integration Service

- [x] 7.1 Create `services/adb_service.py` with ADBService class
- [x] 7.2 Implement `list_devices(adb_path)` → parse `adb devices -l` output
- [x] 7.3 Implement `install_apk(adb_path, apk_path, log_callback)` → run `adb install -r`
- [x] 7.4 Implement `launch_app(adb_path, package, activity, log_callback)` → run `adb shell am start -n`
- [x] 7.5 Handle ADB not found, device offline, install failure with proper error messages

## 8. Action Execution Engine

- [x] 8.1 Create `services/action_runner.py` with ActionRunner class
- [x] 8.2 Implement `run_clean(profile, log_callback, cancel_check)` → calls WSLService.clean_wsl_dir
- [x] 8.3 Implement `run_build(profile, log_callback, cancel_check)` → clean (except .buildozer) → copy source → exec buildozer
- [x] 8.4 Implement `run_patch(profile, log_callback, cancel_check)` → iterate enabled patches, apply each
- [x] 8.5 Implement `run_download(profile, log_callback, cancel_check)` → find APK in WSL → copy to Windows
- [x] 8.6 Implement `run_launch(profile, log_callback, cancel_check)` → install APK via ADB → launch app
- [x] 8.7 Run all actions in background thread with `cancel_check` callback (threading.Event)
- [x] 8.8 Emit progress events (action_state, log_line) via Queue/Kivy Property for UI binding

## 9. Patch System

- [x] 9.1 Create `patches/__init__.py` with `@register_patch(name, description)` decorator and PatchRegistry singleton
- [x] 9.2 Create `services/patch_service.py` with apply_patches(patches_list, buildozer_path, log_callback)
- [x] 9.3 Implement per-patch try/except so one failure doesn't stop others
- [x] 9.4 Create example patch in `patches/example_patches.py` (e.g., disable analytics)

## 10. Scenario Orchestration

- [x] 10.1 Create `services/scenario_service.py` with ScenarioService class
- [x] 10.2 Define predefined scenarios: "Build and Patch", "Clean Build", "Clean Build + Patch", "Build and Run"
- [x] 10.3 Implement `run_scenario(scenario, profile, log_callback, cancel_check)` → execute actions in sequence, respect stop_on_failure
- [x] 10.4 Create `screens/actions_screen.py` with action buttons, scenario selector, progress display
- [x] 10.5 Create `kv/actions_screen.kv` with scenario dropdown, Run/Cancel buttons, per-action status grid, log panel embed
- [x] 10.6 Create `screens/scenario_builder_screen.py` with drag-to-reorder action list, name input, save button
- [x] 10.7 Create `kv/scenario_builder_screen.kv`
- [x] 10.8 Display scenario run results (start time, duration, per-action status, combined log)

## 11. Main Application Shell

- [x] 11.1 Create `kv/main.kv` with ScreenManager, navigation sidebar/tabs to Profiles, Actions, Log
- [x] 11.2 Implement navigation between screens via ScreenManager
- [x] 11.3 Wire LogService to all action/execution components
- [x] 11.4 Create `app.py` with BuildozerManagerApp class bootstrapping all services
- [x] 11.5 Add WSL status indicator in UI header
- [ ] 11.6 Test full workflow: create profile → configure → clean build → patch → run
