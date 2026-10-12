# PSE-Jacobian — Guide (Step 1: foundation + the "Case" tab)

## What this is
An application that uses **your PSE agents to independently reproduce and audit** the
counterexample to the Jacobian Conjecture (Alpöge / Claude Fable 5, July 2026): a
map C³ → C³ with constant Jacobian determinant −2 that is **not injective** (3-to-1).

The point is not to "trust the news" but to **check the object itself** — three times,
along different routes, then compare the results (master file ethos: *refute-by-default*).

## How to run
```
cd "~/Desktop/PSE Jacobian/app"
./run.sh
```
or `python3 run.py`. Requires `python3, PySide6, sympy, numpy, matplotlib`
(see `requirements.txt`; already installed on your machine).

## What you see in the "Case" tab
1. **Map under investigation** — the three components + the claimed collision (→ (−1/4,0,0)).
2. **"Run investigation" button** — starts **three units, each in its own thread**.
3. **Three panels** (running in parallel, separately):
   - **Unit 1 · Algebra (adaptive fission):** starts with 1 agent and **spawns as many as
     needed**. Symbolic determinant, numeric determinant (25 random points), exact
     substitution of the points, numeric collision check. If agents agree → it stops; if
     one **disagrees → it escalates** (spawns all + raises a flag). On the clean
     counterexample it spawns 4 agents.
   - **Unit 2 · Fiber:** **solves** F(x,y,z)=(−1/4,0,0) itself and **discovers** the
     preimages (they are not handed to it). Computes the geometric degree (=3) and the
     local Jacobian at each sheet (=−2).
   - **Unit 3 · Edge:** checks quasi-homogeneity (C\*-equivariance, weights (2,1,−1)) and
     lifts the map to n=4, n=5 (determinant stays −2 → holds for every n≥3).
4. **θ (theta)** under each panel: measures genuine engagement. Healthy = oscillation in
   [25,35], σ≈1.5–3. If a unit "rubber-stamps without working" → flatline → red flag.
5. **Comparator (Seldon/Physician)** at the bottom: cross-checks
   - the fiber Unit 2 **discovered** == the points Unit 1 **verified**;
   - det J agrees across all three units;
   - fiber cardinality == geometric degree == number of points;
   - all three ruled CONFIRMED.
   Consensus is declared **only if every check passes and there is no disagreement**.
6. **Graphics (right):** 3D real view (the three preimages + the hidden C\*-orbit that
   connects two of them), 2D projections, and an exact table.

## What you should get
- Unit 1: CONFIRMED, 4 agents. Unit 2: CONFIRMED, 3 preimages, degree 3. Unit 3: CONFIRMED.
- Comparator: **"CONSENSUS … Jacobian Conjecture DISPROVED for n≥3", confidence 100%.**

## Code layout
```
app/
  run.py, run.sh, requirements.txt
  pse_jacobian/
    constants.py            # PSE constants (70/30 relaxed — this is non-human-facing)
    mathengine/             # pure mathematics (sympy/numpy)
      known.py              # the map + claimed points (everything is recomputed, nothing trusted)
      keller.py             # Jacobian (symbolic+numeric), Keller test, collisions
      fiber.py              # fiber solving, geometric degree, local determinant
      structure.py          # quasi-homogeneity, dimension lift
    pse/
      theta.py              # ThetaMonitor (engagement / rubber-stamp detection)
      unit.py, units.py     # the three units + adaptive fission
      comparator.py         # Seldon/Physician cross-checks
    gui/                    # PySide6: window, "Case" tab, threads, matplotlib graphics
    llm/                    # provider abstraction (stub; wired in a later step)
```
The PSE master architecture file is **left untouched**.

## Update (fixes after the first launch)
- **The window now fits the screen**: never larger than the available area (95%×92%),
  centered; the whole content sits inside a *scroll* area so on a small screen it scrolls
  instead of spilling off-screen. Minimum size 700×480.
- **SR/EN language switch** at the top left (a "Jezik / Language" dropdown). It translates
  **everything** — not just the GUI, but unit verdicts, fission messages and the
  comparator. Switching language rebuilds the tabs (current results are cleared; just run
  the investigation again).

