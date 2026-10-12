"""QThread wrapper for a (possibly slow / network) LLM call, so the GUI never freezes."""
from PySide6.QtCore import QThread, Signal

from ..llm.providers import LLMError


class LLMWorker(QThread):
    done = Signal(str)      # raw response text
    failed = Signal(str)    # error message

    def __init__(self, provider, system, user, max_tokens=800):
        super().__init__()
        self.provider = provider
        self.system = system
        self.user = user
        self.max_tokens = max_tokens

    def run(self):
        try:
            text = self.provider.complete(self.system, self.user, self.max_tokens)
            self.done.emit(text)
        except LLMError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class ChatWorker(QThread):
    """Multi-turn chat call off the GUI thread."""
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, provider, messages, system=None, max_tokens=800):
        super().__init__()
        self.provider = provider
        self.messages = messages
        self.system = system
        self.max_tokens = max_tokens

    def run(self):
        try:
            text = self.provider.chat(self.messages, system=self.system,
                                      max_tokens=self.max_tokens)
            self.done.emit(text)
        except LLMError as exc:
            self.failed.emit(str(exc))
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
