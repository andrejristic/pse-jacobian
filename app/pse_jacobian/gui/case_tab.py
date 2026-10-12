"""The 'Case' tab: three PSE units investigate the counterexample separately, in
their own threads, then the comparator cross-checks their independent results.
"""
import statistics

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                               QGroupBox, QTextEdit, QTableWidget, QTableWidgetItem,
                               QHeaderView, QSplitter, QFrame, QScrollArea)

from ..mathengine import known
from ..pse.units import AlgebraUnit, FiberUnit, EdgeUnit
from ..pse import comparator
from ..i18n import t
from .worker import UnitWorker
from .plot_canvas import FiberView

STATUS_COLOR = {
    "CONFIRMED": "#2e7d32", "DISAGREEMENT": "#c62828",
    "INCONCLUSIVE": "#e65100", "PENDING": "#555",
    "RUNNING": "#1565c0", "ERROR": "#c62828",
}


class UnitPanel(QGroupBox):
    def __init__(self, title, mission):
        super().__init__(title)
        lay = QVBoxLayout(self)
        self.status = QLabel("● PENDING")
        self.status.setStyleSheet("font-weight:bold; color:#555;")
        m = QLabel(mission); m.setWordWrap(True)
        m.setStyleSheet("color:#666; font-size:11px;")
        self.log = QTextEdit(); self.log.setReadOnly(True)
        self.log.setMinimumHeight(80)
        self.log.setStyleSheet("font-family:monospace; font-size:11px;")
        self.verdict = QLabel(""); self.verdict.setWordWrap(True)
        self.verdict.setStyleSheet("font-size:11px;")
        self.theta = QLabel("θ: —"); self.theta.setStyleSheet("font-size:11px; color:#444;")
        for w in (self.status, m, self.log, self.theta, self.verdict):
            lay.addWidget(w)

    def set_status(self, text, color):
        self.status.setText("● " + text)
        self.status.setStyleSheet(f"font-weight:bold; color:{color};")

    def append(self, msg):
        self.log.append(msg)

    def set_report(self, rep):
        self.set_status(rep.status, STATUS_COLOR.get(rep.status, "#555"))
        self.verdict.setText(t("verdict_prefix") + rep.verdict)
        traj = rep.theta_trajectory
        mean = statistics.fmean(traj) if traj else 0
        sig = statistics.pstdev(traj) if len(traj) > 1 else 0
        self.theta.setText(t("theta_line", mean=mean, sig=sig,
                             health=rep.theta_health, n=len(traj)))


class CaseTab(QWidget):
    def __init__(self):
        super().__init__()
        self.reports = {}
        self.workers = {}
        self._build()

    def _build(self):
        # everything lives inside a scroll area so the window can be smaller than the
        # content on small screens (content scrolls instead of overflowing off-screen).
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        title = QLabel(t("case_title"))
        title.setFont(QFont("", 14, QFont.Bold))
        root.addWidget(title)

        mapbox = QGroupBox(t("mapbox_title"))
        ml = QVBoxLayout(mapbox)
        for s in known.COMPONENT_STR:
            lab = QLabel(s); lab.setStyleSheet("font-family:monospace; font-size:12px;")
            ml.addWidget(lab)
        tgt = QLabel(t("claimed_collision"))
        tgt.setStyleSheet("color:#666; font-size:11px;")
        ml.addWidget(tgt)
        root.addWidget(mapbox)

        self.run_btn = QPushButton(t("run_btn"))
        self.run_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.run_btn.clicked.connect(self.run_investigation)
        root.addWidget(self.run_btn)

        split = QSplitter(Qt.Horizontal)
        units_col = QWidget(); uc = QVBoxLayout(units_col)
        self.p1 = UnitPanel(t("panel_alg"), t("mission_alg"))
        self.p2 = UnitPanel(t("panel_fib"), t("mission_fib"))
        self.p3 = UnitPanel(t("panel_edge"), t("mission_edge"))
        for p in (self.p1, self.p2, self.p3):
            uc.addWidget(p)
        split.addWidget(units_col)
        self.fiber_view = FiberView()
        self.fiber_view.setMinimumHeight(380)
        split.addWidget(self.fiber_view)
        split.setSizes([520, 520])
        root.addWidget(split, 1)

        line = QFrame(); line.setFrameShape(QFrame.HLine); root.addWidget(line)
        comp_box = QGroupBox(t("comp_title"))
        cl = QVBoxLayout(comp_box)
        self.headline = QLabel(t("waiting"))
        self.headline.setWordWrap(True)
        self.headline.setFont(QFont("", 12, QFont.Bold))
        cl.addWidget(self.headline)
        self.xtable = QTableWidget(); self.xtable.setColumnCount(3)
        self.xtable.setHorizontalHeaderLabels([t("xh_check"), t("xh_result"), t("xh_detail")])
        self.xtable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.xtable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.xtable.setMaximumHeight(170)
        cl.addWidget(self.xtable)
        self.dislog = QLabel(""); self.dislog.setWordWrap(True)
        self.dislog.setStyleSheet("color:#c62828; font-size:11px;")
        cl.addWidget(self.dislog)
        root.addWidget(comp_box)

    # ---------------- run ----------------
    def run_investigation(self):
        self.run_btn.setEnabled(False)
        self.reports.clear()
        self.headline.setText(t("investigating")); self.dislog.setText("")
        self.headline.setStyleSheet("")
        self.xtable.setRowCount(0)
        units = {
            "J1": (self.p1, AlgebraUnit(known.COMPONENTS, known.VARS,
                                        known.CLAIMED_PREIMAGES, known.CLAIMED_TARGET)),
            "J2": (self.p2, FiberUnit(known.COMPONENTS, known.VARS, known.CLAIMED_TARGET,
                                      extra_targets=[(0, 1, 0), (1, 0, 0)])),
            "J3": (self.p3, EdgeUnit(known.COMPONENTS, known.VARS, known.GRADING,
                                     known.COMPONENT_WEIGHTS)),
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
        return {"J1": self.p1, "J2": self.p2, "J3": self.p3}[tag]

    def _on_progress(self, tag, msg):
        self._panel(tag).append(msg)

    def _on_finished(self, tag, report):
        if report is None:
            self._panel(tag).set_status(t("st_error"), STATUS_COLOR["ERROR"])
        else:
            self.reports[tag] = report
            self._panel(tag).set_report(report)
            if tag == "J2":
                self.fiber_view.update_fiber(report, "(−1/4, 0, 0)")
        if len(self.reports) == 3:
            self._run_comparator()

    def _run_comparator(self):
        self.run_btn.setEnabled(True)
        cr = comparator.compare(self.reports["J1"], self.reports["J2"], self.reports["J3"])
        color = STATUS_COLOR.get(cr.consensus, "#555")
        self.headline.setText(cr.headline + "\n" + t("confidence", c=cr.confidence))
        self.headline.setStyleSheet(f"color:{color};")
        self.xtable.setRowCount(len(cr.cross_checks))
        for r, c in enumerate(cr.cross_checks):
            self.xtable.setItem(r, 0, QTableWidgetItem(c.name))
            mark = QTableWidgetItem(t("mark_ok") if c.ok else t("mark_no"))
            mark.setForeground(Qt.darkGreen if c.ok else Qt.red)
            self.xtable.setItem(r, 1, mark)
            self.xtable.setItem(r, 2, QTableWidgetItem(c.detail))
        self.dislog.setText(
            "" if not cr.disagreements else t("disagreements") + " | ".join(cr.disagreements))
