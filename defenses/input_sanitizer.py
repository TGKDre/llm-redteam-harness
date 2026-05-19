
import re

PATTERNS = [
    r"ignore (all |previous |prior )?(instructions?|prompts?|context)",
    r"disregard (all |previous |your )?(instructions?|guidelines?|rules?)",
    r"override (system|safety|previous|all) (prompt|instructions?|restrictions?)",
    r"you (are|were) (now|henceforth) (called|named|acting as)",
]
_compiled = [re.compile(p, re.IGNORECASE) for p in PATTERNS]

def sanitize(text):
    triggered, matched, result = False, [], text
    for pat in _compiled:
        m = pat.search(result)
        if m:
            triggered = True
            matched.append(m.group(0))
            result = pat.sub("[REDACTED BY SECURITY FILTER]", result)
    return result, triggered, matched