## Tab 2 — Workbench
Enter **any** polynomial map C^n → C^n and the swarm classifies it. Three units in
separate threads:
- **Keller check (fission):** symbolic + numeric Jacobian → is det J a nonzero constant
  (the conjecture's premise)? If symbolic and numeric disagree → escalation.
- **Injectivity / fiber:** geometric degree over image-sampled targets; if the degree
  is > 1 it produces an explicit example collision.
- **Inverse:** if injective (degree 1) it attempts to **construct an explicit polynomial
  inverse** and displays it; if not injective there is no inverse.

The **verdict** (classification) is one of:
- **COUNTEREXAMPLE** — a Keller map that is NOT injective (disproves the conjecture);
- **invertible** — Keller and injective (consistent with the conjecture);
- **not a Keller map** — the premise fails, the conjecture does not apply;
- **inconclusive**.

The **Preset** dropdown has ready cases for each type: *Counterexample (Alpöge/Fable)*,
*Automorphism (x+y², y)* → inverse (y0−y1², y1), *Identity*, *Not Keller (x², y)*. Or
enter your own: variables in the first field ("x, y, z"), components one per line.

This is the tool for checking **future third-party "counterexamples"** too — just paste
the polynomials.

## Tab 3 — Discovery
Reproducing the **method itself** (Alpöge + Fable): the LLM **proposes** a candidate
map, and the swarm **verifies it exactly**. The Guardian is *refute-by-default* — most
proposals FAIL, and that filter is the point.

- **Provider** (dropdown):
  - *Local simulation (test, no network)* — returns the known counterexample; to try the flow without a key.
  - *Local GGUF / LM Studio* — run a model in LM Studio (server at `http://localhost:1234/v1`).
  - *Claude / Mistral / Groq* — enter an API key in the field, or leave it empty to read
    from the environment: `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`.
- **Task** — the message to the model (default: "propose an explicit counterexample…"). Edit freely.
- **Propose (LLM)** → the model returns a `VARS:/MAP:` response; the app extracts the map,
  fills the editable fields, and **auto-runs verification** (the same three units as the Workbench).
- **Verdict** as in the Workbench: COUNTEREXAMPLE / invertible / not-Keller / inconclusive.

The model need not be right — if the proposal is bad, the swarm **catches and rejects**
it. If the format isn't `VARS:/MAP:`, edit the fields manually then "Verify proposal".

## Tab 4 — n=2 Frontier
Since the **plane conjecture (n=2) is open**, this tab is an experimental platform. It
generates genuine **Keller maps in two variables** (by composing elementary automorphisms
— shears + triangular affine) and the swarm tests each independently, **accumulating
evidence**.

- Controls: **k** (number of factors = complexity), **number of maps**, **seed** (reproducibility).
- For each map the table shows: seed, factors, det J, whether it is Keller, whether it is
  invertible (an actual polynomial inverse was constructed), and the verdict.
- Summary (green): e.g. "20 maps: Keller 20/20, invertible 20/20, COUNTEREXAMPLES: 0 —
  consistent with the open conjecture". If a row ever shows Keller=✓ / invertible=✗ with a
  proof of non-injectivity — a red warning (that would be news).

**Honestly:** this does NOT settle n=2. This family (tame automorphisms) is always
invertible by construction; the purpose is to show the pattern and provide a testbed, not
a proof. (A bug caught along the way: sympy `subs` is sequential and corrupted the
composition — fixed with `simultaneous=True`; every inverse is now verified as inv∘F = id.)

## Tab 5 — Family
Searches for **other explicit counterexamples** in dimension 3. Two findings:
- **Coefficient rigidity:** perturbing the bare coefficients of the original map breaks the
  Keller property almost always — in the tested grid the only Keller map is the original.
  The shape is isolated.
- **Affine orbit (infinite):** but conjugation **G = A∘F∘B** (A, B invertible affine)
  ALWAYS yields a new counterexample: det stays ±2, non-injectivity is preserved, and the
  three colliding points map exactly (w_i = B⁻¹(p_i), common image A(q)). The
  counterexample is one point of an infinite orbit.

Controls: number of variants + seed → **Generate family**. Table: variant, det J, Keller,
3-to-1, map preview. Click a row → **detail** (the full map in `VARS:/MAP:` format + the
collision points) which you can copy into the **Workbench** or **Discovery** tab.

Verification is fast and exact: det via the chain rule (det G = det(A)·(−2)·det(B)) with a
spot check, and the collision exactly through the small original F.

## Tab 6 — Diagnostics (full PSE machinery)
Run diagnostics (the same three Case units) and see the **entire PSE interior**:
- **theta trajectories** for all three units on one plot, with the healthy band [25,35];
- **per-unit table:** μ(θ), σ(θ), ρ (autocorrelation), health
  (healthy/enmeshed/withdrawn/flatline), **attractor** (Narcissistic/Borderline/
  Codependent/Schizoid/none) and **dominant game** + confidence C;
- **posterior over the 10 games** (click a unit) with bars;
- **fission log** (Unit 1's agents);
- **Seldon/Physician:** swarm geometry + consensus + finding ("swarm healthy" or red).

**The game forms are domain-adapted** (adversarial mathematical verification), as the PSE
master permits. Attractors and the Bayesian machinery are unchanged; only the roster:
- kept from the master: **Nash Substrate, Signalling, War of Attrition, Global Games, ESS**;
- dropped: Iterated PD, Chicken, Stag Hunt, Bargaining, All-Pay, Correlated Equilibrium;
- **added (new):** **Prover–Verifier** (interactive proof), **Bluff-Catching**,
  **Byzantine Consensus**, **Inspection Game**, **Screening/Lemons**.

Typical healthy outcome: Algebra → *Inspection Game* (how many agents to spend via
fission), Fiber → *Prover–Verifier*, Edge → *War of Attrition*; all "healthy", attractor
"none", Physician: swarm healthy. Each unit has its own theta phase so the curves separate.

## Tab 7 — Chat
A multi-turn conversation with an LLM about the counterexample and the app. Same providers
as Discovery:
- *Local simulation* (offline, no key) — replies instantly for testing;
- *LM Studio* (`http://localhost:1234/v1`), *Claude*, *Mistral*, *Groq* (key in the field or env).

The model is grounded by a system prompt containing the verified facts (map C³→C³, det −2,
three points → (−1/4,0,0), n=2 open), so the conversation stays accurate. It answers in the
language you write in. "Clear" resets the history.

## Tab 8 — Report
**Generate report** → the swarm runs the case and composes a document: time, environment
(Python/sympy versions), the map, the exactly-verified facts (det −2, three points →
target), all three unit verdicts, the comparator cross-checks + consensus, structure,
conclusion. **Export** to `.txt`, `.html` or `.pdf`. Every generation and export is written
to an **append-only audit ledger** (`~/.pse_jacobian/audit.log`) — timestamped proof that
YOU reproduced the experiment.

## Installation (.deb)
Package: `pse-jacobian_0.1.0_all.deb` (in `app/`).

**Install:**
```
cd ~/"Desktop/PSE Jacobian/app"
sudo dpkg -i pse-jacobian_0.1.0_all.deb
```
The only dependency is `python3`, so it installs cleanly. Launch from the menu
(**PSE-Jacobian**, Education/Science) or the terminal: `pse-jacobian`.

**Layout:** app in `/opt/pse-jacobian`, launcher `/usr/bin/pse-jacobian`, `.desktop` +
icon, guides in `/usr/share/doc/pse-jacobian`.

**Python packages:** the launcher uses `~/pse-venv` if present (your case — PySide6/
sympy/numpy/matplotlib live there). Otherwise install the recommended ones:
`sudo apt install python3-pyside6 python3-sympy python3-numpy python3-matplotlib`, or make
a venv: `python3 -m venv ~/pse-venv && ~/pse-venv/bin/pip install PySide6 sympy numpy matplotlib`.

**Uninstall:** `sudo dpkg -r pse-jacobian`.
**Rebuild the package:** `sh packaging/build_deb.sh`.

---
**Done — all 8 tabs + the .deb.** The app reproduces and audits the counterexample,
measures the space of the conjecture, all on the PSE architecture (theta, attractors,
domain-adapted game forms, Seldon/Physician, adaptive fission), with a report and an
audit ledger as proof that YOU reproduced the experiment.
