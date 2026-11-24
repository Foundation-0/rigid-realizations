# All 2,288 realizations of the 11-vertex graph L2288 are real

Graph: the 11-vertex rigid graph with integer code 18120782205838348 (Grasegger, Koutschan and Tsigaridas encoding,
as in the table of Capco et al., arXiv:1701.05500). It has 19 bars and the most complex realizations of any
11-vertex rigid graph in that table: 2,288.

Status in this repository's terms: **claimed**. In plain terms: a program written separately from the search accepts
the certificate (VERIFIED), and the repository's own two programs agree (REPRODUCED). Nobody outside the project has checked it.

## What is proved

1. **All 2,288 realizations are real at these bar lengths.** The 19 squared lengths are the exact fractions in
   `l2288_certificate.json` (also listed with decimals in `l2288_lengths.json`). Scale is fixed by bar (3, 9) of length 1.
   Every bar length is within 0.8% of 1. The triangle {3, 9, 10} is pinned: vertex 3 at the origin, vertex 9 at (1, 0),
   vertex 10 above the axis at exact rational coordinates.
2. **1,144 boxes, one solution each.** For each of 1,144 boxes (side 2^-35 in each of 16 coordinates) the checkers prove
   in exact or ball arithmetic that the box holds exactly one real solution and that the Jacobian is invertible there.
   The Krawczyk test does this. The worst contraction bound is 3.7e-6, against a limit of 1.
3. **The boxes are pairwise disjoint.** The smallest distance between two centres is 5.7e-3, against a box side of 2.9e-11.
4. **Mirror images double the count.** Reflecting a realization in the line through the pinned bar gives a different
   realization (the repository's convention, see NOTE.md). So 1,144 boxes give 2 x 1,144 = 2,288 real realizations
   modulo rotation and translation.
5. **The complex count is 2,288.** A generic choice of lengths gives exactly 2,288 complex realizations, by three
   implementations of the recursion of Capco et al.: `scripts/laman_count.py` (written from the paper with exact
   integers), `scripts/verify_capco_laman.py` (the repository's), and the authors' C++ library `lnumber`. They agree on
   this graph and on the 10-vertex graph (880). At the repository's own checks, `scripts/validate_laman_count.py` runs
   the second implementation against the maximal counts for 6 to 12 vertices (24, 56, 136, 344, 880, 2288, 6180), against
   the repository's implementation on 72 random rigid graphs, and on graphs that are not rigid.
   The `lnumber` run is a saved output only (`outputs/laman_crosscheck_lnumber.out`), because it needs that library built locally.
6. **So no further realization exists at these lengths.** The number of isolated complex solutions at any fixed
   lengths cannot exceed the generic count (parameter continuation, Morgan and Sommese 1989). This step is a cited
   theorem, not a computation made here. With 2,288 real ones found, r_2(L2288) = c_2(L2288) = 2,288.

## The growth bound

Gluing copies of a graph along a shared triangle gives, for a graph with N real realizations on 11 vertices,
at least 2 x (N/2)^k real realizations on 3 + 8k vertices (Bartzos, Emiris, Legersky and Tsigaridas, arXiv:1811.12800,
Theorem on gluing; the formula was checked against the TeX source of that paper). With N = 2,288 the growth per vertex is

    1144^(1/8) = 2.4116

| Source | Graph | Real realizations | Growth per vertex |
|---|---|---|---|
| Bartzos et al. 2018, verified | 10 vertices | 860 | 430^(1/7) = 2.3780 |
| this repository's L880 certificate | 10 vertices | 880 | 440^(1/7) = 2.3858 |
| this result | 11 vertices | 2,288 | 1144^(1/8) = 2.4116 |

A survey of February 2025 (Grasegger, arXiv:2502.04736) still quotes about 2.378 for real realizations.
Two web searches and three paper sources found no earlier report of 2,288 real realizations or of a bound above 2.378.
That is "no earlier report found", not a proof that none exists.
The bound is the published gluing theorem applied to this count. No gluing certificate was built here.

## Checkers and saved outputs

| Program | Method | Needs | Saved output |
|---|---|---|---|
| `scripts/verify_l2288_independent.py` | exact rationals, Newton operator, own preconditioner; also checks the integer code and the expected count | Python 3, NumPy | `outputs/verify_l2288_independent.out` |
| `scripts/verify_l2288_exact.py` | exact rationals, Newton operator | Python 3, NumPy | `outputs/verify_l2288_exact.out` |
| `scripts/verify_l2288_arb.py` | interval Krawczyk test in ball arithmetic | Python 3, NumPy, python-flint | `outputs/verify_l2288_arb.out` |
| `scripts/validate_laman_count.py` | the complex count (item 5) | Python 3 | `outputs/validate_laman_count.out` |

The first was written separately from the other two. All three use the same Krawczyk argument, so they are
independent as programs but not as mathematics. NumPy is used only to guess a preconditioner. The proofs are exact and do not
depend on that guess.

Proof steps raise errors (`SystemExit`), never a bare `assert`, so the results are the same under `python3 -O`.
`tests/test_l2288.py` checks that a shifted centre, a changed length, a duplicate box, a moved pin and a replaced
edge are each rejected, with and without `-O`.

## Rerun (from the repository root)

```bash
python3 -I -O rigid_realizations_l880_pr_bundle/scripts/verify_l2288_independent.py rigid_realizations_l880_pr_bundle/results/l2288-all-2288-real/l2288_certificate.json 18120782205838348 2288   # about 10 s
python3 -I rigid_realizations_l880_pr_bundle/scripts/verify_l2288_exact.py rigid_realizations_l880_pr_bundle/results/l2288-all-2288-real/l2288_certificate.json                              # about 10 s
python3 -I rigid_realizations_l880_pr_bundle/scripts/verify_l2288_arb.py rigid_realizations_l880_pr_bundle/results/l2288-all-2288-real/l2288_certificate.json                                # about 3 s
python3 -I -O rigid_realizations_l880_pr_bundle/scripts/validate_laman_count.py [--with-12]                                                                                                   # about 45 s, 100 s with 12
python3 -m unittest discover -s rigid_realizations_l880_pr_bundle/tests -v
```

## Certificate format

This certificate uses the format of the other bundle certificates, not the `boxes` format of NOTE.md. Keys: `edges`
(1-based pairs), `code` (integer code, checked), `sq_lengths` (exact squared lengths, in edge order), `pinned` (exact
coordinates of the triangle), `triangle`, `free_vertices` (order of the unknowns), `box_radius_exp2` (r = 2^-k),
`center_scale_exp2` (centres are integers divided by 2^m) and `centers` (1,144 integer vectors of length 16).
Edge lengths are the positive square roots of `sq_lengths`.

## Not verified

- The search that found the lengths cannot be replayed step for step, because one solver setting was changed during the run.
  The certificate does not depend on the search.
- The solver's count of 1,144 solutions was not confirmed by a separate completeness test. The complex count rests on the recursion.
- The parameter continuation step (item 6) and the published gluing theorem are cited, not recomputed.
- That 2,288 is the largest complex count of any 11-vertex rigid graph is Capco et al.'s computer result. It was not rechecked here.
  It would make 2,288 the largest possible real count on 11 vertices.
- The `lnumber` agreement is a saved run from a library built without OpenMP, not the stock package.
- No one outside the project has checked the certificate.

## Related

- Issue 4 (lower bounds for 11 to 13 vertices). Issue 20 (blind re-check of the L880 certificate): see `../l880-blind-recheck/`.
- The 12-vertex result: `../l12-3904-real/`.
