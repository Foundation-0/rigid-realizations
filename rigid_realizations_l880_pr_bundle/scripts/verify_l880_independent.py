#!/usr/bin/env python3
"""
Second Zero-Shared-Code Independent Exact Rational Interval Verifier for L880.
1. Exhaustively checks Laman's sparsity condition |E'| <= 2|V'| - 3 across all 2^10 vertex subsets.
2. Evaluates K(X) = c - Y*F(c) + (I - Y*DF(X))*(X - c) directly using an explicit exact rational
   interval arithmetic class `RatInterval` over `fractions.Fraction`, with zero shared arithmetic
   helpers from `verify_l880_krawczyk.py`.
"""
import json
from itertools import combinations
from pathlib import Path
import sys
import time
from fractions import Fraction

DEFAULT_CERT = Path(__file__).resolve().parent.parent / "results" / "l880-all-880-real" / "l880_certificate.json"


class RatInterval:
    __slots__ = ("lo", "hi")

    def __init__(self, lo: Fraction, hi: Fraction | None = None):
        if hi is None:
            hi = lo
        if lo > hi:
            raise ValueError("Inverted rational interval.")
        self.lo = lo
        self.hi = hi

    def __add__(self, other: "RatInterval") -> "RatInterval":
        return RatInterval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other: "RatInterval") -> "RatInterval":
        return RatInterval(self.lo - other.hi, self.hi - other.lo)

    def __neg__(self) -> "RatInterval":
        return RatInterval(-self.hi, -self.lo)

    def scale(self, c: Fraction) -> "RatInterval":
        if c >= 0:
            return RatInterval(c * self.lo, c * self.hi)
        return RatInterval(c * self.hi, c * self.lo)

    def strictly_inside(self, outer: "RatInterval") -> bool:
        return outer.lo < self.lo and self.hi < outer.hi


def verify_laman_graph(num_v: int, edges: list[tuple[int, int]]) -> int:
    if len(edges) != 2 * num_v - 3:
        raise ValueError("Edge count != 2|V| - 3.")
    if len({(min(u, v), max(u, v)) for u, v in edges}) != len(edges):
        raise ValueError("Duplicate edge detected.")
    for u, v in edges:
        if u == v or not (1 <= u <= num_v and 1 <= v <= num_v):
            raise ValueError("Self-loop or out-of-range vertex.")
    verts = list(range(1, num_v + 1))
    checked = 0
    for k in range(2, num_v):
        for sub in combinations(verts, k):
            checked += 1
            s = set(sub)
            cnt = sum(1 for (u, v) in edges if u in s and v in s)
            if cnt > 2 * k - 3:
                raise ValueError(f"Laman subgraph inequality violated on {sub}: {cnt} > {2*k - 3}")
    return checked


