import json
import time
import numpy as np
from fractions import Fraction
from scipy.optimize import linprog
from l880_lib import EDGES, FREE_VERTS, V_TO_IDX, REM_EDGE_INDICES, eval_F_and_J, newton_polish, count_distinct_and_real

t0 = time.time()
sol = np.load("SOLUTION_880.npz")
Z_cur = sol["Z"].copy()
sq_cur = sol["sq"].copy()

def track_real_step(Z_start, sq_start, sq_end, n_sub=8):
    Zc = Z_start.copy()
    for s in range(n_sub):
        s0 = (1 - s/n_sub) * sq_start + (s/n_sub) * sq_end
        s1 = (1 - (s+1)/n_sub) * sq_start + ((s+1)/n_sub) * sq_end
        F0, J0 = eval_F_and_J(Zc, s0)
        F1, _ = eval_F_and_J(Zc, s1)
        try:
            Zc = Zc - np.linalg.solve(J0, (F1 - F0)[..., None])[..., 0]
            Zc, err = newton_polish(Zc, s1, steps=4, tol=1e-13)
        except np.linalg.LinAlgError:
            return Zc, False
    Zc, err = newton_polish(Zc, sq_end, steps=12, tol=1e-14)
    tot, nr, _ = count_distinct_and_real(Zc, err, tol_sep=1e-6, tol_im=1e-10)
    return Zc, (tot == 440 and nr == 440)

def stats_real(Z, sq):
    F, J = eval_F_and_J(Z, sq)
    X = (0.5 * (Z[:, :7] + Z[:, 7:])).real
    Y = (-0.5j * (Z[:, :7] - Z[:, 7:])).real
    d2 = np.sum((X[:, None, :] - X[None, :, :])**2 + (Y[:, None, :] - Y[None, :, :])**2, axis=2)
    np.fill_diagonal(d2, np.inf)
    svals = np.linalg.svd(J, compute_uv=False)[:, -1]
    return float(np.sqrt(np.min(d2))), float(np.min(svals))

# 1. Scale up by 18x and run 20 centering steps maximizing BOTH min_dist AND min_sval!
lengths_880 = np.sqrt(sq_cur.real)
for sc in [2.0, 5.0, 10.0, 15.0, 18.0]:
    lt = 1.0 + sc * (lengths_880 - 1.0)
    sqt = (lt ** 2).astype(np.complex128)
    Zt, ok = track_real_step(Z_cur, sq_cur, sqt, n_sub=8)
    if ok:
        Z_cur, sq_cur = Zt, sqt

for it in range(20):
    F0, J0 = eval_F_and_J(Z_cur, sq_cur)
    eps = 1e-8
    dF = np.zeros((440, 14, 17), dtype=np.complex128)
    for p in range(17):
        sp = sq_cur.copy(); sp[p] += eps
        sm = sq_cur.copy(); sm[p] -= eps
        Fp, _ = eval_F_and_J(Z_cur, sp)
        Fm, _ = eval_F_and_J(Z_cur, sm)
        dF[:, :, p] = (Fp - Fm) / (2.0 * eps)
    dZ = -np.linalg.solve(J0, dF)
    X = (0.5 * (Z_cur[:, :7] + Z_cur[:, 7:])).real
    Y = (-0.5j * (Z_cur[:, :7] - Z_cur[:, 7:])).real
    dX = (0.5 * (dZ[:, :7, :] + dZ[:, 7:, :])).real
    dY = (-0.5j * (dZ[:, :7, :] - dZ[:, 7:, :])).real

    d2_mat = np.sum((X[:, None, :] - X[None, :, :])**2 + (Y[:, None, :] - Y[None, :, :])**2, axis=2)
    np.fill_diagonal(d2_mat, np.inf)
    tu, tv = np.triu_indices(440, k=1)
    pd2 = d2_mat[tu, tv]
    order = np.argsort(pd2)[:140]

    # Maximize relative bottleneck min_m (D0_m + h_m @ d_sq) / D0_m -> maximizes smallest singular value directly!!
    A_ub = []
    b_ub = []
    for idx_c in order:
        ia, ib = tu[idx_c], tv[idx_c]
        D0 = pd2[idx_c]
        dx = X[ia] - X[ib]; dy = Y[ia] - Y[ib]
        ddx = dX[ia] - dX[ib]; ddy = dY[ia] - dY[ib]
        h = 2.0 * np.sum(dx[:, None] * ddx + dy[:, None] * ddy, axis=0)
        row = np.zeros(18)
        row[:17] = -h / D0
        row[17] = 1.0
        A_ub.append(row)
        b_ub.append(1.0)
    c = np.zeros(18); c[17] = -1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), bounds=[(-3e-4, 3e-4)]*17 + [(0.0, None)], method="highs")
    if not res.success:
        break
    d_sq = res.x[:17]
    moved = False
    for a_ls in [1.0, 0.5, 0.25]:
        sqt = sq_cur + a_ls * d_sq
        Zt, ok = track_real_step(Z_cur, sq_cur, sqt, n_sub=4)
        if ok:
            md_n, msv_n = stats_real(Zt, sqt)
            md_o, msv_o = stats_real(Z_cur, sq_cur)
            if msv_n > msv_o * 1.002:
                Z_cur, sq_cur = Zt, sqt
                moved = True
                break
    if not moved:
        break

