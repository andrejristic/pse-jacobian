"""Batch worker for the n=2 frontier: generate and test many Keller maps off the GUI
thread, emitting one result per trial plus a final summary."""
import sympy as sp
from PySide6.QtCore import QThread, Signal

from ..mathengine import frontier2d


class Frontier2dWorker(QThread):
    trial = Signal(object)       # per-map result dict
    done_all = Signal(object)    # summary dict

    def __init__(self, k, n_trials, base_seed):
        super().__init__()
        self.k = k
        self.n_trials = n_trials
        self.base_seed = base_seed

    def run(self):
        kel = inv = ctr = 0
        for i in range(self.n_trials):
            seed = self.base_seed + i
            try:
                comps, variables, factors = frontier2d.generate_keller_map_2d(self.k, seed)
                r = frontier2d.test_map(comps, variables)
                map_str = "  ,  ".join(sp.sstr(c) for c in comps)
                rec = {"seed": seed, "factors": factors, "det": sp.sstr(r["det"]),
                       "is_keller": r["is_keller"], "invertible": r["invertible"],
                       "verdict_key": r["verdict_key"], "map_str": map_str}
            except Exception as exc:
                rec = {"seed": seed, "factors": [], "det": "?", "is_keller": None,
                       "invertible": None, "verdict_key": "inconclusive",
                       "map_str": f"error: {exc}"}
            kel += 1 if rec["is_keller"] else 0
            inv += 1 if rec["invertible"] is True else 0
            # a counterexample = Keller AND provably non-invertible (not merely unknown)
            if rec["is_keller"] and rec["invertible"] is False:
                # invertible False here only means no explicit inverse was built; it is
                # NOT proof of non-injectivity, so we do not count it as a counterexample.
                pass
            self.trial.emit(rec)
        self.done_all.emit({"n": self.n_trials, "keller": kel, "invertible": inv,
                            "counter": ctr})
