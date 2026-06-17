## Why

Building Kivy APKs for Android via Buildozer + WSL is a repetitive, error-prone workflow with no dedicated tooling. Developers must manually manage profiles, WSL file copies, ADB commands, and patching across sessions. A desktop GUI streamlines this into a repeatable, auditable process — reducing friction and eliminating manual mistakes.

## What Changes

- Create a new Python + Kivy desktop application ("Buildozer Manager") for managing Kivy→Android build workflows
- Profile CRUD: store per-project settings (sourcedir, buildozer.spec path, ADB path, excluded files, WSL working directory, patches)
- Action system: Clean, Build, Patch, Download APK, Run (install+launch) with progress and logs
- Scenario system: compose actions into repeatable sequences (e.g. "clean build + run")
- WSL integration: manage file copy to WSL, execute buildozer commands, clean WSL working dir
- ADB integration: install APK and launch app on connected device
- Patch system: user-defined methods that modify `.buildozer` files in WSL after copy
- Real-time log viewer with timestamps, duration tracking, and save-to-file
- Persistent storage (JSON) for profiles, scenarios, and app settings
- Project skeleton: `main.py`, `.kv` files, screen navigation, data models, service layer

## Capabilities

### New Capabilities
- `profile-management`: Create, edit, delete, and select application profiles with all build settings
- `action-execution`: Run individual build actions (Clean, Build, Patch, Download, Run) with status and timing
- `scenario-orchestration`: Compose actions into named scenarios; execute sequentially with aggregated logging
- `wsl-integration`: Copy source to WSL directory, execute buildozer commands, clean WSL working directory
- `adb-integration`: Detect connected devices, install APK, launch app via ADB
- `patch-system`: Define and apply named patches that modify files in `.buildozer` within WSL
- `log-viewer`: Real-time terminal-style log output, per-session timestamps, duration tracking, save-to-file
- `persistent-storage`: Save/load profiles, settings, and scenarios to JSON on disk

### Modified Capabilities
<!-- No existing capabilities to modify. -->

## Impact

- New Python project with Kivy GUI framework
- Dependencies: `kivy`, `pathlib` (stdlib), `subprocess` (stdlib), `json` (stdlib), `enum` (stdlib)
- No changes to existing code — greenfield project
- Windows+WSL primary target; cross-platform where practical
