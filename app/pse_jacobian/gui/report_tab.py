"""The 'Report' tab: run the case, compose a reproduction report, export it
(.txt/.html/.pdf), and keep an append-only audit ledger."""
import html
import os

from PySide6.QtGui import QFont, QTextDocument, QPdfWriter, QPageSize
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                               QGroupBox, QPlainTextEdit, QScrollArea, QFileDialog)

from ..mathengine import known
from ..pse.units import AlgebraUnit, FiberUnit, EdgeUnit
from ..pse import comparator, report, audit
from ..i18n import t
from .worker import UnitWorker


class ReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self.reports = {}
        self.workers = {}
        self.text = ""
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); root = QVBoxLayout(content)
        scroll.setWidget(content); outer.addWidget(scroll)

        title = QLabel(t("rep_title")); title.setFont(QFont("", 13, QFont.Bold))
        title.setWordWrap(True)
        root.addWidget(title)

        row = QHBoxLayout()
        self.gen_btn = QPushButton(t("rep_generate"))
        self.gen_btn.setStyleSheet("padding:8px; font-weight:bold;")
        self.gen_btn.clicked.connect(self.generate)
        row.addWidget(self.gen_btn)
        self.txt_btn = QPushButton(t("rep_export_txt"))
        self.pdf_btn = QPushButton(t("rep_export_pdf"))
        self.html_btn = QPushButton(t("rep_export_html"))
        self.txt_btn.clicked.connect(lambda: self.export("txt"))
        self.pdf_btn.clicked.connect(lambda: self.export("pdf"))
        self.html_btn.clicked.connect(lambda: self.export("html"))
        for b in (self.txt_btn, self.pdf_btn, self.html_btn):
            b.setEnabled(False); row.addWidget(b)
        row.addStretch(1)
        root.addLayout(row)

        self.status = QLabel(""); self.status.setStyleSheet("color:#2e7d32; font-size:11px;")
        root.addWidget(self.status)

        self.view = QPlainTextEdit(); self.view.setReadOnly(True)
        self.view.setStyleSheet("font-family:monospace; font-size:11px;")
        self.view.setMinimumHeight(280)
        root.addWidget(self.view)

        lbox = QGroupBox(t("rep_ledger")); ll = QVBoxLayout(lbox)
        self.ledger = QPlainTextEdit(); self.ledger.setReadOnly(True)
        self.ledger.setStyleSheet("font-family:monospace; font-size:10px; color:#555;")
        self.ledger.setMinimumHeight(120)
        ll.addWidget(self.ledger)
        root.addWidget(lbox)
        self._refresh_ledger()

    # ---- generate ----
    def generate(self):
        self.gen_btn.setEnabled(False)
        self.reports.clear()
        self.status.setText(t("rep_running"))
        units = {"J1": AlgebraUnit(known.COMPONENTS, known.VARS,
                                   known.CLAIMED_PREIMAGES, known.CLAIMED_TARGET),
                 "J2": FiberUnit(known.COMPONENTS, known.VARS, known.CLAIMED_TARGET,
                                 extra_targets=[(0, 1, 0), (1, 0, 0)]),
                 "J3": EdgeUnit(known.COMPONENTS, known.VARS, known.GRADING,
                                known.COMPONENT_WEIGHTS)}
        for tag, unit in units.items():
            w = UnitWorker(tag, unit)
            w.finished.connect(self._on_finished)
            self.workers[tag] = w
            w.start()

    def _on_finished(self, tag, rep):
        if rep is not None:
            self.reports[tag] = rep
        if len(self.reports) == 3:
            self._compose()

    def _compose(self):
        self.gen_btn.setEnabled(True)
        cr = comparator.compare(self.reports["J1"], self.reports["J2"], self.reports["J3"])
        self.text = report.build(self.reports["J1"], self.reports["J2"],
                                 self.reports["J3"], cr)
        self.view.setPlainText(self.text)
        for b in (self.txt_btn, self.pdf_btn, self.html_btn):
            b.setEnabled(True)
        audit.append(t("rep_audit_report"), f"{cr.consensus} {cr.confidence:.0%}")
        self.status.setText("")
        self._refresh_ledger()

    # ---- export ----
    def export(self, kind):
        if not self.text:
            return
        home = os.path.expanduser("~")
        default = os.path.join(home, f"pse_jacobian_izvjestaj.{kind}")
        path, _ = QFileDialog.getSaveFileName(self, "", default,
                                              f"*.{kind}")
        if not path:
            return
        try:
            if kind == "txt":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.text)
            elif kind == "html":
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"<pre>{html.escape(self.text)}</pre>")
            elif kind == "pdf":
                writer = QPdfWriter(path)
                writer.setPageSize(QPageSize(QPageSize.A4))
                doc = QTextDocument()
                doc.setHtml("<pre style='font-family:monospace; font-size:9pt'>"
                            + html.escape(self.text) + "</pre>")
                doc.print_(writer)
        except Exception as exc:
            self.status.setStyleSheet("color:#c62828; font-size:11px;")
            self.status.setText(t("rep_export_err", e=exc))
            return
        audit.append(t("rep_audit_export"), path)
        self.status.setStyleSheet("color:#2e7d32; font-size:11px;")
        self.status.setText(t("rep_saved", p=path))
        self._refresh_ledger()

    def _refresh_ledger(self):
        self.ledger.setPlainText(audit.read_all())
        self.ledger.verticalScrollBar().setValue(
            self.ledger.verticalScrollBar().maximum())
