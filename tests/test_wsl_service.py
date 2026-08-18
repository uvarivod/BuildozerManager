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


class TestWslAccessiblePath:
    def test_windows_path_converted(self, service):
        result = service._wsl_accessible_path(r"C:\PycharmProjects\cs2\bin\my.keystore")
        assert result == "/mnt/c/PycharmProjects/cs2/bin/my.keystore"

    def test_windows_path_lowercase_drive(self, service):
        result = service._wsl_accessible_path(r"D:\certs\key.jks")
        assert result == "/mnt/d/certs/key.jks"

    def test_linux_path_unchanged(self, service):
        result = service._wsl_accessible_path("/home/alex/keys/my.keystore")
        assert result == "/home/alex/keys/my.keystore"

    def test_forward_slash_windows_path(self, service):
        result = service._wsl_accessible_path("E:/certs/key.store")
        assert result == "/mnt/e/certs/key.store"

    def test_mixed_backslashes_converted(self, service):
        result = service._wsl_accessible_path(r"F:\certs\sub\key.jks")
        assert result == "/mnt/f/certs/sub/key.jks"

    def test_whitespace_stripped(self, service):
        result = service._wsl_accessible_path(r"  C:\certs\key.jks  ")
        assert result == "/mnt/c/certs/key.jks"


class TestShq:
    def test_plain_value_unchanged(self, service):
        assert service._shq("keystore.jks") == "keystore.jks"

    def test_value_with_spaces(self, service):
        assert service._shq("my keystore.jks") == "my keystore.jks"

    def test_single_quote_escaped(self, service):
        assert service._shq("it's") == "it'\\''s"


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


class TestDeriveSignedName:
    def test_release_suffix_replaced(self):
        assert WSLService._derive_signed_name("MyApp-release.aab") == "MyApp-signed.aab"

    def test_no_release_suffix_appends_signed(self):
        assert WSLService._derive_signed_name("MyApp.aab") == "MyApp-signed.aab"

    def test_other_suffix_appends_signed(self):
        assert WSLService._derive_signed_name("MyApp-debug.aab") == "MyApp-debug-signed.aab"


class TestCheckSigningTools:
    def test_returns_false_when_wsl_fields_missing(self, service):
        ok, err = service.check_signing_tools(simple_profile(wsl_dir="", wsl_distro=""))
        assert ok is False
        assert "WSL Build Directory" in err

    def test_success_when_tools_found(self, service, monkeypatch):
        profile = simple_profile()
        class FakeResult:
            returncode = 0
            stdout = "/usr/bin/jarsigner\n/usr/bin/zipalign\n"
            stderr = ""
        called = {}
        def fake_run(cmd, **kw):
            called["cmd"] = cmd
            return FakeResult()
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", fake_run)

        ok, err = service.check_signing_tools(profile)
        assert ok is True
        assert err == ""
        assert called["cmd"][:3] == ["wsl.exe", "--distribution", "Ubuntu"]

    def test_zipalign_checked_by_command_only(self, service, monkeypatch):
        profile = simple_profile()
        results = iter([
            type("R", (), {"returncode": 0, "stdout": "/usr/bin/jarsigner", "stderr": ""})(),
            type("R", (), {"returncode": 0, "stdout": "/usr/bin/zipalign", "stderr": ""})(),
        ])
        captured = []
        def fake_run(cmd, **kw):
            captured.append(cmd)
            return next(results)
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", fake_run)

        ok, err = service.check_signing_tools(profile)
        assert ok is True
        assert err == ""
        zipalign_cmd = " ".join(captured[1][3:])
        assert "command -v zipalign" in zipalign_cmd
        assert "zipalign -h" not in zipalign_cmd

    def test_failure_when_tools_missing(self, service, monkeypatch):
        class FakeResult:
            returncode = 1
            stdout = ""
            stderr = "jarsigner: command not found"
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", lambda *a, **kw: FakeResult())

        ok, err = service.check_signing_tools(simple_profile())
        assert ok is False
        assert err == "jarsigner,zipalign"

    def test_failure_reports_only_missing_tool(self, service, monkeypatch):
        profile = simple_profile()
        results = iter([
            type("R", (), {"returncode": 0, "stdout": "/usr/bin/jarsigner", "stderr": ""})(),
            type("R", (), {"returncode": 1, "stdout": "", "stderr": "zipalign: not found"})(),
        ])
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", lambda *a, **kw: next(results))

        ok, err = service.check_signing_tools(profile)
        assert ok is False
        assert err == "zipalign"

    def test_timeout_returns_failure(self, service, monkeypatch):
        import subprocess
        def raise_timeout(*a, **kw):
            raise subprocess.TimeoutExpired("wsl.exe", 30)
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", raise_timeout)

        ok, err = service.check_signing_tools(simple_profile())
        assert ok is False
        assert "timed out" in err

    def test_wsl_not_found_returns_failure(self, service, monkeypatch):
        def raise_not_found(*a, **kw):
            raise FileNotFoundError("wsl.exe")
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", raise_not_found)

        ok, err = service.check_signing_tools(simple_profile())
        assert ok is False
        assert "wsl.exe not found" in err

    def test_generic_exception_returns_failure(self, service, monkeypatch):
        def raise_error(*a, **kw):
            raise RuntimeError("boom")
        monkeypatch.setattr("src.services.wsl_service.subprocess.run", raise_error)

        ok, err = service.check_signing_tools(simple_profile())
        assert ok is False
        assert "boom" in err


