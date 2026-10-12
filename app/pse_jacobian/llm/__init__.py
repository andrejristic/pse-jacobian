"""LLM provider abstraction (local gguf / LM Studio, Claude, Mistral, Groq).

Turn 1: interface + stub only. Wired into a Chat tab and the Discovery loop in later
turns. No keys are hardcoded; they are read from the environment / a config dialog.
"""
from .providers import (LLMProvider, list_providers, extract_map,  # noqa: F401
                        LLMError, SPECS)
