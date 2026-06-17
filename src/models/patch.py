from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Patch:
    name: str
    description: str = ""
    enabled: bool = True


class PatchRegistry:
    _patches: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, description: str = ""):
        def decorator(func):
            cls._patches[name] = func
            func._patch_name = name
            func._patch_description = description
            return func
        return decorator

    @classmethod
    def get(cls, name: str) -> Callable | None:
        return cls._patches.get(name)

    @classmethod
    def list_patches(cls) -> list[Patch]:
        return [
            Patch(name=name, description=getattr(func, "_patch_description", ""))
            for name, func in cls._patches.items()
        ]
