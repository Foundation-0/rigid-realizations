# Equations and certificates

This note sets out the equations this project solves and the file format for a claimed count of real
realizations. No certificate exists yet.

## The equations in the plane

A graph G has vertices 1, …, n and a set E of edges (the bars). Each edge ij has a length λ_ij > 0. A realization
places points p_1, …, p_n in the plane so that

    |p_i − p_j|² = λ_ij²    for every edge ij in E.

Moving or turning a realization gives another one. To count each shape once, pin one edge uv:

    p_u = (0, 0),    p_v = (λ_uv, 0).

The unknowns are the 2(n − 2) coordinates of the other vertices. A minimally rigid graph in the plane has 2n − 3
edges, so after pinning there are 2n − 4 equations, as many as there are unknowns. For generic lengths the system has
finitely many solutions.

Mirror images count separately: reflecting a solution in the line through the pinned edge gives another solution.
When reproducing the counts of [arXiv:1811.12800](https://arxiv.org/abs/1811.12800), check that the paper counts the
same way.

## The equations in space

A minimally rigid graph in space has 3n − 6 edges. Pin a triangle of edges uvw: p_u at the origin,
p_v = (λ_uv, 0, 0), and p_w in the plane z = 0 with positive y. The coordinates of p_w follow from the three lengths.
Its y-coordinate may be a square root, which the checker encloses in an interval. The 3(n − 3) coordinates of the
other vertices then satisfy 3n − 9 equations, again as many as there are unknowns. Mirror images in the plane z = 0
count separately. A certificate may remove the motions another way if it says how.

## What is counted

- c(G) is the number of complex solutions for generic lengths. For L880 it is 880.
- r(G, λ) is the number of real solutions for the lengths λ. Each one is a shape that can be built.

A solution is non-degenerate when the Jacobian matrix of the system (its matrix of partial derivatives) is
invertible there. For any choice of lengths, the number of non-degenerate solutions is at most c(G). So a
certificate with c(G) non-degenerate real solutions shows that the real count reaches the complex count.

## Certificate format

One JSON file per claim, in a folder `certificates/`. A complete example for the triangle with sides 6, 5 and 5,
which has two real realizations, (3, 4) and (3, −4) for the third vertex:

```json
{
  "graph": "triangle",
  "dimension": 2,
  "n": 3,
  "edges": [[1, 2], [1, 3], [2, 3]],
  "lengths": ["6", "5", "5"],
  "pinned": [1, 2],
  "unknowns": ["x3", "y3"],
  "boxes": [
    [["29/10", "31/10"], ["39/10", "41/10"]],
    [["29/10", "31/10"], ["-41/10", "-39/10"]]
  ],
  "complex_count": 2,
  "claimed_real_count": 2,
  "made_by": "worked example in NOTE.md"
}
```

- `lengths[i]` is the length of `edges[i]`, an exact rational written as an integer or as "p/q". The equations then
  have rational coefficients.
- `pinned` names the pinned edge in the plane, or the pinned triangle in space, as described above.
- `unknowns` lists the free coordinates. Each box gives one interval per unknown, in the same order, with rational
  end points.
- The checker proves, for each box, that it holds exactly one solution and that the Jacobian is invertible on it.
  The Krawczyk test does this: it is an interval-arithmetic test that, when it passes, proves a box contains exactly
  one solution. The test runs over real intervals, so the solution it finds is real.
- The boxes must not overlap, so no solution is counted twice.
- `claimed_real_count` is the number of boxes. It is a lower bound on r(G, λ).
- `made_by` names the program with its version or commit, the person and any agent, and the date.

A second program, sharing no code with the one that made the file, re-checks every certificate before a count is
claimed. [point-charges](https://github.com/Foundation-0/point-charges) uses the same scheme for its certificates.
