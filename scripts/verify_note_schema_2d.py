#!/usr/bin/env python3
"""Zero-float pure-stdlib Krawczyk verifier for 2D NOTE.md certificate JSON files."""
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path


def combinatorial_c2(edges_1based):
    """c_2(G) via Capco et al. bigraph recurrence (same as verify_capco_laman.compute_c2)."""
    capco_path = Path(__file__).resolve().parent.parent / "rigid_realizations_l880_pr_bundle" / "scripts" / "verify_capco_laman.py"
    spec = importlib.util.spec_from_file_location("verify_capco_laman", capco_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Capco verifier from {capco_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.compute_c2(edges_1based)


def verify_laman(n, edges):
    if len(edges) != 2 * n - 3:
        raise ValueError(f"Expected {2*n-3} edges, got {len(edges)}")
    adj_sets = [(u - 1, v - 1) for u, v in edges]
    for mask in range(1, 1 << n):
        k = mask.bit_count()
        if k < 2:
            continue
        cnt = sum(1 for u, v in adj_sets if (mask >> u) & 1 and (mask >> v) & 1)
        if cnt > 2 * k - 3:
            raise ValueError(f"Laman condition violated on subset mask={mask}")


def approx_inv_dyadic(mat_q, bits=44):
    """Pure integer/Fraction approximate matrix inverse rounded to 2^-bits (zero floats)."""
    scale = 1 << bits
    d = len(mat_q)
    A = [[(mat_q[i][j].numerator * scale) // mat_q[i][j].denominator for j in range(d)] for i in range(d)]
    B = [[scale if i == j else 0 for j in range(d)] for i in range(d)]
    for col in range(d):
        piv = max(range(col, d), key=lambda r: abs(A[r][col]))
        if A[piv][col] == 0:
            raise ZeroDivisionError("Singular Jacobian center")
        A[col], A[piv] = A[piv], A[col]
        B[col], B[piv] = B[piv], B[col]
        pv = A[col][col]
        for j in range(d):
            A[col][j] = (A[col][j] * scale) // pv
            B[col][j] = (B[col][j] * scale) // pv
        for r in range(d):
            if r == col or A[r][col] == 0:
                continue
            fac = A[r][col]
            for j in range(d):
                A[r][j] -= (fac * A[col][j]) // scale
                B[r][j] -= (fac * B[col][j]) // scale
    return [[Fraction(B[i][j], scale) for j in range(d)] for i in range(d)]


def verify_certificate(path):
    with open(path, "r", encoding="utf-8") as f:
        cert = json.load(f)
    if cert["dimension"] != 2:
        raise ValueError("This verifier checks 2D edge-pinned NOTE.md certificates.")
    n = int(cert["n"])
    edges = [tuple(e) for e in cert["edges"]]
    if "complex_count" not in cert:
        raise ValueError("Certificate missing complex_count.")
    complex_count = int(cert["complex_count"])
    claimed = int(cert["claimed_real_count"])
    if claimed > complex_count:
        raise ValueError(f"claimed_real_count {claimed} exceeds complex_count {complex_count}")
    c2 = combinatorial_c2([[u, v] for u, v in edges])
    if complex_count != c2:
        raise ValueError(f"complex_count {complex_count} disagrees with combinatorial c_2(G)={c2}")
    verify_laman(n, edges)
    lengths = [Fraction(s) for s in cert["lengths"]]
    if any(ell <= 0 for ell in lengths):
        raise ValueError("All bar lengths must be strictly positive.")
    sq_lengths = [ell * ell for ell in lengths]
    u_pin, v_pin = cert["pinned"]
    pin_idx = None
    for idx, (u, v) in enumerate(edges):
        if (u, v) == (u_pin, v_pin) or (v, u) == (u_pin, v_pin):
            pin_idx = idx
            break
    if pin_idx is None:
        raise ValueError("Pinned vertices must form an edge in 2D.")
    L_pin = lengths[pin_idx]
    free_verts = [v for v in range(1, n + 1) if v not in (u_pin, v_pin)]
    v_to_idx = {v: i for i, v in enumerate(free_verts)}
    rem_indices = [k for k in range(len(edges)) if k != pin_idx]
    dim = 2 * (n - 2)
    boxes = cert["boxes"]
    if len(boxes) != claimed:
        raise ValueError("Box count mismatch with claimed_real_count.")
    if len(boxes) > complex_count:
        raise ValueError(f"{len(boxes)} boxes exceed complex_count {complex_count}")

    parsed_boxes = []
    for box in boxes:
        if len(box) != dim:
            raise ValueError("Box dimension mismatch.")
        b_iv = []
        for lo_s, hi_s in box:
            lo, hi = Fraction(lo_s), Fraction(hi_s)
            if lo >= hi:
                raise ValueError("Non-positive box width.")
            b_iv.append((lo, hi))
        parsed_boxes.append(b_iv)

    for a in range(len(parsed_boxes)):
        ba = parsed_boxes[a]
        for b in range(a + 1, len(parsed_boxes)):
            bb = parsed_boxes[b]
            if all(max(ba[k][0], bb[k][0]) <= min(ba[k][1], bb[k][1]) for k in range(dim)):
                raise ValueError(f"Boxes {a} and {b} overlap or touch.")

    max_ratio = Fraction(0)
    for b_idx, box in enumerate(parsed_boxes):
        centers = [(lo + hi) / 2 for lo, hi in box]
        radii = [(hi - lo) / 2 for lo, hi in box]

        def xy_c(v):
            if v == u_pin:
                return Fraction(0), Fraction(0)
            if v == v_pin:
                return L_pin, Fraction(0)
            i = 2 * v_to_idx[v]
            return centers[i], centers[i + 1]

        def xy_iv(v):
            if v == u_pin:
                return (Fraction(0), Fraction(0)), (Fraction(0), Fraction(0))
            if v == v_pin:
                return (L_pin, L_pin), (Fraction(0), Fraction(0))
            i = 2 * v_to_idx[v]
            return box[i], box[i + 1]

        F_c = [Fraction(0)] * dim
        J_c = [[Fraction(0)] * dim for _ in range(dim)]
        J_iv = [[(Fraction(0), Fraction(0)) for _ in range(dim)] for _ in range(dim)]

        for row, k_ed in enumerate(rem_indices):
            u, v = edges[k_ed]
            xu, yu = xy_c(u)
            xv, yv = xy_c(v)
            dx, dy = xu - xv, yu - yv
            F_c[row] = dx * dx + dy * dy - sq_lengths[k_ed]
            xui, yui = xy_iv(u)
            xvi, yvi = xy_iv(v)
            dx_lo, dx_hi = 2 * (xui[0] - xvi[1]), 2 * (xui[1] - xvi[0])
            dy_lo, dy_hi = 2 * (yui[0] - yvi[1]), 2 * (yui[1] - yvi[0])
            if u in v_to_idx:
                iu = 2 * v_to_idx[u]
                J_c[row][iu] = 2 * dx
                J_c[row][iu + 1] = 2 * dy
                J_iv[row][iu] = (dx_lo, dx_hi)
                J_iv[row][iu + 1] = (dy_lo, dy_hi)
            if v in v_to_idx:
                iv = 2 * v_to_idx[v]
                J_c[row][iv] = -2 * dx
                J_c[row][iv + 1] = -2 * dy
                J_iv[row][iv] = (-dx_hi, -dx_lo)
                J_iv[row][iv + 1] = (-dy_hi, -dy_lo)

        R_q = approx_inv_dyadic(J_c, bits=44)
        for i in range(dim):
            rf_i = sum(R_q[i][k] * F_c[k] for k in range(dim))
            rad_sum = Fraction(0)
            for j in range(dim):
                acc_lo, acc_hi = Fraction(0), Fraction(0)
                for k in range(dim):
                    rk = R_q[i][k]
                    if rk == 0:
                        continue
                    j_lo, j_hi = J_iv[k][j]
                    if rk > 0:
                        acc_lo += rk * j_lo
                        acc_hi += rk * j_hi
                    else:
                        acc_lo += rk * j_hi
                        acc_hi += rk * j_lo
                one = Fraction(1) if i == j else Fraction(0)
                m_ij = max(abs(one - acc_hi), abs(one - acc_lo))
                rad_sum += m_ij * radii[j]
            k_abs = abs(-rf_i) + rad_sum
            if k_abs >= radii[i]:
                raise ValueError(f"Krawczyk failed on box {b_idx}, coord {i}")
            ratio = k_abs / radii[i]
            if ratio > max_ratio:
                max_ratio = ratio

    print(
        f"PASS {cert['graph']}: certified {len(parsed_boxes)}/{cert['complex_count']} "
        f"real realizations (max contraction < { (max_ratio.numerator * 1000000) // max_ratio.denominator + 1 }e-6)"
    )


if __name__ == "__main__":
    for p in sys.argv[1:]:
        verify_certificate(p)
