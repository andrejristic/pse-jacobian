"""Tiny i18n layer. One dict per language, `t(key, **fmt)` looks up the current
language and formats. Missing key -> returns the key (never crashes). Language is a
process-global; the GUI rebuilds its tabs on toggle so every string is re-resolved.
"""

_LANG = "sr"


def set_lang(lang):
    global _LANG
    if lang in STRINGS:
        _LANG = lang


def get_lang():
    return _LANG


def t(key, **fmt):
    s = STRINGS.get(_LANG, {}).get(key)
    if s is None:
        s = STRINGS["sr"].get(key, key)
    return s.format(**fmt) if fmt else s


STRINGS = {
    "sr": {
        # --- main window ---
        "win_title": "PSE-Jacobian  v{v}  —  reprodukcija kontraprimjera",
        "tab_case": "Slučaj",
        "lang_label": "Jezik:",
        # --- case tab ---
        "case_title": "Slučaj: kontraprimjer Jacobianove konjekture (C³ → C³)",
        "mapbox_title": "Mapa pod istragom (tvrdi se: det J = −2, ne-injektivna)",
        "claimed_collision": "tvrđena kolizija: 3 različite tačke → (−1/4, 0, 0)",
        "run_btn": "▶  Pokreni istragu (3 jedinice, zasebne niti)",
        "panel_alg": "Jedinica 1 · Algebra (adaptivna fisija)",
        "panel_fib": "Jedinica 2 · Vlakno (otkriva nezavisno)",
        "panel_edge": "Jedinica 3 · Rub (struktura)",
        "comp_title": "Komparator (Seldon / Physician) — refute-by-default",
        "waiting": "Čeka pokretanje…",
        "xh_check": "unakrsna provjera",
        "xh_result": "rezultat",
        "xh_detail": "detalj",
        "investigating": "Istraga u toku…",
        "st_running": "RADI…",
        "st_error": "GREŠKA",
        "theta_line": "θ̄={mean:.1f}  σ={sig:.2f}  [{health}]  ({n} koraka)",
        "verdict_prefix": "→ ",
        "disagreements": "Neslaganja: ",
        "confidence": "(pouzdanost {c:.0%})",
        "mark_ok": "✓ OK",
        "mark_no": "✗ NE",
        # --- missions / names ---
        "mission_alg": "{nepotvrđena tvrdnja → prekontroliši simbolički i numerički → presuda}",
        "mission_fib": "{izmjeri vlakno → riješi F(x)=cilj od nule → geometrijski stepen}",
        "mission_edge": "{zašto pada n≥3 a n=2 ostaje → kvazi-homogenost + dizanje dimenzije}",
        "name_alg": "Jedinica 1 · Algebra",
        "name_fib": "Jedinica 2 · Vlakno",
        "name_edge": "Jedinica 3 · Rub",
        # --- unit 1 progress + verdicts ---
        "alg_spawn": "⑂ fisija: spawnujem agenta {id} [{method}] za '{claim}'",
        "alg_refute": "⚠ agent {id} OPOVRGAVA '{claim}' → eskalacija (spawn svih)",
        "alg_v_conf": ("det J = {det} (konstanta ≠ 0) i 3 različite tačke → ista slika "
                       "⇒ NEinjektivno. Potvrđeno kroz {n} nezavisnih agenata (fisija)."),
        "alg_v_dis": "NESLAGANJE među agentima — tvrdnja nije potvrđena.",
        "alg_v_inc": "Nedovoljno nezavisnih potvrda.",
        "det_agent_sym": "simbolički det J = {det}",
        "det_agent_num": "det J jednak u svih 25 slučajnih tačaka = {val}",
        "det_agent_ff": "det J konstantan i mod {p}",
        "col_agent_exact": "egzaktno: sve 3 tačke → {tgt}",
        "col_agent_num": "numerička (float) provjera kolizije",
        # --- unit 2 ---
        "fib_solve": "rješavam sistem F(x,y,z) = cilj (Gröbner/solve_poly_system)…",
        "fib_found": "otkriveno {n} praslika (bez pomoći)",
        "fib_degree": "geometrijski stepen ≈ {deg} (broj praslika po cilju: {counts})",
        "fib_v_conf": ("Vlakno ima {n} praslike (stepen ≈ {deg}); lokalni Jakobijan = "
                       "{det} u SVAKOJ (nema lokalnog preklapanja) ⇒ globalno {n}-na-1."),
        "fib_v_inc": "Vlakno nije jednoznačno ne-injektivno.",
        # --- unit 3 ---
        "edge_struct": "provjeravam C*-ekvivarijantnost (kvazi-homogenost)…",
        "edge_lift": "dižem na n=4 i n=5 preko F×id…",
        "edge_v_conf": ("Mapa je kvazi-homogena (težine {w}); treća varijabla z (težina 2) "
                        "je nužna. F×id čuva det = {det} u n=4 i n=5 ⇒ kontraprimjer se diže "
                        "na svako n≥3. (n=2 nema ovu strukturu → ostaje otvoreno.)"),
        "edge_v_inc": "Struktura nije potvrđena.",
        # --- comparator ---
        "cc1": "Vlakno (J2 otkrio) == tačke (J1 potvrdio)",
        "cc1_d": "J1 potvrdio {a}, J2 nezavisno otkrio {b}; skupovi {eq}",
        "eq_same": "identični", "eq_diff": "RAZLIČITI",
        "cc2": "det J jednak u J1 (algebra), J2 (lokalno), J3 (n=4,5)",
        "cc2_d": "vrijednosti: {{{vals}}}",
        "cc3": "kardinalnost vlakna == geom. stepen == broj tačaka",
        "cc3_d": "praslika={n}, stepen={deg}, tačaka={t}",
        "cc4": "sve tri jedinice presudile CONFIRMED (nezavisno)",
        "dis_fiber": "Otkriveno vlakno se ne poklapa s potvrđenim tačkama.",
        "dis_det": "Jakobijan se razlikuje među jedinicama.",
        "dis_card": "Broj praslika / stepen / tačaka se ne slažu.",
        "dis_status": "Bar jedna jedinica nije potvrdila.",
        "dis_flat": "{tag}: theta flatline — moguć 'pečat bez rada'.",
        "head_conf": ("KONSENZUS: tri nezavisna puta se slažu — konstantan Jakobijan ≠ 0 "
                      "a mapa je ne-injektivna. Jacobian Conjecture OBORENA za n≥3."),
        "head_dis": "RAZILAŽENJE — tvrdnja NIJE jednoglasno potvrđena. Vidi log neslaganja.",
        "head_inc": "Neodlučno — nedovoljno slaganja.",
        # --- plot ---
        "pv_3d": "3D (realno)", "pv_2d": "2D presjeci", "pv_tab": "Tabela (egzaktno)",
        "pv_ph": "Pokreni istragu →",
        "pv_h_pre": "praslika (x, y, z)", "pv_h_img": "F(praslika)",
        "pv_h_det": "lokalni det J", "pv_h_note": "napomena",
        "pv_3d_title": "Vlakno: tri praslike → ista slika (3-na-1)",
        "pv_orbit": "C*-orbita (skrivena simetrija)",
        "pv_2d_title": "2D projekcije praslika + C*-orbita",
        "pv_note_orbit": "na C*-orbiti (λ=−1)", "pv_note_fixed": "fiksna tačka orbite",
        # --- workbench ---
        "tab_workbench": "Radionica",
        "wb_title": "Radionica: klasifikuj bilo koju polinomsku mapu Cⁿ→Cⁿ",
        "wb_vars_label": "Varijable (npr. x, y, z):",
        "wb_comps_label": "Komponente (jedna po liniji):",
        "wb_preset_label": "Primjer:",
        "wb_analyze": "▶  Analiziraj mapu",
        "wb_panel_keller": "Keller-provjera (fisija)",
        "wb_panel_inj": "Injektivnost / vlakno",
        "wb_panel_inv": "Inverz",
        "wb_verdict_title": "Presuda (klasifikacija mape)",
        "wb_parse_error": "Greška u unosu: {e}",
        "wb_name_keller": "Keller-provjera",
        "wb_mission_keller": "{je li det J konstanta ≠ 0?}",
        "wb_name_inj": "Injektivnost",
        "wb_mission_inj": "{geometrijski stepen preko uzoraka iz slike}",
        "wb_name_inv": "Inverz",
        "wb_mission_inv": "{ako je injektivna → pokušaj eksplicitan inverz}",
        "wb_v_keller_yes": "Jeste Keller-mapa: det J = {det} (konstanta ≠ 0).",
        "wb_v_keller_no": "NIJE Keller-mapa: det J = {det} nije konstanta ≠ 0.",
        "wb_keller_anomaly": "Nesklad simboličkog i numeričkog Jakobijana — eskalacija.",
        "wb_v_inj_yes": "Injektivna (stepen 1): svako vlakno = 1 tačka.",
        "wb_v_inj_no": "{deg}-na-1 (NIJE injektivna). Primjer kolizije: {pts} → {tgt}.",
        "wb_v_inj_fail": "Stepen nije utvrđen ({e}).",
        "wb_inv_check": "brza provjera injektivnosti…",
        "wb_inv_try": "pokušavam eksplicitan inverz…",
        "wb_v_inv_yes": "Inverz postoji (polinomijalan): {inv}",
        "wb_v_inv_no": "Nema inverza (mapa nije injektivna).",
        "wb_v_inv_maybe": "Injektivna, ali eksplicitan inverz nije konstruisan automatski.",
        "wb_cc_consistency": "inverz ⇔ stepen 1",
        "wb_cc_consistency_d": "inverz={inv}, stepen={deg}",
        "wb_yes": "da", "wb_no": "ne",
        "wb_head_counter": "KONTRAPRIMJER: Keller-mapa koja NIJE injektivna ⇒ obara Jacobian Conjecture.",
        "wb_head_invertible": "Keller-mapa i injektivna ⇒ invertibilna (u skladu s konjekturom).",
        "wb_head_notkeller": "Nije Keller-mapa (det J nije konstanta ≠ 0) — konjektura se ne primjenjuje.",
        "wb_head_inconclusive": "Neodlučno — stepen/status nije utvrđen.",
        "preset_counterexample": "Kontraprimjer (Alpöge/Fable)",
        "preset_automorphism": "Automorfizam (x+y², y)",
        "preset_identity": "Identitet",
        "preset_not_keller": "Nije Keller (x², y)",
        "preset_custom": "— vlastita —",
        # --- discovery ---
        "tab_discovery": "Otkriće",
        "disc_title": "Otkriće: LLM predlaže, roj egzaktno provjerava",
        "disc_sub": ("Reprodukcija same metode (Alpöge + Fable): kreativni model smišlja "
                     "kandidat-mapu, a deterministički roj je provjerava. Guardian je "
                     "refute-by-default — većina predloga PADNE, i to je poenta."),
        "disc_provider": "LLM provajder",
        "disc_provider_label": "Provajder:",
        "disc_key_ph": "prazno = uzmi iz okruženja (env)",
        "disc_task_label": "Zadatak (poruka modelu):",
        "disc_task_default": ("Predloži EKSPLICITAN kontraprimjer Jacobianovoj konjekturi: "
                              "polinomsku mapu C^3→C^3 sa konstantnim ne-nula Jakobijanom "
                              "koja NIJE injektivna. Vrati SAMO u formatu VARS:/MAP:."),
        "disc_propose": "▶  Predloži (LLM)",
        "disc_verify": "Provjeri predlog (roj)",
        "disc_raw_label": "Sirov odgovor LLM-a:",
        "disc_calling": "zovem LLM…",
        "disc_llm_error": "LLM greška: {e}",
        "disc_no_map": ("Nisam uspio izvući mapu iz odgovora — provjeri format (VARS:/MAP:) "
                        "ili je uredi ručno pa „Provjeri predlog\"."),
        "disc_system": ("You are a mathematics proposal engine. Propose ONE explicit "
                        "polynomial map C^n -> C^n as a CANDIDATE for verification. "
                        "Output ONLY in this exact format, nothing else:\n"
                        "VARS: <comma-separated variables>\nMAP:\n"
                        "<one polynomial per line, Python/sympy syntax, ** for powers>\n"
                        "Use exact integer/rational coefficients. Do not explain."),
        # --- n=2 frontier ---
        "tab_frontier": "n=2 Granica",
        "fr_title": "n=2 Granica: eksperimentalna platforma za otvorenu ravan-konjekturu",
        "fr_sub": ("Ravan-konjektura (n=2) je OTVORENA. Generišemo prave Keller-mape u 2 "
                   "varijable (kompozicijom elementarnih automorfizama) i roj svaku "
                   "nezavisno testira. Gomilamo dokaze — ali ovo NE može riješiti "
                   "konjekturu: ova familija (pitomi automorfizmi) ne može sadržati "
                   "hipotetsku „divlju\" Keller-mapu ako postoji."),
        "fr_k": "Složenost (broj faktora k):",
        "fr_n": "Broj mapa:",
        "fr_seed": "Sjeme:",
        "fr_run": "▶  Generiši i testiraj",
        "fr_running": "generišem i testiram…  ({i}/{n})",
        "fr_summary": "{n} mapa testirano: Keller {kel}/{n}, invertibilnih {inv}/{n}, KONTRAPRIMJERA: {ctr}",
        "fr_summary_consistent": "Sve invertibilne — u skladu s otvorenom ravan-konjekturom (nije dokaz).",
        "fr_summary_counter": "PAŽNJA: nađen kandidat-kontraprimjer! Provjeri ga u Radionici.",
        "fr_h_seed": "sjeme", "fr_h_factors": "faktori", "fr_h_det": "det J",
        "fr_h_keller": "Keller", "fr_h_inv": "invertibilno", "fr_h_verdict": "presuda",
        "fr_v_invertible": "invertibilna", "fr_v_notkeller": "nije Keller",
        "fr_v_noinv": "Keller, inverz nekonstruisan", "fr_v_inc": "neodlučno",
        "fr_disclaimer": ("Napomena: ovaj generator pravi pitome automorfizme (uvijek "
                          "invertibilne). Svrha je pokazati obrazac i dati teren, ne "
                          "dokazati n=2. Ako se ikad pojavi red gdje je Keller=✓ a "
                          "invertibilno=✗ uz dokaz ne-injektivnosti — to je vijest."),
        # --- family ---
        "tab_family": "Porodica",
        "fam_title": "Porodica: druge eksplicitne kontraprimjere u dimenziji 3 (afina orbita)",
        "fam_sub": ("Afina konjugacija G = A∘F∘B (A,B invertibilne afine) uvijek daje NOVI "
                    "kontraprimjer: det ostaje ±2, ne-injektivnost se čuva, a kolizione "
                    "tačke se preslikaju egzaktno. Kontraprimjer je jedna tačka beskonačne "
                    "orbite eksplicitnih „braće\"."),
        "fam_rigid": ("Krutost koeficijenata: u mreži deformacija golih koeficijenata oko "
                      "originala, jedini Keller je original — oblik je izolovan. Sloboda je "
                      "u afinoj grupi, ne u koeficijentima."),
        "fam_n": "Broj varijanti:",
        "fam_seed": "Sjeme:",
        "fam_run": "▶  Generiši porodicu",
        "fam_running": "generišem varijante…  ({i}/{n})",
        "fam_summary": ("{n} različitih eksplicitnih kontraprimjera: svi Keller (det=±2≠0), "
                        "svi 3-na-1. Orbita je beskonačna."),
        "fam_h_seed": "varijanta", "fam_h_det": "det J", "fam_h_keller": "Keller",
        "fam_h_coll": "3-na-1", "fam_h_prev": "pregled mape (G₀)",
        "fam_detail_label": "Detalj izabrane varijante (klikni red; kopiraj u Radionicu):",
        # --- diagnostics ---
        "tab_diagnostics": "Dijagnostika",
        "dg_title": "Dijagnostika: puna PSE mašinerija (theta · attractori · game-forme · Seldon/Physician)",
        "dg_run": "▶  Pokreni dijagnostiku",
        "dg_waiting": "Pokreni dijagnostiku →",
        "dg_running": "radim…",
        "dg_h_unit": "jedinica", "dg_h_mu": "μ(θ)", "dg_h_sigma": "σ(θ)",
        "dg_h_rho": "ρ (ACF1)", "dg_h_health": "zdravlje", "dg_h_attr": "atraktor",
        "dg_h_game": "dominantna igra", "dg_h_conf": "C",
        "dg_posterior_label": "Posterior nad 10 igara (klikni jedinicu u tabeli):",
        "dg_fission": "Log fisije (Jedinica 1 — adaptivni agenti)",
        "dg_seldon": "Seldon / Physician",
        "dg_geometry": "Geometrija roja:",
        "dg_consensus": "Konsenzus:",
        "dg_physician": "Physician nalaz:",
        "dg_phys_ok": "Nema patološkog atraktora — roj zdrav.",
        "dg_phys_flag": "Pažnja: {u} pokazuje {a}.",
        "dg_geo_none": "STABILNO (nema patološkog atraktora)",
        "dg_geo_narcissistic": "CIRCLE (cikliranje bez napretka)",
        "dg_geo_borderline": "HELIX (oscilujuća amplituda)",
        "dg_geo_codependent": "CLOSING SPIRAL (kolaps ka fiksnoj tački)",
        "dg_geo_schizoid": "OPENING SPIRAL (rast ka kolapsu — najopasnije)",
        # --- chat ---
        "tab_chat": "Chat",
        "chat_title": "Chat: razgovaraj s modelom o kontraprimjeru i aplikaciji",
        "chat_send": "Pošalji",
        "chat_clear": "Očisti",
        "chat_input_ph": "Napiši poruku…",
        "chat_you": "Ti",
        "chat_assistant": "Asistent",
        "chat_thinking": "…razmišljam…",
        "chat_error": "Greška: {e}",
        "chat_system": ("You are an assistant embedded in the PSE-Jacobian app. Context "
                        "(verified by the app, exact arithmetic): the Jacobian Conjecture "
                        "is disproved in dimension ≥3 by an explicit map C^3→C^3 with "
                        "constant Jacobian determinant −2 that is 3-to-1 — the points "
                        "(0,0,-1/4), (1,-3/2,13/2), (-1,3/2,13/2) all map to (-1/4,0,0). "
                        "The plane case n=2 remains open. Help the user understand the "
                        "mathematics and the app; be concise and honest; if unsure, say so. "
                        "Answer in the user's language."),
        # --- report ---
        "tab_report": "Izvještaj",
        "rep_title": "IZVJEŠTAJ — reprodukcija kontraprimjera Jacobianove konjekture",
        "rep_generate": "▶  Generiši izvještaj",
        "rep_export_txt": "Izvezi .txt",
        "rep_export_pdf": "Izvezi .pdf",
        "rep_export_html": "Izvezi .html",
        "rep_ledger": "Audit knjiga (append-only)",
        "rep_running": "generišem…",
        "rep_saved": "Sačuvano: {p}",
        "rep_export_err": "Greška pri izvozu: {e}",
        "rep_h_time": "Vrijeme", "rep_h_env": "Okruženje",
        "rep_h_map": "Mapa (C³→C³):",
        "rep_h_facts": "Egzaktno provjerene činjenice:",
        "rep_const": "konstanta ≠ 0",
        "rep_h_units": "Presude jedinica (nezavisni putevi):",
        "rep_h_comparator": "Komparator (unakrsne provjere):",
        "rep_h_consensus": "Konsenzus",
        "rep_h_structure": "Struktura:",
        "rep_struct_line": ("Kvazi-homogena; težine (x,y,z)=(−1,1,2), (a,b,c)=(2,1,−1); "
                            "F×id čuva det ⇒ važi za svako n≥3."),
        "rep_h_conclusion": "Zaključak:",
        "rep_conclusion": ("Jacobian Conjecture je OBORENA za n≥3 (n=2 ostaje otvoreno). "
                           "Reprodukovano lokalno, egzaktnom aritmetikom."),
        "rep_audit_report": "IZVJEŠTAJ generisan",
        "rep_audit_export": "IZVOZ",
    },
    "en": {
        "win_title": "PSE-Jacobian  v{v}  —  counterexample reproduction",
        "tab_case": "Case",
        "lang_label": "Language:",
        "case_title": "Case: counterexample to the Jacobian Conjecture (C³ → C³)",
        "mapbox_title": "Map under investigation (claim: det J = −2, non-injective)",
        "claimed_collision": "claimed collision: 3 distinct points → (−1/4, 0, 0)",
        "run_btn": "▶  Run investigation (3 units, separate threads)",
        "panel_alg": "Unit 1 · Algebra (adaptive fission)",
        "panel_fib": "Unit 2 · Fiber (discovers independently)",
        "panel_edge": "Unit 3 · Edge (structure)",
        "comp_title": "Comparator (Seldon / Physician) — refute-by-default",
        "waiting": "Waiting to run…",
        "xh_check": "cross-check",
        "xh_result": "result",
        "xh_detail": "detail",
        "investigating": "Investigation running…",
        "st_running": "RUNNING…",
        "st_error": "ERROR",
        "theta_line": "θ̄={mean:.1f}  σ={sig:.2f}  [{health}]  ({n} steps)",
        "verdict_prefix": "→ ",
        "disagreements": "Disagreements: ",
        "confidence": "(confidence {c:.0%})",
        "mark_ok": "✓ OK",
        "mark_no": "✗ NO",
        "mission_alg": "{unverified claim → re-check symbolically and numerically → verdict}",
        "mission_fib": "{measure the fiber → solve F(x)=target from scratch → geometric degree}",
        "mission_edge": "{why n≥3 fails but n=2 remains → quasi-homogeneity + dimension lift}",
        "name_alg": "Unit 1 · Algebra",
        "name_fib": "Unit 2 · Fiber",
        "name_edge": "Unit 3 · Edge",
        "alg_spawn": "⑂ fission: spawning agent {id} [{method}] for '{claim}'",
        "alg_refute": "⚠ agent {id} REFUTES '{claim}' → escalation (spawn all)",
        "alg_v_conf": ("det J = {det} (nonzero constant) and 3 distinct points → same image "
                       "⇒ NON-injective. Confirmed via {n} independent agents (fission)."),
        "alg_v_dis": "DISAGREEMENT among agents — claim not confirmed.",
        "alg_v_inc": "Insufficient independent confirmations.",
        "det_agent_sym": "symbolic det J = {det}",
        "det_agent_num": "det J equal at all 25 random points = {val}",
        "det_agent_ff": "det J constant mod {p} as well",
        "col_agent_exact": "exact: all 3 points → {tgt}",
        "col_agent_num": "numeric (float) collision check",
        "fib_solve": "solving system F(x,y,z) = target (Gröbner/solve_poly_system)…",
        "fib_found": "discovered {n} preimages (unaided)",
        "fib_degree": "geometric degree ≈ {deg} (preimages per target: {counts})",
        "fib_v_conf": ("The fiber has {n} preimages (degree ≈ {deg}); local Jacobian = "
                       "{det} at EACH (no local folding) ⇒ globally {n}-to-1."),
        "fib_v_inc": "Fiber is not unambiguously non-injective.",
        "edge_struct": "checking C*-equivariance (quasi-homogeneity)…",
        "edge_lift": "lifting to n=4 and n=5 via F×id…",
        "edge_v_conf": ("The map is quasi-homogeneous (weights {w}); the third variable z "
                        "(weight 2) is essential. F×id preserves det = {det} in n=4 and n=5 "
                        "⇒ the counterexample lifts to every n≥3. (n=2 lacks this structure "
                        "→ stays open.)"),
        "edge_v_inc": "Structure not confirmed.",
        "cc1": "Fiber (J2 discovered) == points (J1 verified)",
        "cc1_d": "J1 verified {a}, J2 independently discovered {b}; sets {eq}",
        "eq_same": "identical", "eq_diff": "DIFFERENT",
        "cc2": "det J equal across J1 (algebra), J2 (local), J3 (n=4,5)",
        "cc2_d": "values: {{{vals}}}",
        "cc3": "fiber cardinality == geom. degree == #points",
        "cc3_d": "preimages={n}, degree={deg}, points={t}",
        "cc4": "all three units ruled CONFIRMED (independently)",
        "dis_fiber": "Discovered fiber does not match the verified points.",
        "dis_det": "Jacobian differs across units.",
        "dis_card": "Preimage count / degree / points disagree.",
        "dis_status": "At least one unit did not confirm.",
        "dis_flat": "{tag}: theta flatline — possible 'rubber-stamp'.",
        "head_conf": ("CONSENSUS: three independent routes agree — constant nonzero Jacobian "
                      "yet non-injective. Jacobian Conjecture DISPROVED for n≥3."),
        "head_dis": "DISAGREEMENT — the claim is NOT unanimously confirmed. See the log.",
        "head_inc": "Inconclusive — insufficient agreement.",
        "pv_3d": "3D (real)", "pv_2d": "2D sections", "pv_tab": "Table (exact)",
        "pv_ph": "Run investigation →",
        "pv_h_pre": "preimage (x, y, z)", "pv_h_img": "F(preimage)",
        "pv_h_det": "local det J", "pv_h_note": "note",
        "pv_3d_title": "Fiber: three preimages → same image (3-to-1)",
        "pv_orbit": "C*-orbit (hidden symmetry)",
        "pv_2d_title": "2D projections of preimages + C*-orbit",
        "pv_note_orbit": "on C*-orbit (λ=−1)", "pv_note_fixed": "orbit fixed point",
        # --- workbench ---
        "tab_workbench": "Workbench",
        "wb_title": "Workbench: classify any polynomial map Cⁿ→Cⁿ",
        "wb_vars_label": "Variables (e.g. x, y, z):",
        "wb_comps_label": "Components (one per line):",
        "wb_preset_label": "Preset:",
        "wb_analyze": "▶  Analyze map",
        "wb_panel_keller": "Keller check (fission)",
        "wb_panel_inj": "Injectivity / fiber",
        "wb_panel_inv": "Inverse",
        "wb_verdict_title": "Verdict (map classification)",
        "wb_parse_error": "Input error: {e}",
        "wb_name_keller": "Keller check",
        "wb_mission_keller": "{is det J a nonzero constant?}",
        "wb_name_inj": "Injectivity",
        "wb_mission_inj": "{geometric degree via image-sampled targets}",
        "wb_name_inv": "Inverse",
        "wb_mission_inv": "{if injective → attempt an explicit inverse}",
        "wb_v_keller_yes": "It IS a Keller map: det J = {det} (nonzero constant).",
        "wb_v_keller_no": "NOT a Keller map: det J = {det} is not a nonzero constant.",
        "wb_keller_anomaly": "Symbolic vs numeric Jacobian mismatch — escalation.",
        "wb_v_inj_yes": "Injective (degree 1): every fiber = 1 point.",
        "wb_v_inj_no": "{deg}-to-1 (NOT injective). Example collision: {pts} → {tgt}.",
        "wb_v_inj_fail": "Degree not determined ({e}).",
        "wb_inv_check": "quick injectivity check…",
        "wb_inv_try": "attempting an explicit inverse…",
        "wb_v_inv_yes": "Inverse exists (polynomial): {inv}",
        "wb_v_inv_no": "No inverse (the map is not injective).",
        "wb_v_inv_maybe": "Injective, but an explicit inverse was not constructed automatically.",
        "wb_cc_consistency": "inverse ⇔ degree 1",
        "wb_cc_consistency_d": "inverse={inv}, degree={deg}",
        "wb_yes": "yes", "wb_no": "no",
        "wb_head_counter": "COUNTEREXAMPLE: a Keller map that is NOT injective ⇒ disproves the Jacobian Conjecture.",
        "wb_head_invertible": "Keller map and injective ⇒ invertible (consistent with the conjecture).",
        "wb_head_notkeller": "Not a Keller map (det J is not a nonzero constant) — the conjecture does not apply.",
        "wb_head_inconclusive": "Inconclusive — degree/status not determined.",
        "preset_counterexample": "Counterexample (Alpöge/Fable)",
        "preset_automorphism": "Automorphism (x+y², y)",
        "preset_identity": "Identity",
        "preset_not_keller": "Not Keller (x², y)",
        "preset_custom": "— custom —",
        # --- discovery ---
        "tab_discovery": "Discovery",
        "disc_title": "Discovery: the LLM proposes, the swarm verifies exactly",
        "disc_sub": ("Reproducing the method itself (Alpöge + Fable): a creative model "
                     "invents a candidate map, a deterministic swarm verifies it. The "
                     "Guardian is refute-by-default — most proposals FAIL, and that filter "
                     "is the point."),
        "disc_provider": "LLM provider",
        "disc_provider_label": "Provider:",
        "disc_key_ph": "empty = read from environment (env)",
        "disc_task_label": "Task (message to the model):",
        "disc_task_default": ("Propose an EXPLICIT counterexample to the Jacobian "
                              "Conjecture: a polynomial map C^3→C^3 with constant nonzero "
                              "Jacobian that is NOT injective. Return ONLY in VARS:/MAP: "
                              "format."),
        "disc_propose": "▶  Propose (LLM)",
        "disc_verify": "Verify proposal (swarm)",
        "disc_raw_label": "Raw LLM response:",
        "disc_calling": "calling the LLM…",
        "disc_llm_error": "LLM error: {e}",
        "disc_no_map": ("Could not extract a map from the response — check the format "
                        "(VARS:/MAP:) or edit it manually then 'Verify proposal'."),
        "disc_system": ("You are a mathematics proposal engine. Propose ONE explicit "
                        "polynomial map C^n -> C^n as a CANDIDATE for verification. "
                        "Output ONLY in this exact format, nothing else:\n"
                        "VARS: <comma-separated variables>\nMAP:\n"
                        "<one polynomial per line, Python/sympy syntax, ** for powers>\n"
                        "Use exact integer/rational coefficients. Do not explain."),
        # --- n=2 frontier ---
        "tab_frontier": "n=2 Frontier",
        "fr_title": "n=2 Frontier: an experimental platform for the open plane conjecture",
        "fr_sub": ("The plane conjecture (n=2) is OPEN. We generate genuine Keller maps in "
                   "two variables (by composing elementary automorphisms) and the swarm "
                   "tests each independently. We accumulate evidence — but this CANNOT "
                   "settle the conjecture: this family (tame automorphisms) cannot contain "
                   "a hypothetical 'wild' Keller map, should one exist."),
        "fr_k": "Complexity (number of factors k):",
        "fr_n": "Number of maps:",
        "fr_seed": "Seed:",
        "fr_run": "▶  Generate and test",
        "fr_running": "generating and testing…  ({i}/{n})",
        "fr_summary": "{n} maps tested: Keller {kel}/{n}, invertible {inv}/{n}, COUNTEREXAMPLES: {ctr}",
        "fr_summary_consistent": "All invertible — consistent with the open plane conjecture (not a proof).",
        "fr_summary_counter": "ATTENTION: a candidate counterexample was found! Check it in the Workbench.",
        "fr_h_seed": "seed", "fr_h_factors": "factors", "fr_h_det": "det J",
        "fr_h_keller": "Keller", "fr_h_inv": "invertible", "fr_h_verdict": "verdict",
        "fr_v_invertible": "invertible", "fr_v_notkeller": "not Keller",
        "fr_v_noinv": "Keller, no explicit inverse", "fr_v_inc": "inconclusive",
        "fr_disclaimer": ("Note: this generator produces tame automorphisms (always "
                          "invertible). Its purpose is to show the pattern and provide a "
                          "testbed, not to prove n=2. If a row ever shows Keller=✓ and "
                          "invertible=✗ with a proof of non-injectivity — that is news."),
        # --- family ---
        "tab_family": "Family",
        "fam_title": "Family: other explicit counterexamples in dimension 3 (the affine orbit)",
        "fam_sub": ("Affine conjugation G = A∘F∘B (A,B invertible affine) always yields a "
                    "NEW counterexample: det stays ±2, non-injectivity is preserved, and "
                    "the colliding points map exactly. The counterexample is one point of "
                    "an infinite orbit of explicit siblings."),
        "fam_rigid": ("Coefficient rigidity: in a grid of bare-coefficient deformations "
                      "around the original, the only Keller map is the original — the shape "
                      "is isolated. The freedom is in the affine group, not the coefficients."),
        "fam_n": "Number of variants:",
        "fam_seed": "Seed:",
        "fam_run": "▶  Generate family",
        "fam_running": "generating variants…  ({i}/{n})",
        "fam_summary": ("{n} distinct explicit counterexamples: all Keller (det=±2≠0), all "
                        "3-to-1. The orbit is infinite."),
        "fam_h_seed": "variant", "fam_h_det": "det J", "fam_h_keller": "Keller",
        "fam_h_coll": "3-to-1", "fam_h_prev": "map preview (G₀)",
        "fam_detail_label": "Selected variant detail (click a row; copy into the Workbench):",
        # --- diagnostics ---
        "tab_diagnostics": "Diagnostics",
        "dg_title": "Diagnostics: the full PSE machinery (theta · attractors · game forms · Seldon/Physician)",
        "dg_run": "▶  Run diagnostics",
        "dg_waiting": "Run diagnostics →",
        "dg_running": "working…",
        "dg_h_unit": "unit", "dg_h_mu": "μ(θ)", "dg_h_sigma": "σ(θ)",
        "dg_h_rho": "ρ (ACF1)", "dg_h_health": "health", "dg_h_attr": "attractor",
        "dg_h_game": "dominant game", "dg_h_conf": "C",
        "dg_posterior_label": "Posterior over the 10 games (click a unit in the table):",
        "dg_fission": "Fission log (Unit 1 — adaptive agents)",
        "dg_seldon": "Seldon / Physician",
        "dg_geometry": "Swarm geometry:",
        "dg_consensus": "Consensus:",
        "dg_physician": "Physician finding:",
        "dg_phys_ok": "No pathological attractor — swarm healthy.",
        "dg_phys_flag": "Attention: {u} shows {a}.",
        "dg_geo_none": "STABLE (no pathological attractor)",
        "dg_geo_narcissistic": "CIRCLE (cycles without progress)",
        "dg_geo_borderline": "HELIX (oscillating amplitude)",
        "dg_geo_codependent": "CLOSING SPIRAL (collapse to a fixed point)",
        "dg_geo_schizoid": "OPENING SPIRAL (growth toward collapse — most dangerous)",
        # --- chat ---
        "tab_chat": "Chat",
        "chat_title": "Chat: talk to a model about the counterexample and the app",
        "chat_send": "Send",
        "chat_clear": "Clear",
        "chat_input_ph": "Write a message…",
        "chat_you": "You",
        "chat_assistant": "Assistant",
        "chat_thinking": "…thinking…",
        "chat_error": "Error: {e}",
        "chat_system": ("You are an assistant embedded in the PSE-Jacobian app. Context "
                        "(verified by the app, exact arithmetic): the Jacobian Conjecture "
                        "is disproved in dimension ≥3 by an explicit map C^3→C^3 with "
                        "constant Jacobian determinant −2 that is 3-to-1 — the points "
                        "(0,0,-1/4), (1,-3/2,13/2), (-1,3/2,13/2) all map to (-1/4,0,0). "
                        "The plane case n=2 remains open. Help the user understand the "
                        "mathematics and the app; be concise and honest; if unsure, say so. "
                        "Answer in the user's language."),
        # --- report ---
        "tab_report": "Report",
        "rep_title": "REPORT — reproduction of the Jacobian Conjecture counterexample",
        "rep_generate": "▶  Generate report",
        "rep_export_txt": "Export .txt",
        "rep_export_pdf": "Export .pdf",
        "rep_export_html": "Export .html",
        "rep_ledger": "Audit ledger (append-only)",
        "rep_running": "generating…",
        "rep_saved": "Saved: {p}",
        "rep_export_err": "Export error: {e}",
        "rep_h_time": "Time", "rep_h_env": "Environment",
        "rep_h_map": "Map (C³→C³):",
        "rep_h_facts": "Exactly verified facts:",
        "rep_const": "nonzero constant",
        "rep_h_units": "Unit verdicts (independent routes):",
        "rep_h_comparator": "Comparator (cross-checks):",
        "rep_h_consensus": "Consensus",
        "rep_h_structure": "Structure:",
        "rep_struct_line": ("Quasi-homogeneous; weights (x,y,z)=(−1,1,2), (a,b,c)=(2,1,−1); "
                            "F×id preserves det ⇒ holds for every n≥3."),
        "rep_h_conclusion": "Conclusion:",
        "rep_conclusion": ("The Jacobian Conjecture is DISPROVED for n≥3 (n=2 remains open). "
                           "Reproduced locally, with exact arithmetic."),
        "rep_audit_report": "REPORT generated",
        "rep_audit_export": "EXPORT",
    },
}
