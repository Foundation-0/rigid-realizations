> The full report of the research agent that scouted physics, chemistry and materials, Earth and climate science for Foundation0 on 19 October 2026, kept as it was written. It is model output: a fact in it was checked against its source only where [fact-check.md](fact-check.md) says so. Paths starting with `scratch/` were the scouting session's temporary folder; see [README.md](README.md) for where those files are now.

# Scouting: physics, chemistry and materials, Earth and climate, engineering (19 Oct 2026)

I read the arXiv abstract pages and key PDFs directly. The checks on who else is working on each lead are web searches, so they are not exhaustive. Anything marked *(unverified)* comes from a secondary source or a page I did not open.

## 1. rigid-realizations (engineering, with a chemistry link)
- **Question:** Can bar lengths be chosen so that all 880 complex realizations of the 10-vertex framework with the most of them are real? How far does "all real" go: n = 11–13 in the plane, and 8 vertices in space?
- **Why now:**
  - The largest possible number of real realizations is settled in the plane only up to n = 9: 136 for n = 8 and 344 for n = 9, all real. For n = 10 the best is at least 860 of 880. Eight more solutions were found but failed verification by less than 10⁻⁸ ([Bartzos, Emiris, Legerský, Tsigaridas, JSC 2021](https://arxiv.org/abs/1811.12800)).
  - In space, the 8-vertex graph G160 has 160 complex embeddings, but only 132 real ones have been found.
  - In Feb 2025, [Grasegger](https://arxiv.org/abs/2502.04736) settled the complex maxima for all n ≤ 13. He wrote that the complex-counting methods give little information about real counts, and he still cites a real growth rate of about 2.378ⁿ, against at least 2.5997ⁿ for complex counts.
- **Who else:** The Grasegger, Dewar and Schicho circle works on complex counts ([2510.02988](https://arxiv.org/abs/2510.02988); I did not open it). I searched "real realizations/embeddings" with Laman/Geiringer for 2024–26 and found no paper on maximal real counts.
- **How a result is checked:** Publish rational bar lengths plus a certified enclosure of every real solution (Krawczyk, or HomotopyContinuation.jl's `certify`). If the certified real count equals the known complex count, the case is closed. Anyone can re-run the check in minutes.
- **First step:** Take the L880 lengths printed in the paper, solve the system, certify the 860 real solutions, and look at the 8 near-degenerate ones. Then search locally around them. Repeat for G160 (132 real).
- **Data and tools:** Bartzos and Legerský's code on Zenodo (ref. [2] of the paper); graph encodings in the appendix of Grasegger 2025; HomotopyContinuation.jl; PHCpack.
- **Member fit:** incentre-lattices (rigidity) and Ahraz's exact search plus checking. The real-root certification is the same machinery as point-charges.
- **Risks and what would kill it:**
  - Some graphs provably have fewer real than complex realizations. The known obstruction (4 ∤ c₂) does not apply to 880.
  - The audience is narrow: rigidity theory, real algebraic geometry and mechanism design.
  - Kill: no gain beyond 860 after two weeks and no visible obstruction.

## 2. certified-orbits (physics; checking computer-claimed results)
- **Question:** Which of the more than 150,000 published numerical periodic orbits of the three-body problem provably exist, and which of the "stable" ones are provably KAM-stable?
- **Why now:**
  - Li and Liao reported 10,059 new 3D orbits ([2508.08568](https://arxiv.org/abs/2508.08568), Aug 2025; *Sci. China PMA* 69:119515, 2026), after 135,445 planar ones in 2021 ([data](https://numericaltank.sjtu.edu.cn/three-body/three-body.htm)).
  - Hristov, Hristova and Tanikawa list 971 linearly stable orbits only as candidates for KAM stability ([2510.22802](https://arxiv.org/abs/2510.22802), Oct 2025).
  - An earlier Hristov et al. paper found 12,409 free-fall orbits and criticised the consistency of earlier lists ([2308.16159](https://arxiv.org/abs/2308.16159)).
  - A July 2026 paper uses physics-informed neural networks (PINNs) to find orbits ([2607.23501](https://arxiv.org/abs/2607.23501)).
  - A 2024 note says proofs that these numerical orbits exist "still remain to be provided, with a few exceptions" ([Ion, SCSS 2024](https://ceur-ws.org/Vol-3754/paper08.pdf)).
- **Who else:** Computer-assisted proofs exist only for the figure-eight and a few choreographies (Kapela, Zgliczyński and Simó, 2003–2017; [Kapela's papers](https://ww2.ii.uj.edu.pl/~kapela/papers/papers.html)). I searched for computer-assisted proofs and validated numerics together with Li–Liao, Hristov and Šuvakov for 2025–26 and found no paper certifying any catalogue.
- **How a result is checked:** An interval Newton–Krawczyk proof on each orbit's symmetric half-period shooting map. Each proof is a file that others re-run.
- **First step:** Download the Li–Liao 3D list and the Hristov stable list. Certify the 20 equal-mass orbits with the shortest periods and log each failure.
- **Data and tools:** published initial conditions (numericaltank, GitHub sjtu-liao/three-body); the CAPD library, or TaylorIntegration.jl with IntervalArithmetic.jl.
- **Member fit:** point-charges (certified numerics); Ryan Shea's rented compute for the bulk run; rohanarun's agent queue.
- **Risks and what would kill it:**
  - Long, very unstable orbits blow up the interval enclosures, so multiple shooting is needed.
  - Some initial conditions may be printed with too few digits.
  - Tell Kapela and Zgliczyński early; they may collaborate.
  - Kill: fewer than half of the 50 shortest orbits certify within two weeks.

## 3. relative-equilibria (physics; direct extension of point-charges)
- **Question:** Exactly how many relative equilibria do N = 5, 6 and 7 identical point vortices have, and how many central configurations do 8 equal masses have?
- **Why now:**
  - Moczurad and Zgliczyński certified complete lists for 5, 6 and 7 equal masses. For n = 8 they only proved that non-symmetric configurations exist ([1812.07279](https://arxiv.org/abs/1812.07279)).
  - Their 2026 work moved to unequal masses for five bodies ([2601.01165](https://arxiv.org/abs/2601.01165), Jan and Jul 2026).
  - For identical vortices, a Sept 2026 paper classifies only N = 4 ([2609.15090](https://arxiv.org/abs/2609.15090)).
  - For N ≥ 5 there are only numerical catalogues: Campbell and Ziff 1978, and continuation up to N ≤ 8 in a [2012 thesis](https://ross.aoe.vt.edu/papers/dirksen-2012-thesis.pdf). Rigorous proofs so far cover only some configurations on the sphere ([2309.04320](https://arxiv.org/abs/2309.04320)).
- **Who else:** The four-body cases are busy: [2606.19596](https://arxiv.org/abs/2606.19596) (Jun 2026), [2609.01857](https://arxiv.org/abs/2609.01857) (Sep 2026) and [2610.04593](https://arxiv.org/abs/2610.04593) (Oct 2026). I found no certified count for N ≥ 5 identical vortices or for 8 equal masses.
- **How a result is checked:** Certified boxes, each containing exactly one solution, plus exclusion certificates for the rest of the search region, as in point-charges.
- **First step:** Adapt the point-charges certifier to the planar central-configuration equations, with the potential's exponent as a parameter. Reproduce the known count for 5 equal masses, then run 5 vortices (logarithmic potential).
- **Data and tools:** the point-charges code; IntervalArithmetic.jl; HomotopyContinuation.jl to generate candidates.
- **Member fit:** point-charges and Ahraz. Relative equilibria of vortices are equilibria of 2D logarithmic charges in a rotating frame.
- **Risks and what would kill it:**
  - The Kraków group could publish first.
  - For n = 8, the lower bounds on distances between bodies may leave a search region too large to cover.
  - Identical vortices might have continuous families of equilibria rather than a finite count; that would be a result in itself.
  - Kill: a published certified count for these N.

## 4. wwssn-microseisms (Earth and climate)
- **Question:** Did ocean wave energy, as recorded in seismic microseisms, change between 1962–78 and today?
- **Why now:**
  - The USGS released the WWSSN film-chip scans on 14 July 2025 under CC0: about 3.7 million single-day records from 1962–78, described as about 5% of the archive ([release](https://www.usgs.gov/data/world-wide-standardized-seismographic-network-film-chip-scans)).
  - Aster et al. found that wave energy has been rising by 0.27% a year at 52 stations since the late 1980s. They wrote that extending the record into the analog era "offers an opportunity" ([Nat Commun 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10620394/)).
  - The USGS says "few researchers have utilized large numbers of these records" ([Nagle-McNaughton 2022](https://pubs.usgs.gov/publication/70231381)).
- **Who else:** Single-station analog studies exist: Bromirski 2023 (Berkeley, 1931–2021) and Lecocq et al. 2020 (Belgium, the 1953 storm), both cited in Aster et al. The USGS authors themselves (Aster, Ringler, Lee) are the likeliest competitors and collaborators. I found no multi-station microseism study using WWSSN since the release.
- **How a result is checked:** Compare the series measured from the scans with the ERA5 wave reanalysis, and with modern digital data from the same sites where the records overlap. Anyone can re-measure the same TIFF files.
- **First step:**
  1. Get Globus access.
  2. Inventory which stations have continuous days rather than only days around events.
  3. Measure the long-period trace amplitude for one month at ALQ (Albuquerque, whose calibration Ringler et al. 2020 assessed) and at one coastal station.
  4. Correlate the result with ERA5 swell.
- **Data and tools:** the scans; Lee (2022) digitised waveforms; DigitSeis; Peterson and Hutt 2014 instrument responses; ERA5; EarthScope FDSN.
- **Member fit:** the plate-eclipses pattern (an old photographic archive joined to modern data); Ryan Shea for a GPU image pipeline.
- **Risks and what would kill it:**
  - The 5% may have been chosen around events.
  - The metadata gives 1961–1996 while the summary says 1962–78.
  - Instrument gains changed over time.
  - The USGS may publish first.
  - Kill: no station has about 3 years of near-continuous days, or the pilot amplitudes don't track ERA5.

## 5. cod-symmetry (chemistry and materials)
- **Question:** How many of the 535,015 Crystallography Open Database (COD) structures have more symmetry than reported?
- **Why now:**
  - Avdeev found that 0.65% of 223,076 ICSD entries were reported with lower symmetry than they have. Of the flagged non-centrosymmetric entries, 74% are actually centrosymmetric, which matters for piezoelectric and nonlinear-optical screening ([Acta B, Sept 2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11457106/)).
  - The COD is CC0 and held 535,015 entries on 17 Oct 2026 ([COD](https://www.crystallography.net/cod/)).
- **Who else:** I found no survey of COD. COD's published validation checks CIFs against the CIF dictionaries ([Vaitkus et al. 2021](https://journals.iucr.org/j/issues/2021/02/00/yr5065/index.html)).
- **How a result is checked:** Each flag comes with a transformation and a new space group that anyone can re-run with spglib or PLATON's ADDSYM. The COD maintainers decide.
- **First step:** Mirror the COD and run spglib at two tolerances on the inorganic subset. Compare the rate with ICSD's and send 20 cases to the maintainers.
- **Member fit:** Ahraz's agent team (exhaustive checking); little compute needed.
- **Risks and what would kill it:**
  - Disorder and hydrogen positions will produce false flags.
  - The significance is modest.
  - Kill: the maintainers already flag these cases.

## Rejected as crowded
- **Thomson problem for small N:** N = 8 was proved by Kryvonos, Liehr and Taylor (arXiv 2609.22077, 18 Sep 2026) and separately by Tooby-Smith and Zughaid. N = 7 was given a Lean proof by Claude agents ([Vals AI, 28 Sep 2026](https://www.vals.ai/blogs/thomson-n7-lean-proof)).
- **Table of absolutely maximally entangled (AME) states:** three papers in Aug–Sep 2026 ([2608.01011](https://arxiv.org/abs/2608.01011), [2608.05781](https://arxiv.org/abs/2608.05781) (AI-assisted), 2609.11796).
- **Four-body central configurations:** four papers in 12 months (listed under candidate 3).
- **Costas arrays:** a GPU census at order 30 and of symmetric arrays of orders 37–42 (2608.28690, Aug 2026). Orders 32 and 33 have been open for more than 25 years, so the odds of a result in weeks are low.
- **AI-discovered materials (GNoME, MatterGen, A-Lab):**
  - Critics are already active.
  - Nature reportedly corrected the A-Lab paper in Jan 2026 *(unverified, secondary source)*.
  - An agent has already reproduced 111 published Quantum ESPRESSO (DFT) papers ([2604.12198](https://arxiv.org/abs/2604.12198)).
- **Multistationarity of small reaction networks:** active (2608.01116; *J Math Biol* 2025).
- **Navier–Stokes:** OpenAI's claim of Sept 2026 is under public dispute ([CNBC](https://www.cnbc.com/2026/09/09/openai-navier-stokes-math-problem-solved.html)).
- **SIC-POVMs:** not crowded, but specialist number theory. Exact solutions are known up to d = 57 and existence up to d = 196 ([2512.13201](https://arxiv.org/abs/2512.13201)), so new results would take more than weeks.

No files were written apart from the downloaded PDFs in the scratchpad, scratch/dl1.
