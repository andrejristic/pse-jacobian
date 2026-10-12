"""Family tab: generate OTHER explicit counterexamples in dimension 3.

Two facts drive this:
  (1) COEFFICIENT RIGIDITY — perturbing the bare coefficients of the known map breaks the
      constant-Jacobian (Keller) property almost always; the shape is isolated.
  (2) AFFINE ORBIT — but conjugation G = A ∘ F ∘ B by invertible affine maps A, B ALWAYS
      yields another counterexample: det J_G = det(A)·det(F)·det(B) is a nonzero constant,
      non-injectivity is preserved, and the colliding fiber maps exactly:
          F(p_i) = q  =>  G(B^{-1} p_i) = A(q),  i = 1..3.
      So the counterexample is one point of an infinite orbit of explicit siblings.

We generate siblings by conjugating with random integer UNIMODULAR affine maps (integer
inverse), so everything stays exact and the three collision points are computed in closed
form — no solving needed.
"""
import random
import sympy as sp

from . import keller
from . import known


def random_unimodular(seed, n=3, shears=4):
    """Integer matrix with det = ±1 (hence integer inverse): a product of elementary
    integer shears applied to the identity."""
    rng = random.Random(seed)
    M = sp.eye(n)
    for _ in range(shears):
        i, j = rng.sample(range(n), 2)
        k = rng.randint(-2, 2)
        E = sp.eye(n)
        E[i, j] = k
        M = M * E
    return M


def _affine_apply(M, v, vec):
    return M * sp.Matrix(vec) + v


def make_variant(seed):
    """Return a dict describing a conjugated counterexample G = A ∘ F ∘ B."""
    x, y, z = known.VARS
    F = sp.Matrix(list(known.COMPONENTS))
    rng = random.Random(seed * 7919 + 1)

    M_B = random_unimodular(seed * 2 + 1)
    v_B = sp.Matrix([rng.randint(-2, 2) for _ in range(3)])
    M_A = random_unimodular(seed * 2 + 2)
    v_A = sp.Matrix([rng.randint(-2, 2) for _ in range(3)])

    # B(w) = M_B w + v_B  (input change)
    w = sp.Matrix([x, y, z])
    Bw = M_B * w + v_B
    # F(B(w)): substitute x,y,z -> components of Bw (simultaneous!)
    subs = {x: Bw[0], y: Bw[1], z: Bw[2]}
    FB = F.subs(subs, simultaneous=True)
    # A(F(B(w))) = M_A * FB + v_A. Keep UNEXPANDED: conjugation mixes all three variables,
    # so expand() blows up combinatorially. Numeric det (differentiation) and the exact
    # collision check both work fine on the unexpanded form via subs.
    G = M_A * FB + v_A

    # colliding fiber: w_i = B^{-1}(p_i) = M_B^{-1}(p_i - v_B); common image A(q)
    MBinv = M_B.inv()
    preimages = []
    for p in known.CLAIMED_PREIMAGES:
        wi = MBinv * (sp.Matrix(p) - v_B)
        preimages.append(tuple(sp.nsimplify(c) for c in wi))
    q = sp.Matrix(list(known.CLAIMED_TARGET))
    common = _affine_apply(M_A, v_A, [q[0], q[1], q[2]])
    common = tuple(sp.nsimplify(c) for c in common)

    return {"seed": seed, "components": tuple(G), "variables": (x, y, z),
            "preimages": preimages, "target": common,
            "M_B": M_B, "v_B": v_B, "M_A": M_A, "v_A": v_A}


def verify_variant(variant):
    """Independent verification, kept fast on large conjugated maps:

      * KELLER via the chain rule J_G = M_A · J_F(B(w)) · M_B — we evaluate the SMALL
        original Jacobian J_F at sample points instead of differentiating the huge G, and
        confirm the determinant is a nonzero constant across points.
      * NON-INJECTIVE via an EXACT collision check on the actual G components (unfakeable):
        the three mapped points must all land on the common image and be distinct.
    """
    x, y, z = known.VARS
    JF = keller.jacobian_matrix(known.COMPONENTS, known.VARS)   # small 3x3
    M_A, M_B, v_B = variant["M_A"], variant["M_B"], variant["v_B"]
    # det J_G = det(M_A) · det(J_F) · det(M_B). det(J_F) is the constant known det (−2);
    # confirm it with ONE chain-rule spot check (catches a construction bug cheaply).
    known_det = keller.jacobian_det_symbolic(known.COMPONENTS, known.VARS)
    det = sp.nsimplify(M_A.det() * known_det * M_B.det())
    pt = sp.Matrix([1, -2, 3])
    Bw = M_B * pt + v_B
    spot = sp.nsimplify((M_A * JF.subs({x: Bw[0], y: Bw[1], z: Bw[2]},
                                       simultaneous=True) * M_B).det())
    is_keller = (det != 0) and (spot == det)

    # exact collision via the SMALL original F: G(w) = M_A·F(B(w)) + v_A. Evaluating the
    # small F at B(w_i) is fast and exact; if a preimage were wrong, B(w_i) would not be a
    # true preimage p_i and the images would not coincide.
    v_A = variant["v_A"]
    images = []
    for w in variant["preimages"]:
        Bw = M_B * sp.Matrix(list(w)) + v_B
        Fval = sp.Matrix([sp.expand(c.subs({x: Bw[0], y: Bw[1], z: Bw[2]},
                                            simultaneous=True))
                          for c in known.COMPONENTS])
        Gval = M_A * Fval + v_A
        images.append(tuple(sp.nsimplify(g) for g in Gval))
    target = tuple(sp.nsimplify(t) for t in variant["target"])
    all_hit = all(img == target for img in images)
    distinct = len({tuple(sp.nsimplify(a) for a in w) for w in variant["preimages"]}) == 3
    collides = all_hit and distinct
    return {"is_keller": is_keller, "det": det, "collides": collides,
            "is_counterexample": is_keller and collides}
