from dataclasses import dataclass, field
from enum import Enum, auto


class ActionType(Enum):
    ACTION = auto()
    PATCH = auto()


@dataclass
class CustomAction:
    id: str
    name: str
    description: str = ""
    type: ActionType = ActionType.ACTION
    logic: str = ""
    is_builtin: bool = False
