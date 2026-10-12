"""The four pathological attractors (Section 7 of the PSE master), unchanged in spirit.

Our theta is the OTHER-directed compute % (~30 healthy). The master's pathology detection
is written on the SELF-weight scale (~0.70 healthy), so we convert self = 1 - theta/100
and apply the master thresholds. Healthy units => 'none'.

  NARCISSISTIC  self > 0.73, low variance      (withdrawn into self / mirror)
  BORDERLINE    high variance, low autocorr     (oscillating threat/savior)
  CODEPENDENT   self < 0.67, low variance       (dissolved into the other)
  SCHIZOID      flatline variance, empty registry (rubber-stamp / absent engagement)
"""
import statistics


def _acf1(series, mean):
    num = sum((series[i] - mean) * (series[i + 1] - mean) for i in range(len(series) - 1))
    den = sum((v - mean) ** 2 for v in series) or 1e-9
    return num / den


def classify(theta_series, registry_size=1):
    """Return one of narcissistic / borderline / codependent / schizoid / none."""
    if len(theta_series) < 2:
        return "none"
    mean = statistics.fmean(theta_series)
    self_w = 1.0 - mean / 100.0                 # convert other% -> self weight
    sd = statistics.pstdev(theta_series) / 100.0
    acf = _acf1(theta_series, mean)

    if sd < 0.01 and registry_size <= 0:
        return "schizoid"                        # flatline + empty registry
    if self_w > 0.73 and sd < 0.02:
        return "narcissistic"
    if sd > 0.05 and acf < 0.5:
        return "borderline"
    if self_w < 0.67 and sd < 0.02:
        return "codependent"
    return "none"


# swarm-level attractor geometry (Base Seldon Engine), isomorphic to the unit pathologies
GEOMETRY = {
    "narcissistic": "CIRCLE (cikliranje bez napretka)",
    "borderline": "HELIX (oscilujuća amplituda)",
    "codependent": "CLOSING SPIRAL (kolaps ka fiksnoj tački)",
    "schizoid": "OPENING SPIRAL (rast ka kolapsu — najopasnije)",
    "none": "STABILNO (nema patološkog atraktora)",
}
