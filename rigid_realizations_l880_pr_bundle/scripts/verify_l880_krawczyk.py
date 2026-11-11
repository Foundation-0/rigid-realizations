#!/usr/bin/env python3
"""
Primary Exact Rational Interval Krawczyk Verifier for L880 (All 880 Real Realizations).
Uses ONLY Python's standard library (`json`, `fractions.Fraction`, `math.lcm`, `pathlib`, `sys`).
Zero floating-point operations are performed along the verification path.
"""
import json
from math import lcm
from pathlib import Path
import sys
import time
from fractions import Fraction

DEFAULT_CERT = Path(__file__).resolve().parent.parent / "results" / "l880-all-880-real" / "l880_certificate.json"


def verify_certificate_dict(cert: dict) -> dict:
    t0 = time.time()
    edges = [tuple(e) for e in cert["edges"]]
    rem_idx = cert["remaining_edge_indices"]
    free_v = cert["free_vertices"]
    v_map = {v: i for i, v in enumerate(free_v)}

    # Verify GKT row-major MSB upper-triangular encoding == 4778440734593
    edge_set = {(min(u, v), max(u, v)) for u, v in edges}
    pairs_row = [(i, j) for i in range(1, 11) for j in range(i + 1, 11)]
    gkt_code = sum((1 << (44 - k)) for k, p in enumerate(pairs_row) if p in edge_set)
    if gkt_code != 4778440734593:
        raise ValueError(f"Graph encoding {gkt_code} != 4778440734593 (L880).")

    # 1. Verify exact positivity of all 17 edge lengths and exact Heronian identity on pinned triangle (7, 2, 3)
    edge_lengths = [Fraction(s) for s in cert["edge_lengths"]]
    if len(edges) != 17 or len(edge_lengths) != 17:
        raise ValueError("Expected 17 edges and 17 edge lengths.")
    for e_len in edge_lengths:
        if e_len <= 0:
            raise ValueError("Non-positive edge length.")
    sq_len = [L * L for L in edge_lengths]

    pin_x = {int(k): Fraction(v[0]) for k, v in cert["pinned_vertices"].items()}
    pin_y = {int(k): Fraction(v[1]) for k, v in cert["pinned_vertices"].items()}

    for p_e_idx in (3, 4, 6):
        a, b = edges[p_e_idx]
        d2_exact = (pin_x[a] - pin_x[b]) ** 2 + (pin_y[a] - pin_y[b]) ** 2
        if d2_exact != sq_len[p_e_idx]:
            raise ValueError(f"Pinned edge {edges[p_e_idx]} fails exact rational distance!")

    det_orient = (pin_x[2] - pin_x[7]) * (pin_y[3] - pin_y[7]) - (pin_y[2] - pin_y[7]) * (pin_x[3] - pin_x[7])
    if det_orient <= 0:
        raise ValueError("Pinned base triangle is degenerate or wrong orientation!")

    # 2. Scaled integer parameters for exact rational Krawczyk certification
    c_bits = int(cert["center_scale_exp2"])
    r_bits = int(cert["box_radius_exp2"])
    y_bits = int(cert["precond_scale_exp2"])
    if c_bits < r_bits:
        raise ValueError("center_scale_exp2 must be >= box_radius_exp2")
    C_DEN = 1 << c_bits
    R_NUM_IN_C = 1 << (c_bits - r_bits)
    r_frac = Fraction(1, 1 << r_bits)

    centers_num = cert["centers_num"]
    preconds_num = cert["preconds_num"]
    n_boxes = len(centers_num)
    if n_boxes != 440 or len(preconds_num) != 440:
        raise ValueError(f"Expected 440 boxes and preconditioners, got {n_boxes}")

    # 3. Pairwise disjointness of all 440 closed l_infinity boxes in R^14
    two_r_int = 2 * R_NUM_IN_C
    min_center_linf_int = None
    for a in range(n_boxes):
        ca = centers_num[a]
        for b in range(a + 1, n_boxes):
            cb = centers_num[b]
            sep = max(abs(ca[i] - cb[i]) for i in range(14))
            if sep <= two_r_int:
                raise ValueError(f"Boxes {a} and {b} overlap or touch!")
            if min_center_linf_int is None or sep < min_center_linf_int:
                min_center_linf_int = sep

    Q_PIN = 1
    for v in (7, 2, 3):
        Q_PIN = lcm(Q_PIN, pin_x[v].denominator, pin_y[v].denominator)
    Q_ALL = lcm(Q_PIN, C_DEN)
    mul_c = Q_ALL // C_DEN
    pin_x_I = {v: int(pin_x[v] * Q_ALL) for v in (7, 2, 3)}
    pin_y_I = {v: int(pin_y[v] * Q_ALL) for v in (7, 2, 3)}

    Q_SQ = 1
    for e_idx in rem_idx:
        Q_SQ = lcm(Q_SQ, sq_len[e_idx].denominator)
    Q_F = lcm(Q_ALL * Q_ALL, Q_SQ)
    mul_d2 = Q_F // (Q_ALL * Q_ALL)
    sq_len_I = {e_idx: int(sq_len[e_idx] * Q_F) for e_idx in rem_idx}

    edge_lip_w = [16 if ((edges[e_idx][0] in v_map) and (edges[e_idx][1] in v_map)) else 4 for e_idx in rem_idx]

    Y_DEN = 1 << y_bits
    max_kappa = Fraction(0)
    max_krawczyk_ratio = Fraction(0)

    # 4. Exact Krawczyk interval verification on all 440 boxes
    YQ_DIAG = Y_DEN * Q_ALL
    YF_DEN = Y_DEN * Q_F
    for b_idx in range(n_boxes):
        c_raw = centers_num[b_idx]
        Y_raw = preconds_num[b_idx]
        c_I = [val * mul_c for val in c_raw]

        F_I = [0] * 14
        DF_I = [[0] * 14 for _ in range(14)]
        for eq_i, e_idx in enumerate(rem_idx):
            u_v, v_v = edges[e_idx]
            xa = c_I[2 * v_map[u_v]] if u_v in v_map else pin_x_I[u_v]
            ya = c_I[2 * v_map[u_v] + 1] if u_v in v_map else pin_y_I[u_v]
            xb = c_I[2 * v_map[v_v]] if v_v in v_map else pin_x_I[v_v]
            yb = c_I[2 * v_map[v_v] + 1] if v_v in v_map else pin_y_I[v_v]
            dx = xa - xb
            dy = ya - yb
            F_I[eq_i] = (dx * dx + dy * dy) * mul_d2 - sq_len_I[e_idx]
            if u_v in v_map:
                ia = v_map[u_v]
                DF_I[eq_i][2 * ia] = 2 * dx
                DF_I[eq_i][2 * ia + 1] = 2 * dy
            if v_v in v_map:
                ib = v_map[v_v]
                DF_I[eq_i][2 * ib] = -2 * dx
                DF_I[eq_i][2 * ib + 1] = -2 * dy

        for i in range(14):
            Yi = Y_raw[i]
            yf_num = abs(sum(Yi[k] * F_I[k] for k in range(14)))
            yf_frac = Fraction(yf_num, YF_DEN)

            alpha_num = 0
            for j in range(14):
                prod = sum(Yi[k] * DF_I[k][j] for k in range(14))
                alpha_num += abs(YQ_DIAG - prod) if i == j else abs(prod)
            alpha_i = Fraction(alpha_num, YQ_DIAG)

            beta_num = sum(abs(Yi[k]) * edge_lip_w[k] for k in range(14))
            beta_r_i = Fraction(beta_num, Y_DEN) * r_frac

            kappa_i = alpha_i + beta_r_i
            if kappa_i >= 1:
                raise ValueError(f"Box {b_idx} row {i}: contraction kappa_i >= 1!")
            k_rad_i = yf_frac + kappa_i * r_frac
            if k_rad_i >= r_frac:
                raise ValueError(f"Box {b_idx} row {i}: Krawczyk radius >= box radius!")

            if kappa_i > max_kappa:
                max_kappa = kappa_i
            ratio_i = k_rad_i / r_frac
            if ratio_i > max_krawczyk_ratio:
                max_krawczyk_ratio = ratio_i

    elapsed = time.time() - t0
    return {
        "verified_boxes": n_boxes,
        "verified_SE2_realizations": 2 * n_boxes,
        "box_radius": str(r_frac),
        "min_center_linf_separation": f"{min_center_linf_int}/{C_DEN}",
        "min_center_linf_separation_approx": round(min_center_linf_int / C_DEN, 8),
        "max_contraction_kappa_exact": str(max_kappa),
        "max_contraction_kappa_approx": round(float(max_kappa), 8),
        "max_krawczyk_inclusion_ratio_approx": round(float(max_krawczyk_ratio), 8),
        "elapsed_seconds": round(elapsed, 3),
    }


def verify_certificate(path: str | Path = DEFAULT_CERT) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        cert = json.load(fh)
    return verify_certificate_dict(cert)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CERT
    res = verify_certificate(target)
    print("EXACT RATIONAL KRAWCZYK CERTIFICATE PASSED!")
    for k, v in res.items():
        print(f"  {k}: {v}")
