# PSE-Jacobian — Vodič (Korak 1: temelj + tab „Slučaj")

## Šta je ovo
Aplikacija koja **tvojim PSE agentima nezavisno reprodukuje i revidira** kontraprimjer
Jacobianove konjekture (Alpöge / Claude Fable 5, jul 2026), mapu C³ → C³ sa
konstantnim Jakobijanom −2 koja **nije injektivna** (3-na-1).

Poenta nije „vjerovati vijesti" nego **provjeriti sam objekat** — i to tri puta,
različitim putevima, pa uporediti rezultate (master fajl: *refute-by-default*).

## Kako se pokreće
```
cd "~/Desktop/PSE Jacobian/app"
./run.sh
```
ili `python3 run.py`. Treba: `python3, PySide6, sympy, numpy, matplotlib`
(vidi `requirements.txt`; sve je već instalirano na tvojoj mašini).

## Šta vidiš u tabu „Slučaj"
1. **Mapa pod istragom** — tri komponente + tvrđena kolizija (→ (−1/4,0,0)).
2. Dugme **„Pokreni istragu"** — startuje **tri jedinice, svaku u svojoj niti**.
3. **Tri panela** (rade paralelno, zasebno):
   - **Jedinica 1 · Algebra (adaptivna fisija):** kreće s 1 agentom pa **spawnuje još
     koliko treba**. Simbolički det, numerički det (25 slučajnih tačaka), egzaktno
     uvrštavanje tačaka, numerička provjera. Ako se agenti slože → staje; ako se neko
     **ne slaže → eskalira** (spawnuje sve + digne zastavicu). Na čistom kontraprimjeru
     spawnuje 4 agenta.
   - **Jedinica 2 · Vlakno:** **sama rješava** F(x,y,z)=(−1/4,0,0) i **otkriva** praslike
     (ne dobija ih). Računa geometrijski stepen (=3) i lokalni Jakobijan u svakoj (=−2).
   - **Jedinica 3 · Rub:** provjeri kvazi-homogenost (C\*-ekvivarijantnost, težine
     (2,1,−1)) i digne mapu na n=4, n=5 (det ostaje −2 → važi za svako n≥3).
4. **θ (theta)** ispod svakog panela: mjeri stварно angažovanje. Zdravo = oscilacija u
   [25,35], σ≈1.5–3. Ako bi jedinica „pečatirala bez rada" → flatline → crvena zastavica.
5. **Komparator (Seldon/Physician)** dole: unakrsno poredi:
   - vlakno koje je J2 **otkrio** == tačke koje je J1 **potvrdio**;
   - det J jednak u sve tri jedinice;
   - kardinalnost vlakna == stepen == broj tačaka;
   - sve tri presudile CONFIRMED.
   Konsenzus se proglašava **samo ako sve prođe i nema nijednog neslaganja**.
6. **Grafika (desno):** 3D realni prikaz (tri praslike + skrivena C\*-orbita koja
   povezuje dvije od njih), 2D projekcije, i egzaktna tabela.

## Šta treba da dobiješ
- J1: CONFIRMED, 4 agenta. J2: CONFIRMED, 3 praslike, stepen 3. J3: CONFIRMED.
- Komparator: **„KONSENZUS … Jacobian Conjecture OBORENA za n≥3", pouzdanost 100%.**

## Struktura koda
```
app/
  run.py, run.sh, requirements.txt
  pse_jacobian/
    constants.py            # PSE konstante (70/30 relaksiran, jer nije human-facing)
    mathengine/             # čista matematika (sympy/numpy)
      known.py              # sama mapa + tvrđene tačke (sve se preračunava, ništa se ne vjeruje)
      keller.py             # Jakobijan (simbolički+numerički), Keller-test, kolizije
      fiber.py              # rješavanje vlakna, geometrijski stepen, lokalni det
      structure.py          # kvazi-homogenost, dizanje dimenzije
    pse/
      theta.py              # ThetaMonitor (angažovanje/„pečat bez rada" detekcija)
      unit.py, units.py     # tri jedinice + adaptivna fisija
      comparator.py         # Seldon/Physician unakrsna provjera
    gui/                    # PySide6: prozor, tab „Slučaj", niti, matplotlib grafika
    llm/                    # apstrakcija provajdera (stub; povezuje se kasnije)
```
Master fajl PSE arhitekture se **ne dira**.

