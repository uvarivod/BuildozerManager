import pytest

from src.models.action import Action
from src.models.profile import Profile
from src.services.action_runner import ActionRunner


class TestValidateAction:
    def test_clean_requires_wsl_dir(self):
        p = Profile(name="test", wsl_dir="", wsl_distro="")
        missing = ActionRunner.validate_action(Action.CLEAN, p)
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing

    def test_clean_valid(self):
        p = Profile(name="test", wsl_dir="/wsl", wsl_distro="Ubuntu")
        missing = ActionRunner.validate_action(Action.CLEAN, p)
        assert missing == []

    def test_build_requires_all_fields(self):
        p = Profile(name="test")
        missing = ActionRunner.validate_action(Action.BUILD, p)
        assert "sourcedir" in missing
        assert "spec_path" in missing
        assert "wsl_dir" in missing

    def test_build_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/src/buildozer.spec",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
        )
        missing = ActionRunner.validate_action(Action.BUILD, p)
        assert missing == []

    def test_patch_requires_wsl(self):
        p = Profile(name="test", wsl_dir="", wsl_distro="")
        missing = ActionRunner.validate_action(Action.PATCH, p)
        assert "wsl_dir" in missing
        assert "wsl_distro" in missing
        assert "sourcedir" not in missing

    def test_download_requires_sourcedir_and_wsl(self):
        p = Profile(name="test")
        missing = ActionRunner.validate_action(Action.DOWNLOAD, p)
        assert "sourcedir" in missing
        assert "wsl_dir" in missing

    def test_run_requires_adb_path(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="",
        )
        missing = ActionRunner.validate_action(Action.RUN, p)
        assert "adb_path" in missing

    def test_run_valid(self):
        p = Profile(
            name="test",
            sourcedir="/src",
            spec_path="/sp",
            wsl_dir="/wsl",
            wsl_distro="Ubuntu",
            adb_path="adb",
        )
        missing = ActionRunner.validate_action(Action.RUN, p)
        assert missing == []

    def test_unknown_action(self):
        p = Profile(name="test")
        missing = ActionRunner.validate_action(None, p)
        assert missing == []
