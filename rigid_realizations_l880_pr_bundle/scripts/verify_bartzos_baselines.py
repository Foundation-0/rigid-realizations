#!/usr/bin/env python3
"""
Exact Rational Interval Krawczyk Verifier for Literature Baselines (Bartzos et al., arXiv:1811.12800):
  1. L880 unmodified published edge lengths (p. 16): certifies all 868 real planar realizations
     (434 half-boxes + reflection), resolving the 8 Maple triangle-inequality projection artifacts.
  2. G160 unmodified published 3D edge lengths (p. 19): certifies all 132 real spatial realizations
     (66 chiral boxes + z-reflection, pairwise disjoint in R^15), resolving Open Problem #3a of
     Foundation-0/rigid-realizations.

Uses ONLY Python's standard library (`json`, `fractions.Fraction`, `pathlib`, `sys`).
"""
import json
from pathlib import Path
import sys
import time
from fractions import Fraction

from verify_l880_independent import RatInterval

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_B868 = ROOT / "results" / "l880-bartzos-868" / "l880_bartzos868_certificate.json"
DEFAULT_G132 = ROOT / "results" / "g160-bartzos-132" / "g160_bartzos132_certificate.json"


def _sq_iv(iv: RatInterval) -> RatInterval:
    vals = (iv.lo * iv.lo, iv.hi * iv.hi)
    lo_s = Fraction(0) if (iv.lo <= 0 <= iv.hi) else min(vals)
    return RatInterval(lo_s, max(vals))


def verify_bartzos_l880_868(cert_path: str | Path = DEFAULT_B868) -> dict:
    t0 = time.time()
    with open(cert_path, "r", encoding="utf-8") as fh:
        cert = json.load(fh)

    edges = [tuple(e) for e in cert["edges"]]
    rem_idx = cert["remaining_edge_indices"]
    free_v = cert["free_vertices"]
    v_map = {v: i for i, v in enumerate(free_v)}

    len_q = [Fraction(s) for s in cert["edge_lengths"]]
    if any(L <= 0 for L in len_q):
        raise ValueError("Non-positive edge length.")
    sq_q = [L * L for L in len_q]

    # Verify exact rational enclosure of pinned base triangle (7, 2, 3) including irrational height y3
    x7 = Fraction(cert["pinned_x"]["7"])
    x2 = Fraction(cert["pinned_x"]["2"])
    x3 = Fraction(cert["pinned_x"]["3"])
    y3_lo, y3_hi = (Fraction(s) for s in cert["pinned_y_interval"]["3"])
    if x7 != 0 or x2 != len_q[4]:
        raise ValueError("Pinned x7 or x2 does not match edge (2,7).")
    expected_x3 = (sq_q[4] + sq_q[6] - sq_q[3]) / (2 * len_q[4])
    if x3 != expected_x3:
        raise ValueError("Pinned x3 does not match exact cosine-law coordinate.")
    y3_sq_exact = sq_q[6] - x3 * x3
    if not (y3_lo > 0 and y3_lo * y3_lo <= y3_sq_exact <= y3_hi * y3_hi):
        raise ValueError("Pinned y3 interval does not rigorously enclose sqrt(l_{3,7}^2 - x_3^2) > 0!")

    pin_x_I = {7: RatInterval(x7), 2: RatInterval(x2), 3: RatInterval(x3)}
    pin_y_I = {7: RatInterval(Fraction(0)), 2: RatInterval(Fraction(0)), 3: RatInterval(y3_lo, y3_hi)}

    c_den = Fraction(1, 1 << int(cert["center_scale_exp2"]))
    y_den = Fraction(1, 1 << int(cert["precond_scale_exp2"]))
    rad = Fraction(1, 1 << int(cert["box_radius_exp2"]))

    centers = [[Fraction(v) * c_den for v in row] for row in cert["centers_num"]]
    preconds = cert["preconds_num"]
    if len(centers) != 434 or len(preconds) != 434:
        raise ValueError("Expected 434 boxes for Bartzos L880.")

    for i in range(434):
        for j in range(i + 1, 434):
            if not any(abs(centers[i][d] - centers[j][d]) > 2 * rad for d in range(14)):
                raise ValueError(f"Bartzos L880 boxes {i} and {j} overlap!")

    max_kappa = Fraction(0)
    max_ratio = Fraction(0)
    for b_i in range(434):
        c = centers[b_i]
        X_box = [RatInterval(c[d] - rad, c[d] + rad) for d in range(14)]
        Ym = [[Fraction(v) * y_den for v in row] for row in preconds[b_i]]

        F_c_I = []
        DF_box = [[RatInterval(Fraction(0)) for _ in range(14)] for _ in range(14)]
        for eq_i, e_i in enumerate(rem_idx):
            u, v = edges[e_i]
            if u in v_map:
                iu = v_map[u]
                xu_c, yu_c = RatInterval(c[2 * iu]), RatInterval(c[2 * iu + 1])
                xu_I, yu_I = X_box[2 * iu], X_box[2 * iu + 1]
            else:
                xu_c, yu_c = pin_x_I[u], pin_y_I[u]
                xu_I, yu_I = pin_x_I[u], pin_y_I[u]
            if v in v_map:
                iv = v_map[v]
                xv_c, yv_c = RatInterval(c[2 * iv]), RatInterval(c[2 * iv + 1])
                xv_I, yv_I = X_box[2 * iv], X_box[2 * iv + 1]
            else:
                xv_c, yv_c = pin_x_I[v], pin_y_I[v]
                xv_I, yv_I = pin_x_I[v], pin_y_I[v]

            F_c_I.append(_sq_iv(xu_c - xv_c) + _sq_iv(yu_c - yv_c) - RatInterval(sq_q[e_i]))
            dx_I = (xu_I - xv_I).scale(Fraction(2))
            dy_I = (yu_I - yv_I).scale(Fraction(2))
            if u in v_map:
                iu = v_map[u]
                DF_box[eq_i][2 * iu] = dx_I
                DF_box[eq_i][2 * iu + 1] = dy_I
            if v in v_map:
                iv = v_map[v]
                DF_box[eq_i][2 * iv] = -dx_I
                DF_box[eq_i][2 * iv + 1] = -dy_I

        for i in range(14):
            k_int = RatInterval(c[i])
            for k in range(14):
                if Ym[i][k] != 0:
                    k_int = k_int - F_c_I[k].scale(Ym[i][k])
            row_norm = Fraction(0)
            for j in range(14):
                acc = RatInterval(Fraction(1 if i == j else 0))
                for k in range(14):
                    if Ym[i][k] != 0 and (DF_box[k][j].lo != 0 or DF_box[k][j].hi != 0):
                        acc = acc - DF_box[k][j].scale(Ym[i][k])
                mag = max(abs(acc.lo), abs(acc.hi))
                row_norm += mag
                k_int = k_int + RatInterval(-mag * rad, mag * rad)
            if row_norm >= 1:
                raise ValueError(f"Bartzos L880 box {b_i} row {i} non-contractive!")
            if not k_int.strictly_inside(X_box[i]):
                raise ValueError(f"Bartzos L880 box {b_i} row {i} inclusion failed!")
            if row_norm > max_kappa:
                max_kappa = row_norm
            hw = max(k_int.hi - c[i], c[i] - k_int.lo)
            if hw / rad > max_ratio:
                max_ratio = hw / rad

    return {
        "graph": "L880 (Bartzos et al. unmodified lengths)",
        "verified_half_boxes": 434,
        "verified_SE2_realizations": 868,
        "max_contraction_kappa_approx": round(float(max_kappa), 8),
        "max_inclusion_ratio_approx": round(float(max_ratio), 8),
        "elapsed_seconds": round(time.time() - t0, 3),
    }


