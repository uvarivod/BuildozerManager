import shutil
from pathlib import Path

import pytest

from src.services.wsl_service import WSLService


@pytest.fixture
def service():
    return WSLService()


class TestStripAnsi:
    def test_no_ansi(self, service):
        assert service._strip_ansi("hello world") == "hello world"

    def test_simple_color(self, service):
        assert service._strip_ansi("\x1B[32mgreen\x1B[0m") == "green"

    def test_multiple_sequences(self, service):
        result = service._strip_ansi("\x1B[1m\x1B[31mBOLD RED\x1B[0m")
        assert result == "BOLD RED"

    def test_cursor_move(self, service):
        result = service._strip_ansi("line1\x1B[Kline2")
        assert result == "line1line2"

    def test_clear_screen(self, service):
        result = service._strip_ansi("\x1B[2Jcleared")
        assert result == "cleared"

    def test_empty_string(self, service):
        assert service._strip_ansi("") == ""

    def test_only_ansi(self, service):
        assert service._strip_ansi("\x1B[32m\x1B[0m") == ""


class TestLinuxDir:
    def test_unc_path(self, service, sample_profile):
        result = service._linux_dir(sample_profile)
        assert result == "/home/alex/bui"

    def test_linux_path(self, service):
        profile = simple_profile(wsl_dir="/home/user/project", wsl_distro="Ubuntu")
        result = service._linux_dir(profile)
        assert result == "home/user/project"

    def test_unc_path_different_distro(self, service):
        profile = simple_profile(
            wsl_dir="\\\\wsl.localhost\\Debian\\home\\dev\\app",
            wsl_distro="Debian",
        )
        result = service._linux_dir(profile)
        assert result == "/home/dev/app"


class TestWslPath:
    def test_unc_path_preserved(self, service, sample_profile):
        """When wsl_dir is a full UNC path, _wsl_path returns it as-is."""
        path = service._wsl_path(sample_profile)
        assert str(path) == "\\\\wsl.localhost\\Ubuntu-22.04\\home\\alex\\bui"

    def test_linux_path_prepends_distro(self, service):
        """When wsl_dir is a Linux path, _wsl_path prepends the UNC distro prefix."""
        profile = simple_profile(
            wsl_dir="/home/user/app",
            wsl_distro="Ubuntu",
        )
        path = service._wsl_path(profile)
        assert str(path) == "\\\\wsl$\\Ubuntu\\home\\user\\app"


class TestParseBuildozerLine:
    def test_step(self, service):
        result = service._parse_buildozer_line("# Setting up toolchain")
        assert result == ("info", "Step: Setting up toolchain")

    def test_info(self, service):
        result = service._parse_buildozer_line("[INFO]:    Building project")
        assert result == ("info", "Building project")

    def test_info_no_colon(self, service):
        result = service._parse_buildozer_line("[INFO] Building project")
        assert result == ("info", "Building project")

    def test_info_case_insensitive(self, service):
        result = service._parse_buildozer_line("[info]: building")
        assert result == ("info", "building")

    def test_warn(self, service):
        result = service._parse_buildozer_line("[WARN]: Low disk space")
        assert result == ("warn", "Low disk space")

    def test_warning_long_form(self, service):
        result = service._parse_buildozer_line("[WARNING]: Something")
        assert result == ("warn", "Something")

    def test_error(self, service):
        result = service._parse_buildozer_line("[ERROR]: Build failed")
        assert result == ("error", "Build failed")

    def test_debug(self, service):
        result = service._parse_buildozer_line("some random output")
        assert result == ("debug", "some random output")

    def test_noise_stty(self, service):
        result = service._parse_buildozer_line("stty: standard input: Invalid argument")
        assert result is None

    def test_noise_rm_f(self, service):
        result = service._parse_buildozer_line("-> running rm -f /some/file")
        assert result is None

    def test_empty_line(self, service):
        assert service._parse_buildozer_line("") is None
        assert service._parse_buildozer_line("   ") is None

    def test_ansi_stripped_before_parse(self, service):
        result = service._parse_buildozer_line("\x1B[32m[INFO]: OK\x1B[0m")
        assert result == ("info", "OK")


class TestNoiseFiltering:
    """Tests for _TOOL_CMDS_RE and _GCC_CONT_RE patterns used in exec_buildozer."""

    def test_tool_cmd_gcc(self, service):
        clean = "\t  gcc -c source.c -o source.o"
        assert service._TOOL_CMDS_RE.match(clean.strip())

    def test_tool_cmd_gpp(self, service):
        assert service._TOOL_CMDS_RE.match("g++ -std=c++17 main.cpp")

    def test_tool_cmd_ld(self, service):
        assert service._TOOL_CMDS_RE.match("ld -o output file.o")

    def test_tool_cmd_ar(self, service):
        assert service._TOOL_CMDS_RE.match("ar rcs lib.a a.o")

    def test_tool_cmd_make_not_matched(self, service):
        """make was intentionally removed from TOOL_CMDS_RE to show status/errors."""
        assert not service._TOOL_CMDS_RE.match("make[1]: Entering directory")
        assert not service._TOOL_CMDS_RE.match("make -j 8 all")

    def test_gcc_continuation(self, service):
        assert service._GCC_CONT_RE.match("-DUSE_FEATURE_X=1")
        assert service._GCC_CONT_RE.match("-o /tmp/out.o")
        assert service._GCC_CONT_RE.match("-I/usr/include")
        assert service._GCC_CONT_RE.match("-Wall -Wextra")

    def test_gcc_flag_not_confused_with_word(self, service):
        assert not service._GCC_CONT_RE.match("Download")
        assert not service._GCC_CONT_RE.match("Checking")
        assert not service._GCC_CONT_RE.match("[INFO]")


