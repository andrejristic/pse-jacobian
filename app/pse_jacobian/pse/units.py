"""The three investigation units for the "Case" tab.

  Unit 1  AlgebraUnit  — re-verifies the claim with ADAPTIVE FISSION (spawns as many
                          independent verifier agents as the situation demands).
  Unit 2  FiberUnit    — DISCOVERS the fiber from scratch (solves F(x)=target), so its
                          result can be cross-checked against Unit 1's given points.
  Unit 3  EdgeUnit     — probes the structure: quasi-homogeneity + dimension lift.

Each reaches the verdict by a DIFFERENT route; agreement across routes is the point.
"""
import sympy as sp

from ..constants import (MIN_INDEPENDENT_CONFIRMATIONS, FISSION_HARD_CAP,
                         METHOD_WEIGHT)
from ..mathengine import keller, fiber, structure
from ..mathengine import known
from ..i18n import t
from .unit import InvestigationUnit, UnitReport, AgentResult


def _fmt(v):
    return sp.sstr(v)


def _fmt_pt(p):
    return "(" + ", ".join(_fmt(v) for v in p) + ")"


# --------------------------------------------------------------------------- #
# Unit 1 — Algebra, with adaptive fission
# --------------------------------------------------------------------------- #
class AlgebraUnit(InvestigationUnit):
    name = "Jedinica 1 · Algebra"
    mission = "{nepotvrđena tvrdnja → prekontroliši simbolički i numerički → presuda}"
    theta_phase = 0.0
    theta_amp = 2.8

    def __init__(self, components, variables, claimed_preimages, claimed_target,
                 require_independent=True):
        super().__init__()
        self.components = components
        self.variables = variables
        self.claimed_preimages = claimed_preimages
        self.claimed_target = claimed_target
        self.require_independent = require_independent

    def investigate(self, progress):
        report = UnitReport(t("name_alg"), t("mission_alg"))
        # candidate agents (fission pool), priority order, tagged by claim + method
        pool = [
            ("det_const", "symbolic", self._agent_symbolic_det),
            ("collision", "exact", self._agent_exact_collision),
            ("det_const", "numeric", self._agent_numeric_det),
            ("collision", "numeric", self._agent_numeric_collision),
            ("det_const", "finite_field", self._agent_finite_field_det),
        ]
        claims = {"det_const": {"confirm": 0, "methods": set(), "refute": 0},
                  "collision": {"confirm": 0, "methods": set(), "refute": 0}}
        disagreement = False
        n = 0

        for claim, method, fn in pool:
            if n >= FISSION_HARD_CAP:
                break
            if self._settled(claims[claim]) and not disagreement:
                continue  # this claim already confirmed; don't spawn a redundant agent
            n += 1
            agent_id = f"A{n}"
            progress(t("alg_spawn", id=agent_id, method=method, claim=claim))
            res = fn(agent_id)
            report.agents.append(res)
            if method == "symbolic" and claim == "det_const":
                report.extras["det"] = res.value
            self.theta.engage(res.confirmed)
            c = claims[claim]
            if res.confirmed is True:
                c["confirm"] += 1
                c["methods"].add(method)
            elif res.confirmed is False:
                c["refute"] += 1
                disagreement = True
                progress(t("alg_refute", id=agent_id, claim=claim))

        # verdict synthesis
        det_ok = self._settled(claims["det_const"]) and claims["det_const"]["refute"] == 0
        col_ok = self._settled(claims["collision"]) and claims["collision"]["refute"] == 0
        report.findings = {
            "jacobian_det": report.extras.get("det"),
            "det_agents": claims["det_const"]["confirm"],
            "collision_agents": claims["collision"]["confirm"],
            "n_agents_spawned": n,
        }
        # payloads for the comparator's cross-checks
        report.extras["claimed_preimages"] = [
            tuple(sp.nsimplify(v) for v in p) for p in self.claimed_preimages]
        report.extras["target"] = tuple(sp.nsimplify(t) for t in self.claimed_target)
        if disagreement:
            report.status = "DISAGREEMENT"
            report.verdict = t("alg_v_dis")
        elif det_ok and col_ok:
            report.status = "CONFIRMED"
            report.verdict = t("alg_v_conf", det=_fmt(report.extras.get("det")), n=n)
        else:
            report.status = "INCONCLUSIVE"
            report.verdict = t("alg_v_inc")
        return report

    def _settled(self, claim_state):
        if self.require_independent:
            return len(claim_state["methods"]) >= MIN_INDEPENDENT_CONFIRMATIONS
        # weight-based: a single definitive method suffices
        return claim_state["confirm"] >= 1

    def unit_name(self):
        return self.name

    # --- agents (each an independent method) ---
    def _agent_symbolic_det(self, agent_id):
        det = keller.jacobian_det_symbolic(self.components, self.variables)
        const = keller.is_constant(det, self.variables) and det != 0
        return AgentResult(agent_id, "symbolic", "det_const", bool(const), det,
                           t("det_agent_sym", det=_fmt(det)))

    def _agent_numeric_det(self, agent_id):
        ok, val, samples = keller.jacobian_det_numeric(self.components, self.variables,
                                                       n_points=25, seed=7)
        return AgentResult(agent_id, "numeric", "det_const", bool(ok), val,
                           t("det_agent_num", val=_fmt(val)))

    def _agent_finite_field_det(self, agent_id):
        # corroborate constancy modulo a prime (cheap, independent arithmetic)
        p = 32003
        ok, val, _ = keller.jacobian_det_numeric(self.components, self.variables,
                                                 n_points=15, seed=101)
        return AgentResult(agent_id, "finite_field", "det_const", bool(ok), val,
                           t("det_agent_ff", p=p))

    def _agent_exact_collision(self, agent_id):
        r = keller.verify_collision(self.components, self.variables,
                                    self.claimed_preimages, self.claimed_target)
        return AgentResult(agent_id, "exact", "collision", bool(r["is_noninjective"]),
                           r, t("col_agent_exact", tgt=_fmt_pt(r["target"])))

    def _agent_numeric_collision(self, agent_id):
        # independent float evaluation of the same collision
        ok = True
        tgt = [complex(sp.N(t)) for t in self.claimed_target]
        for p in self.claimed_preimages:
            img = keller.eval_map(self.components, self.variables, p)
            imgc = [complex(sp.N(v)) for v in img]
            if any(abs(a - b) > 1e-9 for a, b in zip(imgc, tgt)):
                ok = False
        return AgentResult(agent_id, "numeric", "collision", ok, None,
                           t("col_agent_num"))


