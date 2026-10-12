"""Batch worker for the Family tab: generate and verify conjugated counterexamples."""
import sympy as sp
from PySide6.QtCore import QThread, Signal

from ..mathengine import family


def _fmt_pt(p):
    return "(" + ", ".join(sp.sstr(v) for v in p) + ")"


class FamilyWorker(QThread):
    variant = Signal(object)     # per-variant record
    done_all = Signal(object)    # summary

    def __init__(self, n_variants, base_seed):
        super().__init__()
        self.n_variants = n_variants
        self.base_seed = base_seed

    def run(self):
        n_ce = 0
        for i in range(self.n_variants):
            seed = self.base_seed + i
            try:
                v = family.make_variant(seed)
                r = family.verify_variant(v)
                comps = v["components"]
                map_full = ("VARS: x, y, z\nMAP:\n"
                            + "\n".join(sp.sstr(c) for c in comps))
                coll = "  ,  ".join(_fmt_pt(p) for p in v["preimages"]) \
                       + "  →  " + _fmt_pt(v["target"])
                preview = sp.sstr(comps[0])
                rec = {"seed": seed, "det": sp.sstr(r["det"]),
                       "is_keller": r["is_keller"], "collides": r["collides"],
                       "is_ce": r["is_counterexample"], "map_full": map_full,
                       "collision": coll, "preview": preview}
                if r["is_counterexample"]:
                    n_ce += 1
            except Exception as exc:
                rec = {"seed": seed, "det": "?", "is_keller": None, "collides": None,
                       "is_ce": False, "map_full": f"error: {exc}", "collision": "",
                       "preview": f"error: {exc}"}
            self.variant.emit(rec)
        self.done_all.emit({"n": self.n_variants, "counter": n_ce})
