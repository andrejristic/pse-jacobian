"""Provider-agnostic LLM layer using only the standard library (urllib).

Targets:
  local     -> OpenAI-compatible /chat/completions (LM Studio, llama.cpp server, ...)
  groq      -> OpenAI-compatible (Groq)
  mistral   -> OpenAI-compatible (Mistral)
  claude    -> Anthropic /v1/messages
  sim       -> offline local stub (no network): returns a canned proposal for testing

No key is hardcoded; keys come from the GUI field or the environment. Network calls are
wrapped so a failure returns a readable error string instead of crashing the thread.
"""
import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass


@dataclass
class ProviderSpec:
    key: str
    label: str
    default_endpoint: str
    default_model: str
    env_key: str        # environment variable to read the API key from
    openai_style: bool  # True -> /chat/completions ; False -> Anthropic messages


SPECS = {
    "sim":     ProviderSpec("sim", "Lokalna simulacija (test, bez mreže)", "", "sim", "", True),
    "local":   ProviderSpec("local", "Lokalni GGUF / LM Studio",
                            "http://localhost:1234/v1", "local-model", "", True),
    "claude":  ProviderSpec("claude", "Claude (Anthropic)",
                            "https://api.anthropic.com", "claude-fable-5",
                            "ANTHROPIC_API_KEY", False),
    "mistral": ProviderSpec("mistral", "Mistral",
                            "https://api.mistral.ai/v1", "mistral-large-latest",
                            "MISTRAL_API_KEY", True),
    "groq":    ProviderSpec("groq", "Groq",
                            "https://api.groq.com/openai/v1",
                            "llama-3.3-70b-versatile", "GROQ_API_KEY", True),
}


def list_providers():
    return list(SPECS.values())


# canned proposal for the offline test provider (the known counterexample)
_SIM_RESPONSE = """VARS: x, y, z
MAP:
(1 + x*y)**3 * z + y**2*(1 + x*y)*(4 + 3*x*y)
y + 3*x*(1 + x*y)**2 * z + 3*x*y**2*(4 + 3*x*y)
2*x - 3*x**2*y - x**3*z
"""


class LLMError(Exception):
    pass


class LLMProvider:
    def __init__(self, key, endpoint=None, model=None, api_key=None, timeout=60):
        if key not in SPECS:
            raise LLMError(f"Nepoznat provajder: {key}")
        self.spec = SPECS[key]
        self.endpoint = (endpoint or self.spec.default_endpoint).rstrip("/")
        self.model = model or self.spec.default_model
        self.api_key = api_key or (os.environ.get(self.spec.env_key, "")
                                   if self.spec.env_key else "")
        self.timeout = timeout

    def complete(self, system, user, max_tokens=800):
        """One-shot: used by the Discovery tab."""
        return self.chat([{"role": "user", "content": user}], system=system,
                         max_tokens=max_tokens)

    def chat(self, messages, system=None, max_tokens=800):
        """Multi-turn: `messages` is a list of {role, content} (user/assistant)."""
        if self.spec.key == "sim":
            return self._sim_chat(messages)
        if self.spec.openai_style:
            return self._openai_chat(messages, system, max_tokens)
        return self._anthropic_chat(messages, system, max_tokens)

    def _sim_chat(self, messages):
        last = next((m["content"] for m in reversed(messages)
                     if m["role"] == "user"), "")
        return ("[sim — offline test provajder]\n"
                "Kontraprimjer je potvrđen: mapa C³→C³ s Jakobijanom −2 koja je 3-na-1, "
                "pa Jacobian Conjecture pada za n≥3 (n=2 ostaje otvoreno). "
                f"Pitao si: „{last[:120]}“. Poveži pravi provajder (LM Studio/Claude/"
                "Mistral/Groq) za stvaran razgovor.")

    # --- OpenAI-compatible (local / groq / mistral) ---
    def _openai_chat(self, messages, system, max_tokens):
        url = f"{self.endpoint}/chat/completions"
        msgs = ([{"role": "system", "content": system}] if system else []) + messages
        body = {"model": self.model, "messages": msgs,
                "max_tokens": max_tokens, "temperature": 0.7}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        data = self._post(url, body, headers)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise LLMError(f"Neočekivan odgovor: {json.dumps(data)[:300]}")

    # --- Anthropic (claude) ---
    def _anthropic_chat(self, messages, system, max_tokens):
        url = f"{self.endpoint}/v1/messages"
        body = {"model": self.model, "max_tokens": max_tokens, "messages": messages}
        if system:
            body["system"] = system
        headers = {"Content-Type": "application/json",
                   "x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
        data = self._post(url, body, headers)
        try:
            return data["content"][0]["text"]
        except (KeyError, IndexError):
            raise LLMError(f"Neočekivan odgovor: {json.dumps(data)[:300]}")

    def _post(self, url, body, headers):
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            raise LLMError(f"HTTP {exc.code}: {detail}")
        except urllib.error.URLError as exc:
            raise LLMError(f"Mreža/veza: {exc.reason}")
        except Exception as exc:
            raise LLMError(str(exc))


def extract_map(text):
    """Pull (vars_string, components_string) out of an LLM response.

    Expected format:
        VARS: x, y, z
        MAP:
        <component 1>
        <component 2>
        ...
    Returns (vars_str_or_None, components_str_or_None). Tolerates code fences and stray
    prose; on failure returns (None, None) so the caller can show the raw text.
    """
    import sympy as _sp
    vars_s = None
    comps = []
    lines = text.splitlines()
    in_map = False
    for ln in lines:
        s = ln.strip().strip("`").strip()
        up = s.upper()
        if up.startswith("VARS:"):
            vars_s = s.split(":", 1)[1].strip()
            in_map = False
            continue
        if up.startswith("MAP:"):
            in_map = True
            continue
        if in_map:
            if not s or s.startswith("#"):
                continue
            try:
                _sp.sympify(s)          # keep only lines that are real expressions
            except Exception:
                in_map = False          # trailing prose / fence -> stop collecting
                continue
            comps.append(s)
    return vars_s, ("\n".join(comps) if comps else None)