def simple_profile(wsl_dir="/home/user", wsl_distro="Ubuntu", **kwargs):
    from src.models.profile import Profile
    return Profile(
        name="simple",
        sourcedir="/src",
        wsl_dir=wsl_dir,
        wsl_distro=wsl_distro,
        **kwargs,
    )


def _make_fake_wsl_delete(tmp_path):
    """Return a _wsl_delete mock that deletes files locally from tmp_path."""
    def fake(profile, linux_path):
        name = Path(linux_path).name
        target = tmp_path / name
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
        return True
    return fake


class TestDeleteWslContents:
    def test_no_directory_returns_true(self, service, mock_log_callback):
        result = service._delete_wsl_contents(
            simple_profile(), log_callback=mock_log_callback
        )
        assert result is True

    def test_deletes_non_excluded_files(self, service, monkeypatch, tmp_path):
        (tmp_path / "main.py").write_text("x")
        (tmp_path / ".buildozer").mkdir()
        (tmp_path / ".buildozer" / "cache").write_text("x")
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", _make_fake_wsl_delete(tmp_path))

        service._delete_wsl_contents(simple_profile(), exclude={".buildozer"})

        assert (tmp_path / ".buildozer").exists()
        assert not (tmp_path / "main.py").exists()

    def test_excluded_files_skipped(self, service, monkeypatch, tmp_path):
        (tmp_path / "keep_me").write_text("x")
        (tmp_path / "delete_me").write_text("x")
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", _make_fake_wsl_delete(tmp_path))

        service._delete_wsl_contents(simple_profile(), exclude={"keep_me"})

        assert (tmp_path / "keep_me").exists()
        assert not (tmp_path / "delete_me").exists()

    def test_cancel_stops_deletion(self, service, monkeypatch, tmp_path):
        for i in range(5):
            (tmp_path / f"file{i}").write_text("x")
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", lambda p, lp: True)

        called = {"count": 0}
        def cancel_check():
            called["count"] += 1
            return called["count"] > 2

        result = service._delete_wsl_contents(
            simple_profile(), cancel_check=cancel_check
        )
        assert result is False


class TestSyncSrc:
    def test_merges_buildozer_and_user_exclusions(self, service, monkeypatch, tmp_path):
        (tmp_path / ".buildozer").mkdir()
        (tmp_path / "user_cache").mkdir()
        (tmp_path / "main.py").write_text("x")
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", _make_fake_wsl_delete(tmp_path))
        monkeypatch.setattr(service, "copy_source_to_wsl", lambda *a, **kw: True)
        profile = simple_profile(delete_exclusions=["user_cache"])

        result = service.sync_src(profile)

        assert result is True
        assert (tmp_path / ".buildozer").exists()
        assert (tmp_path / "user_cache").exists()
        assert not (tmp_path / "main.py").exists()

    def test_calls_copy_source_after_deletion(self, service, monkeypatch, tmp_path):
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", lambda p, lp: True)
        copy_called = False
        def fake_copy(*a, **kw):
            nonlocal copy_called
            copy_called = True
            return True
        monkeypatch.setattr(service, "copy_source_to_wsl", fake_copy)

        service.sync_src(simple_profile())

        assert copy_called is True

    def test_returns_false_when_delete_fails(self, service, monkeypatch, tmp_path):
        (tmp_path / "some_file").write_text("x")
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", lambda p, lp: False)

        result = service.sync_src(simple_profile())

        assert result is False


class TestCleanWslProject:
    def test_deletes_everything_including_buildozer(self, service, monkeypatch, tmp_path):
        (tmp_path / ".buildozer").mkdir()
        (tmp_path / "main.py").write_text("x")
        monkeypatch.setattr(service, "_wsl_path", lambda p: tmp_path)
        monkeypatch.setattr(service, "_wsl_delete", _make_fake_wsl_delete(tmp_path))

        result = service.clean_wsl_project(simple_profile())

        assert result is True
        assert not (tmp_path / ".buildozer").exists()
        assert not (tmp_path / "main.py").exists()

    def test_no_directory_returns_true(self, service, mock_log_callback):
        result = service.clean_wsl_project(
            simple_profile(), log_callback=mock_log_callback
        )
        assert result is True
