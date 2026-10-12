"""Domain-adapted game-form posterior (the Extended Seldon Engine for this app).

The master file's 11 clinical game forms are replaced by 10 forms that actually occur in
MATHEMATICAL ADVERSARIAL VERIFICATION (a verifier unit vs. the claim/proposal/source it
investigates). Attractors and the Bayesian machinery are unchanged; only the roster is
domain-tuned, exactly as the PSE master permits ("game-theory games may be adapted").

Kept from master (adapted): Nash Substrate, Signalling, War of Attrition, Global Games,
Evolutionary/ESS. Added (domain-specific): Prover–Verifier (interactive proof),
Bluff-Catching, Byzantine Consensus, Inspection Game, Screening/Lemons.

Each form has a continuous signature over theta statistics (sigma, rho, drift) plus a
discrete modifier over verification signals (escalation via fission, survival of the
claim, disagreement, theta spike, Keller-filter). The posterior is P ∝ exp(-D + mod),
normalized; confidence C = 1 - H(P)/log2(N) as in the master file.
"""
import math
import statistics


def _theta_stats(theta):
    if len(theta) < 2:
        return 0.0, 0.0, 0.0
    m = statistics.fmean(theta)
    sd = statistics.pstdev(theta)
    num = sum((theta[i] - m) * (theta[i + 1] - m) for i in range(len(theta) - 1))
    den = sum((v - m) ** 2 for v in theta) or 1e-9
    rho = num / den
    diffs = [theta[i + 1] - theta[i] for i in range(len(theta) - 1)]
    tv = sum(abs(d) for d in diffs) or 1e-9
    drift = abs(sum(diffs)) / tv          # 1 = monotone, 0 = oscillating
    return sd / 100.0, rho, drift


# key, display name, (sigma_c, rho_c, drift_c), modifier(features)->log-boost
GAMES = [
    ("nash", "Nash Substrate", (0.017, 0.70, 0.15),
     lambda f: 0.6 * f["surv"] - 0.5 * f["esc"]),
    ("prover_verifier", "Prover–Verifier (interactive proof)", (0.020, 0.55, 0.20),
     lambda f: 0.9 * f["esc"] + 0.5 * f["surv"]),
    ("byzantine", "Byzantine Consensus", (0.030, 0.10, 0.20),
     lambda f: 1.6 * f["disagree"] + 0.4 * f["esc"]),
    ("bluff", "Bluff-Catching", (0.045, -0.20, 0.25),
     lambda f: 1.4 * (1 - f["surv"]) + 0.9 * f["spike"]),
    ("inspection", "Inspection Game", (0.020, 0.40, 0.20),
     lambda f: 0.7 * min(f["n_ag"], 6) / 3.0),
    ("attrition", "War of Attrition", (0.009, 0.95, 0.90),
     lambda f: 1.3 * f["drift"]),
    ("signalling", "Signalling (cheap vs costly)", (0.045, 0.05, 0.20),
     lambda f: 0.4 + 0.5 * f["spike"]),
    ("global", "Global Games (info-sensitive)", (0.060, 0.10, 0.20),
     lambda f: 0.9 * f["spike"]),
    ("screening", "Screening / Lemons", (0.020, 0.50, 0.20),
     lambda f: 0.8 * f["keller"]),
    ("ess", "Evolutionary / ESS (swarm)", (0.020, 0.50, 0.30),
     lambda f: -0.3),
]
NAME = {k: n for k, n, _, _ in GAMES}


def _features(report):
    theta = report.theta_trajectory or []
    sig, rho, drift = _theta_stats(theta)
    spike = 1.0 if (theta and max(theta) > 35.5) else 0.0
    n_ag = report.findings.get("n_agents_spawned", 0) or 0
    surv = 1.0 if report.status == "CONFIRMED" else 0.0
    disagree = 1.0 if report.status == "DISAGREEMENT" else 0.0
    esc = min(1.0, max(0.0, (n_ag - 2) / 4.0)) + disagree
    keller = 1.0 if report.findings.get("is_keller") else 0.0
    return {"sig": sig, "rho": rho, "drift": drift, "spike": spike, "surv": surv,
            "disagree": disagree, "esc": esc, "n_ag": n_ag, "keller": keller}


def posterior(report):
    f = _features(report)
    scores = {}
    for key, _name, (sc, rc, dc), mod in GAMES:
        dcont = ((f["sig"] - sc) ** 2) / 0.0009 + ((f["rho"] - rc) ** 2) / 0.6 \
            + ((f["drift"] - dc) ** 2) / 0.35
        scores[key] = math.exp(-dcont + mod(f))
    tot = sum(scores.values()) or 1.0
    probs = {k: v / tot for k, v in scores.items()}
    H = -sum(p * math.log2(p) for p in probs.values() if p > 0)
    C = 1 - H / math.log2(len(GAMES))
    dom = max(probs, key=probs.get)
    return {"probs": probs, "dominant": dom, "dominant_name": NAME[dom],
            "confidence": C, "sigma": f["sig"], "rho": f["rho"], "drift": f["drift"]}
