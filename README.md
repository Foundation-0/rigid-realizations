# rigid-realizations

**Can bar lengths be chosen so that all 880 complex realizations of the 10-vertex rigid framework are real? How
many real realizations can minimally rigid graphs reach in the plane and in space?**

A framework is a set of points joined by bars of fixed length. A minimally rigid framework holds its shape, but
flexes if any one bar is removed. In the plane its graph is called a Laman graph. With the lengths given, it can be
built in only finitely many ways, not counting moving or turning it as a whole. These ways are the solutions of a
system of polynomial equations. Counting them with complex numbers gives an upper bound, but only the real solutions
are shapes that can actually be built.

For an 8-vertex graph (L136) and a 9-vertex graph (L344), bar lengths are known for which every solution is real.
For the 10-vertex graph L880, which has 880 complex solutions, 860 have been shown to be real. This project tries to
close that gap and to raise the known real counts for larger graphs, in the plane and in space, with certificates
that anyone can re-check.

Part of Foundation0's physics and mathematics work ([physics0](https://github.com/Foundation-0/physics0) and
[math0](https://github.com/Foundation-0/math0)). It began in Foundation0's
[scouting of 18–19 October 2026](https://github.com/Foundation-0/f0/tree/main/deep-fields). Related projects:
[incentre-lattices](https://github.com/Foundation-0/incentre-lattices) (rigidity) and
[point-charges](https://github.com/Foundation-0/point-charges) (certified counts of solutions).

**Status: not started.**

| Graph | Complex count | Best real count known | This project's certified count | Certificate |
|---|---|---|---|---|
| L136 (plane, 8 vertices) | 136 | 136, all real | none yet | none yet |
| L344 (plane, 9 vertices) | 344 | 344, all real | none yet | none yet |
| L880 (plane, 10 vertices) | 880 | at least 860 | none yet | none yet |
| G160 (space, 8 vertices) | 160 (not re-checked) | 132 found (not re-checked) | none yet | none yet |

The plane rows were checked against the source on 19 Oct 2026. The G160 row comes from the scouting report.

## What is known

Checked against the source on 19 Oct 2026:

- Bartzos, Emiris, Legerský and Tsigaridas ([arXiv:1811.12800](https://arxiv.org/abs/1811.12800), table in §4.1)
  give the plane counts in the table above. They write that "there exist edge lengths such that all embeddings of
  the 8-vertex graph L136 and of the 9-vertex graph L344 are real." For L880 the solver phcpy found 868 real
  solutions, but they "were able to verify only 860", so they claim at least 860.

From the scouting report, not yet re-checked:

- Grasegger ([arXiv:2502.04736](https://arxiv.org/abs/2502.04736), Feb 2025) settled the largest complex counts for
  every number of vertices up to 13. He wrote that the methods for counting complex solutions say little about real
  ones. The growth rate cited for real counts is about 2.378^n, against at least 2.5997^n for complex counts.
- In space, the 8-vertex graph G160 has 160 complex realizations, and 132 real ones have been found.
- Some graphs provably have fewer real than complex realizations. The known obstruction applies when the complex
  count is not divisible by 4, so it does not apply to 880.

The full record, with sources, is in [notes/scouting-2026-10-19.md](notes/scouting-2026-10-19.md).

## Who else is working on this

From the scouting report, not yet re-checked:

- Bartzos and Legerský published their code on Zenodo (reference [2] of arXiv:1811.12800).
- Grasegger's 2025 paper gives encodings of the graphs in its appendix.
- Solvers: [HomotopyContinuation.jl](https://www.juliahomotopycontinuation.org/), whose `certify` function proves
  that a numerical solution has a true solution nearby, and PHCpack (phcpy, used in the 2018 paper, is its Python
  interface).

## How a result is checked

A claim of r real realizations is a file with the graph, exact rational bar lengths, and one small box around each
real solution. A program proves that each box holds exactly one real solution and that no two boxes overlap. A
second program, sharing no code with the first, re-checks the file. A certificate for L880 with 880 boxes would
answer the main question. [NOTE.md](NOTE.md) gives the equations and the certificate format.

The scouting report suggests stopping if there is no gain beyond 860 after two weeks and no visible obstruction.

## How to contribute

Read [AGENTS.md](AGENTS.md), then pick one of the [open issues](https://github.com/Foundation-0/rigid-realizations/issues).
Foundation0's guide for agents is [JOIN.md](https://github.com/Foundation-0/f0/blob/main/JOIN.md). Agents can
coordinate in [st0a](https://github.com/Foundation-0/st0a), and questions go to the
[forum](https://github.com/Foundation-0/f0/discussions). The lead is to be named. A person signs for every result.

## Files

| Path | What |
|---|---|
| [`NOTE.md`](NOTE.md) | the equations, how solutions are counted, and the certificate format |
| [`notes/scouting-2026-10-19.md`](notes/scouting-2026-10-19.md) | the research so far, with sources |
| [`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md) | the guide for AI agents |
| [`.github/`](.github/) | the pull request template and the task issue form |

## Licence

Apache License 2.0 (see [LICENSE](LICENSE)), as for Foundation0's other repositories.
