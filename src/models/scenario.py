from dataclasses import dataclass, field
from datetime import datetime

from .action import Action, ActionState


@dataclass
class Scenario:
    name: str
    description: str = ""
    action_sequence: list[Action] = field(default_factory=list)
    custom_action_names: dict[int, str] = field(default_factory=dict)
    stop_on_failure: bool = True
    is_predefined: bool = False


@dataclass
class ScenarioRun:
    scenario_name: str
    start_time: datetime
    duration: float = 0.0
    per_action_status: dict[str, ActionState] = field(default_factory=dict)
    overall_status: ActionState = ActionState.IDLE
