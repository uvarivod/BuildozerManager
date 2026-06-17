import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from queue import Queue
from typing import Any


class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    SUCCESS = auto()


LEVEL_COLORS = {
    LogLevel.DEBUG: "AAAAAA",
    LogLevel.INFO: "FFFFFF",
    LogLevel.WARN: "FFFF00",
    LogLevel.ERROR: "FF4444",
    LogLevel.SUCCESS: "44FF44",
}

LEVEL_NAMES = {
    LogLevel.DEBUG: "DEBUG",
    LogLevel.INFO: "INFO",
    LogLevel.WARN: "WARN",
    LogLevel.ERROR: "ERROR",
    LogLevel.SUCCESS: "SUCCESS",
}


@dataclass
class LogEvent:
    timestamp: datetime
    level: LogLevel
    message: str
    source: str = ""

    def formatted(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        level_str = LEVEL_NAMES.get(self.level, "INFO")
        color = LEVEL_COLORS.get(self.level, "FFFFFF")
        source_part = f" [{self.source}]" if self.source else ""
        return f"[b]{ts}[/b] [{color}]{level_str}[/color]{source_part} {self.message}"

    def plain_text(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        level_str = LEVEL_NAMES.get(self.level, "INFO")
        source_part = f" [{self.source}]" if self.source else ""
        return f"[{ts}] {level_str}{source_part} {self.message}"


class LogService:
    _instance: "LogService | None" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "LogService":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._events: list[LogEvent] = []
        self._listeners: list[Callable[[LogEvent], Any]] = []
        self._lock = threading.Lock()

    def log(self, level: LogLevel, message: str, source: str = ""):
        event = LogEvent(
            timestamp=datetime.now(),
            level=level,
            message=message,
            source=source,
        )
        with self._lock:
            self._events.append(event)
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                listener(event)
            except Exception:
                pass

    def debug(self, message: str, source: str = ""):
        self.log(LogLevel.DEBUG, message, source)

    def info(self, message: str, source: str = ""):
        self.log(LogLevel.INFO, message, source)

    def warn(self, message: str, source: str = ""):
        self.log(LogLevel.WARN, message, source)

    def error(self, message: str, source: str = ""):
        self.log(LogLevel.ERROR, message, source)

    def success(self, message: str, source: str = ""):
        self.log(LogLevel.SUCCESS, message, source)

    def subscribe(self, listener: Callable[[LogEvent], Any]):
        with self._lock:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[LogEvent], Any]):
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def get_all(self) -> list[LogEvent]:
        with self._lock:
            return list(self._events)

    def get_plain_text(self) -> str:
        return "\n".join(e.plain_text() for e in self.get_all())

    def clear(self):
        with self._lock:
            self._events.clear()
