"""Base structures for PSE investigation units."""
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .theta import ThetaMonitor


@dataclass
class AgentResult:
    """One verifier sub-agent's finding (produced by fission inside a unit)."""
    agent_id: str
    method: str                 # symbolic / numeric / exact / groebner / finite_field
    claim: str                  # which sub-claim this agent addressed
    confirmed: Optional[bool]   # True=confirms, False=refutes, None=inconclusive
    value: Any = None
    detail: str = ""


@dataclass
class UnitReport:
    unit_name: str
    mission: str
    agents: list = field(default_factory=list)          # list[AgentResult]
    findings: dict = field(default_factory=dict)         # structured results
    verdict: str = "PENDING"                             # human-readable conclusion
    status: str = "PENDING"        # CONFIRMED / DISAGREEMENT / INCONCLUSIVE
    theta_trajectory: list = field(default_factory=list)
    theta_health: str = "healthy"
    extras: dict = field(default_factory=dict)           # cross-check payloads


class InvestigationUnit:
    """A PSE unit with a bounded mission. Runs synchronously; a GUI thread wraps it.

    Subclasses implement `investigate(progress)` and return a UnitReport.
    """
    name = "unit"
    mission = "{state, action, outcome}"
    theta_phase = 0.0
    theta_amp = 2.6

    def __init__(self):
        self.theta = ThetaMonitor(phase=self.theta_phase, amp=self.theta_amp)

    def investigate(self, progress: Callable[[str], None]) -> UnitReport:
        raise NotImplementedError

    def run(self, progress: Optional[Callable[[str], None]] = None) -> UnitReport:
        progress = progress or (lambda _msg: None)
        report = self.investigate(progress)
        report.theta_trajectory = self.theta.trajectory()
        report.theta_health = self.theta.health()
        return report