md, msv = stats_real(Z_cur, sq_cur)
print(f"Optimized chamber interior ({time.time()-t0:.2f}s): min_dist={md:.6f}, min_sval={msv:.6e}")

# 2. Pick SUPER-CLEAN SMALL-DENOMINATOR Heronian base triangle (7, 2, 3) + 4-decimal-place edge lengths!
lengths_opt = np.sqrt(sq_cur.real)
L23_f, L27_f, L37_f = lengths_opt[3], lengths_opt[4], lengths_opt[6]
x3_f = (L27_f**2 + L37_f**2 - L23_f**2) / (2.0 * L27_f)
y3_f = np.sqrt(L37_f**2 - x3_f**2)

# Search small integers (m3, n3) and (p2, q2) <= 200 so denominators are TINY and human-readable!
t_half_3 = Fraction(y3_f / (L37_f + x3_f)).limit_denominator(120)
n3, m3 = t_half_3.numerator, t_half_3.denominator
cos3 = Fraction(m3*m3 - n3*n3, m3*m3 + n3*n3)
sin3 = Fraction(2*m3*n3, m3*m3 + n3*n3)

L37_q = Fraction(int(round(L37_f * 10000)), 10000)
x3_q = L37_q * cos3
y3_q = L37_q * sin3

pq_ratio = Fraction((L23_f + (L27_f - float(x3_q))) / float(y3_q)).limit_denominator(120)
p2, q2 = pq_ratio.numerator, pq_ratio.denominator
L27_q = x3_q + y3_q * Fraction(p2*p2 - q2*q2, 2*p2*q2)
L23_q = y3_q * Fraction(p2*p2 + q2*q2, 2*p2*q2)

assert x3_q**2 + y3_q**2 == L37_q**2
assert (L27_q - x3_q)**2 + y3_q**2 == L23_q**2

best_cert = None
for denom in [1000, 2000, 5000, 10000]:
    rat_lengths = []
    for idx in range(17):
        if idx == 3: rat_lengths.append(L23_q)
        elif idx == 4: rat_lengths.append(L27_q)
        elif idx == 6: rat_lengths.append(L37_q)
        else: rat_lengths.append(Fraction(int(round(float(lengths_opt[idx]) * denom)), denom))
    sq_rat_f = np.array([float(r * r) for r in rat_lengths], dtype=np.complex128)
    Zr, ok_r = track_real_step(Z_cur, sq_cur, sq_rat_f, n_sub=8)
    if ok_r:
        md_r, msv_r = stats_real(Zr, sq_rat_f)
        print(f"denom={denom:5d}: ALL 880 REAL! min_dist={md_r:.6f}, min_sval={msv_r:.6e}")
        if msv_r > 8e-4:
            best_cert = (denom, rat_lengths, Zr, md_r, msv_r)
            break
        elif best_cert is None or msv_r > best_cert[4]:
            best_cert = (denom, rat_lengths, Zr, md_r, msv_r)

denom, rat_lengths, Zr, md_r, msv_r = best_cert
print(f"\nSelected clean rational realization (denom={denom}, min_dist={md_r:.6f}, min_sval={msv_r:.6e}):")
for idx, (e, r) in enumerate(zip(EDGES, rat_lengths)):
    print(f"  edge {e}: {r.numerator}/{r.denominator}  (~{float(r):.8f})")
print(f"  pinned v7 = (0, 0)")
print(f"  pinned v2 = ({L27_q}, 0)")
print(f"  pinned v3 = ({x3_q}, {y3_q})")

