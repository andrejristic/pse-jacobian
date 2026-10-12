"""The 'Workbench' tab: enter any polynomial map C^n -> C^n; the swarm classifies it
(Keller? injective? invertible?) and delivers a verdict w.r.t. the Jacobian Conjecture.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QLineEdit, QPlainTextEdit, QComboBox,
                               QScrollArea, QSplitter, QFrame, QTableWidget,
                               QTableWidgetItem, QHeaderView)

from ..mathengine import general
from ..pse.workbench_units import KellerUnit, InjectivityUnit, InverseUnit
from ..pse import workbench_synth
from ..i18n import t
from .worker import UnitWorker
from .case_tab import UnitPanel, STATUS_COLOR
from .plot_canvas import FiberView


class WorkbenchTab(QWidget):
    def __init__(self):
        super().__init__()
        self.reports = {}
        self.workers = {}
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("wb_title")); title.setFont(QFont("", 14, QFont.Bold))
        root.addWidget(title)

        # --- input ---
        inbox = QGroupBox()
        il = QVBoxLayout(inbox)
        prow = QHBoxLayout()
        prow.addWidget(QLabel(t("wb_preset_label")))
        self.preset = QComboBox()
        for key, vs, body in general.PRESETS:
            self.preset.addItem(t(key), (vs, body))
        self.preset.addItem(t("preset_custom"), None)
        self.preset.currentIndexChanged.connect(self._on_preset)
        prow.addWidget(self.preset); prow.addStretch(1)
        il.addLayout(prow)

        il.addWidget(QLabel(t("wb_vars_label")))
        self.vars_edit = QLineEdit("x, y, z")
        il.addWidget(self.vars_edit)
        il.addWidget(QLabel(t("wb_comps_label")))
        self.comps_edit = QPlainTextEdit()
        self.comps_edit.setStyleSheet("font-family:monospace;")
        self.comps_edit.setMinimumHeight(90)
        il.addWidget(self.comps_edit)
        root.addWidget(inbox)

        self.run_btn = QPushButton(t("wb_analyze"))
        self.run_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.run_btn.clicked.connect(self.analyze)
        root.addWidget(self.run_btn)

        # --- units + fiber ---
        split = QSplitter(Qt.Horizontal)
        col = QWidget(); cc = QVBoxLayout(col)
        self.pk = UnitPanel(t("wb_panel_keller"), t("wb_mission_keller"))
        self.pi = UnitPanel(t("wb_panel_inj"), t("wb_mission_inj"))
        self.pv = UnitPanel(t("wb_panel_inv"), t("wb_mission_inv"))
        for p in (self.pk, self.pi, self.pv):
            cc.addWidget(p)
        split.addWidget(col)
        self.fiber_view = FiberView(); self.fiber_view.setMinimumHeight(360)
        split.addWidget(self.fiber_view)
        split.setSizes([520, 520])
        root.addWidget(split, 1)

        # --- verdict ---
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
        self.xtable.setMaximumHeight(120)
        vl.addWidget(self.xtable)
        root.addWidget(vbox)

        # default to the counterexample preset
        self.preset.setCurrentIndex(0)
        self._on_preset(0)

    def _on_preset(self, _idx):
        data = self.preset.currentData()
        if data is None:
            return
        vs, body = data
        self.vars_edit.setText(vs)
        self.comps_edit.setPlainText(body)

    # ---------------- run ----------------
    def analyze(self):
        try:
            comps, variables = general.parse_map(self.vars_edit.text(),
                                                 self.comps_edit.toPlainText())
        except general.MapParseError as exc:
            self.headline.setText(t("wb_parse_error", e=exc))
            self.headline.setStyleSheet("color:#c62828;")
            return
        self.run_btn.setEnabled(False)
        self.reports.clear()
        self.headline.setText(t("investigating")); self.headline.setStyleSheet("")
        self.xtable.setRowCount(0)
        units = {
            "K": (self.pk, KellerUnit(comps, variables)),
            "I": (self.pi, InjectivityUnit(comps, variables)),
            "V": (self.pv, InverseUnit(comps, variables)),
        }
        for tag, (panel, unit) in units.items():
            panel.log.clear()
            panel.set_status(t("st_running"), STATUS_COLOR["RUNNING"])
            panel.verdict.setText("")
            w = UnitWorker(tag, unit)
            w.progress.connect(self._on_progress)
            w.finished.connect(self._on_finished)
            self.workers[tag] = w
            w.start()

    def _panel(self, tag):
        return {"K": self.pk, "I": self.pi, "V": self.pv}[tag]

    def _on_progress(self, tag, msg):
        self._panel(tag).append(msg)

    def _on_finished(self, tag, report):
        if report is None:
            self._panel(tag).set_status(t("st_error"), STATUS_COLOR["ERROR"])
        else:
            self.reports[tag] = report
            self._panel(tag).set_report(report)
            if tag == "I" and report.extras.get("discovered_preimages"):
                self.fiber_view.update_fiber(report, "cilj / target")
        if len(self.reports) == 3:
            self._synthesize()

    def _synthesize(self):
        self.run_btn.setEnabled(True)
        r = workbench_synth.classify_reports(
            self.reports["K"], self.reports["I"], self.reports["V"])
        color = STATUS_COLOR.get(r.consensus, "#555")
        self.headline.setText(r.headline)
        self.headline.setStyleSheet(f"color:{color};")
        self.xtable.setRowCount(len(r.cross_checks))
        for i, (name, ok, detail) in enumerate(r.cross_checks):
            self.xtable.setItem(i, 0, QTableWidgetItem(name))
            mark = QTableWidgetItem(t("mark_ok") if ok else t("mark_no"))
            mark.setForeground(Qt.darkGreen if ok else Qt.red)
            self.xtable.setItem(i, 1, mark)
            self.xtable.setItem(i, 2, QTableWidgetItem(detail))
