from enum import Enum, auto


class Action(Enum):
    SYNC_SRC = auto()
    CLEAN = auto()
    BUILD = auto()
    BUILD_AAB = auto()
    PATCH = auto()
    PULL_APK = auto()
    PULL_AAB = auto()
    RUN = auto()
    SIGN_APK = auto()
    CUSTOM_SCRIPT = auto()

    @property
    def description(self) -> str:
        return _ACTION_DESCRIPTIONS[self]


_ACTION_DESCRIPTIONS: dict[Action, str] = {
    Action.SYNC_SRC: "Sync source files to WSL",
    Action.CLEAN: "Clean WSL working directory",
    Action.BUILD: "Build APK with Buildozer",
    Action.BUILD_AAB: "Build AAB with Buildozer (release)",
    Action.PATCH: "Apply patches to .buildozer",
    Action.PULL_APK: "Download APK from WSL",
    Action.PULL_AAB: "Download AAB from WSL",
    Action.RUN: "Install and run APK on device",
    Action.SIGN_APK: "Sign Android App (AAB)",
    Action.CUSTOM_SCRIPT: "Run a custom script",
}


class ActionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
    SKIPPED = auto()
