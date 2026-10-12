"""The known counterexample (Alpöge / Claude Fable 5, July 2026), C^3 -> C^3.

Two independent public sources (johndcook.com, Secret Blogging Seminar) agree on this
map; every number below is re-derived at runtime by the engine, never trusted as-is.
"""
import sympy as sp

# Coordinates
x, y, z = sp.symbols('x y z')
VARS = (x, y, z)

# The three component polynomials
A = (1 + x*y)**3 * z + y**2 * (1 + x*y) * (4 + 3*x*y)
B = y + 3*x*(1 + x*y)**2 * z + 3*x*y**2 * (4 + 3*x*y)
C = 2*x - 3*x**2*y - x**3*z
COMPONENTS = (A, B, C)

# Human-readable strings (for GUI display)
COMPONENT_STR = (
    "a = (1 + x·y)³·z + y²·(1 + x·y)·(4 + 3·x·y)",
    "b = y + 3·x·(1 + x·y)²·z + 3·x·y²·(4 + 3·x·y)",
    "c = 2·x − 3·x²·y − x³·z",
)

# The claim under audit
CLAIMED_JACOBIAN = sp.Integer(-2)

# The claimed colliding fiber (three distinct inputs -> one output)
CLAIMED_TARGET = (sp.Rational(-1, 4), sp.Integer(0), sp.Integer(0))
CLAIMED_PREIMAGES = (
    (sp.Integer(0),  sp.Integer(0),   sp.Rational(-1, 4)),
    (sp.Integer(1),  sp.Rational(-3, 2), sp.Rational(13, 2)),
    (sp.Integer(-1), sp.Rational(3, 2),  sp.Rational(13, 2)),
)

# Weighted grading under which the map is quasi-homogeneous / C*-equivariant.
#   (x,y,z) weights = (-1, +1, +2); (a,b,c) weights = (+2, +1, -1).
GRADING = {x: -1, y: 1, z: 2}
COMPONENT_WEIGHTS = (2, 1, -1)
