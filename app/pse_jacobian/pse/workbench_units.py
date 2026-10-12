"""Workbench units — classify an ARBITRARY polynomial map C^n -> C^n.

  KellerUnit       — is det J a nonzero constant? (adaptive fission: symbolic + numeric)
  InjectivityUnit  — geometric degree over image-sampled targets; find a collision if k>1
  InverseUnit      — if injective, attempt an explicit polynomial inverse

They run in separate threads; a small synthesizer (workbench_synth) classifies the map.
"""
import sympy as sp

from ..mathengine import keller, fiber, general
from ..i18n import t
from .unit import InvestigationUnit, UnitReport, AgentResult


def _fmt(v):
    return sp.sstr(v)


def _fmt_pt(p):
    return "(" + ", ".join(_fmt(v) for v in p) + ")"


class KellerUnit(InvestigationUnit):
    def __init__(self, components, variables):
        super().__init__()
        self.components = components
        self.variables = variables

    def investigate(self, progress):
        report = UnitReport(t("wb_name_keller"), t("wb_mission_keller"))
        # agent 1: symbolic (definitive)
        progress(t("alg_spawn", id="A1", method="symbolic", claim="keller"))
        det = keller.jacobian_det_symbolic(self.components, self.variables)
        is_const = keller.is_constant(det, self.variables)
        is_keller = is_const and det != 0
        report.agents.append(AgentResult("A1", "symbolic", "keller", is_keller, det,
                                         t("det_agent_sym", det=_fmt(det))))
        self.theta.engage(is_keller)

        # agent 2: numeric corroboration of constancy
        progress(t("alg_spawn", id="A2", method="numeric", claim="keller"))
        all_eq, val, _ = keller.jacobian_det_numeric(self.components, self.variables,
                                                     n_points=25, seed=7)
        report.agents.append(AgentResult("A2", "numeric", "keller", all_eq, val,
                                         t("det_agent_num", val=_fmt(val))))
        self.theta.engage()

        # consistency: symbolic constancy must match numeric constancy
        if is_const != all_eq:
            progress(t("wb_keller_anomaly"))
            self.theta.engage(False)   # spike
            keller.jacobian_det_numeric(self.components, self.variables, n_points=40, seed=99)
            report.status = "DISAGREEMENT"
            report.verdict = t("wb_keller_anomaly")
            report.findings["is_keller"] = False
            return report

        report.findings["is_keller"] = bool(is_keller)
        report.extras["det"] = det
        report.status = "CONFIRMED"
        report.verdict = (t("wb_v_keller_yes", det=_fmt(det)) if is_keller
                          else t("wb_v_keller_no", det=_fmt(det)))
        return report


class InjectivityUnit(InvestigationUnit):
    def __init__(self, components, variables):
        super().__init__()
        self.components = components
        self.variables = variables

    def investigate(self, progress):
        report = UnitReport(t("wb_name_inj"), t("wb_mission_inj"))
        progress(t("fib_solve"))
        targets = fiber.image_targets(self.components, self.variables, k=3, seed=2)
        self.theta.engage(source="targets")
        try:
            deg, counts = fiber.geometric_degree(self.components, self.variables, targets)
        except Exception as exc:
            report.status = "INCONCLUSIVE"
            report.verdict = t("wb_v_inj_fail", e=exc)
            report.findings["degree"] = None
            return report
        self.theta.engage(source="degree")
        progress(t("fib_degree", deg=deg, counts=counts))

        report.findings["degree"] = deg
        if deg == 1:
            report.status = "CONFIRMED"
            report.verdict = t("wb_v_inj_yes")
        elif deg and deg >= 2:
            tg, pre = fiber.find_collision(self.components, self.variables, targets)
            report.extras["collision"] = (tg, pre)
            report.extras["discovered_preimages"] = pre or []
            report.extras["real_preimages"] = fiber.real_preimages(pre or [])
            report.extras["target"] = tg
            pts = " , ".join(_fmt_pt(p) for p in (pre or [])[:3])
            report.status = "CONFIRMED"
            report.verdict = t("wb_v_inj_no", deg=deg, pts=pts, tgt=_fmt_pt(tg) if tg else "?")
        else:
            report.status = "INCONCLUSIVE"
            report.verdict = t("wb_v_inj_fail", e="degree=None")
        return report


class InverseUnit(InvestigationUnit):
    def __init__(self, components, variables):
        super().__init__()
        self.components = components
        self.variables = variables

    def investigate(self, progress):
        report = UnitReport(t("wb_name_inv"), t("wb_mission_inv"))
        progress(t("wb_inv_check"))
        # independent quick injectivity check
        targets = fiber.image_targets(self.components, self.variables, k=2, seed=5)
        try:
            deg, _ = fiber.geometric_degree(self.components, self.variables, targets)
        except Exception:
            deg = None
        self.theta.engage(source="degree")

        if deg == 1:
            progress(t("wb_inv_try"))
            inv = general.attempt_inverse(self.components, self.variables)
            self.theta.engage(source="invert")
            report.findings["inverse"] = inv
            if inv:
                inv_str = " , ".join(f"{_fmt(k)} = {_fmt(v)}" for k, v in inv.items())
                report.status = "CONFIRMED"
                report.verdict = t("wb_v_inv_yes", inv=inv_str)
            else:
                report.status = "INCONCLUSIVE"
                report.verdict = t("wb_v_inv_maybe")
        else:
            report.findings["inverse"] = None
            self.theta.engage(source="noinv")
            report.status = "CONFIRMED"
            report.verdict = t("wb_v_inv_no")
        return report
