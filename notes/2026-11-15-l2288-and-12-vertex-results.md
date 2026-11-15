# 15 November 2026: the 11-vertex and 12-vertex results, and two gaps in the L880 code

This note records what a separate review found when it followed the repository's open target for 11 vertices
(issue 4). It adds to `g160-and-v11-13-findings.md` and does not replace it. Marks: **[F]** fact checked by a
program, **[I]** inference, **[N]** numerical, not certified.

## 11 vertices: all 2,288 realizations are real

- [F] For the 11-vertex graph with integer code 18120782205838348 there are 19 exact squared bar lengths at which all
  2,288 complex realizations are real. The certificate, the proof and the checkers are in
  `rigid_realizations_l880_pr_bundle/results/l2288-all-2288-real/` (read `PROOF.md` there first).
- [F] Three checkers accept it. One was written separately from the other two. The complex count 2,288 comes from three
  implementations of the recursion of Capco et al.
- [F] Gluing copies along a triangle gives growth per vertex of 1144^(1/8) = 2.4116, against 430^(1/7) = 2.3780
  published and 440^(1/7) = 2.3858 from the L880 certificate.
- [F] The graph has no vertex of degree two. None of its 16 reductions by the second Henneberg step is L880.
  The figure 1,760 in the existing note and in the README is the bound 2 x 880 for a different 11-vertex graph, one
  built from L880 by the simplest vertex step. It is not the count of this graph.
- [N] The earlier exploratory counts in the existing note, 1,582 near the unit lengths and 1,404 on the 0.08 shell, are
  lower than what the push reached from near-unit lengths. The push went through 1,532, 1,932, 2,180 and 2,280 before 2,288.

## 12 vertices: 3,904 of 6,180 real, and why this graph cannot raise the bound

- [F] For the 12-vertex graph with the most complex realizations, 6,180 (code 1514126886600097825), the same method reached
  a point with 3,904 real realizations. Certificate and checkers: `results/l12-3904-real/`. Three checkers accept it.
- [F] This graph has no triangle and no rigid proper subgraph on three or more vertices. Copies can only be glued along
  one bar, which adds 10 vertices per copy. The growth per vertex is then N^(1/10) for N real realizations.
- [F] All 6,180 real would give 6180^(1/10) = 2.394, below 2.4116. The certified 3,904 give 2.286. So this graph cannot
  raise the bound, however many of its realizations are made real.
- [N] Near equal lengths, 588 of the 6,180 solutions run off to infinity. That caps the near-unit method at about 5,592.
- [I] A 12-vertex graph with a triangle and a large count is the open target for raising the bound further.

## Two gaps in the L880 code

- [F] `scripts/discovery/lp_push_880.py` loads `fast_climb_best.npz` (line 6). No committed script writes that file.
  The push from 868 to 880 cannot be rerun from the repository as it stands.
- [F] The code uses a step fraction of 0.25 (line 130). The note `l880-880-and-868-diagnostics.md` says 0.30.
  Which value found the certificate is not recorded.

## Checks that were added

- `scripts/laman_count.py` is a second implementation of the complex count, validated by `scripts/validate_laman_count.py`.
- `scripts/verify_l880_blind_recheck.py` is a standard-library re-check of the L880 certificate, for issue 20.
  See `results/l880-blind-recheck/RESULT.md`.

## Not verified

The search paths cannot be replayed step for step. The published theorems behind the recursion and the gluing formula
were applied, not re-derived. That 2,288 and 6,180 are the largest complex counts for 11 and 12 vertices is the
published table's claim and was not rechecked.
