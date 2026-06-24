from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models.patch import PatchRegistry
from src.models.profile import Profile
from src.services.patch_service import PatchService


class TestPatchService:
    def setup_method(self):
        PatchRegistry._patches = {}
        self.service = PatchService()

    def test_apply_patches_empty_list(self):
        result = self.service.apply_patches([], Path("."))
        assert result is True

    def test_apply_patches_unknown_patch(self):
        result = self.service.apply_patches(["nonexistent"], Path("."))
        assert result is True

    def test_apply_patches_calls_registered_function(self):
        mock_func = MagicMock()
        PatchRegistry._patches["test-patch"] = mock_func

        result = self.service.apply_patches(["test-patch"], Path("/buildozer"))
        assert result is True
        mock_func.assert_called_once_with(
            Path("/buildozer"), profile=None, log_callback=None
        )

    def test_apply_patches_passes_profile(self):
        mock_func = MagicMock()
        PatchRegistry._patches["test-patch"] = mock_func
        profile = Profile(name="test")

        result = self.service.apply_patches(
            ["test-patch"], Path("/buildozer"), profile=profile
        )
        assert result is True
        mock_func.assert_called_once_with(
            Path("/buildozer"), profile=profile, log_callback=None
        )

    def test_apply_patches_passes_log_callback(self):
        mock_func = MagicMock()
        PatchRegistry._patches["test-patch"] = mock_func
        log_cb = MagicMock()

        result = self.service.apply_patches(
            ["test-patch"], Path("/buildozer"), log_callback=log_cb
        )
        assert result is True
        mock_func.assert_called_once_with(
            Path("/buildozer"), profile=None, log_callback=log_cb
        )

    def test_apply_patches_reports_failure(self):
        def failing_func(*args, **kwargs):
            raise RuntimeError("patch failed")

        PatchRegistry._patches["failing"] = failing_func

        result = self.service.apply_patches(["failing"], Path("."))
        assert result is False

    def test_apply_patches_continues_on_failure(self):
        call_order = []

        def first_ok(*args, **kwargs):
            call_order.append("first")

        def second_fail(*args, **kwargs):
            call_order.append("second")
            raise RuntimeError("fail")

        def third_ok(*args, **kwargs):
            call_order.append("third")

        PatchRegistry._patches["a"] = first_ok
        PatchRegistry._patches["b"] = second_fail
        PatchRegistry._patches["c"] = third_ok

        result = self.service.apply_patches(["a", "b", "c"], Path("."))
        assert result is False
        assert call_order == ["first", "second", "third"]

    def test_apply_patches_with_profile_logging(self):
        PatchRegistry._patches = {}

        @PatchRegistry.register("log-test", "test")
        def log_test(buildozer_path, **kwargs):
            pass

        log_cb = MagicMock()
        profile = Profile(name="test")

        result = self.service.apply_patches(
            ["log-test"], Path("/p"), log_callback=log_cb, profile=profile
        )
        assert result is True
        log_cb.assert_any_call("info", "Applying patch: log-test")
        log_cb.assert_any_call("success", "Patch 'log-test' applied")
