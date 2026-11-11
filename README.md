# rigid-realizations

**Can bar lengths be chosen so that all 880 complex realizations of the 10-vertex rigid framework are real? How many real realizations can minimally rigid graphs reach in the plane and in space?**

A framework is a set of points joined by bars of fixed length. A minimally rigid framework holds its shape, but flexes if any one bar is removed. In the plane its graph is called a Laman graph. With the lengths given, it can be built in only finitely many ways, not counting moving or turning it as a whole. These ways are the solutions of a system of polynomial equations. Counting them with complex numbers gives an upper bound, but only the real solutions are shapes that can actually be built.

For an 8-vertex graph (L136) and a 9-vertex graph (L344), bar lengths are known for which every solution is real. For the 10-vertex graph L880, which has 880 complex solutions, 860 had been certified in prior literature. This project certifies all 880 real realizations of L880, matching its complex bound (r_2(10) = c_2(10) = 880) and raising the asymptotic planar lower bound from 430^(1/7) ≈ 2.377989^n to 440^(1/7) ≈ 2.385811^n, along with certified baseline suites in 2D and 3D with zero-float verifiers.

Part of Foundation0's physics and mathematics work ([physics0](https://github.com/Foundation-0/physics0) and [math0](https://github.com/Foundation-0/math0)). It began in Foundation0's [scouting of 18-19 October 2026](https://github.com/Foundation-0/f0/tree/main/deep-fields). Related projects: [incentre-lattices](https://github.com/Foundation-0/incentre-lattices) (rigidity) and [point-charges](https://github.com/Foundation-0/point-charges) (certified counts of solutions).

## Results Table

| Graph | Dimension | Vertices (n) | Complex Count | Certified Real Count | Status | Notes |
|---|---|---|---|---|---|---|
| Prism_6 | 2D | 6 | 24 | 24 | claimed | Shared Heronian rational base triangle with L880 |
| L136 | 2D | 8 | 136 | 136 | claimed | All real certified in NOTE.md schema |
| L344 | 2D | 9 | 344 | 344 | claimed | All real certified at exact rational bar lengths of Bartzos et al. (p. 16) |
| L880 | 2D | 10 | 880 | 880 | claimed | All real certified (r_2(10) = c_2(10) = 880), raising asymptotic planar lower bound from 430^(1/7) ≈ 2.377989^n to 440^(1/7) ≈ 2.385811^n |
| L880 (Bartzos) | 2D | 10 | 880 | 868 | claimed | Unmodified rational bar lengths of Bartzos et al. |
| G160 | 3D | 8 | 160 | 132 | claimed | Unmodified rational bar lengths of Bartzos et al. |

### Glued Planar Lower Bounds (Claimed)
- r_2(11) >= 1,760 (Henneberg-I step on L880)
- r_2(12) >= 4,128 (L344 glued with Prism_6)
- r_2(13) >= 10,560 (L880 glued with Prism_6 along their shared Heronian rational triangle {2, 3, 7}, exceeding prior 10,320)

## Verification Instructions

All certificates are verified using pure-stdlib Python scripts operating on zero-float exact fractions.Fraction arithmetic.

To run the verifiers:

```bash
# Verify all 880 real realizations of L880 via interval Krawczyk method
python3 rigid_realizations_l880_pr_bundle/scripts/verify_l880_krawczyk.py

# Verify L880 using independent verification script
python3 rigid_realizations_l880_pr_bundle/scripts/verify_l880_independent.py

# Verify Laman condition and Capco properties
python3 rigid_realizations_l880_pr_bundle/scripts/verify_capco_laman.py

# Verify Bartzos baselines (L880 868 real and G160 132 real)
python3 rigid_realizations_l880_pr_bundle/scripts/verify_bartzos_baselines.py

# Certify deterministic planar suite (Prism_6: 24/24, L136: 136/136, L344: 344/344)
python3 scripts/certify_planar_suite.py

# Verify 2D NOTE.md schema certificates
python3 scripts/verify_note_schema_2d.py rigid_realizations_l880_pr_bundle/results/prism6_24_cert.json
python3 scripts/verify_note_schema_2d.py rigid_realizations_l880_pr_bundle/results/l136_136_cert.json
python3 scripts/verify_note_schema_2d.py rigid_realizations_l880_pr_bundle/results/l344_344_cert.json

# Run unit test suite
python3 -m unittest discover -s rigid_realizations_l880_pr_bundle/tests
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
| scripts/certify_planar_suite.py | Deterministic generator and certifier for Prism_6, L136, and L344 |
| notes/l880-880-and-868-diagnostics.md | Technical note on L880 parameters, fold walls, and Maple filter analysis |
| notes/g160-and-v11-13-findings.md | Handoff note for G160 and planar n=11..13 bounds |
| notes/literature-2018-2026.md | Literature audit through 2026 |
| AGENTS.md, CLAUDE.md | Guides for AI agents |
| .github/ | Pull request template and issue forms |

## Licence

MIT License.