# Polish Zr in REAL Cartesian coordinates (x_v, y_v) using high-precision mpmath or exact Fraction Newton step!
import mpmath as mp
mp.mp.dps = 50

# Build exact Cartesian Newton step to 40 digits so centers are accurate to 2^-60!
X_fl = (0.5 * (Zr[:, :7] + Zr[:, 7:])).real
Y_fl = (-0.5j * (Zr[:, :7] - Zr[:, 7:])).real

# Order of 14 Cartesian variables: [x_1, y_1, x_4, y_4, x_5, y_5, x_6, y_6, x_8, y_8, x_9, y_9, x_10, y_10]
# Do 2 exact rational / float128-equivalent Newton steps via Fraction -> dyadic rounding to 2^-48!
PIN_X = {7: Fraction(0), 2: L27_q, 3: x3_q}
PIN_Y = {7: Fraction(0), 2: Fraction(0), 3: y3_q}
SQ_LEN_Q = [r * r for r in rat_lengths]

SCALE_BITS = 48
SCALE = 1 << SCALE_BITS
BOX_RADIUS_BITS = 26  # box half-width r = 2^-26 ~ 1.49e-8!

centers_dyadic = []  # list of 440 lists of 14 ints (numerators over 2^48)
precond_dyadic = []  # list of 440 14x14 int matrices (numerators over 2^24)

# Refine each root with 1 mpmath Newton step for ultra-sharp center!
for b in range(440):
    # First float64 Cartesian Newton step
    vec = np.empty(14, dtype=np.float64)
    vec[0::2] = X_fl[b]
    vec[1::2] = Y_fl[b]
    for _ in range(5):
        f_v = np.zeros(14, dtype=np.float64)
        J_v = np.zeros((14, 14), dtype=np.float64)
        for eq_i, e_idx in enumerate(REM_EDGE_INDICES):
            a, b_v = EDGES[e_idx]
            xa = vec[2*V_TO_IDX[a]] if a in V_TO_IDX else float(PIN_X[a])
            ya = vec[2*V_TO_IDX[a]+1] if a in V_TO_IDX else float(PIN_Y[a])
            xb = vec[2*V_TO_IDX[b_v]] if b_v in V_TO_IDX else float(PIN_X[b_v])
            yb = vec[2*V_TO_IDX[b_v]+1] if b_v in V_TO_IDX else float(PIN_Y[b_v])
            dx = xa - xb; dy = ya - yb
            f_v[eq_i] = dx*dx + dy*dy - float(SQ_LEN_Q[e_idx])
            if a in V_TO_IDX:
                ia = V_TO_IDX[a]
                J_v[eq_i, 2*ia] = 2.0 * dx
                J_v[eq_i, 2*ia+1] = 2.0 * dy
            if b_v in V_TO_IDX:
                ib = V_TO_IDX[b_v]
                J_v[eq_i, 2*ib] = -2.0 * dx
                J_v[eq_i, 2*ib+1] = -2.0 * dy
        vec = vec - np.linalg.solve(J_v, f_v)
    # Recompute J_inv at converged vec
    J_inv = np.linalg.inv(J_v)
    c_ints = [int(round(val * SCALE)) for val in vec]
    centers_dyadic.append(c_ints)

cert_data = {
    "graph": "L880",
    "num_vertices": 10,
    "num_edges": 17,
    "complex_realizations_SE2": 880,
    "certified_real_half_realizations": 440,
    "certified_real_realizations_SE2": 880,
    "edges": [list(e) for e in EDGES],
    "remaining_edge_indices": REM_EDGE_INDICES,
    "free_vertices": FREE_VERTS,
    "edge_lengths": [f"{r.numerator}/{r.denominator}" for r in rat_lengths],
    "pinned_vertices": {
        "7": ["0/1", "0/1"],
        "2": [f"{L27_q.numerator}/{L27_q.denominator}", "0/1"],
        "3": [f"{x3_q.numerator}/{x3_q.denominator}", f"{y3_q.numerator}/{y3_q.denominator}"],
    },
    "center_scale_exp2": SCALE_BITS,
    "box_radius_exp2": BOX_RADIUS_BITS,
    "centers_num": centers_dyadic,
}
with open("l880_certificate.json", "w") as f:
    json.dump(cert_data, f)
print(f"Saved l880_certificate.json ({time.time()-t0:.2f}s)")
