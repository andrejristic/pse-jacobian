"""Main window: screen-aware sizing, language toggle, tab host.

Turn 1 has a single tab ('Case'); later turns add the rest. The language toggle
rebuilds the tabs so every string is re-resolved through i18n.
"""
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QToolBar, QComboBox, QLabel,
                               QWidget)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, QTimer

from .case_tab import CaseTab
from .workbench_tab import WorkbenchTab
from .discovery_tab import DiscoveryTab
from .frontier_tab import FrontierTab
from .family_tab import FamilyTab
from .diagnostics_tab import DiagnosticsTab
from .chat_tab import ChatTab
from .report_tab import ReportTab
from .. import __version__
from ..i18n import t, set_lang, get_lang


class MainWindow(QMainWindow):
    # safety margin on every side, so all four edges stay on-screen and grabbable
    SCREEN_MARGIN = 24
    # generous clearance above the PHYSICAL screen bottom, measured from full geometry —
    # robust even when the WM fails to exclude a bottom panel from availableGeometry
    # (as on some Cinnamon/Mint setups). The window is resizable, so the user can always
    # grow it afterwards if they want less bottom gap.
    BOTTOM_RESERVE = 96

    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 420)   # can shrink small; content scrolls
        self._fitted = False
        self._build_toolbar()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._populate_tabs()
        self._apply_initial_size()

    # ---- sizing ----
    def _avail(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        return screen.availableGeometry()

    def _usable(self):
        """The rectangle the window frame must stay inside.

        Horizontal + top come from availableGeometry() (respects side/top panels). The
        BOTTOM is measured from the PHYSICAL screen bottom (full geometry) minus a
        generous reserve, so a bottom taskbar can't clip the window even when the WM
        doesn't report it in availableGeometry.
        """
        screen = self.screen() or QGuiApplication.primaryScreen()
        avail, full = screen.availableGeometry(), screen.geometry()
        m = self.SCREEN_MARGIN
        left = avail.left() + m
        top = avail.top() + m
        width = avail.width() - 2 * m
        bottom_limit = min(avail.bottom(), full.bottom() - self.BOTTOM_RESERVE)
        height = max(self.minimumHeight(), bottom_limit - top)
        return (left, top, width, height)

    def _center_in_usable(self):
        ux, uy, uw, uh = self._usable()
        fg = self.frameGeometry()
        x = ux + max(0, (uw - fg.width()) // 2)
        y = uy + max(0, (uh - fg.height()) // 2)
        self.move(self.x() + (x - fg.left()), self.y() + (y - fg.top()))

    def _apply_initial_size(self):
        """Rough sizing before the window is shown (frame size not yet known)."""
        _ux, _uy, uw, uh = self._usable()
        w = max(self.minimumWidth(), min(1120, uw))
        h = max(self.minimumHeight(), min(800, uh))
        self.resize(w, h)
        self._center_in_usable()

    def showEvent(self, event):
        super().showEvent(event)
        # After the first real show the window FRAME (title bar + borders) is known, so
        # we can fit precisely and center inside the usable area.
        if not self._fitted:
            self._fitted = True
            QTimer.singleShot(0, self._fit_precisely)

    def _fit_precisely(self):
        _ux, _uy, uw, uh = self._usable()
        frame = self.frameGeometry()
        extra_w = frame.width() - self.width()      # title bar + borders overhead
        extra_h = frame.height() - self.height()
        new_w = min(self.width(), max(self.minimumWidth(), uw - extra_w))
        new_h = min(self.height(), max(self.minimumHeight(), uh - extra_h))
        if (new_w, new_h) != (self.width(), self.height()):
            self.resize(new_w, new_h)
        self._center_in_usable()

    # ---- toolbar / language ----
    def _build_toolbar(self):
        tb = QToolBar()
        tb.setMovable(False)
        self.addToolBar(tb)
        self.lang_label = QLabel(" " + t("lang_label") + " ")
        tb.addWidget(self.lang_label)
        self.lang_box = QComboBox()
        self.lang_box.addItem("Srpski", "sr")
        self.lang_box.addItem("English", "en")
        self.lang_box.setCurrentIndex(0 if get_lang() == "sr" else 1)
        self.lang_box.currentIndexChanged.connect(self._on_lang_changed)
        tb.addWidget(self.lang_box)

    def _on_lang_changed(self, _idx):
        set_lang(self.lang_box.currentData())
        self.lang_label.setText(" " + t("lang_label") + " ")
        self._populate_tabs()
        self.setWindowTitle(t("win_title", v=__version__))

    # ---- tabs ----
    def _populate_tabs(self):
        current = self.tabs.currentIndex()
        self.tabs.clear()
        self.tabs.addTab(CaseTab(), t("tab_case"))
        self.tabs.addTab(WorkbenchTab(), t("tab_workbench"))
        self.tabs.addTab(DiscoveryTab(), t("tab_discovery"))
        self.tabs.addTab(FrontierTab(), t("tab_frontier"))
        self.tabs.addTab(FamilyTab(), t("tab_family"))
        self.tabs.addTab(DiagnosticsTab(), t("tab_diagnostics"))
        self.tabs.addTab(ChatTab(), t("tab_chat"))
        self.tabs.addTab(ReportTab(), t("tab_report"))
        if 0 <= current < self.tabs.count():
            self.tabs.setCurrentIndex(current)
        self.setWindowTitle(t("win_title", v=__version__))
