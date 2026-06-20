import pytest

from src.models.profile import Profile
from src.services.apk_service import APKService


@pytest.fixture
def service():
    return APKService()


def test_get_package_name_returns_empty_when_no_spec(service, tmp_path):
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_package_name(profile) == ""


def test_get_package_name_parses_domain_and_name(service, tmp_path):
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "package.domain = com.example\n"
        "package.name = myapp\n"
        "app.title = My App\n"
    )
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_package_name(profile) == "com.example.myapp"


def test_get_package_name_with_quoted_values(service, tmp_path):
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        'package.domain = "org.test"\n'
        'package.name = "awesome-app"\n'
    )
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_package_name(profile) == "org.test.awesome-app"


def test_get_package_name_returns_empty_when_fields_missing(service, tmp_path):
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text("app.title = My App\n")
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_package_name(profile) == ""


def test_find_latest_apk_returns_none_when_no_bin_dir(service, tmp_path, monkeypatch):
    wsl_dir = tmp_path / "wsl_home"
    wsl_dir.mkdir(parents=True)
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "package.domain = com.example\n"
        "package.name = myapp\n"
    )
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir=str(wsl_dir.as_posix()),
        wsl_distro="Ubuntu",
    )
    monkeypatch.setattr(service, "_wsl_path", lambda p: wsl_dir)
    assert service.find_latest_apk(profile) is None


def test_find_latest_apk_returns_matching_apk(service, tmp_path, monkeypatch):
    wsl_dir = tmp_path / "wsl_home"
    wsl_dir.mkdir(parents=True)
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "package.domain = com.example\n"
        "package.name = myapp\n"
    )
    bin_dir = wsl_dir / "bin"
    bin_dir.mkdir(parents=True)
    apk_file = bin_dir / "myapp-0.1-arm64-debug.apk"
    apk_file.write_text("fake apk content")
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir=str(wsl_dir.as_posix()),
        wsl_distro="Ubuntu",
    )
    monkeypatch.setattr(service, "_wsl_path", lambda p: wsl_dir)
    result = service.find_latest_apk(profile)
    assert result is not None
    assert result.name == "myapp-0.1-arm64-debug.apk"


def test_find_latest_apk_returns_newest_matching(service, tmp_path, monkeypatch):
    wsl_dir = tmp_path / "wsl_home"
    wsl_dir.mkdir(parents=True)
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "package.domain = com.example\n"
        "package.name = myapp\n"
    )
    bin_dir = wsl_dir / "bin"
    bin_dir.mkdir(parents=True)

    old = bin_dir / "myapp-0.1-arm64-debug.apk"
    old.write_text("old")
    new = bin_dir / "myapp-0.2-arm64-debug.apk"
    new.write_text("newer content")

    import time
    time.sleep(0.01)
    new.touch()

    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir=str(wsl_dir.as_posix()),
        wsl_distro="Ubuntu",
    )
    monkeypatch.setattr(service, "_wsl_path", lambda p: wsl_dir)
    result = service.find_latest_apk(profile)
    assert result is not None
    assert result.name == "myapp-0.2-arm64-debug.apk"


def test_find_latest_apk_ignores_non_matching_apks(service, tmp_path, monkeypatch):
    wsl_dir = tmp_path / "wsl_home"
    wsl_dir.mkdir(parents=True)
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "package.domain = com.example\n"
        "package.name = myapp\n"
    )
    bin_dir = wsl_dir / "bin"
    bin_dir.mkdir(parents=True)
    other_apk = bin_dir / "other-app-1.0-debug.apk"
    other_apk.write_text("other")
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir=str(wsl_dir.as_posix()),
        wsl_distro="Ubuntu",
    )
    monkeypatch.setattr(service, "_wsl_path", lambda p: wsl_dir)
    assert service.find_latest_apk(profile) is None


def test_get_version_returns_empty_when_no_spec(service, tmp_path):
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_version(profile) == ""


def test_get_version_method1(service, tmp_path):
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "#version = 0.99\n"
        "version = 1.1.0\n"
    )
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_version(profile) == "1.1.0"


def test_get_short_name_returns_empty_when_no_spec(service, tmp_path):
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_short_name(profile) == ""


def test_get_version_with_regex_and_filename(service, tmp_path):
    src_file = tmp_path / "src" / "main.py"
    src_file.parent.mkdir(parents=True)
    src_file.write_text("__version__ = '2.0.0'\n")
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "#version.regex = __version__ = ['\"]+(.*)['\"]+\n"
        "#version.filename = %(source.dir)s/src/main.py\n"
    )
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_version(profile) == ""


def test_get_version_short_name(service, tmp_path):
    spec_file = tmp_path / "buildozer.spec"
    spec_file.write_text(
        "package.domain = com.example\n"
        "package.name = kivysimpleapp\n"
    )
    profile = Profile(
        name="test",
        sourcedir=str(tmp_path),
        wsl_dir="/home/wsl",
        wsl_distro="Ubuntu",
    )
    assert service.get_short_name(profile) == "kivysimpleapp"
