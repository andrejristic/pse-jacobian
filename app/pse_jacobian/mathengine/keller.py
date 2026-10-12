"""Core Keller-map operations, all exact where possible.

A "Keller map" is a polynomial map with constant nonzero Jacobian determinant — the
premise of the Jacobian Conjecture. These functions are method-diverse on purpose so
the PSE swarm can confirm the same fact along independent routes.
"""
import random
import sympy as sp


def jacobian_matrix(components, variables):
    return sp.Matrix(list(components)).jacobian(sp.Matrix(list(variables)))


def jacobian_det_symbolic(components, variables):
    """Route 1 (definitive): fully expanded symbolic determinant."""
    return sp.expand(jacobian_matrix(components, variables).det())


def is_constant(expr, variables):
    expr = sp.simplify(expr)
    return not any(expr.has(v) for v in variables)


def jacobian_det_numeric(components, variables, n_points=25, seed=0):
    """Route 2 (corroborating): evaluate det(J) at random integer points.

    Returns (all_equal, common_value_or_None, samples). If det is a constant it must
    take that same value at every probe; any disagreement is a red flag.
    """
    J = jacobian_matrix(components, variables)
    rng = random.Random(seed)
    values, samples = set(), []
    for _ in range(n_points):
        pt = {v: sp.Integer(rng.randint(-6, 6)) for v in variables}
        val = sp.nsimplify(J.subs(pt).det())
        values.add(val)
        samples.append((tuple(pt[v] for v in variables), val))
    all_equal = len(values) == 1
    common = next(iter(values)) if all_equal else None
    return all_equal, common, samples


def eval_map(components, variables, point):
    """Evaluate F at a point given as a tuple aligned with `variables`.

    Uses expand (not simplify): at rational points a polynomial expands to an exact
    number, and simplify would be needlessly slow on large (e.g. conjugated) maps.
    """
    sub = {v: sp.nsimplify(p) for v, p in zip(variables, point)}
    return tuple(sp.expand(c.subs(sub, simultaneous=True)) for c in components)


def verify_collision(components, variables, preimages, target):
    """Exact route: check every claimed preimage maps to `target`, and that the
    preimages are genuinely distinct.

    Returns a dict with per-point images, a match flag, and a distinct flag.
    """
    target = tuple(sp.nsimplify(t) for t in target)
    images = [eval_map(components, variables, p) for p in preimages]
    all_hit = all(img == target for img in images)
    distinct = len({tuple(sp.nsimplify(v) for v in p) for p in preimages}) == len(preimages)
    return {
        "target": target,
        "images": images,
        "all_hit_target": all_hit,
        "preimages_distinct": distinct,
        "is_noninjective": all_hit and distinct and len(preimages) >= 2,
    }


def is_keller_map(components, variables):
    """Return (is_keller, det). Keller <=> det is a nonzero constant."""
    det = jacobian_det_symbolic(components, variables)
    return (is_constant(det, variables) and det != 0, det)
