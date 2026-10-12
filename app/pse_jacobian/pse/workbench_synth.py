"""Workbench synthesizer — classify the map from the three unit reports and cross-check
their consistency (refute-by-default, like the Case comparator)."""
from dataclasses import dataclass, field

from ..mathengine import general
from ..i18n import t


@dataclass
class WorkbenchResult:
    verdict_key: str = "inconclusive"
    headline: str = ""
    consensus: str = "INCONCLUSIVE"     # CONFIRMED / DISAGREEMENT / INCONCLUSIVE
    cross_checks: list = field(default_factory=list)   # (name, ok, detail)
    disagreements: list = field(default_factory=list)


def classify_reports(keller_r, inj_r, inv_r):
    res = WorkbenchResult()
    is_keller = keller_r.findings.get("is_keller")
    degree = inj_r.findings.get("degree")
    inverse = inv_r.findings.get("inverse")

    res.verdict_key = general.classify(is_keller, degree)

    # consistency cross-check: an explicit inverse exists  <=>  degree == 1
    inv_found = inverse is not None
    consistent = (inv_found == (degree == 1)) if degree is not None else True
    res.cross_checks.append(
        (t("wb_cc_consistency"), consistent,
         t("wb_cc_consistency_d", inv=(t("wb_yes") if inv_found else t("wb_no")), deg=degree)))
    if not consistent:
        res.disagreements.append(t("wb_cc_consistency"))

    # a unit in disagreement (Keller anomaly) is a red flag
    if keller_r.status == "DISAGREEMENT":
        res.disagreements.append(keller_r.verdict)

    headlines = {
        "counterexample": t("wb_head_counter"),
        "keller_invertible": t("wb_head_invertible"),
        "not_keller": t("wb_head_notkeller"),
        "inconclusive": t("wb_head_inconclusive"),
    }
    res.headline = headlines.get(res.verdict_key, headlines["inconclusive"])
    if res.disagreements:
        res.consensus = "DISAGREEMENT"
    elif res.verdict_key == "inconclusive":
        res.consensus = "INCONCLUSIVE"
    else:
        res.consensus = "CONFIRMED"
    return res
