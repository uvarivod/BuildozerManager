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


def simple_profile(wsl_dir="/home/user", wsl_distro="Ubuntu"):
    from src.models.profile import Profile
    return Profile(
        name="simple",
        sourcedir="/src",
        wsl_dir=wsl_dir,
        wsl_distro=wsl_distro,
    )
