"""The 'Discovery' tab: an LLM PROPOSES a candidate map; the swarm VERIFIES it exactly.

This reproduces the actual discovery method (creative generation + rigorous symbolic
verification). The Guardian is refute-by-default: most LLM proposals will fail the
Keller/injectivity checks, and that filter is the point.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QLineEdit, QPlainTextEdit, QComboBox,
                               QScrollArea, QFrame, QTableWidget, QTableWidgetItem,
                               QHeaderView)

from ..mathengine import general
from ..pse.workbench_units import KellerUnit, InjectivityUnit, InverseUnit
from ..pse import workbench_synth
from ..llm import providers
from ..i18n import t
from .worker import UnitWorker
from .llm_worker import LLMWorker
from .case_tab import UnitPanel, STATUS_COLOR


def _system_prompt():
    return t("disc_system")


class DiscoveryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.reports = {}
        self.workers = {}
        self.llm_worker = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("disc_title")); title.setFont(QFont("", 14, QFont.Bold))
        root.addWidget(title)
        sub = QLabel(t("disc_sub")); sub.setWordWrap(True)
        sub.setStyleSheet("color:#666; font-size:11px;")
        root.addWidget(sub)

        # --- provider config ---
        cfg = QGroupBox(t("disc_provider"))
        g = QVBoxLayout(cfg)
        r1 = QHBoxLayout()
        self.provider = QComboBox()
        for spec in providers.list_providers():
            self.provider.addItem(spec.label, spec.key)
        self.provider.currentIndexChanged.connect(self._on_provider)
        r1.addWidget(QLabel(t("disc_provider_label"))); r1.addWidget(self.provider, 1)
        g.addLayout(r1)
        r2 = QHBoxLayout()
        self.endpoint = QLineEdit()
        self.model = QLineEdit()
        r2.addWidget(QLabel("endpoint:")); r2.addWidget(self.endpoint, 2)
        r2.addWidget(QLabel("model:")); r2.addWidget(self.model, 1)
        g.addLayout(r2)
        r3 = QHBoxLayout()
        self.api_key = QLineEdit(); self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText(t("disc_key_ph"))
        r3.addWidget(QLabel("API key:")); r3.addWidget(self.api_key, 1)
        g.addLayout(r3)
        root.addWidget(cfg)

        # --- task ---
        root.addWidget(QLabel(t("disc_task_label")))
        self.task = QPlainTextEdit(t("disc_task_default"))
        self.task.setMinimumHeight(60)
        root.addWidget(self.task)

        brow = QHBoxLayout()
        self.propose_btn = QPushButton(t("disc_propose"))
        self.propose_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.propose_btn.clicked.connect(self.propose)
        self.verify_btn = QPushButton(t("disc_verify"))
        self.verify_btn.clicked.connect(self.verify)
        brow.addWidget(self.propose_btn); brow.addWidget(self.verify_btn)
        root.addLayout(brow)

        # --- LLM raw + parsed map ---
        self.raw = QPlainTextEdit(); self.raw.setReadOnly(True)
        self.raw.setMaximumHeight(110)
        self.raw.setStyleSheet("font-family:monospace; font-size:11px; color:#444;")
        root.addWidget(QLabel(t("disc_raw_label")))
        root.addWidget(self.raw)

        prow = QHBoxLayout()
        self.vars_edit = QLineEdit("x, y, z")
        prow.addWidget(QLabel(t("wb_vars_label"))); prow.addWidget(self.vars_edit, 1)
        root.addLayout(prow)
        root.addWidget(QLabel(t("wb_comps_label")))
        self.comps_edit = QPlainTextEdit()
        self.comps_edit.setStyleSheet("font-family:monospace;")
        self.comps_edit.setMinimumHeight(70)
        root.addWidget(self.comps_edit)

        # --- verification panels + verdict ---
        vrow = QHBoxLayout()
        self.pk = UnitPanel(t("wb_panel_keller"), t("wb_mission_keller"))
        self.pi = UnitPanel(t("wb_panel_inj"), t("wb_mission_inj"))
        self.pv = UnitPanel(t("wb_panel_inv"), t("wb_mission_inv"))
        for p in (self.pk, self.pi, self.pv):
            vrow.addWidget(p)
        root.addLayout(vrow)

        line = QFrame(); line.setFrameShape(QFrame.HLine); root.addWidget(line)
        vbox = QGroupBox(t("wb_verdict_title"))
        vl = QVBoxLayout(vbox)
        self.headline = QLabel(""); self.headline.setWordWrap(True)
        self.headline.setFont(QFont("", 12, QFont.Bold))
        vl.addWidget(self.headline)
        self.xtable = QTableWidget(); self.xtable.setColumnCount(3)
        self.xtable.setHorizontalHeaderLabels([t("xh_check"), t("xh_result"), t("xh_detail")])
        self.xtable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.xtable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.xtable.setMaximumHeight(110)
        vl.addWidget(self.xtable)
        root.addWidget(vbox)

        self._on_provider(0)

    # ---- provider ----
    def _on_provider(self, _idx):
        spec = providers.SPECS[self.provider.currentData()]
        self.endpoint.setText(spec.default_endpoint)
        self.model.setText(spec.default_model)
        self.endpoint.setEnabled(spec.key not in ("sim",))
        self.api_key.setEnabled(bool(spec.env_key))

    def _make_provider(self):
        key = self.provider.currentData()
        return providers.LLMProvider(key, endpoint=self.endpoint.text(),
                                     model=self.model.text(),
                                     api_key=self.api_key.text() or None)

    # ---- propose (LLM) ----
    def propose(self):
        try:
            prov = self._make_provider()
        except providers.LLMError as exc:
            self.raw.setPlainText(str(exc)); return
        self.propose_btn.setEnabled(False)
        self.raw.setPlainText(t("disc_calling"))
        self.llm_worker = LLMWorker(prov, _system_prompt(), self.task.toPlainText())
        self.llm_worker.done.connect(self._on_llm_done)
        self.llm_worker.failed.connect(self._on_llm_failed)
        self.llm_worker.start()

    def _on_llm_failed(self, msg):
        self.propose_btn.setEnabled(True)
        self.raw.setPlainText(t("disc_llm_error", e=msg))

    def _on_llm_done(self, text):
        self.propose_btn.setEnabled(True)
        self.raw.setPlainText(text)
        vs, comps = providers.extract_map(text)
        if vs:
            self.vars_edit.setText(vs)
        if comps:
            self.comps_edit.setPlainText(comps)
            self.verify()          # auto-verify a parseable proposal
        else:
            self.headline.setText(t("disc_no_map"))
            self.headline.setStyleSheet("color:#e65100;")

    # ---- verify (swarm) ----
    def verify(self):
        try:
            comps, variables = general.parse_map(self.vars_edit.text(),
                                                 self.comps_edit.toPlainText())
        except general.MapParseError as exc:
            self.headline.setText(t("wb_parse_error", e=exc))
            self.headline.setStyleSheet("color:#c62828;"); return
        self.verify_btn.setEnabled(False)
        self.reports.clear()
        self.headline.setText(t("investigating")); self.headline.setStyleSheet("")
        self.xtable.setRowCount(0)
        units = {"K": (self.pk, KellerUnit(comps, variables)),
                 "I": (self.pi, InjectivityUnit(comps, variables)),
                 "V": (self.pv, InverseUnit(comps, variables))}
        for tag, (panel, unit) in units.items():
            panel.log.clear()
            panel.set_status(t("st_running"), STATUS_COLOR["RUNNING"])
            panel.verdict.setText("")
            w = UnitWorker(tag, unit)
            w.progress.connect(lambda tg, m, p=panel: p.append(m))
            w.finished.connect(self._on_unit_done)
            self.workers[tag] = w
            w.start()

    def _panel(self, tag):
        return {"K": self.pk, "I": self.pi, "V": self.pv}[tag]

    def _on_unit_done(self, tag, report):
        if report is None:
            self._panel(tag).set_status(t("st_error"), STATUS_COLOR["ERROR"])
        else:
            self.reports[tag] = report
            self._panel(tag).set_report(report)
        if len(self.reports) == 3:
            self._synthesize()

    def _synthesize(self):
        self.verify_btn.setEnabled(True)
        r = workbench_synth.classify_reports(
            self.reports["K"], self.reports["I"], self.reports["V"])
        self.headline.setText(r.headline)
        self.headline.setStyleSheet(f"color:{STATUS_COLOR.get(r.consensus, '#555')};")
        self.xtable.setRowCount(len(r.cross_checks))
        for i, (name, ok, detail) in enumerate(r.cross_checks):
            self.xtable.setItem(i, 0, QTableWidgetItem(name))
            mark = QTableWidgetItem(t("mark_ok") if ok else t("mark_no"))
            mark.setForeground(Qt.darkGreen if ok else Qt.red)
            self.xtable.setItem(i, 1, mark)
            self.xtable.setItem(i, 2, QTableWidgetItem(detail))