def run_independent_box_verification(cert_path: str | Path = DEFAULT_CERT) -> dict:
    t0 = time.time()
    with open(cert_path, "r", encoding="utf-8") as f:
        cert = json.load(f)

    edges = [tuple(e) for e in cert["edges"]]
    checked_subsets = verify_laman_graph(cert["num_vertices"], edges)

    rem_idx = cert["remaining_edge_indices"]
    free_v = cert["free_vertices"]
    pos_of_v = {v: k for k, v in enumerate(free_v)}

    lengths = [Fraction(s) for s in cert["edge_lengths"]]
    if any(L <= 0 for L in lengths):
        raise ValueError("All edge lengths must be strictly positive.")
    sq_lengths = [L * L for L in lengths]
    pin = {int(k): (Fraction(v[0]), Fraction(v[1])) for k, v in cert["pinned_vertices"].items()}

    for idx in (3, 4, 6):
        u, v = edges[idx]
        if (pin[u][0] - pin[v][0]) ** 2 + (pin[u][1] - pin[v][1]) ** 2 != sq_lengths[idx]:
            raise ValueError("Pinned triangle distance mismatch.")
    area2 = (pin[2][0] - pin[7][0]) * (pin[3][1] - pin[7][1]) - (pin[2][1] - pin[7][1]) * (pin[3][0] - pin[7][0])
    if area2 <= 0:
        raise ValueError("Pinned triangle orientation must be strictly positive.")

    c_den = Fraction(1, 1 << cert["center_scale_exp2"])
    y_den = Fraction(1, 1 << cert["precond_scale_exp2"])
    rad = Fraction(1, 1 << cert["box_radius_exp2"])

    boxes_centers = [[Fraction(val) * c_den for val in row] for row in cert["centers_num"]]
    if len(boxes_centers) != 440:
        raise ValueError("Expected 440 box centers.")

    for i in range(440):
        ci = boxes_centers[i]
        for j in range(i + 1, 440):
            cj = boxes_centers[j]
            if not any(ci[d] + rad < cj[d] - rad or cj[d] + rad < ci[d] - rad for d in range(14)):
                raise ValueError(f"Boxes {i} and {j} intersect!")

    worst_row_norm = Fraction(0)
    worst_width_ratio = Fraction(0)

    for b_idx in range(440):
        c = boxes_centers[b_idx]
        X_box = [RatInterval(c[d] - rad, c[d] + rad) for d in range(14)]
        Y = [[Fraction(val) * y_den for val in row] for row in cert["preconds_num"][b_idx]]

        F_c = []
        DF_box = [[RatInterval(Fraction(0)) for _ in range(14)] for _ in range(14)]

        for eq_i, e_idx in enumerate(rem_idx):
            u, v = edges[e_idx]
            if u in pos_of_v:
                iu = pos_of_v[u]
                xu_c, yu_c = c[2 * iu], c[2 * iu + 1]
                xu_I, yu_I = X_box[2 * iu], X_box[2 * iu + 1]
            else:
                xu_c, yu_c = pin[u]
                xu_I, yu_I = RatInterval(xu_c), RatInterval(yu_c)

            if v in pos_of_v:
                iv = pos_of_v[v]
                xv_c, yv_c = c[2 * iv], c[2 * iv + 1]
                xv_I, yv_I = X_box[2 * iv], X_box[2 * iv + 1]
            else:
                xv_c, yv_c = pin[v]
                xv_I, yv_I = RatInterval(xv_c), RatInterval(yv_c)

            F_c.append((xu_c - xv_c) ** 2 + (yu_c - yv_c) ** 2 - sq_lengths[e_idx])
            dx_I = (xu_I - xv_I).scale(Fraction(2))
            dy_I = (yu_I - yv_I).scale(Fraction(2))

            if u in pos_of_v:
                iu = pos_of_v[u]
                DF_box[eq_i][2 * iu] = dx_I
                DF_box[eq_i][2 * iu + 1] = dy_I
            if v in pos_of_v:
                iv = pos_of_v[v]
                DF_box[eq_i][2 * iv] = -dx_I
                DF_box[eq_i][2 * iv + 1] = -dy_I

        for i in range(14):
            shift_c = c[i] - sum((Y[i][k] * F_c[k] for k in range(14)), Fraction(0))
            k_int = RatInterval(shift_c)
            row_norm = Fraction(0)
            for j in range(14):
                acc = RatInterval(Fraction(1 if i == j else 0))
                for k in range(14):
                    y_ik = Y[i][k]
                    if y_ik != 0 and (DF_box[k][j].lo != 0 or DF_box[k][j].hi != 0):
                        acc = acc - DF_box[k][j].scale(y_ik)
                mag = max(abs(acc.lo), abs(acc.hi))
                row_norm += mag
                k_int = k_int + RatInterval(-mag * rad, mag * rad)

            if row_norm >= 1:
                raise ValueError(f"Non-contractive row norm {row_norm} >= 1 at box {b_idx} row {i}")
            if not k_int.strictly_inside(X_box[i]):
                raise ValueError(f"Box {b_idx} coord {i}: Krawczyk interval not strictly inside X_box!")
            if row_norm > worst_row_norm:
                worst_row_norm = row_norm
            half_w = max(k_int.hi - c[i], c[i] - k_int.lo)
            if half_w / rad > worst_width_ratio:
                worst_width_ratio = half_w / rad

    return {
        "laman_subgraph_subsets_checked": checked_subsets,
        "independent_interval_boxes_verified": 440,
        "total_SE2_real_realizations": 880,
        "worst_contraction_row_norm": round(float(worst_row_norm), 8),
        "worst_interval_inclusion_ratio": round(float(worst_width_ratio), 8),
        "elapsed_seconds": round(time.time() - t0, 3),
    }


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CERT
    out = run_independent_box_verification(target)
    print("SECOND INDEPENDENT EXACT INTERVAL VERIFIER PASSED!")
    for k, v in out.items():
        print(f"  {k}: {v}")
