"""Fiber visualization (1c): 3D real view + 2D projections + exact table.

Shows the three preimages of the collision target, and the hidden C*-orbit
lambda·(x,y,z) = (x/lambda, lambda·y, lambda^2·z) that organizes them — two of the
three non-origin preimages sit on the SAME real orbit (lambda = -1).
"""
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
import sympy as sp

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTableWidget,
                               QTableWidgetItem, QHeaderView)

from ..i18n import t


def _orbit_point(p0, t):
    """Real C* action on a base point p0=(x0,y0,z0): (x0/t, y0*t, z0*t^2)."""
    x0, y0, z0 = p0
    return (x0 / t, y0 * t, z0 * t * t)


class _Canvas(FigureCanvasQTAgg):
    def __init__(self, projection=None):
        self.fig = Figure(figsize=(5, 4), tight_layout=True)
        self.ax = self.fig.add_subplot(111, projection=projection)
        super().__init__(self.fig)


class FiberView(QWidget):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.c3d = _Canvas(projection="3d")
        self.c2d = _Canvas()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            [t("pv_h_pre"), t("pv_h_img"), t("pv_h_det"), t("pv_h_note")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.c3d, t("pv_3d"))
        self.tabs.addTab(self.c2d, t("pv_2d"))
        self.tabs.addTab(self.table, t("pv_tab"))
        lay = QVBoxLayout(self)
        lay.addWidget(self.tabs)
        self._placeholder()

    def _placeholder(self):
        for c in (self.c3d, self.c2d):
            c.ax.clear()
            txt = getattr(c.ax, "text2D", c.ax.text)   # 3D axes need text2D
            txt(0.5, 0.5, t("pv_ph"), ha="center", va="center",
                transform=c.ax.transAxes)
            c.draw()

    def update_fiber(self, report, target_str):
        real = report.extras.get("real_preimages", [])
        exact = report.extras.get("discovered_preimages", [])
        local_dets = report.findings.get("local_dets", [])
        self._draw_3d(real)
        self._draw_2d(real)
        self._fill_table(exact, local_dets, target_str)

    # ---- 3D ----
    def _draw_3d(self, real):
        ax = self.c3d.ax
        ax.clear()
        if real:
            base = None
            for p in real:
                if all(abs(v) > 1e-9 for v in p):
                    base = p
                    break
            if base is not None:
                ts = np.concatenate([np.linspace(-2.2, -0.32, 200),
                                     np.linspace(0.32, 2.2, 200)])
                orbit = np.array([_orbit_point(base, t) for t in ts])
                ax.plot(orbit[:, 0], orbit[:, 1], orbit[:, 2],
                        color="#888", lw=1, label=t("pv_orbit"))
            xs, ys, zs = zip(*real)
            ax.scatter(xs, ys, zs, s=70, color="#d1495b", depthshade=False)
            for p in real:
                ax.text(p[0], p[1], p[2], f"  ({p[0]:g}, {p[1]:g}, {p[2]:g})",
                        fontsize=8)
            ax.legend(loc="upper left", fontsize=8)
        ax.set_xlabel("x"); ax.set_ylabel("y"); ax.set_zlabel("z")
        ax.set_title(t("pv_3d_title"), fontsize=10)
        self.c3d.draw()

    # ---- 2D ----
    def _draw_2d(self, real):
        fig = self.c2d.fig
        fig.clear()
        pairs = [(0, 1, "x", "y"), (0, 2, "x", "z"), (1, 2, "y", "z")]
        for k, (i, j, li, lj) in enumerate(pairs):
            ax = fig.add_subplot(1, 3, k + 1)
            if real:
                base = next((p for p in real if all(abs(v) > 1e-9 for v in p)), None)
                if base is not None:
                    ts = np.concatenate([np.linspace(-2.2, -0.32, 200),
                                         np.linspace(0.32, 2.2, 200)])
                    orb = np.array([_orbit_point(base, t) for t in ts])
                    ax.plot(orb[:, i], orb[:, j], color="#bbb", lw=1)
                for p in real:
                    ax.scatter(p[i], p[j], s=45, color="#d1495b")
            ax.set_xlabel(li); ax.set_ylabel(lj)
            ax.grid(True, alpha=0.3)
        fig.suptitle(t("pv_2d_title"), fontsize=10)
        self.c2d.draw()

    # ---- table ----
    def _fill_table(self, exact, local_dets, target_str):
        self.table.setRowCount(len(exact))
        for r, p in enumerate(exact):
            pstr = "(" + ", ".join(sp.sstr(v) for v in p) + ")"
            det = sp.sstr(local_dets[r]) if r < len(local_dets) else "?"
            note = t("pv_note_orbit") if r != 1 else t("pv_note_fixed")
            for col, val in enumerate([pstr, target_str, det, note]):
                item = QTableWidgetItem(val)
                self.table.setItem(r, col, item)
