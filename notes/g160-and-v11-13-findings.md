# Technical Handoff Note: G160 (3D) and Planar Lower Bounds for n = 11, 12, 13

## 1. G160 (n = 8, 3D, Issue #3) Findings and Obstructions
- **Claimed baseline (bundle; pending independent verification)**: Claimed certificate for ≥ 132 of 160 real spatial realizations: 66 chiral branches at Bartzos et al.'s rational bar lengths via 80-bit rational base-height Krawczyk enclosure (`max kappa = 0.000499 < 1`).
- **Monodromy spectrum (numerical, not reproduced — no driver or data in repo)**: Numerical monodromy found 160 solutions, consistent with the known c_3(G160) = 160 (80 chiral branches). At Bartzos's point (bar lengths spanning [0.398, 11.993]), the 14 non-real chiral branches split bimodally:
  - 3 near-real conjugate pairs with |Im| in {0.4725, 1.0806, 1.3896}
  - 4 deep conjugate pairs with |Im| in {8.3880, 8.8343, 12.8176, 13.2829}
- **Negative / Dead-End Regimes (numerical exploration)**:
  - Near-unit perturbations (1 +/- 0.02) reach at most 96 / 160 real realizations.
  - Local Trust-Region LP climbs starting from Bartzos's chamber hit a strict fold wall at 132 / 160, where pushing the |Im| = 0.4725 pair real forces an existing real pair across a fold wall.
- **Recommended Next Step for > 132**: Start from an all-real 7-vertex G48 (48 / 48 real) configuration and perform controlled degenerate vertex-splitting / wide-range parameter monodromy across distant chambers.

## 2. Planar n = 11, 12, 13 lower bounds and L2288 (Issue #4)
- **Conditional glued planar lower bounds (≥; Prism_6 certificate not yet in repo; L880 certificate pending independent verification)**:
  - Gluing Prism_6 (all 24 real known from Borcea–Streinu 2004; no certificate in this repo) onto the claimed L880 certificate (880 / 880 if independently verified) along the shared Heronian base triangle {2, 3, 7} would give r_2(13) ≥ 10,560 once the Prism_6 certificate is committed and verified (the bound implied by Bartzos et al.'s formula is 6,880).
  - Similarly, gluing Prism_6 onto L344 along an L344 triangle would give r_2(12) ≥ 4,128 once a Prism_6 certificate exists on such a triangle (not the L880-base Prism_6 triangle in this repo's spec).
  - A Henneberg-I step on L880 gives r_2(11) ≥ 1,760 when the L880 certificate is accepted.
- **L2288 monodromy (numerical, not reproduced — no driver or data in repo)**:
  - For the maximal 11-vertex graph L2288 (c_2 = 2,288, GKT integer code 18120782205838348), exploratory runs used isotropic coordinates; there is no committed monodromy driver in this repository (`scripts/l2288_lib.py` is library-only).
  - Along the near-unit ray (0.002 * delta), numerically (uncertified) 1,582 / 2,288 appear real (with one pair closer than 10^-7).
  - At the well-separated 0.08 shell, numerically (uncertified) 1,404 / 2,288 appear real.
  - Scaling the multi-branch Trust-Region LP solver with higher precision near unit or multi-ray sampling may push beyond 1,760 on n = 11 (speculative).
