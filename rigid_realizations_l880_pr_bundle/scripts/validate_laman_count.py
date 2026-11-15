"""Validation of laman_count.py, the second implementation of the complex count (Capco et al., arXiv:1701.05500).

Checks, each reported on its own line. Any failure raises SystemExit, so the result is the same under python3 -O.
  1. The maximal graphs for 6 to 11 vertices (12 with --with-12, about one minute) give 24, 56, 136, 344, 880, 2288
     (6180 for 12). The graphs are given by integer codes in the convention of laman_count.decode.
  2. The 10-vertex and 11-vertex graphs of the L880 and L2288 certificates, by their published integer codes.
  3. Graphs built only by the simplest vertex step give 2^(n-2) for 3 to 10 vertices.
  4. Agreement with the repository's own implementation (verify_capco_laman.compute_c2) on the maximal graphs up
     to 11 vertices and on 72 random rigid graphs with 4 to 9 vertices.
  5. Graphs that are not rigid give 0 or raise an error, not a count.
Usage: python3 -I validate_laman_count.py [--with-12]
"""
import os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laman_count import decode, encode, is_laman, laman_number
from verify_capco_laman import compute_c2


def die(msg):
    raise SystemExit("FAIL: " + msg)


# Maximal graphs, one per number of vertices, in the convention of laman_count.decode
MAX_CODES = {6: 29327, 7: 1714767, 8: 106235230, 9: 22097893737, 10: 9502097324865,
             11: 18366593399180321, 12: 1514126886600097825}
EXPECT = {6: 24, 7: 56, 8: 136, 9: 344, 10: 880, 11: 2288, 12: 6180}
CERT_CODES = {4778440734593: 880, 18120782205838348: 2288}


def henneberg(n, rng):
    E = {(0, 1)}
    k = 2
    while k < n:
        V = list(range(k))
        if rng.random() < 0.5 or len(E) < 2:
            u, v = rng.sample(V, 2)
            E |= {(min(u, k), max(u, k)), (min(v, k), max(v, k))}
        else:
            u, v = rng.choice(sorted(E))
            w = rng.choice([x for x in V if x not in (u, v)])
            E.discard((u, v))
            E |= {(u, k), (v, k), (w, k)}
        k += 1
    return sorted(E)


def one_based(e):
    return [(a + 1, b + 1) for a, b in e]


top = 12 if "--with-12" in sys.argv else 11
maximal_edges = {}
for n in range(6, top + 1):
    nn, e = decode(MAX_CODES[n])
    t = time.time()
    if nn != n or not is_laman(n, e): die(f"maximal graph for {n} vertices is not a rigid graph on {n} vertices")
    got = laman_number(e)
    if got != EXPECT[n]: die(f"n={n}: got {got}, expected {EXPECT[n]}")
    maximal_edges[n] = e
    print(f"1. maximal graph, {n} vertices: {got} (expected {EXPECT[n]})")

for code, want in CERT_CODES.items():
    n, e = decode(code)
    if not is_laman(n, e): die(f"code {code} is not rigid")
    got = laman_number(e)
    if got != want: die(f"code {code}: got {got}, expected {want}")
    print(f"2. code {code}: {n} vertices, {got} (expected {want})")

for n in range(3, 11):
    e = [(0, 1)] + [(i, j) for j in range(2, n) for i in (j - 2, j - 1)]
    got = laman_number(e)
    if got != 2 ** (n - 2): die(f"simplest-step graph on {n} vertices: got {got}")
print("3. graphs built by the simplest step alone give 2^(n-2) for n = 3..10")

for n, e in sorted(maximal_edges.items()):
    if n <= 11 and compute_c2(one_based(e)) != EXPECT[n]: die(f"repository implementation disagrees at n={n}")
rng = random.Random(7)
cnt = 0
for n in range(4, 10):
    for _ in range(12):
        e = henneberg(n, rng)
        if not is_laman(n, e): die("generator produced a graph that is not rigid")
        a, b = laman_number(e), compute_c2(one_based(e))
        if a != b: die(f"implementations disagree on {e}: {a} against {b}")
        cnt += 1
print(f"4. agrees with verify_capco_laman.compute_c2 on the maximal graphs up to 11 vertices and on {cnt} random rigid graphs")

n, e = decode(4778440734593)
try:
    r = laman_number(e[:-1])
except ValueError:
    r = "error"
if r not in (0, "error"): die("a graph with one bar removed gave a count")
r2 = laman_number(e + [(5, 9)])
r3 = laman_number([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4)])
if r2 != 0 or r3 != 0: die("an overbraced graph gave a nonzero count")
print(f"5. one bar removed -> {r}; one bar added -> {r2}; K4 with a pendant bar -> {r3}")
print("ALL CHECKS PASSED")
