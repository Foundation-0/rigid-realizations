# Re-check of the L880 certificate with a program that shares no code (issue 20)

Program: `scripts/verify_l880_blind_recheck.py`. Python standard library only. It imports nothing from the
repository's verifiers and shares no code with them. Saved output: `verify_l880_blind_recheck.out`.
Date: 15 November 2026. Status stays **claimed**. This is not peer review, replication or formal verification.

## What it uses from the certificate

Only the edge list, the 17 exact rational lengths, the pinned triangle and the 440 box centres in
`../l880-all-880-real/l880_certificate.json`. It does not use the repository's preconditioner matrices.

## What was checked, and what passed

Each line below is a separate check. Any failure stops the program with a nonzero exit status, also under `python3 -O`.

| Check | Result |
|---|---|
| The graph has 17 edges, no repeated edge, and satisfies the Laman count on every subset of vertices | passed (the graph has integer code 4778440734593) |
| The three pinned vertices satisfy their three bar equations exactly, vertex 7 is at the origin, vertex 2 on the positive x-axis and vertex 3 above it | passed |
| 14 equations in 14 unknowns | passed |
| Each of the 440 boxes (half-width 2^-26) holds exactly one real solution with an invertible Jacobian, by the Newton-operator argument in exact rational arithmetic | passed, worst contraction bound 2.493e-4 against a limit of 1 |
| The boxes are pairwise disjoint | passed, smallest centre distance 0.0844 against a box side of 3.0e-8 |
| The counts claimed in the file (440 boxes, 880 real, 880 complex) match the boxes given | passed |

So 440 boxes give 440 real realizations with vertex 3 above the axis. Their mirror images give 880 modulo rotation and translation.

## Rerun

```bash
python3 -I -O rigid_realizations_l880_pr_bundle/scripts/verify_l880_blind_recheck.py rigid_realizations_l880_pr_bundle/results/l880-all-880-real/l880_certificate.json   # about 2 s
python3 -m unittest discover -s rigid_realizations_l880_pr_bundle/tests -p "test_l880_blind*.py" -v
```

The tests show that a shifted centre, a changed length, a duplicate box, a moved pin, a replaced edge and a wrong
claimed count are each rejected, with and without `-O`.

## What could still be wrong

- This checks that the boxes hold real solutions. That the generic complex count is 880 is a separate fact. It rests on the
  second implementation of the recursion (`scripts/laman_count.py`, three implementations agree, see
  `../l2288-all-2288-real/PROOF.md` item 5) and on the cited parameter continuation theorem.
- Both this program and the repository's verifier use the Krawczyk argument. They are different programs, not different mathematics.
- A float guess is used for the preconditioner. It cannot make a wrong box pass, because every bound is then proved in exact arithmetic.
- The program was written by the review team, which had also read the repository. It is not "blind" in the sense of never having seen the repository's code.
- Nobody outside the project has run it.
