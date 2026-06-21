from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Profile:
    name: str
    sourcedir: str = ""
    spec_path: str = ""
    adb_path: str = "adb"
    excluded_files: list[str] = field(default_factory=list)
    wsl_dir: str = ""
    wsl_distro: str = "Ubuntu-22.04"
    patches: list[str] = field(default_factory=list)
    delete_exclusions: list[str] = field(default_factory=list)
