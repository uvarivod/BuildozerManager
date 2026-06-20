from enum import Enum, auto


class Action(Enum):
    CLEAN = auto()
    BUILD = auto()
    PATCH = auto()
    DOWNLOAD = auto()
    PULL_APK = auto()
    RUN = auto()


class ActionState(Enum):
    IDLE = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()
