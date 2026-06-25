from enum import Enum, auto


class Action(Enum):
    SYNC_SRC = auto()
    CLEAN = auto()
    BUILD = auto()
    PATCH = auto()
    PULL_APK = auto()
    RUN = auto()

    @property
    def description(self) -> str:
        return _ACTION_DESCRIPTIONS[self]


_ACTION_DESCRIPTIONS: dict[Action, str] = {
    Action.SYNC_SRC: "Sync source files to WSL",
    Action.CLEAN: "Clean WSL working directory",
    Action.BUILD: "Build APK with Buildozer",
    Action.PATCH: "Apply patches to .buildozer",
    Action.PULL_APK: "Download APK from WSL",
    Action.RUN: "Install and run APK on device",
}


class ActionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
    SKIPPED = auto()
