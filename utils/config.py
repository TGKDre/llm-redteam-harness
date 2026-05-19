
from dataclasses import dataclass, field
import os

@dataclass
class HarnessConfig:
    model: str = "gpt-4o"
    provider: str = "openai"
    temperature: float = 0.0
    max_tokens: int = 1024
    defend: bool = False
    report_dir: str = "reports"
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

def load_config(**overrides):
    return HarnessConfig(**{k: v for k, v in overrides.items() if v is not None})