## Ažuriranje (popravke nakon prvog pokretanja)
- **Prozor se sad prilagođava ekranu**: nikad veći od dostupne površine (95%×92%),
  centriran; ceo sadržaj je u *scroll* oblasti pa na malom ekranu skroluje umjesto da
  iscuri van. Minimalna veličina 700×480.
- **Prekidač jezika SR/EN** gore lijevo (padajući meni „Jezik / Language"). Prevodi se
  **sve** — ne samo GUI, nego i presude jedinica, poruke fisije i komparator. Promjena
  jezika prezida tabove (trenutni rezultati se očiste; samo ponovo pokreni istragu).

## Tab 2 — Radionica (Workbench)
Uneseš **bilo koju** polinomsku mapu Cⁿ→Cⁿ, a roj je klasifikuje. Tri jedinice u
zasebnim nitima:
- **Keller-provjera (fisija):** simbolički + numerički Jakobijan → je li det J konstanta
  ≠ 0 (premisa konjekture)? Ako se simbolički i numerički ne slažu → eskalacija.
- **Injektivnost / vlakno:** geometrijski stepen preko ciljeva uzorkovanih iz slike;
  ako je stepen > 1 → nađe konkretan primjer kolizije.
- **Inverz:** ako je injektivna (stepen 1) → pokuša da **konstruiše eksplicitan
  polinomijalni inverz** i prikaže ga; ako nije injektivna → nema inverza.

**Presuda** (klasifikacija) je jedno od:
- **KONTRAPRIMJER** — Keller-mapa koja NIJE injektivna (obara konjekturu);
- **invertibilna** — Keller i injektivna (u skladu s konjekturom);
- **nije Keller-mapa** — premisa pada, konjektura se ne primjenjuje;
- **neodlučno**.

Padajući meni **„Primjer"** ima gotove slučajeve za svaki tip: *Kontraprimjer
(Alpöge/Fable)*, *Automorfizam (x+y², y)* → inverz (y0−y1², y1), *Identitet*,
*Nije Keller (x², y)*. Ili uneseš svoje: varijable u prvom polju („x, y, z"),
komponente jedna po liniji.

Ovo je alat kojim provjeravaš i **buduće tuđe „kontraprimjere"** — samo ubaciš polinome.

## Tab 3 — Otkriće (Discovery)
Reprodukcija **same metode** (Alpöge + Fable): LLM **predloži** kandidat-mapu, a roj je
**egzaktno provjeri**. Guardian je *refute-by-default* — većina predloga PADNE, i to je
poenta (filter na lažne predloge).

- **Provajder** (padajući meni):
  - *Lokalna simulacija (test, bez mreže)* — vraća poznati kontraprimjer; za probu toka bez ključa.
  - *Lokalni GGUF / LM Studio* — upali model u LM Studiju (server na `http://localhost:1234/v1`).
  - *Claude / Mistral / Groq* — unesi API ključ u polje, ili ga ostavi prazno pa se čita
    iz okruženja: `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`.
- **Zadatak** — poruka modelu (podrazumijevano: „predloži eksplicitan kontraprimjer…"). Uredi po želji.
- **Predloži (LLM)** → model vrati odgovor u formatu `VARS:/MAP:`; aplikacija izvuče mapu,
  ubaci je u editabilna polja i **automatski pokrene provjeru** (iste tri jedinice kao Radionica).
- **Presuda** ista kao u Radionici: KONTRAPRIMJER / invertibilna / nije-Keller / neodlučno.

Model ne mora da pogodi — ako predlog ne valja, roj to **uhvati i odbaci**. Ako format
nije `VARS:/MAP:`, uredi polja ručno pa „Provjeri predlog".

## Tab 4 — n=2 Granica (Frontier)
Pošto je **ravan-konjektura (n=2) otvorena**, ovaj tab je eksperimentalna platforma.
Generiše prave **Keller-mape u 2 varijable** (kompozicijom elementarnih automorfizama —
smicanja + trougaone afine), a roj svaku nezavisno testira i **gomila dokaze**.

- Kontrole: **k** (broj faktora = složenost), **broj mapa**, **sjeme** (za ponovljivost).
- Za svaku mapu tabela pokazuje: sjeme, faktore, det J, je li Keller, je li invertibilna
  (konstruisan pravi polinomijalni inverz), presudu.
- Sažetak (zeleno): npr. „20 mapa: Keller 20/20, invertibilnih 20/20, KONTRAPRIMJERA: 0 —
  u skladu s otvorenom konjekturom". Ako se ikad pojavi red Keller=✓ / invertibilno=✗ uz
  dokaz ne-injektivnosti — crveno upozorenje (to bi bila vijest).

**Iskreno:** ovo NE rješava n=2. Ova familija (pitomi automorfizmi) je uvijek
invertibilna po konstrukciji; svrha je pokazati obrazac i dati teren, ne dokaz. (Bug koji
sam usput uhvatio: sympy `subs` je sekvencijalan pa je kvario kompoziciju — riješeno sa
`simultaneous=True`; svi inverzi se sad verifikuju kao inv∘F = identitet.)

## Tab 5 — Porodica (Family)
Traži **druge eksplicitne kontraprimjere** u dimenziji 3. Dva nalaza:
- **Krutost koeficijenata:** ako mijenjaš gole koeficijente originalne mape, Keller-svojstvo
  puca skoro uvijek — u testiranoj mreži jedini Keller je original. Oblik je izolovan.
- **Afina orbita (beskonačna):** ali konjugacija **G = A∘F∘B** (A, B invertibilne afine)
  UVIJEK daje novi kontraprimjer: det ostaje ±2, ne-injektivnost se čuva, a tri kolizione
  tačke se preslikaju egzaktno (w_i = B⁻¹(p_i), zajednička slika A(q)). Kontraprimjer je
  jedna tačka beskonačne orbite.

Kontrole: broj varijanti + sjeme → **Generiši porodicu**. Tabela: varijanta, det J, Keller,
3-na-1, pregled mape. Klikni red → **detalj** (puna mapa u `VARS:/MAP:` formatu + kolizione
tačke) koji možeš kopirati u **Radionicu** ili **Otkriće**.

Verifikacija je brza i egzaktna: det preko lančanog pravila (det G = det(A)·(−2)·det(B)) uz
kontrolnu tačku, a kolizija egzaktno preko malog originalnog F.

## Tab 6 — Dijagnostika (puna PSE mašinerija)
Pokreneš dijagnostiku (ista tri Case jedinice) i vidiš **cijelu PSE unutrašnjost**:
- **theta trajektorije** sve tri jedinice na jednom grafu, sa zdravim pojasom [25,35];
- **tabela po jedinici:** μ(θ), σ(θ), ρ (autokorelacija), zdravlje
  (healthy/enmeshed/withdrawn/flatline), **atraktor** (Narcissistic/Borderline/
  Codependent/Schizoid/none) i **dominantna igra** + pouzdanost C;
- **posterior nad 10 igara** (klikni jedinicu) sa trakama;
- **log fisije** (agenti Jedinice 1);
- **Seldon/Physician:** geometrija roja + konsenzus + nalaz („roj zdrav" ili crveno).

**Game-forme su prilagođene domenu** (adversarijalna matematička verifikacija), kako PSE
master dozvoljava. Attractori i Bayes ostaju netaknuti; promijenjen je skup igara:
- zadržano iz mastera: **Nash Substrate, Signalling, War of Attrition, Global Games, ESS**;
- izbačeno: Iterated PD, Chicken, Stag Hunt, Bargaining, All-Pay, Correlated Equilibrium;
- **dodato (novo):** **Prover–Verifier** (interaktivni dokaz), **Bluff-Catching**,
  **Byzantine Consensus**, **Inspection Game**, **Screening/Lemons**.

Tipičan zdrav ishod: Algebra → *Inspection Game* (koliko agenata potrošiti fisijom),
Vlakno → *Prover–Verifier*, Rub → *War of Attrition*; svi „healthy", atraktor „none",
Physician: roj zdrav. Svaka jedinica ima svoju theta fazu pa se krive razdvajaju.

## Tab 7 — Chat
Višekružni razgovor s LLM-om o kontraprimjeru i aplikaciji. Isti provajderi kao Otkriće:
- *Lokalna simulacija* (offline, bez ključa) — odmah odgovara za probu;
- *LM Studio* (`http://localhost:1234/v1`), *Claude*, *Mistral*, *Groq* (ključ u polje ili env).

Model je „ugrijan" kontekstom (sistemski prompt sadrži potvrđene činjenice: mapa C³→C³,
det −2, tri tačke → (−1/4,0,0), n=2 otvoreno) pa razgovor ostaje utemeljen. Odgovara na
jeziku kojim mu pišeš. „Očisti" resetuje istoriju.

## Tab 8 — Izvještaj
**Generiši izvještaj** → roj odradi slučaj i sastavi se dokument: vrijeme, okruženje
(Python/sympy verzije), mapa, egzaktno provjerene činjenice (det −2, tri tačke → cilj),
presude sve tri jedinice, unakrsne provjere komparatora + konsenzus, struktura, zaključak.
**Izvoz** u `.txt`, `.html` ili `.pdf`. Svako generisanje i izvoz se upisuje u
**append-only audit knjigu** (`~/.pse_jacobian/audit.log`) — to je dokaz da si *ti* lično
ponovio eksperiment, s vremenskim pečatom.

## Instalacija (.deb)
Paket: `pse-jacobian_0.1.0_all.deb` (u `app/`).

**Instaliraj:**
```
cd ~/"Desktop/PSE Jacobian/app"
sudo dpkg -i pse-jacobian_0.1.0_all.deb
```
Zavisnost je samo `python3`, pa se instalira čisto. Pokreni iz menija
(**PSE-Jacobian**, kategorija Obrazovanje/Nauka) ili iz terminala: `pse-jacobian`.

**Gdje šta ide:** app u `/opt/pse-jacobian`, launcher `/usr/bin/pse-jacobian`,
`.desktop` + ikona u sistemu, vodiči u `/usr/share/doc/pse-jacobian`.

**Python paketi:** launcher prvo koristi `~/pse-venv` ako postoji (tvoj slučaj — tamo su
PySide6/sympy/numpy/matplotlib). Ako ga nema (npr. kod prijatelja), instaliraj preporučene:
`sudo apt install python3-pyside6 python3-sympy python3-numpy python3-matplotlib`
ili naprav­i venv: `python3 -m venv ~/pse-venv && ~/pse-venv/bin/pip install PySide6 sympy numpy matplotlib`.

**Deinstalacija:** `sudo dpkg -r pse-jacobian`.
**Ponovna izgradnja paketa:** `sh packaging/build_deb.sh`.

---
**Gotovo — svih 8 tabova + .deb.** Aplikacija reprodukuje i revidira kontraprimjer,
mjeri prostor konjekture, i sve to na PSE arhitekturi (theta, attractori, domenske
game-forme, Seldon/Physician, adaptivna fisija), s izvještajem i audit knjigom kao
dokazom da si *ti* ponovio eksperiment.
