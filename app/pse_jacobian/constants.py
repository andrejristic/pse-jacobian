"""PSE core constants (single source of truth), taken from the PSE Master Architecture.

Per the master file, the 70/30 split is only binding in HUMAN-FACING situations; in a
non-human-facing task (like this one) theta is repurposed as an internal
engagement/confidence signal and the other constructs (game forms, fission triggers)
are adapted freely. We keep the healthy-band numbers because they still give us a
principled "is this unit actually working or just rubber-stamping" test.
"""

SELF_WEIGHT = 0.70
OTHER_WEIGHT_MAX = 0.30

THETA_OPTIMAL = 30.00
THETA_MIN = 25.00
THETA_MAX = 35.00
THETA_HEALTHY_SIGMA = (0.015, 0.03)   # healthy variance band (as fraction)
SCHIZOID_SIGMA_MAX = 0.01             # flatline below this = "rubber-stamp" unit

# Adaptive-fission policy (Unit 1). Repurposed from SHARED_LIB fission rules:
#   "progress confirmation -> contracts; contradiction -> extends + spawns units".
MIN_INDEPENDENT_CONFIRMATIONS = 2     # per sub-claim, before a unit may conclude
FISSION_HARD_CAP = 8                  # never spawn more than this many verifier agents

# Method authority weights (how much one agent's confirmation counts toward a claim).
#   symbolic/exact = definitive; numeric = corroborating.
METHOD_WEIGHT = {
    "symbolic": 2,
    "exact": 2,
    "groebner": 2,
    "numeric": 1,
    "finite_field": 1,
}
