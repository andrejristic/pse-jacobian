"""Compose the reproduction report from live unit reports + the comparator result."""
import datetime
import platform

import sympy as sp

from ..mathengine import known
from ..i18n import t


def _fmt_pt(p):
    return "(" + ", ".join(sp.sstr(v) for v in p) + ")"


def build(r1, r2, r3, cr):
    """Return the full report as plain text (current UI language)."""
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    env = f"Python {platform.python_version()}, sympy {sp.__version__}"

    L = []
    L.append(t("rep_title"))
    L.append("=" * 64)
    L.append(f"{t('rep_h_time')}: {ts}")
    L.append(f"{t('rep_h_env')}: {env}")
    L.append("")

    L.append(t("rep_h_map"))
    for s in known.COMPONENT_STR:
        L.append("  " + s)
    L.append("")

    L.append(t("rep_h_facts"))
    L.append(f"  det J = -2   ({t('rep_const')})")
    pts = "  ,  ".join(_fmt_pt(p) for p in known.CLAIMED_PREIMAGES)
    L.append(f"  {pts}")
    L.append(f"    ->  {_fmt_pt(known.CLAIMED_TARGET)}   (3 → 1)")
    L.append("")

    L.append(t("rep_h_units"))
    for r in (r1, r2, r3):
        L.append(f"  [{r.status}] {r.unit_name} — θ:{r.theta_health}")
        L.append(f"      {r.verdict}")
    L.append("")

    L.append(t("rep_h_comparator"))
    for c in cr.cross_checks:
        L.append(f"  [{'OK' if c.ok else 'NE'}] {c.name}")
    L.append(f"  {t('rep_h_consensus')}: {cr.consensus}  ({cr.confidence:.0%})")
    if cr.disagreements:
        L.append("  ! " + " | ".join(cr.disagreements))
    L.append("")

    L.append(t("rep_h_structure"))
    L.append("  " + t("rep_struct_line"))
    L.append("")

    L.append(t("rep_h_conclusion"))
    L.append("  " + t("rep_conclusion"))
    return "\n".join(L)
