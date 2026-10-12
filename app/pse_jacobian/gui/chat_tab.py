"""The 'Chat' tab: a multi-turn conversation with an LLM about the counterexample and
the app. Same provider layer as Discovery (local gguf/LM Studio, Claude, Mistral, Groq,
plus an offline 'sim' provider)."""
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QLineEdit, QPlainTextEdit, QComboBox,
                               QScrollArea)

from ..llm import providers
from ..i18n import t
from .llm_worker import ChatWorker


class ChatTab(QWidget):
    def __init__(self):
        super().__init__()
        self.history = []          # list of {role, content}
        self.worker = None
        self._build()

    def _build(self):
        # scroll wrapper so the whole tab (incl. the input row) is always reachable,
        # exactly like the other tabs — on a short screen the content scrolls.
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("chat_title")); title.setFont(QFont("", 14, QFont.Bold))
        title.setWordWrap(True)
        root.addWidget(title)

        cfg = QGroupBox(t("disc_provider")); g = QVBoxLayout(cfg)
        r1 = QHBoxLayout()
        self.provider = QComboBox()
        for spec in providers.list_providers():
            self.provider.addItem(spec.label, spec.key)
        self.provider.currentIndexChanged.connect(self._on_provider)
        r1.addWidget(QLabel(t("disc_provider_label"))); r1.addWidget(self.provider, 1)
        g.addLayout(r1)
        r2 = QHBoxLayout()
        self.endpoint = QLineEdit(); self.model = QLineEdit()
        r2.addWidget(QLabel("endpoint:")); r2.addWidget(self.endpoint, 2)
        r2.addWidget(QLabel("model:")); r2.addWidget(self.model, 1)
        g.addLayout(r2)
        r3 = QHBoxLayout()
        self.api_key = QLineEdit(); self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText(t("disc_key_ph"))
        r3.addWidget(QLabel("API key:")); r3.addWidget(self.api_key, 1)
        g.addLayout(r3)
        root.addWidget(cfg)

        self.view = QPlainTextEdit(); self.view.setReadOnly(True)
        self.view.setStyleSheet("font-size:12px;")
        self.view.setMinimumHeight(260)
        root.addWidget(self.view, 1)

        row = QHBoxLayout()
        self.input = QPlainTextEdit(); self.input.setMaximumHeight(70)
        self.input.setPlaceholderText(t("chat_input_ph"))
        row.addWidget(self.input, 1)
        col = QVBoxLayout()
        self.send_btn = QPushButton(t("chat_send"))
        self.send_btn.setStyleSheet("padding:6px; font-weight:bold;")
        self.send_btn.clicked.connect(self.send)
        self.clear_btn = QPushButton(t("chat_clear"))
        self.clear_btn.clicked.connect(self.clear)
        col.addWidget(self.send_btn); col.addWidget(self.clear_btn)
        row.addLayout(col)
        root.addLayout(row)

        self._on_provider(0)

    def _on_provider(self, _idx):
        spec = providers.SPECS[self.provider.currentData()]
        self.endpoint.setText(spec.default_endpoint)
        self.model.setText(spec.default_model)
        self.endpoint.setEnabled(spec.key != "sim")
        self.api_key.setEnabled(bool(spec.env_key))

    def _make_provider(self):
        return providers.LLMProvider(self.provider.currentData(),
                                     endpoint=self.endpoint.text(),
                                     model=self.model.text(),
                                     api_key=self.api_key.text() or None)

    def _render(self, pending=False):
        parts = []
        for m in self.history:
            who = t("chat_you") if m["role"] == "user" else t("chat_assistant")
            parts.append(f"{who}: {m['content']}")
        if pending:
            parts.append(f"{t('chat_assistant')}: {t('chat_thinking')}")
        self.view.setPlainText("\n\n".join(parts))
        self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().maximum())

    def send(self):
        text = self.input.toPlainText().strip()
        if not text:
            return
        try:
            prov = self._make_provider()
        except providers.LLMError as exc:
            self.history.append({"role": "assistant", "content": t("chat_error", e=exc)})
            self._render(); return
        self.history.append({"role": "user", "content": text})
        self.input.clear()
        self.send_btn.setEnabled(False)
        self._render(pending=True)
        self.worker = ChatWorker(prov, list(self.history), system=t("chat_system"))
        self.worker.done.connect(self._on_done)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_done(self, reply):
        self.send_btn.setEnabled(True)
        self.history.append({"role": "assistant", "content": reply})
        self._render()

    def _on_failed(self, msg):
        self.send_btn.setEnabled(True)
        self.history.append({"role": "assistant", "content": t("chat_error", e=msg)})
        self._render()

    def clear(self):
        self.history = []
        self._render()
