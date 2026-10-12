"""Fiber geometry: solve F(x)=target from scratch, count preimages, geometric degree.

This is Unit 2's territory — it *discovers* the collision instead of being handed it,
which is what makes the cross-check against Unit 1 meaningful.
"""
import sympy as sp
from sympy.solvers.polysys import solve_poly_system

from . import keller


def solve_fiber(components, variables, target):
    """Return the list of preimages of `target` as tuples of sympy numbers."""
    target = [sp.nsimplify(t) for t in target]
    eqs = [c - t for c, t in zip(components, target)]
    sols = solve_poly_system(eqs, *variables)
    # normalise to simplified tuples
    return [tuple(sp.nsimplify(sp.simplify(v)) for v in s) for s in sols]


def geometric_degree(components, variables, sample_targets):
    """Estimate the generic fiber size (geometric degree) by solving over several
    targets and taking the maximum finite count observed.
    """
    counts = []
    for t in sample_targets:
        try:
            counts.append(len(solve_fiber(components, variables, t)))
        except Exception:
            continue
    return (max(counts) if counts else None), counts


def local_jacobian_at(components, variables, point):
    """The Jacobian determinant evaluated at a specific preimage (should equal the
    constant everywhere — no local folding at any sheet of the fiber)."""
    J = keller.jacobian_matrix(components, variables)
    sub = {v: sp.nsimplify(p) for v, p in zip(variables, point)}
    return sp.nsimplify(J.subs(sub).det())


def image_targets(components, variables, k=3, seed=1):
    """Return k targets guaranteed to lie in the image (F evaluated at random integer
    points), so fiber counts are never empty and the generic degree is well estimated.
    """
    import random
    rng = random.Random(seed)
    targets = []
    for _ in range(k):
        pt = {v: sp.Integer(rng.randint(-3, 3)) for v in variables}
        targets.append(tuple(sp.nsimplify(c.subs(pt)) for c in components))
    return targets


def find_collision(components, variables, targets):
    """Return an explicit list of >=2 colliding preimages if some sampled target has a
    fiber of size >=2, else None."""
    for tg in targets:
        pre = solve_fiber(components, variables, tg)
        if len(pre) >= 2:
            return tg, pre
    return None, None


def real_preimages(preimages):
    """Filter to preimages that are purely real (for 3D plotting)."""
    out = []
    for p in preimages:
        if all(sp.im(sp.nsimplify(v)) == 0 for v in p):
            out.append(tuple(float(sp.re(v)) for v in p))
    return out
