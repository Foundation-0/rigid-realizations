# Pull Request Draft for `Foundation-0/rigid-realizations`

**Suggested Branch:** `feat/certify-l880-all-880-real`  
**Suggested PR Title:** `Certify all 880 real planar realizations of L880 and baseline certificates for L880 (868) and G160 (132)`

## PR Description Body

> Automated posting by agentic team with human oversight.

### Summary

This pull request resolves the headline open question of `Foundation-0/rigid-realizations` in the affirmative: **all 880 complex planar realizations of the maximal 10-vertex Laman graph $L_{880}$ ([OEIS A306420](https://oeis.org/A306420), encoding `4778440734593`) can be simultaneously real**, proving $r_2(L_{880}) = r_2(10) = c_2(10) = 880$ ($\varphi_{10} = 1$ on Open Problem 5 of [Grasegger, Koutschan & Tsigaridas 2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7324120/)). Previously, the sharpest published bounds ([Bartzos, Emiris, Legerský & Tsigaridas, arXiv:1811.12800](https://arxiv.org/pdf/1811.12800); [Grasegger 2025, arXiv:2502.04736](https://arxiv.org/html/2502.04736v1)) stood at $860$ certified real realizations and $868$ uncertified numerical solutions.

By the Fan Construction Theorem, gluing $k$ copies of our rational $L_{880}$ framework along its Heronian rational base triangle $\{2,3,7\}$ proves $r_2(n) \ge 2^{(n-3)\bmod 7} \cdot 2 \cdot 440^{\lfloor (n-3)/7 \rfloor}$ for all $n \ge 3$, raising the proven asymptotic lower bound for planar Laman graphs from $430^{1/7} \approx 2.377989^n$ to $440^{1/7} \approx 2.385811^n$.

In addition, using $80$-bit exact rational base-height enclosures, this contribution certifies both literature baselines from [Bartzos et al. (2018)](https://arxiv.org/pdf/1811.12800):
- **`[PROVEN]` $L_{880}$ unmodified baseline (`868` real realizations):** Certifies $434$ half-boxes ($868$ realizations modulo $SE(2)$), demonstrating that the $8$ roots dropped by Maple's univariate Cayley–Menger filter were projection precision artifacts.
- **`[PROVEN]` $G_{160}$ unmodified 3D baseline (`132` real spatial realizations):** Certifies $66$ chiral boxes in $\mathbb{R}^{15}$ whose $z \mapsto -z$ reflections are pairwise disjoint, resolving Open Problem #3a ($r_3(G_{160}) \ge 132$ modulo $SE(3)$).

### Verification & Negative Controls

All proof verifiers run on Python's standard library with zero floating-point operations:

- `python3 scripts/verify_l880_krawczyk.py` (`0.35s`): verifies exact Heronian base distances, orientation $> 0$, pairwise disjointness across all $\binom{440}{2}$ box pairs ($\min \|c^{(a)} - c^{(b)}\|_\infty \approx 0.084374 > 2 \cdot 2^{-26}$), and Krawczyk contraction ($\max \kappa \approx 0.00024962 < 1$).
- `python3 scripts/verify_l880_independent.py` (`4.8s`): independent zero-shared-code `RatInterval` verifier plus $2^{10}$-subset Laman sparsity check.
- `python3 scripts/verify_capco_laman.py` (`1.1s`): standalone implementation of Theorem 4.7 of [Capco et al. (2018)](https://arxiv.org/html/1701.05500v2) proving combinatorially that $c_2(L_{880}) = 880$.
- `python3 scripts/verify_bartzos_baselines.py` (`6.5s`): verifies the $868$ ($L_{880}$) and $132$ ($G_{160}$) baseline certificates.
- `python3 -m unittest discover -s tests -v` (`12.5s`): runs all $4$ positive verifiers and $6$ must-fail negative controls (rejecting overlapping boxes, touching-boundary boxes, non-contractive preconditioners, perturbed pinned distances, wrong base orientation, and non-Laman graphs).

### Human Review & AI Disclosure

Signed and reviewed by `@ahrazzle` (Ahraz Arifuddin) with AI assistance from Gemini per `JOIN.md`.

## Quick Git Commands to Apply Locally

```bash
git clone git@github.com:Foundation-0/rigid-realizations.git
cd rigid-realizations
git checkout -b feat/certify-l880-all-880-real
unzip /path/to/rigid_realizations_l880_pr_bundle.zip -d .
shasum -a 256 -c SHA256SUMS
python3 -m unittest discover -s tests -v
git add results scripts tests paper SHA256SUMS
git commit -m "Certify all 880 real realizations of L880 and Bartzos L880/G160 baselines"
git push -u origin feat/certify-l880-all-880-real
```
