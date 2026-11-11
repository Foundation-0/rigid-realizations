# rigid-realizations

**Can bar lengths be chosen so that all 880 complex realizations of the 10-vertex rigid framework are real? How many real realizations can minimally rigid graphs reach in the plane and in space?**

A framework is a set of points joined by bars of fixed length. A minimally rigid framework holds its shape, but flexes if any one bar is removed. In the plane its graph is called a Laman graph. With the lengths given, it can be built in only finitely many ways, not counting moving or turning it as a whole. These ways are the solutions of a system of polynomial equations. Counting them with complex numbers gives an upper bound, but only the real solutions are shapes that can actually be built.

For an 8-vertex graph (L136) and a 9-vertex graph (L344), the literature gives bar lengths for which every solution is real (Bartzos et al. 2018). For the 10-vertex graph L880, which has 880 complex solutions, prior literature had Maple-certified r_2(L880) ≥ 860 and reported 868 solutions numerically via homotopy continuation. This project claims (pending independent verification) a certificate that all 880 realizations of L880 are real (r_2(10) = c_2(10) = 880), which would raise the asymptotic lower bound for real planar realizations from 430^(1/7) ≈ 2.377989^n to 440^(1/7) ≈ 2.385811^n. Committed baseline certificates at Bartzos et al.'s published lengths support r_2 ≥ 868 in the plane and r_3 ≥ 132 for G160 in 3D (also pending independent verification), checked by zero-float verifiers in the L880 bundle.

Part of Foundation0's physics and mathematics work ([physics0](https://github.com/Foundation-0/physics0) and [math0](https://github.com/Foundation-0/math0)). It began in Foundation0's [scouting of 18-19 October 2026](https://github.com/Foundation-0/f0/tree/main/deep-fields). Related projects: [incentre-lattices](https://github.com/Foundation-0/incentre-lattices) (rigidity) and [point-charges](https://github.com/Foundation-0/point-charges) (certified counts of solutions).

## Results Table

| Graph | Dimension | Vertices (n) | Complex Count | Real count | Status | Notes |
|---|---|---|---|---|---|---|
| Prism_6 | 2D | 6 | 24 | 24 (all-real known: Borcea–Streinu 2004) | certificate not yet in repo | New lengths sharing L880's base triangle |
| L136 | 2D | 8 | 136 | 136 (known: Bartzos et al. 2018) | certificate not yet in repo | New lengths, not Bartzos's |
| L344 | 2D | 9 | 344 | 344 (known: Bartzos et al. 2018) | certificate not yet in repo | Bartzos et al.'s lengths |
| L880 | 2D | 10 | 880 | 880 | claimed (pending independent verification) | Computer-assisted certificate in bundle; φ_10 = 1 if verified |
| L880 (Bartzos) | 2D | 10 | 880 | ≥ 868 | claimed (pending independent verification) | Certified lower bound at unmodified Bartzos et al. lengths |
| G160 | 3D | 8 | 160 | ≥ 132 | claimed (pending independent verification) | Certified lower bound at unmodified Bartzos et al. lengths |

### Glued Planar Lower Bounds (Claimed)
- r_2(11) >= 1,760 (Henneberg-I step on L880; conditional on L880 certificate)
- r_2(12) >= 4,128 (L344 glued with Prism_6); needs the Prism_6 certificate
- r_2(13) >= 10,560 (L880 glued with Prism_6 along the shared triangle {2, 3, 7}; needs the Prism_6 certificate. The bound implied by Bartzos et al.'s formula is 6,880.)

## Verification Instructions

Certificates in `rigid_realizations_l880_pr_bundle/` are checked using pure-stdlib Python scripts operating on zero-float `fractions.Fraction` arithmetic.

To run the verifiers:

```bash
# Verify all 880 real realizations of L880 via interval Krawczyk method
python3 rigid_realizations_l880_pr_bundle/scripts/verify_l880_krawczyk.py

# Verify L880 using independent verification script
python3 rigid_realizations_l880_pr_bundle/scripts/verify_l880_independent.py

# Verify Laman condition and Capco properties
python3 rigid_realizations_l880_pr_bundle/scripts/verify_capco_laman.py

# Verify Bartzos baselines (L880 ≥ 868 and G160 ≥ 132 certified lower bounds)
python3 rigid_realizations_l880_pr_bundle/scripts/verify_bartzos_baselines.py

# For Prism_6, L136, L344: verify each results/{name}_{count}_cert.json when present; exit 1 if any are missing
python3 scripts/certify_planar_suite.py

# Integrity manifests (from repository root)
sha256sum -c SHA256SUMS
sha256sum -c rigid_realizations_l880_pr_bundle/SHA256SUMS

# Run unit tests (repository root scripts + bundle verifiers)
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s rigid_realizations_l880_pr_bundle/tests -v
```

## What is known

- Bartzos, Emiris, Legersky and Tsigaridas (arXiv:1811.12800)
- Grasegger (arXiv:2502.04736)

## Files

| Path | What |
|---|---|
| NOTE.md | Equations, solution counting, and certificate format |
| rigid_realizations_l880_pr_bundle/ | Complete L880 bundle with paper, results, scripts, and tests |
| scripts/verify_note_schema_2d.py | Pure-stdlib Krawczyk verifier for 2D NOTE.md JSON certificates |
| scripts/certify_planar_suite.py | For Prism_6, L136, and L344: verify each `rigid_realizations_l880_pr_bundle/results/{name}_{count}_cert.json` when present; exit nonzero if any expected file is missing (does not write JSON; none committed). Expected Prism_6 path: `prism_6_24_cert.json`. |
| notes/l880-880-and-868-diagnostics.md | Technical note on L880 parameters, fold walls, and Maple filter analysis |
| notes/g160-and-v11-13-findings.md | Handoff note for G160 and planar n=11..13 bounds |
| notes/literature-2018-2026.md | Literature audit through 2026 |
| AGENTS.md, CLAUDE.md | Guides for AI agents |
| .github/ | Pull request template and issue forms |

## Licence

Apache License 2.0 (see [LICENSE](LICENSE)), as for Foundation0's other repositories.
