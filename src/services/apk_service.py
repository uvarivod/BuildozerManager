import re
from pathlib import Path

from src.models.profile import Profile


class APKService:
    _LOCAL_SPEC = "buildozer.spec"

    def _wsl_path(self, profile: Profile) -> Path:
        return Path(f"\\\\wsl$\\{profile.wsl_distro}") / profile.wsl_dir.lstrip("/")

    def _spec_path(self, profile: Profile) -> Path:
        return Path(profile.sourcedir) / self._LOCAL_SPEC

    def get_package_name(self, profile: Profile) -> str:
        spec_path = self._spec_path(profile)
        if not spec_path.is_file():
            return ""

        content = spec_path.read_text(encoding="utf-8", errors="replace")
        domain = ""
        name = ""
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key == "package.domain":
                domain = value
            elif key == "package.name":
                name = value
        if domain and name:
            return f"{domain}.{name}"
        return ""

    def get_short_name(self, profile: Profile) -> str:
        spec_path = self._spec_path(profile)
        if not spec_path.is_file():
            return ""
        for line in spec_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() == "package.name":
                return value.strip().strip("\"'")
        return ""

    def get_version(self, profile: Profile) -> str:
        spec_path = self._spec_path(profile)
        if not spec_path.is_file():
            return ""
        content = spec_path.read_text(encoding="utf-8", errors="replace")
        version = ""
        version_regex = ""
        version_filename = ""
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or "=" not in stripped:
                continue
            is_commented = stripped.startswith("#")
            key, _, value = stripped.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if is_commented:
                if key == "version.regex":
                    version_regex = value
                elif key == "version.filename":
                    version_filename = value
            elif key == "version":
                version = value
        if version:
            return version
        if version_regex and version_filename:
            file_rel = version_filename.replace("%(source.dir)s/", "").replace("%(source.dir)s", "")
            file_path = Path(profile.sourcedir) / file_rel
            if file_path.is_file():
                match = re.search(version_regex, file_path.read_text(encoding="utf-8", errors="replace"))
                if match:
                    return match.group(1)
        return ""

    def find_latest_apk(self, profile: Profile) -> Path | None:
        wsl_root = self._wsl_path(profile)
        bin_path = wsl_root / "bin"

        if not bin_path.is_dir():
            return None

        short_name = self.get_short_name(profile)
        if not short_name:
            return None

        version = self.get_version(profile)

        candidates = sorted(
            [p for p in bin_path.rglob("*.apk")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if version:
            exact_prefix = f"{short_name}-{version}-"
            matching = [p for p in candidates if p.stem.lower().startswith(exact_prefix.lower())]
            if matching:
                return matching[0]

        broad_prefix = f"{short_name}-"
        matching = [p for p in candidates if p.stem.lower().startswith(broad_prefix.lower())]
        if matching:
            return matching[0]

        return None
