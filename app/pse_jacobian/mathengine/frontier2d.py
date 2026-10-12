"""n=2 frontier: generate Keller maps in two variables and test them.

The plane (n=2) Jacobian Conjecture is OPEN. We cannot settle it; we can build an
experimental platform. We generate genuine Keller maps by composing elementary
automorphisms (shears + triangular affine) — every such map has a constant nonzero
Jacobian by construction — and then INDEPENDENTLY test whether the swarm finds each one
invertible. Accumulated evidence ("N maps, all invertible, 0 counterexamples") is
consistent with the conjecture but is NOT a proof: this family (tame automorphisms)
cannot contain a hypothetical wild Keller map, if one exists.
"""
import random
import sympy as sp

from . import keller, general


def _random_poly(var, rng, max_deg=2, lo=-2, hi=2):
    deg = rng.randint(1, max_deg)
    return sum(rng.randint(lo, hi) * var**d for d in range(deg + 1))


def _elementary(kind, x, y, rng):
    """Return one elementary automorphism of C^2 as (f0, f1)."""
    if kind == "shear_x":                 # x -> x + p(y)
        return (x + _random_poly(y, rng), y)
    if kind == "shear_y":                 # y -> y + q(x)
        return (x, y + _random_poly(x, rng))
    # triangular affine, det = a*d (nonzero constant)
    a = rng.choice([1, -1, 2])
    d = rng.choice([1, -1])
    b = rng.randint(-2, 2)
    e, f = rng.randint(-2, 2), rng.randint(-2, 2)
    return (a * x + b * y + e, d * y + f)


def generate_keller_map_2d(k, seed):
    """Compose k elementary automorphisms. Returns (components, variables, factors)."""
    x, y = sp.symbols("x y")
    rng = random.Random(seed)
    cur0, cur1 = x, y
    kinds = ["shear_x", "shear_y", "affine"]
    used = []
    for _ in range(k):
        kind = rng.choice(kinds)
        f0, f1 = _elementary(kind, x, y, rng)
        # compose: new = f ∘ current  (substitute x->cur0, y->cur1 in f).
        # simultaneous=True is essential: cur0 contains y, so a sequential subs would
        # then rewrite those y's when substituting y->cur1 and corrupt the composition.
        n0 = sp.expand(f0.subs({x: cur0, y: cur1}, simultaneous=True))
        n1 = sp.expand(f1.subs({x: cur0, y: cur1}, simultaneous=True))
        cur0, cur1 = n0, n1
        used.append(kind)
    return (cur0, cur1), (x, y), used


def test_map(components, variables):
    """Return dict: is_keller, det, invertible (bool/None), inverse, verdict_key."""
    is_keller, det = keller.is_keller_map(components, variables)
    inverse = None
    invertible = None
    if is_keller:
        inverse = general.attempt_inverse(components, variables)
        invertible = inverse is not None
    if not is_keller:
        verdict = "not_keller"
    elif invertible:
        verdict = "keller_invertible"
    elif invertible is False:
        verdict = "keller_no_explicit_inverse"   # injective-unknown; not a counterexample
    else:
        verdict = "inconclusive"
    return {"is_keller": bool(is_keller), "det": det, "invertible": invertible,
            "inverse": inverse, "verdict_key": verdict}
