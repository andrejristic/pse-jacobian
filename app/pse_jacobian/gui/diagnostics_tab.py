"""The 'Diagnostics' tab: the full PSE machinery for a run — theta trajectories, the four
attractors, the domain-adapted 10 game-form posterior, adaptive-fission log, and the
Seldon/Physician swarm view."""
import statistics

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QGroupBox,
                               QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
                               QPlainTextEdit)

from ..mathengine import known
from ..pse.units import AlgebraUnit, FiberUnit, EdgeUnit
from ..pse import comparator, gameforms, attractors
from ..i18n import t
from .worker import UnitWorker
from .plot_canvas import _Canvas

GEO_KEY = {"none": "dg_geo_none", "narcissistic": "dg_geo_narcissistic",
           "borderline": "dg_geo_borderline", "codependent": "dg_geo_codependent",
           "schizoid": "dg_geo_schizoid"}


class DiagnosticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.reports = {}
        self.workers = {}
        self.posts = {}
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("dg_title")); title.setFont(QFont("", 14, QFont.Bold))
        title.setWordWrap(True)
        root.addWidget(title)

        self.run_btn = QPushButton(t("dg_run"))
        self.run_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.run_btn.clicked.connect(self.run_diag)
        root.addWidget(self.run_btn)

        self.canvas = _Canvas(); self.canvas.setMinimumHeight(240)
        self._theta_placeholder()
        root.addWidget(self.canvas)

        self.table = QTableWidget(); self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            [t("dg_h_unit"), t("dg_h_mu"), t("dg_h_sigma"), t("dg_h_rho"),
             t("dg_h_health"), t("dg_h_attr"), t("dg_h_game"), t("dg_h_conf")])
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.table.setMaximumHeight(150)
        self.table.cellClicked.connect(self._on_row)
        root.addWidget(self.table)

        root.addWidget(QLabel(t("dg_posterior_label")))
        self.posterior = QPlainTextEdit(); self.posterior.setReadOnly(True)
        self.posterior.setStyleSheet("font-family:monospace; font-size:11px;")
        self.posterior.setMaximumHeight(150)
        root.addWidget(self.posterior)

        fbox = QGroupBox(t("dg_fission")); fl = QVBoxLayout(fbox)
        self.fission = QPlainTextEdit(); self.fission.setReadOnly(True)
        self.fission.setStyleSheet("font-family:monospace; font-size:11px;")
        self.fission.setMaximumHeight(120)
        fl.addWidget(self.fission)
        root.addWidget(fbox)

        sbox = QGroupBox(t("dg_seldon")); sl = QVBoxLayout(sbox)
        self.geometry = QLabel(""); self.geometry.setWordWrap(True)
        self.consensus = QLabel(""); self.consensus.setWordWrap(True)
        self.physician = QLabel(""); self.physician.setWordWrap(True)
        self.physician.setFont(QFont("", 11, QFont.Bold))
        for w in (self.geometry, self.consensus, self.physician):
            sl.addWidget(w)
        root.addWidget(sbox)

    def _theta_placeholder(self):
        ax = self.canvas.ax; ax.clear()
        ax.text(0.5, 0.5, t("dg_waiting"), ha="center", va="center",
                transform=ax.transAxes)
        self.canvas.draw()

    # ---- run ----
    def run_diag(self):
        self.run_btn.setEnabled(False)
        self.reports.clear(); self.posts.clear()
        self.table.setRowCount(0); self.fission.clear(); self.posterior.clear()
        self.geometry.setText(""); self.consensus.setText(t("dg_running"))
        self.physician.setText("")
        units = {
            "J1": AlgebraUnit(known.COMPONENTS, known.VARS,
                              known.CLAIMED_PREIMAGES, known.CLAIMED_TARGET),
            "J2": FiberUnit(known.COMPONENTS, known.VARS, known.CLAIMED_TARGET,
                            extra_targets=[(0, 1, 0), (1, 0, 0)]),
            "J3": EdgeUnit(known.COMPONENTS, known.VARS, known.GRADING,
                           known.COMPONENT_WEIGHTS),
        }
        for tag, unit in units.items():
            w = UnitWorker(tag, unit)
            w.finished.connect(self._on_finished)
            self.workers[tag] = w
            w.start()

    def _on_finished(self, tag, report):
        if report is not None:
            self.reports[tag] = report
        if len(self.reports) == 3:
            self._render()

    # ---- render ----
    def _render(self):
        self.run_btn.setEnabled(True)
        order = [("J1", "Algebra"), ("J2", "Fiber"), ("J3", "Edge")]
        # theta plot
        ax = self.canvas.ax; ax.clear()
        ax.axhspan(25, 35, color="#c8e6c9", alpha=0.4, label="healthy [25,35]")
        for tag, name in order:
            traj = self.reports[tag].theta_trajectory
            ax.plot(range(len(traj)), traj, marker="o", label=name)
        ax.set_xlabel("korak / step"); ax.set_ylabel("θ")
        ax.set_ylim(20, 40); ax.legend(fontsize=8, loc="upper right")
        ax.set_title("theta trajektorije", fontsize=10)
        self.canvas.draw()

        # per-unit table + posteriors
        self.table.setRowCount(3)
        worst = "none"
        worst_unit = None
        for row, (tag, name) in enumerate(order):
            r = self.reports[tag]
            traj = r.theta_trajectory
            mu = statistics.fmean(traj); sd = statistics.pstdev(traj) if len(traj) > 1 else 0
            g = gameforms.posterior(r); self.posts[tag] = (name, g)
            attr = attractors.classify(traj, registry_size=1)
            if attr != "none" and worst == "none":
                worst, worst_unit = attr, name
            cells = [name, f"{mu:.1f}", f"{sd:.2f}", f"{g['rho']:+.2f}",
                     r.theta_health, attr, g["dominant_name"], f"{g['confidence']:.2f}"]
            for col, val in enumerate(cells):
                item = QTableWidgetItem(val)
                if col == 4 and val != "healthy":
                    item.setForeground(Qt.red)
                if col == 5 and val != "none":
                    item.setForeground(Qt.red)
                self.table.setItem(row, col, item)

        # fission log (Unit 1)
        lines = []
        for a in self.reports["J1"].agents:
            mark = "✓" if a.confirmed else ("✗" if a.confirmed is False else "?")
            lines.append(f"{a.agent_id} [{a.method:12s}] {a.claim:10s} {mark}  {a.detail}")
        self.fission.setPlainText("\n".join(lines))

        # Seldon / Physician
        self.geometry.setText(t("dg_geometry") + " " + t(GEO_KEY[worst]))
        cr = comparator.compare(self.reports["J1"], self.reports["J2"], self.reports["J3"])
        self.consensus.setText(t("dg_consensus") + " " + cr.consensus
                               + (" — " + " | ".join(cr.disagreements) if cr.disagreements else ""))
        if worst == "none" and not cr.disagreements:
            self.physician.setText(t("dg_physician") + " " + t("dg_phys_ok"))
            self.physician.setStyleSheet("color:#2e7d32; font-weight:bold;")
        else:
            self.physician.setText(t("dg_physician") + " "
                                   + t("dg_phys_flag", u=worst_unit or "?", a=worst))
            self.physician.setStyleSheet("color:#c62828; font-weight:bold;")

        self._on_row(0, 0)

    def _on_row(self, row, _col):
        order = ["J1", "J2", "J3"]
        if 0 <= row < len(order) and order[row] in self.posts:
            name, g = self.posts[order[row]]
            lines = [f"{name} — game-form posterior (C={g['confidence']:.2f}, "
                     f"σ={g['sigma']:.3f}, ρ={g['rho']:+.2f}, drift={g['drift']:.2f}):"]
            for k, v in sorted(g["probs"].items(), key=lambda kv: -kv[1]):
                bar = "█" * int(round(v * 30))
                lines.append(f"  {gameforms.NAME[k]:34s} {v*100:5.1f}%  {bar}")
            self.posterior.setPlainText("\n".join(lines))
