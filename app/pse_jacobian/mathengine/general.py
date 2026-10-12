"""General (arbitrary-map) support for the Workbench tab: parse a user map, attempt a
polynomial inverse, and classify the map with respect to the Jacobian Conjecture.
"""
import sympy as sp

from . import keller


class MapParseError(Exception):
    pass


def parse_map(varnames_str, body_str):
    """Parse variables ('x, y, z') and one component polynomial per line.

    Returns (components tuple, variables tuple). Raises MapParseError on bad input or if
    the number of components != number of variables (Jacobian must be square).
    """
    names = [s.strip() for s in varnames_str.replace(";", ",").split(",") if s.strip()]
    if not names:
        raise MapParseError("Nema varijabli / no variables.")
    syms = sp.symbols(names)
    if not isinstance(syms, (list, tuple)):
        syms = (syms,)
    local = {str(s): s for s in syms}
    lines = [ln.strip() for ln in body_str.splitlines() if ln.strip()]
    if not lines:
        raise MapParseError("Nema komponenti / no components.")
    comps = []
    for i, ln in enumerate(lines, 1):
        try:
            comps.append(sp.sympify(ln, locals=local))
        except Exception as exc:
            raise MapParseError(f"Linija {i}: {exc}")
    if len(comps) != len(syms):
        raise MapParseError(
            f"Broj komponenti ({len(comps)}) ≠ broj varijabli ({len(syms)}); "
            f"Jakobijan mora biti kvadratni.")
    return tuple(comps), tuple(syms)


def attempt_inverse(components, variables, max_terms=200):
    """Best-effort symbolic inverse: solve {y_i = F_i(x)} for the x_i.

    Returns a dict {var: expression_in_y} if a single polynomial-looking inverse is
    found, else None. Wrapped defensively; may return None on hard maps.
    """
    ys = sp.symbols(f"y0:{len(variables)}")
    eqs = [c - y for c, y in zip(components, ys)]
    try:
        sols = sp.solve(eqs, list(variables), dict=True)
    except Exception:
        return None
    if not sols or len(sols) != 1:
        return None
    sol = sols[0]
    if set(sol.keys()) != set(variables):
        return None
    inv = {}
    for v in variables:
        expr = sp.simplify(sol[v])
        if len(str(expr)) > max_terms:      # reject monstrous / non-polynomial blobs
            return None
        inv[v] = expr
    return inv


def classify(is_keller, degree):
    """Return a verdict key describing the map w.r.t. the Jacobian Conjecture."""
    if not is_keller:
        return "not_keller"
    if degree is None:
        return "inconclusive"
    if degree == 1:
        return "keller_invertible"
    if degree >= 2:
        return "counterexample"
    return "inconclusive"


# --- presets so the user can see every verdict type immediately ---
PRESETS = [
    ("preset_counterexample", "x, y, z",
     "(1 + x*y)**3 * z + y**2*(1 + x*y)*(4 + 3*x*y)\n"
     "y + 3*x*(1 + x*y)**2 * z + 3*x*y**2*(4 + 3*x*y)\n"
     "2*x - 3*x**2*y - x**3*z"),
    ("preset_automorphism", "x, y", "x + y**2\ny"),
    ("preset_identity", "x, y", "x\ny"),
    ("preset_not_keller", "x, y", "x**2\ny"),
]
