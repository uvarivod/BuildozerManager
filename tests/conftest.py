from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.models.profile import Profile


@pytest.fixture
def sample_profile():
    return Profile(
        name="test-profile",
        sourcedir="/home/user/project",
        spec_path="/home/user/project/buildozer.spec",
        adb_path="adb",
        excluded_files=["__pycache__", ".git"],
        wsl_dir="\\\\wsl.localhost\\Ubuntu-22.04\\home\\alex\\bui",
        wsl_distro="Ubuntu-22.04",
        patches=["patch1", "patch2"],
        delete_exclusions=[],
    )


@pytest.fixture
def mock_log_callback():
    return MagicMock()
