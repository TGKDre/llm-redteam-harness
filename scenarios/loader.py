
from __future__ import annotations
import yaml
from pathlib import Path
from pydantic import BaseModel, Field

class Scenario(BaseModel):
    id: str
    name: str
    severity: str
    description: str
    system_prompt: str = ""
    user_message: str = ""
    conversation: list[dict] = Field(default_factory=list)
    success_indicators: list[str] = Field(default_factory=list)
    failure_indicators: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

class ScenarioFile(BaseModel):
    name: str
    version: str
    category: str
    description: str
    scenarios: list[Scenario]

def load_scenario_file(path) -> ScenarioFile:
    with Path(path).open() as f:
        return ScenarioFile(**yaml.safe_load(f))

def load_all_scenarios(directory) -> list[Scenario]:
    all_s = []
    for yf in sorted(Path(directory).glob("*.yaml")):
        try:
            all_s.extend(load_scenario_file(yf).scenarios)
        except Exception as e:
            print(f"Warning: {yf}: {e}")
    return all_s
