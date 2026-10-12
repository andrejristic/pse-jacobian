"""QThread wrapper so each PSE unit runs in its own thread (design answer 3a).

The comparator only sees results once every unit thread has finished — i.e. the units
truly investigate 'zasebno' (separately), then their reports are compared.
"""
from PySide6.QtCore import QThread, Signal


class UnitWorker(QThread):
    progress = Signal(str, str)     # (unit_tag, message)
    finished = Signal(str, object)  # (unit_tag, UnitReport)

    def __init__(self, tag, unit):
        super().__init__()
        self.tag = tag
        self.unit = unit

    def run(self):
        def cb(msg):
            self.progress.emit(self.tag, msg)
        try:
            report = self.unit.run(cb)
        except Exception as exc:   # a unit dying must not take the app down
            self.progress.emit(self.tag, f"GREŠKA: {exc}")
            report = None
        self.finished.emit(self.tag, report)