def verify_bartzos_g160_132(cert_path: str | Path = DEFAULT_G132) -> dict:
    t0 = time.time()
    with open(cert_path, "r", encoding="utf-8") as fh:
        cert = json.load(fh)

    edges = [tuple(e) for e in cert["edges"]]
    rem_idx = cert["remaining_edge_indices"]
    free_v = cert["free_vertices"]
    v_map = {v: i for i, v in enumerate(free_v)}

    len_q = [Fraction(s) for s in cert["edge_lengths"]]
    if any(L <= 0 for L in len_q):
        raise ValueError("Non-positive 3D edge length.")
    sq_q = [L * L for L in len_q]

    x1 = Fraction(cert["pinned_x"]["1"])
    x2 = Fraction(cert["pinned_x"]["2"])
    x3 = Fraction(cert["pinned_x"]["3"])
    y3_lo, y3_hi = (Fraction(s) for s in cert["pinned_y_interval"]["3"])
    if x1 != 0 or x2 != len_q[0]:
        raise ValueError("Pinned x1 or x2 mismatch.")
    expected_x3 = (sq_q[0] + sq_q[1] - sq_q[5]) / (2 * len_q[0])
    if x3 != expected_x3:
        raise ValueError("Pinned x3 mismatch.")
    y3_sq_exact = sq_q[1] - x3 * x3
    if not (y3_lo > 0 and y3_lo * y3_lo <= y3_sq_exact <= y3_hi * y3_hi):
        raise ValueError("Pinned y3 interval fails enclosure of sqrt(l_{1,3}^2 - x_3^2) > 0!")

    pin_I = {
        1: (RatInterval(Fraction(0)), RatInterval(Fraction(0)), RatInterval(Fraction(0))),
        2: (RatInterval(x2), RatInterval(Fraction(0)), RatInterval(Fraction(0))),
        3: (RatInterval(x3), RatInterval(y3_lo, y3_hi), RatInterval(Fraction(0))),
    }

    c_den = Fraction(1, 1 << int(cert["center_scale_exp2"]))
    y_den = Fraction(1, 1 << int(cert["precond_scale_exp2"]))
    rad = Fraction(1, 1 << int(cert["box_radius_exp2"]))

    centers_66 = [[Fraction(v) * c_den for v in row] for row in cert["centers_num"]]
    preconds_66 = cert["preconds_num"]
    if len(centers_66) != 66 or len(preconds_66) != 66:
        raise ValueError("Expected 66 chiral boxes for G160.")

    # Verify all 132 boxes (66 chiral + 66 z-reflections) are pairwise disjoint in R^15
    boxes_132 = []
    for c_pos in centers_66:
        c_neg = [(-c_pos[i] if i % 3 == 2 else c_pos[i]) for i in range(15)]
        boxes_132.append(c_pos)
        boxes_132.append(c_neg)
    for i in range(132):
        for j in range(i + 1, 132):
            if not any(abs(boxes_132[i][d] - boxes_132[j][d]) > 2 * rad for d in range(15)):
                raise ValueError(f"G160 3D boxes {i} and {j} overlap!")

    max_kappa = Fraction(0)
    max_ratio = Fraction(0)
    for b_i in range(66):
        c = centers_66[b_i]
        X_box = [RatInterval(c[d] - rad, c[d] + rad) for d in range(15)]
        Ym = [[Fraction(v) * y_den for v in row] for row in preconds_66[b_i]]

        Fc_I = []
        DF_box = [[RatInterval(Fraction(0)) for _ in range(15)] for _ in range(15)]
        for eq_i, e_i in enumerate(rem_idx):
            u, v = edges[e_i]
            if u in v_map:
                iu = v_map[u]
                pu_c = (RatInterval(c[3 * iu]), RatInterval(c[3 * iu + 1]), RatInterval(c[3 * iu + 2]))
                pu_I = (X_box[3 * iu], X_box[3 * iu + 1], X_box[3 * iu + 2])
            else:
                pu_c = pu_I = pin_I[u]
            if v in v_map:
                iv = v_map[v]
                pv_c = (RatInterval(c[3 * iv]), RatInterval(c[3 * iv + 1]), RatInterval(c[3 * iv + 2]))
                pv_I = (X_box[3 * iv], X_box[3 * iv + 1], X_box[3 * iv + 2])
            else:
                pv_c = pv_I = pin_I[v]

            Fc_I.append(
                _sq_iv(pu_c[0] - pv_c[0]) + _sq_iv(pu_c[1] - pv_c[1]) + _sq_iv(pu_c[2] - pv_c[2])
                - RatInterval(sq_q[e_i])
            )
            dI = [(pu_I[m] - pv_I[m]).scale(Fraction(2)) for m in range(3)]
            if u in v_map:
                iu = v_map[u]
                for m in range(3):
                    DF_box[eq_i][3 * iu + m] = dI[m]
            if v in v_map:
                iv = v_map[v]
                for m in range(3):
                    DF_box[eq_i][3 * iv + m] = -dI[m]

        for i in range(15):
            k_int = RatInterval(c[i])
            for k in range(15):
                if Ym[i][k] != 0:
                    k_int = k_int - Fc_I[k].scale(Ym[i][k])
            row_norm = Fraction(0)
            for j in range(15):
                acc = RatInterval(Fraction(1 if i == j else 0))
                for k in range(15):
                    if Ym[i][k] != 0 and (DF_box[k][j].lo != 0 or DF_box[k][j].hi != 0):
                        acc = acc - DF_box[k][j].scale(Ym[i][k])
                mag = max(abs(acc.lo), abs(acc.hi))
                row_norm += mag
                k_int = k_int + RatInterval(-mag * rad, mag * rad)
            if row_norm >= 1:
                raise ValueError(f"G160 box {b_i} row {i} non-contractive!")
            if not k_int.strictly_inside(X_box[i]):
                raise ValueError(f"G160 box {b_i} row {i} inclusion failed!")
            if row_norm > max_kappa:
                max_kappa = row_norm
            hw = max(k_int.hi - c[i], c[i] - k_int.lo)
            if hw / rad > max_ratio:
                max_ratio = hw / rad

    return {
        "graph": "G160 (Bartzos et al. unmodified 3D lengths)",
        "verified_chiral_boxes": 66,
        "verified_SE3_realizations": 132,
        "max_contraction_kappa_approx": round(float(max_kappa), 8),
        "max_inclusion_ratio_approx": round(float(max_ratio), 8),
        "elapsed_seconds": round(time.time() - t0, 3),
    }


if __name__ == "__main__":
    r1 = verify_bartzos_l880_868()
    print("BARTZOS L880 (868 REAL REALIZATIONS) CERTIFICATE PASSED:")
    for k, v in r1.items():
        print(f"  {k}: {v}")
    r2 = verify_bartzos_g160_132()
    print("BARTZOS G160 (132 REAL 3D REALIZATIONS) CERTIFICATE PASSED:")
    for k, v in r2.items():
        print(f"  {k}: {v}")
