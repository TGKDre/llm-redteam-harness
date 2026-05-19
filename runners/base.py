
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class RunResult:
    scenario_id: str
    scenario_name: str
    category: str
    severity: str
    tags: list
    model: str
    prompt_tokens: int
    output: str
    latency_ms: float
    error: str | None = None
    defended: bool = False
    defense_triggered: bool = False
    attack_succeeded: bool | None = None
    judge_reasoning: str = ""

class BaseRunner(ABC):
    def __init__(self, model: str, **kwargs):
        self.model = model
        self.config = kwargs
    @abstractmethod
    def run(self, system_prompt: str, messages: list[dict]) -> tuple[str, int, float]: ...
