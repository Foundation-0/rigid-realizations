# A 12-vertex graph with 3,904 real realizations out of 6,180

Graph: the 12-vertex rigid graph with the most complex realizations, 6,180, integer code 1514126886600097825
(Capco et al., arXiv:1701.05500). Status in this repository's terms: **claimed**. A separately written program accepts
the certificate (VERIFIED).

## What is proved

1. At the exact squared lengths in `l12_certificate.json`, at least **3,904 of the 6,180** complex realizations are real.
   The certificate has 3,904 boxes. Each holds exactly one real solution with an invertible Jacobian, and the boxes are disjoint.
2. The graph has no triangle, so one bar (1, 2) is pinned, with length 1. Mirror images are then not automatic. Each
   one is a separate solution with its own box, so 3,904 is the full count of realizations found, modulo rotation and translation.
3. The complex count 6,180 is given by `scripts/laman_count.py` (`validate_laman_count.py --with-12`, saved in
   `../l2288-all-2288-real/outputs/validate_laman_count.out`).

This is a lower bound for these lengths. It is **not** a claim that all 6,180 can be real.

## Why this graph cannot raise the growth bound

- The graph contains no triangle and no rigid proper subgraph on three or more vertices. Copies can only be glued
  along a single bar, which adds 10 vertices per copy. With N real realizations the growth per vertex is N^(1/10).
- Even all 6,180 real would give 6180^(1/10) = 2.394, below the 2.4116 of the 11-vertex result. The certified 3,904 give 2.286.
- This is a computation from the graph and the gluing formula. The earlier figure of 2.442 per vertex used the
  triangle formula, which does not apply here.
- Numerically (not certified): near equal bar lengths, 588 of the 6,180 solutions run off to infinity and can never be real there.
  That caps the method used here at about 5,592 for this graph.
- Inference, not a separate certificate: adding one vertex of degree two to the 11-vertex graph doubles its count. So 12
  vertices already have a graph with 4,576 real realizations (2 x 2,288).

## Checkers and saved outputs

| Program | Method | Saved output |
|---|---|---|
| `scripts/verify_edge_frame_independent.py` | exact rationals, written separately; also checks the integer code and expected count | `outputs/verify_edge_frame_independent.out` |
| `scripts/verify_l12_exact.py` | exact rationals | `outputs/verify_l12_exact.out` |
| `scripts/verify_l12_arb.py` | interval Krawczyk test in ball arithmetic (needs python-flint) | `outputs/verify_l12_arb.out` |

Worst contraction bound: 0.159, against a limit of 1. Proof steps raise errors and behave the same under `python3 -O`.

## Rerun (from the repository root)

```bash
python3 -I -O rigid_realizations_l880_pr_bundle/scripts/verify_edge_frame_independent.py rigid_realizations_l880_pr_bundle/results/l12-3904-real/l12_certificate.json 1514126886600097825 3904   # about 55 s
python3 -I -O rigid_realizations_l880_pr_bundle/scripts/verify_l12_exact.py rigid_realizations_l880_pr_bundle/results/l12-3904-real/l12_certificate.json                                         # about 50 s
python3 -I -O rigid_realizations_l880_pr_bundle/scripts/verify_l12_arb.py rigid_realizations_l880_pr_bundle/results/l12-3904-real/l12_certificate.json 1514126886600097825                         # about 7 s
```

## Not verified

- The search path cannot be replayed step for step.
- Whether more than 3,904 can be made real is open.
- Nobody outside the project has checked the certificate.