class TestSignApk:
    def test_missing_aab_returns_failure(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        class FakeProcess:
            def __init__(self):
                self.stdout = ["SIGNING_ERROR: No *.aab file found in bin directory\n"]
                self.returncode = 1
            def wait(self):
                return 0
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", lambda *a, **kw: FakeProcess())

        result = service.sign_apk(profile)
        assert result is False

    def test_success_copies_signed_aab_back(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        class FakeProcess:
            def __init__(self):
                self.stdout = [
                    "[SIGN] Found AAB: MyApp-release.aab\n",
                    "[SIGN] Signing with jarsigner...\n",
                    "[SIGN] Aligning with zipalign...\n",
                    "[SIGN] Output file: MyApp-signed.aab\n",
                    "[/home/user/signing_android_app/MyApp-signed.aab]\n",
                ]
                self.returncode = 0
            def wait(self):
                return 0
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", lambda *a, **kw: FakeProcess())

        result = service.sign_apk(profile)
        assert result is True

    def test_jarsigner_failure_stops_signing(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        class FakeProcess:
            def __init__(self):
                self.stdout = [
                    "[SIGN] Found AAB: MyApp-release.aab\n",
                    "SIGNING_ERROR: jarsigner failed\n",
                ]
                self.returncode = 1
            def wait(self):
                return 0
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", lambda *a, **kw: FakeProcess())

        result = service.sign_apk(profile)
        assert result is False

    def test_cancel_before_start_returns_false(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        result = service.sign_apk(profile, cancel_check=lambda: True)
        assert result is False

    def test_windows_cert_path_converted_to_wsl(self, service, monkeypatch):
        profile = simple_profile(cert_path=r"C:\PycharmProjects\cs2companion\buildignore\my.keystore", cert_password="pass")
        class FakeProcess:
            def __init__(self):
                self.stdout = [
                    "[SIGN] Found AAB: MyApp-release.aab\n",
                    "[SIGN] Signing with jarsigner...\n",
                    "[SIGN] Aligning with zipalign...\n",
                    "[SIGN] Output file: MyApp-signed.aab\n",
                ]
                self.returncode = 0
            def wait(self):
                return 0
        captured = {}
        def fake_popen(cmd, **kw):
            captured["cmd"] = cmd
            return FakeProcess()
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", fake_popen)

        result = service.sign_apk(profile)
        assert result is True
        inner = captured["cmd"][-1]
        assert "/mnt/c/PycharmProjects/cs2companion/buildignore/my.keystore" in inner

    def test_jarsigner_supplies_storepass_and_closes_stdin(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="secret-pass")
        class FakeProcess:
            def __init__(self):
                self.stdout = [
                    "[SIGN] Found AAB: MyApp-release.aab\n",
                    "[SIGN] Signing with jarsigner...\n",
                    "[SIGN] Aligning with zipalign...\n",
                    "[SIGN] Output file: MyApp-signed.aab\n",
                ]
                self.returncode = 0
            def wait(self):
                return 0
        captured = {}
        def fake_popen(cmd, **kw):
            captured["cmd"] = cmd
            return FakeProcess()
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", fake_popen)

        result = service.sign_apk(profile)
        assert result is True
        inner = captured["cmd"][-1]
        assert "-storepass secret-pass" in inner
        assert "-keypass secret-pass" in inner
        assert "< /dev/null" in inner

    def test_zipalign_failure_stops_signing(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        class FakeProcess:
            def __init__(self):
                self.stdout = [
                    "[SIGN] Found AAB: MyApp-release.aab\n",
                    "SIGNING_ERROR: zipalign failed\n",
                ]
                self.returncode = 1
            def wait(self):
                return 0
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", lambda *a, **kw: FakeProcess())

        result = service.sign_apk(profile)
        assert result is False

    def test_sign_apk_wsl_missing_returns_false(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        def raise_not_found(*a, **kw):
            raise FileNotFoundError("wsl.exe")
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", raise_not_found)

        result = service.sign_apk(profile)
        assert result is False

    def test_sign_apk_generic_exception_returns_false(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        def raise_error(*a, **kw):
            raise RuntimeError("wsl failed to start")
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", raise_error)

        result = service.sign_apk(profile)
        assert result is False

    def test_sign_apk_captures_signing_error_with_nonzero_exit(self, service, monkeypatch):
        profile = simple_profile(cert_path="/certs/release.keystore", cert_password="pass")
        captured = []
        class FakeProcess:
            def __init__(self):
                self.stdout = [
                    "[SIGN] Found AAB: MyApp-release.aab\n",
                    "SIGNING_ERROR: jarsigner failed\n",
                ]
                self.returncode = 1
            def wait(self):
                return 0
        monkeypatch.setattr("src.services.wsl_service.subprocess.Popen", lambda *a, **kw: FakeProcess())

        result = service.sign_apk(profile)
        assert result is False
