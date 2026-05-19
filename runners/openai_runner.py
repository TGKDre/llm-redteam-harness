
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from runners.base import BaseRunner

class OpenAIRunner(BaseRunner):
    def __init__(self, model="gpt-4o", api_key="", **kwargs):
        super().__init__(model, **kwargs)
        self._api_key = api_key
        self._cl = None
    def _get(self):
        if not self._cl:
            from openai import OpenAI
            self._cl = OpenAI(api_key=self._api_key or None)
        return self._cl
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def run(self, system_prompt, messages):
        if system_prompt and (not messages or messages[0].get("role") != "system"):
            messages = [{"role":"system","content":system_prompt}] + messages
        t0 = time.perf_counter()
        r = self._get().chat.completions.create(model=self.model, messages=messages,
            temperature=self.config.get("temperature", 0.0),
            max_tokens=self.config.get("max_tokens", 1024))
        return r.choices[0].message.content or "", (r.usage.prompt_tokens if r.usage else 0), (time.perf_counter()-t0)*1000