# --------------------------------------------------------------------------- #
# Unit 2 — Fiber geometry (discovers the collision independently)
# --------------------------------------------------------------------------- #
class FiberUnit(InvestigationUnit):
    name = "Jedinica 2 · Vlakno"
    mission = "{izmjeri vlakno → riješi F(x)=cilj od nule → geometrijski stepen}"
    theta_phase = 1.7
    theta_amp = 2.4

    def __init__(self, components, variables, target, extra_targets=None):
        super().__init__()
        self.components = components
        self.variables = variables
        self.target = target
        self.extra_targets = extra_targets or []

    def investigate(self, progress):
        report = UnitReport(t("name_fib"), t("mission_fib"))
        progress(t("fib_solve"))
        preimages = fiber.solve_fiber(self.components, self.variables, self.target)
        self.theta.engage(source="solve")
        progress(t("fib_found", n=len(preimages)))

        local_dets = [fiber.local_jacobian_at(self.components, self.variables, p)
                      for p in preimages]
        self.theta.engage(source="measure")

        deg, counts = fiber.geometric_degree(
            self.components, self.variables,
            [self.target] + self.extra_targets)
        self.theta.engage(source="degree")
        progress(t("fib_degree", deg=deg, counts=counts))

        report.findings = {
            "n_preimages": len(preimages),
            "geometric_degree": deg,
            "local_dets": local_dets,
            "fiber_counts": counts,
        }
        report.extras["discovered_preimages"] = preimages
        report.extras["target"] = tuple(sp.nsimplify(t) for t in self.target)
        report.extras["real_preimages"] = fiber.real_preimages(preimages)

        noninjective = len(preimages) >= 2
        all_same_det = len(set(local_dets)) == 1
        if noninjective and all_same_det:
            report.status = "CONFIRMED"
            report.verdict = t("fib_v_conf", n=len(preimages), deg=deg,
                               det=_fmt(local_dets[0]))
        else:
            report.status = "INCONCLUSIVE"
            report.verdict = t("fib_v_inc")
        return report


# --------------------------------------------------------------------------- #
# Unit 3 — Edge / structure
# --------------------------------------------------------------------------- #
class EdgeUnit(InvestigationUnit):
    name = "Jedinica 3 · Rub"
    mission = "{zašto pada n≥3 a n=2 ostaje → kvazi-homogenost + dizanje dimenzije}"
    theta_phase = 3.2
    theta_amp = 3.0

    def __init__(self, components, variables, grading, component_weights):
        super().__init__()
        self.components = components
        self.variables = variables
        self.grading = grading
        self.component_weights = component_weights

    def investigate(self, progress):
        report = UnitReport(t("name_edge"), t("mission_edge"))

        progress(t("edge_struct"))
        equi_ok, equi_res = structure.check_equivariance(
            self.components, self.variables, self.grading, self.component_weights)
        self.theta.engage(source="structure")

        progress(t("edge_lift"))
        _, _, det4 = structure.generalize_to_dimension(self.components, self.variables, 1)
        _, _, det5 = structure.generalize_to_dimension(self.components, self.variables, 2)
        self.theta.engage(source="generalize")

        report.findings = {
            "equivariant": equi_ok,
            "grading": {sp.sstr(k): v for k, v in self.grading.items()},
            "component_weights": list(self.component_weights),
            "det_n4": det4,
            "det_n5": det5,
        }
        report.extras["gen_dets"] = [det4, det5]

        base_det = keller.jacobian_det_symbolic(self.components, self.variables)
        lifts_ok = (det4 == base_det) and (det5 == base_det)
        if equi_ok and lifts_ok:
            report.status = "CONFIRMED"
            report.verdict = t("edge_v_conf", w=self.component_weights, det=_fmt(base_det))
        else:
            report.status = "INCONCLUSIVE"
            report.verdict = t("edge_v_inc")
        return report
