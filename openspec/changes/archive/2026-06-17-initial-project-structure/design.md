## Context

Buildozer Manager is a greenfield desktop GUI application for Windows users who build Kivy Android APKs through Buildozer running in WSL. There is no existing codebase. The application must coordinate file system operations across the Windows/WSL boundary, manage subprocess calls to Buildozer and ADB, and present real-time build progress in a responsive UI.

## Goals / Non-Goals

**Goals:**
- Monolithic single-window Kivy app with screen navigation (ScreenManager)
- Data models for Profile, Patch, Action, Scenario with JSON persistence
- MVC-ish separation: `.kv` view files, Python controller classes, service layer for business logic
- Long-running operations (build, copy, ADB) run in background threads with UI progress updates via Clock + Events
- Terminal-style log viewer with ScrollView, color-coded output, auto-scroll, and save-to-file
- WSL file copy via `subprocess` calling `robocopy` or `cp` on WSL side
- ADB commands via `subprocess` calling `adb.exe` with configurable path

**Non-Goals:**
- Not a cross-platform build server — local desktop tool only
- No CI/CD integration, no cloud storage, no multi-user support
- No KivyMD dependency — vanilla Kivy widgets only
- No package manager or auto-updater

## Decisions

1. **Architecture: Service-layer pattern with screen controllers**
   - Services encapsulate domain logic (ProfileService, WSLService, ADBService, BuildService, PatchService, LogService, ScenarioService)
   - Screens (Kivy Screen subclasses) handle UI events and delegate to services
   - Services are stateless singletons; state lives in Profile and Scenario model objects
   - Rationale: keeps `.kv` files clean (presentation only), makes services unit-testable, avoids spaghetti in screen classes

2. **Threading model: threading.Thread + Kivy Clock.schedule_once**
   - Build/copy/ADB operations run on daemon worker threads
   - Threads emit progress via callback or Queue; main thread polls via Clock or binds to StringProperty changes
   - Rationale: Kivy UI must not block; `threading` is stdlib; avoids GIL issues since I/O-bound work

3. **Persistence: JSON files**
   - Profiles stored in `~/.buildozer-manager/profiles.json`
   - Settings in `~/.buildozer-manager/settings.json`
   - Rationale: simple, human-readable, no external DB dependency; easy to debug and backup

4. **WSL integration: \\
   - Use `wsl.exe --distribution <distro>` for commands executed inside WSL
   - File copy: use Python `shutil` on the `//wsl$/Ubuntu/...` network path (Windows can access WSL files via `\\wsl$\`)
   - Rationale: simpler than piping through wsl.exe; leverages Windows native path access

5. **Patch system: Python callables**
   - Each patch is a Python function that receives a Path to the `.buildozer` directory in WSL
   - Patches are discovered via a registry decorated with `@patch(name="...")`
   - Rationale: flexible, extensible, easy to version-control alongside the app

6. **Scenario execution: sequential with aggregation**
   - Scenarios execute actions in order; failure in one action stops the scenario (configurable)
   - Each action's logs are aggregated into a single ScenarioRun log
   - Rationale: simple to implement and debug; failure-fast is safer for build workflows

7. **Log viewer: ReactiveLabel with color tagging**
   - Use Kivy `RecycleView` or plain `ScrollView` + `Label` for log output
   - Log lines tagged with level (`INFO`, `WARN`, `ERROR`, `DEBUG`) for color-coding via markup
   - Timestamps prepended automatically; duration computed from first/last log entry
   - Rationale: RecycleView handles large logs efficiently; markup enables color without custom widgets

## Risks / Trade-offs

- [WSL path access] `\\wsl$\` paths are only available when WSL is running. Mitigation: check WSL status before operations; guide user to start WSL if down.
- [Thread safety] Kivy properties are not thread-safe. Mitigation: use `Clock.schedule_once` or `@mainthread` decorator for all UI updates from threads.
- [Subprocess hangs] Buildozer or ADB may hang indefinitely. Mitigation: subprocess timeout + user-cancellation via process.kill().
- [JSON concurrency] No locking on profile file reads/writes. Mitigation: single-user desktop app — no concurrent access expected.
- [WSL distribution name] Hardcoding "Ubuntu-22.04" breaks for other distros. Mitigation: user-configurable distribution name in profile settings.
