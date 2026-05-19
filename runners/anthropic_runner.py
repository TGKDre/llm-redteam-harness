
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from runners.base import BaseRunner

class AnthropicRunner(BaseRunner):
    def __init__(self, model="claude-3-5-sonnet-20241022", api_key="", **kwargs):
        super().__init__(model, **kwargs)
        self._api_key = api_key
        self._cl = None
    def _get(self):
        if not self._cl:
            import anthropic
            self._cl = anthropic.Anthropic(api_key=self._api_key or None)
        return self._cl
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def run(self, system_prompt, messages):
        msgs = [m for m in messages if m.get("role") != "system"]
        t0 = time.perf_counter()
        r = self._get().messages.create(model=self.model,
            max_tokens=self.config.get("max_tokens",1024),
            system=system_prompt or "", messages=msgs)
        return r.content[0].text if r.content else "", (r.usage.input_tokens if r.usage else 0), (time.perf_counter()-t0)*1000
