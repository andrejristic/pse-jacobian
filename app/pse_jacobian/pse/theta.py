"""ThetaMonitor — repurposed engagement/confidence signal for a non-human-facing unit.

Theta here measures how much of the unit's compute is directed at the *object under
investigation* (the claim/map) rather than at itself. A working unit oscillates in the
healthy band [25,35]; a unit that concludes without actually engaging goes flatline
(sigma < 0.01) and is flagged — the master file's schizoid "rubber-stamp" signature.
A unit that hits a genuine contradiction spikes above 35 (over-absorption of the
anomaly), which is our escalation trigger.
"""
import statistics

from ..constants import (THETA_OPTIMAL, THETA_MIN, THETA_MAX,
                         SCHIZOID_SIGMA_MAX)


class ThetaMonitor:
    def __init__(self, phase=0.0, amp=2.6):
        self.phase = phase       # per-unit phase so trajectories/posteriors differ
        self.amp = amp
        self.history = []
        self.update(THETA_OPTIMAL, source="init")

    def update(self, value, source="work"):
        value = max(0.0, min(100.0, float(value)))
        self.history.append({"value": value, "source": source})

    def engage(self, confirmed=True, source="verify"):
        """Append a healthy oscillating theta for one genuine unit of work.

        A smooth sinusoid around the optimal 30 keeps sigma in the healthy band and
        gives POSITIVE lag-1 autocorrelation (reads as 'Nash substrate / continuation'
        in the game-form posterior — i.e. healthy engagement). A refutation spikes theta
        (over-absorption of the anomaly = escalation signal); doing nothing => flatline.
        """
        import math
        i = len(self.history)
        if confirmed is False:
            self.update(37.5, source="contradiction")
        else:
            self.update(30.0 + self.amp * math.sin(0.8 * i + self.phase), source=source)

    @property
    def current(self):
        return self.history[-1]["value"]

    @property
    def mean(self):
        return statistics.fmean(v["value"] for v in self.history)

    @property
    def sigma(self):
        vals = [v["value"] for v in self.history]
        return statistics.pstdev(vals) if len(vals) > 1 else 0.0

    def health(self):
        """Return one of: healthy / withdrawn / enmeshed / flatline.

        Flatline (schizoid 'rubber-stamp') is only diagnosable over a SUSTAINED series —
        the master file requires an absence of growth over a long window, so a unit with
        only a handful of steps is never flagged schizoid on variance alone.
        """
        if self.mean > THETA_MAX:
            return "enmeshed"           # over-absorbed the anomaly (escalation)
        if self.mean < THETA_MIN:
            return "withdrawn"
        if len(self.history) >= 6 and self.sigma < SCHIZOID_SIGMA_MAX * 100:
            return "flatline"           # rubber-stamp / schizoid signature
        return "healthy"

    def trajectory(self):
        return [v["value"] for v in self.history]
