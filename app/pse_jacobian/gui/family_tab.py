"""The 'Family' tab: generate OTHER explicit counterexamples in dimension 3 as the
affine orbit of the known map. Also states the coefficient-rigidity finding."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QSpinBox, QScrollArea, QTableWidget,
                               QTableWidgetItem, QHeaderView, QPlainTextEdit)

from ..i18n import t
from .family_worker import FamilyWorker


class FamilyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.records = []
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("fam_title")); title.setFont(QFont("", 14, QFont.Bold))
        root.addWidget(title)
        sub = QLabel(t("fam_sub")); sub.setWordWrap(True)
        sub.setStyleSheet("color:#666; font-size:11px;")
        root.addWidget(sub)
        rigid = QLabel(t("fam_rigid")); rigid.setWordWrap(True)
        rigid.setStyleSheet("color:#888; font-size:10px;")
        root.addWidget(rigid)

        ctl = QGroupBox(); c = QHBoxLayout(ctl)
        self.n = QSpinBox(); self.n.setRange(1, 60); self.n.setValue(8)
        self.seed = QSpinBox(); self.seed.setRange(0, 10**6); self.seed.setValue(1)
        c.addWidget(QLabel(t("fam_n"))); c.addWidget(self.n)
        c.addSpacing(12); c.addWidget(QLabel(t("fam_seed"))); c.addWidget(self.seed)
        c.addStretch(1)
        root.addWidget(ctl)

        self.run_btn = QPushButton(t("fam_run"))
        self.run_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.run_btn.clicked.connect(self.run_batch)
        root.addWidget(self.run_btn)

        self.summary = QLabel(""); self.summary.setWordWrap(True)
        self.summary.setFont(QFont("", 12, QFont.Bold))
        root.addWidget(self.summary)

        self.table = QTableWidget(); self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            [t("fam_h_seed"), t("fam_h_det"), t("fam_h_keller"),
             t("fam_h_coll"), t("fam_h_prev")])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setMinimumHeight(220)
        self.table.cellClicked.connect(self._on_row)
        root.addWidget(self.table, 1)

        root.addWidget(QLabel(t("fam_detail_label")))
        self.detail = QPlainTextEdit(); self.detail.setReadOnly(True)
        self.detail.setStyleSheet("font-family:monospace; font-size:11px;")
        self.detail.setMinimumHeight(120)
        root.addWidget(self.detail)

    def run_batch(self):
        self.run_btn.setEnabled(False)
        self.table.setRowCount(0)
        self.records = []
        self.detail.clear()
        self.summary.setText(t("fam_running", i=0, n=self.n.value()))
        self.summary.setStyleSheet("")
        self.worker = FamilyWorker(self.n.value(), self.seed.value())
        self.worker.variant.connect(self._on_variant)
        self.worker.done_all.connect(self._on_done)
        self.worker.start()

    def _on_variant(self, rec):
        self.records.append(rec)
        row = self.table.rowCount(); self.table.insertRow(row)
        cells = [str(rec["seed"]), rec["det"],
                 "✓" if rec["is_keller"] else "✗",
                 "✓" if rec["collides"] else "✗",
                 (rec["preview"][:70] + ("…" if len(rec["preview"]) > 70 else ""))]
        for col, val in enumerate(cells):
            item = QTableWidgetItem(val)
            if col in (2, 3) and (rec["is_keller"] if col == 2 else rec["collides"]):
                item.setForeground(Qt.darkGreen)
            self.table.setItem(row, col, item)
        self.summary.setText(t("fam_running", i=row + 1, n=self.n.value()))

    def _on_row(self, row, _col):
        if 0 <= row < len(self.records):
            rec = self.records[row]
            self.detail.setPlainText(rec["map_full"] + "\n\n# " + rec["collision"])

    def _on_done(self, s):
        self.run_btn.setEnabled(True)
        self.summary.setText(t("fam_summary", n=s["n"]))
        self.summary.setStyleSheet("color:#2e7d32;")
        if self.records:
            self._on_row(0, 0)
