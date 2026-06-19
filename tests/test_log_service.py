from unittest.mock import MagicMock

import pytest

from src.services.log_service import LogEvent, LogLevel, LogService


class TestLogService:
    def teardown_method(self):
        LogService._instance = None

    def test_singleton(self):
        s1 = LogService()
        s2 = LogService()
        assert s1 is s2

    def test_singleton_thread_safe(self):
        LogService._instance = None
        instances = set()

        def create():
            instances.add(id(LogService()))

        threads = [threading.Thread(target=create) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(instances) == 1

    def test_log_creates_event(self):
        LogService._instance = None
        svc = LogService()
        svc.log(LogLevel.INFO, "test message", source="src")
        events = svc.get_all()
        assert len(events) == 1
        assert events[0].message == "test message"
        assert events[0].level == LogLevel.INFO
        assert events[0].source == "src"

    def test_log_level_helpers(self):
        LogService._instance = None
        svc = LogService()
        svc.debug("d")
        svc.info("i")
        svc.warn("w")
        svc.error("e")
        svc.success("s")
        events = svc.get_all()
        assert len(events) == 5
        assert events[0].level == LogLevel.DEBUG
        assert events[1].level == LogLevel.INFO
        assert events[2].level == LogLevel.WARN
        assert events[3].level == LogLevel.ERROR
        assert events[4].level == LogLevel.SUCCESS

    def test_subscribe_receives_events(self):
        LogService._instance = None
        svc = LogService()
        listener = MagicMock()
        svc.subscribe(listener)
        svc.log(LogLevel.INFO, "hello")
        listener.assert_called_once()
        event = listener.call_args[0][0]
        assert isinstance(event, LogEvent)
        assert event.message == "hello"

    def test_unsubscribe_stops_events(self):
        LogService._instance = None
        svc = LogService()
        listener = MagicMock()
        svc.subscribe(listener)
        svc.unsubscribe(listener)
        svc.log(LogLevel.INFO, "should not fire")
        listener.assert_not_called()

    def test_unsubscribe_nonexistent_no_error(self):
        LogService._instance = None
        svc = LogService()
        listener = MagicMock()
        svc.unsubscribe(listener)

    def test_clear(self):
        LogService._instance = None
        svc = LogService()
        svc.log(LogLevel.INFO, "a")
        svc.log(LogLevel.INFO, "b")
        assert len(svc.get_all()) == 2
        svc.clear()
        assert svc.get_all() == []

    def test_get_plain_text(self):
        LogService._instance = None
        svc = LogService()
        svc.log(LogLevel.INFO, "msg1", source="s1")
        svc.log(LogLevel.ERROR, "msg2", source="s2")
        text = svc.get_plain_text()
        assert "msg1" in text
        assert "msg2" in text
        assert "INFO" in text
        assert "ERROR" in text
        assert "[s1]" in text
        assert "[s2]" in text

    def test_listener_exception_does_not_crash(self):
        LogService._instance = None
        svc = LogService()
        broken = MagicMock(side_effect=RuntimeError("boom"))
        working = MagicMock()
        svc.subscribe(broken)
        svc.subscribe(working)
        svc.log(LogLevel.INFO, "test")
        working.assert_called_once()


import threading
