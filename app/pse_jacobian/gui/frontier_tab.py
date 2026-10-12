"""The 'n=2 Frontier' tab: generate Keller maps in two variables and accumulate
evidence about the OPEN plane Jacobian Conjecture. Honest: this cannot settle it."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QSpinBox, QScrollArea, QTableWidget,
                               QTableWidgetItem, QHeaderView)

from ..i18n import t
from .frontier_worker import Frontier2dWorker

VERDICT_KEY = {
    "keller_invertible": "fr_v_invertible",
    "not_keller": "fr_v_notkeller",
    "keller_no_explicit_inverse": "fr_v_noinv",
    "inconclusive": "fr_v_inc",
}


class FrontierTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("fr_title")); title.setFont(QFont("", 14, QFont.Bold))
        root.addWidget(title)
        sub = QLabel(t("fr_sub")); sub.setWordWrap(True)
        sub.setStyleSheet("color:#666; font-size:11px;")
        root.addWidget(sub)

        # controls
        ctl = QGroupBox()
        c = QHBoxLayout(ctl)
        self.k = QSpinBox(); self.k.setRange(2, 5); self.k.setValue(3)
        self.n = QSpinBox(); self.n.setRange(1, 200); self.n.setValue(20)
        self.seed = QSpinBox(); self.seed.setRange(0, 10**6); self.seed.setValue(0)
        c.addWidget(QLabel(t("fr_k"))); c.addWidget(self.k)
        c.addSpacing(12); c.addWidget(QLabel(t("fr_n"))); c.addWidget(self.n)
        c.addSpacing(12); c.addWidget(QLabel(t("fr_seed"))); c.addWidget(self.seed)
        c.addStretch(1)
        root.addWidget(ctl)

        self.run_btn = QPushButton(t("fr_run"))
        self.run_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.run_btn.clicked.connect(self.run_batch)
        root.addWidget(self.run_btn)

        self.summary = QLabel(""); self.summary.setWordWrap(True)
        self.summary.setFont(QFont("", 12, QFont.Bold))
        root.addWidget(self.summary)
        self.note = QLabel(t("fr_disclaimer")); self.note.setWordWrap(True)
        self.note.setStyleSheet("color:#888; font-size:10px;")
        root.addWidget(self.note)

        self.table = QTableWidget(); self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            [t("fr_h_seed"), t("fr_h_factors"), t("fr_h_det"),
             t("fr_h_keller"), t("fr_h_inv"), t("fr_h_verdict")])
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        h.setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setMinimumHeight(300)
        root.addWidget(self.table, 1)

    def run_batch(self):
        self.run_btn.setEnabled(False)
        self.table.setRowCount(0)
        self._kel = self._inv = 0
        self.summary.setText(t("fr_running", i=0, n=self.n.value()))
        self.summary.setStyleSheet("")
        self.worker = Frontier2dWorker(self.k.value(), self.n.value(), self.seed.value())
        self.worker.trial.connect(self._on_trial)
        self.worker.done_all.connect(self._on_done)
        self.worker.start()

    def _on_trial(self, rec):
        row = self.table.rowCount()
        self.table.insertRow(row)
        vkey = VERDICT_KEY.get(rec["verdict_key"], "fr_v_inc")
        cells = [str(rec["seed"]), ", ".join(rec["factors"]), rec["det"],
                 "✓" if rec["is_keller"] else "✗",
                 "✓" if rec["invertible"] else ("✗" if rec["invertible"] is False else "?"),
                 t(vkey)]
        for col, val in enumerate(cells):
            item = QTableWidgetItem(val)
            if col == 4 and rec["invertible"]:
                item.setForeground(Qt.darkGreen)
            self.table.setItem(row, col, item)
        if rec["is_keller"]:
            self._kel += 1
        if rec["invertible"] is True:
            self._inv += 1
        self.summary.setText(t("fr_running", i=row + 1, n=self.n.value()))

    def _on_done(self, s):
        self.run_btn.setEnabled(True)
        line = t("fr_summary", n=s["n"], kel=s["keller"], inv=s["invertible"],
                 ctr=s["counter"])
        tail = (t("fr_summary_counter") if s["counter"] > 0
                else t("fr_summary_consistent"))
        self.summary.setText(line + "\n" + tail)
        self.summary.setStyleSheet("color:#c62828;" if s["counter"] > 0 else "color:#2e7d32;")
