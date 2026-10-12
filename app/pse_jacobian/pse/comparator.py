"""Comparator — the Seldon/Physician role.

It does NO mathematics of its own. It ingests the three independent unit reports and
cross-checks their OVERLAPPING claims, refute-by-default: consensus is declared only
if every cross-check passes and no unit is in disagreement. Any mismatch is logged
loudly (master file: "audit-log silence after activity = suspicion, not relief").
"""
from dataclasses import dataclass, field

import sympy as sp

from ..i18n import t


@dataclass
class CrossCheck:
    name: str
    ok: bool
    detail: str


@dataclass
class ComparatorResult:
    cross_checks: list = field(default_factory=list)
    disagreements: list = field(default_factory=list)
    consensus: str = "PENDING"          # CONFIRMED / DISAGREEMENT / INCONCLUSIVE
    headline: str = ""
    confidence: float = 0.0


def _as_set(points):
    return {tuple(sp.nsimplify(v) for v in p) for p in points}


def compare(algebra, fiber, edge):
    """algebra/fiber/edge are UnitReport objects."""
    res = ComparatorResult()

    # --- cross-check 1: independent fiber discovery matches the verified points ---
    claimed = _as_set(algebra.extras.get("claimed_preimages", []))
    discovered = _as_set(fiber.extras.get("discovered_preimages", []))
    match = bool(claimed) and claimed == discovered
    res.cross_checks.append(CrossCheck(
        t("cc1"), match,
        t("cc1_d", a=len(claimed), b=len(discovered),
          eq=t("eq_same") if match else t("eq_diff"))))
    if not match:
        res.disagreements.append(t("dis_fiber"))

    # --- cross-check 2: the Jacobian value agrees across all three units ---
    det1 = sp.nsimplify(algebra.extras.get("det")) if algebra.extras.get("det") is not None else None
    local_dets = fiber.findings.get("local_dets", [])
    gen_dets = [sp.nsimplify(d) for d in edge.extras.get("gen_dets", [])]
    dets = set()
    if det1 is not None:
        dets.add(det1)
    dets.update(sp.nsimplify(d) for d in local_dets)
    dets.update(gen_dets)
    det_agree = len(dets) == 1 and det1 is not None
    res.cross_checks.append(CrossCheck(
        t("cc2"), det_agree,
        t("cc2_d", vals=", ".join(sp.sstr(d) for d in dets))))
    if not det_agree:
        res.disagreements.append(t("dis_det"))

    # --- cross-check 3: cardinality == geometric degree == #collision points ---
    n_pre = fiber.findings.get("n_preimages")
    deg = fiber.findings.get("geometric_degree")
    card_ok = (n_pre == deg == len(claimed)) and n_pre and n_pre >= 2
    res.cross_checks.append(CrossCheck(
        t("cc3"), bool(card_ok),
        t("cc3_d", n=n_pre, deg=deg, t=len(claimed))))
    if not card_ok:
        res.disagreements.append(t("dis_card"))

    # --- cross-check 4: no unit internally disagreed; all concluded CONFIRMED ---
    statuses = {"J1": algebra.status, "J2": fiber.status, "J3": edge.status}
    all_conf = all(s == "CONFIRMED" for s in statuses.values())
    res.cross_checks.append(CrossCheck(
        t("cc4"), all_conf,
        ", ".join(f"{k}={v}" for k, v in statuses.items())))
    if not all_conf:
        res.disagreements.append(t("dis_status"))

    # --- theta / rubber-stamp screen ---
    for tag, rep in (("J1", algebra), ("J2", fiber), ("J3", edge)):
        if rep.theta_health == "flatline":
            res.disagreements.append(t("dis_flat", tag=tag))

    passed = sum(1 for c in res.cross_checks if c.ok)
    res.confidence = passed / len(res.cross_checks)
    if res.disagreements:
        res.consensus = "DISAGREEMENT"
        res.headline = t("head_dis")
    elif passed == len(res.cross_checks):
        res.consensus = "CONFIRMED"
        res.headline = t("head_conf")
    else:
        res.consensus = "INCONCLUSIVE"
        res.headline = t("head_inc")
    return res
