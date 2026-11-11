import time
import numpy as np

t0 = time.time()

# L880 edges (1-indexed vertices 1..10)
EDGES = [
    (1, 4), (1, 8), (1, 10),
    (2, 3), (2, 7), (2, 10),
    (3, 7), (3, 9),
    (4, 8), (4, 9),
    (5, 7), (5, 8), (5, 10),
    (6, 7), (6, 8), (6, 9),
    (9, 10),
]

BARTZOS_LENGTHS = np.array([
    1.0002169,  # (1, 4)
    1.0001366,  # (1, 8)
    1.0004509,  # (1, 10)
    1.000763,   # (2, 3)
    1.0000575,  # (2, 7)
    1.0006078,  # (2, 10)
    1.0001763,  # (3, 7)
    1.00075,    # (3, 9)
    1.0008574,  # (4, 8)
    1.000536,   # (4, 9)
    1.000491,   # (5, 7)
    1.0002946,  # (5, 8)
    1.0006778,  # (5, 10)
    1.0004699,  # (6, 7)
    1.0002724,  # (6, 8)
    1.0005141,  # (6, 9)
    1.0003913,  # (9, 10)
], dtype=np.float64)

# Free vertices after pinning triangle (7, 2, 3):
# Pin v7 = (0, 0) -> u7 = 0, w7 = 0
# Pin v2 = (L27, 0) -> u2 = L27, w2 = L27
# Pin v3 = (x3, y3) with y3 > 0 (1 of 2 orientations; the reflection y -> -y doubles 440 -> 880!)
FREE_VERTS = [1, 4, 5, 6, 8, 9, 10]  # 7 free vertices -> 14 isotropic coordinates (u_k, w_k)
V_TO_IDX = {v: i for i, v in enumerate(FREE_VERTS)}

# The 14 remaining edges (excluding (2,3), (2,7), (3,7))
REM_EDGE_INDICES = [idx for idx, e in enumerate(EDGES) if e not in [(2, 3), (2, 7), (3, 7)]]
REM_EDGES = [EDGES[idx] for idx in REM_EDGE_INDICES]
assert len(REM_EDGES) == 14

def get_pinned_uw(sq_lengths):
    # sq_lengths has length 17 (can be complex!)
    # edge indices: (2,3)->3, (2,7)->4, (3,7)->6
    s23 = sq_lengths[3]
    s27 = sq_lengths[4]
    s37 = sq_lengths[6]
    L27 = np.sqrt(s27)
    x3 = (s27 + s37 - s23) / (2.0 * L27)
    y3 = np.sqrt(s37 - x3 * x3)
    u = {7: 0.0 + 0.0j, 2: L27 + 0.0j, 3: x3 + 1j * y3}
    w = {7: 0.0 + 0.0j, 2: L27 + 0.0j, 3: x3 - 1j * y3}
    return u, w

def eval_F_and_J(Z, sq_lengths):
    """
    Z: shape (B, 14) complex128, where Z[:, 0:7] = u_free, Z[:, 7:14] = w_free
    sq_lengths: shape (17,) complex128
    Returns F (B, 14), J (B, 14, 14)
    """
    B = Z.shape[0]
    u_pin, w_pin = get_pinned_uw(sq_lengths)
    F = np.zeros((B, 14), dtype=np.complex128)
    J = np.zeros((B, 14, 14), dtype=np.complex128)
    for eq_i, e_idx in enumerate(REM_EDGE_INDICES):
        a, b = EDGES[e_idx]
        ua = Z[:, V_TO_IDX[a]] if a in V_TO_IDX else u_pin[a]
        wa = Z[:, 7 + V_TO_IDX[a]] if a in V_TO_IDX else w_pin[a]
        ub = Z[:, V_TO_IDX[b]] if b in V_TO_IDX else u_pin[b]
        wb = Z[:, 7 + V_TO_IDX[b]] if b in V_TO_IDX else w_pin[b]
        du = ua - ub
        dw = wa - wb
        F[:, eq_i] = du * dw - sq_lengths[e_idx]
        if a in V_TO_IDX:
            ia = V_TO_IDX[a]
            J[:, eq_i, ia] = dw
            J[:, eq_i, 7 + ia] = du
        if b in V_TO_IDX:
            ib = V_TO_IDX[b]
            J[:, eq_i, ib] = -dw
            J[:, eq_i, 7 + ib] = -du
    return F, J

def newton_polish(Z, sq_lengths, steps=8, tol=1e-12):
    for _ in range(steps):
        F, J = eval_F_and_J(Z, sq_lengths)
        err = np.max(np.abs(F), axis=1)
        if np.all(err < tol):
            break
        try:
            delta = np.linalg.solve(J, F[..., None])[..., 0]
        except np.linalg.LinAlgError:
            # Solve row-by-row fallback
            delta = np.zeros_like(Z)
            for b in range(Z.shape[0]):
                try:
                    delta[b] = np.linalg.solve(J[b], F[b])
                except np.linalg.LinAlgError:
                    pass
        Z = Z - delta
    F, _ = eval_F_and_J(Z, sq_lengths)
    err = np.max(np.abs(F), axis=1)
    return Z, err

def track_homotopy(Z_start, sq_start, sq_end, n_steps=25):
    Z = Z_start.copy()
    for s in range(n_steps):
        t = s / n_steps
        dt = 1.0 / n_steps
        sq_curr = (1.0 - t) * sq_start + t * sq_end
        sq_next = (1.0 - (t + dt)) * sq_start + (t + dt) * sq_end
        dsq = sq_next - sq_curr
        # Predictor: J * dZ + dF/dt * dt = 0
        # Note: pinned vertices (2, 3) also move slightly with sq_lengths!
        # Let's use finite-difference or exact dF for predictor + 2 Newton corrector steps:
        F0, J0 = eval_F_and_J(Z, sq_curr)
        F1_pred, _ = eval_F_and_J(Z, sq_next)
        dF = F1_pred - F0
        try:
            dZ = -np.linalg.solve(J0, dF[..., None])[..., 0]
        except np.linalg.LinAlgError:
            dZ = 0.0
        Z = Z + dZ
        # 2 Newton corrector steps at sq_next
        for _ in range(2):
            Fc, Jc = eval_F_and_J(Z, sq_next)
            try:
                Z = Z - np.linalg.solve(Jc, Fc[..., None])[..., 0]
            except np.linalg.LinAlgError:
                pass
    Z, err = newton_polish(Z, sq_end, steps=6)
    return Z, err

# Plant one random generic complex root at base parameters!
rng = np.random.default_rng(20261111)
u_seed_all = {7: 0.0 + 0.0j, 2: 1.2 + 0.1j, 3: 0.4 + 1.1j}
w_seed_all = {7: 0.0 + 0.0j, 2: 1.2 + 0.1j, 3: 0.5 - 0.9j}
# Wait: for get_pinned_uw consistency: u2 == w2 == L27, and x3=(u3+w3)/2, y3=(u3-w3)/(2i)
L27_0 = 1.15 + 0.05j
x3_0 = 0.52 - 0.07j
y3_0 = 0.88 + 0.04j
u_seed_all[2] = w_seed_all[2] = L27_0
u_seed_all[3] = x3_0 + 1j * y3_0
w_seed_all[3] = x3_0 - 1j * y3_0
for v in FREE_VERTS:
    u_seed_all[v] = rng.normal() + 1j * rng.normal()
    w_seed_all[v] = rng.normal() + 1j * rng.normal()

sq_base = np.array([(u_seed_all[a] - u_seed_all[b]) * (w_seed_all[a] - w_seed_all[b]) for (a, b) in EDGES], dtype=np.complex128)
# Check that get_pinned_uw(sq_base) matches u_seed_all[2,3], w_seed_all[2,3] (if sign of sqrt matches, else flip sign of y3_0/L27_0)
up_chk, wp_chk = get_pinned_uw(sq_base)
if abs(up_chk[3] - u_seed_all[3]) > 1e-8:
    # Swap u3, w3 so y3 branch matches np.sqrt
    u_seed_all[3], w_seed_all[3] = up_chk[3], wp_chk[3]
    sq_base = np.array([(u_seed_all[a] - u_seed_all[b]) * (w_seed_all[a] - w_seed_all[b]) for (a, b) in EDGES], dtype=np.complex128)

Z0 = np.array([[u_seed_all[v] for v in FREE_VERTS] + [w_seed_all[v] for v in FREE_VERTS]], dtype=np.complex128)
Z0, err0 = newton_polish(Z0, sq_base)
print("Seed root residual:", err0[0])

# Deduplication helper using round-hash on random projection
proj_vec = rng.normal(size=14) + 1j * rng.normal(size=14)
roots_list = [Z0[0]]
hashes = { (round((Z0[0] @ proj_vec).real, 6), round((Z0[0] @ proj_vec).imag, 6)) }

for loop_i in range(25):
    if len(roots_list) >= 440:
        break
    Z_batch = np.array(roots_list, dtype=np.complex128)
    # Random complex parameters on unit circle perturbation of sq_base
    sq_mid1 = sq_base * np.exp(1j * rng.uniform(-1.8, 1.8, size=17)) * rng.uniform(0.6, 1.5, size=17)
    sq_mid2 = sq_base * np.exp(1j * rng.uniform(-1.8, 1.8, size=17)) * rng.uniform(0.6, 1.5, size=17)
    Z1, e1 = track_homotopy(Z_batch, sq_base, sq_mid1, n_steps=20)
    Z1 = Z1[e1 < 1e-9]
    Z2, e2 = track_homotopy(Z1, sq_mid1, sq_mid2, n_steps=20)
    Z2 = Z2[e2 < 1e-9]
    Z3, e3 = track_homotopy(Z2, sq_mid2, sq_base, n_steps=20)
    Z3 = Z3[e3 < 1e-10]
    vals = Z3 @ proj_vec
    added = 0
    for r, val in zip(Z3, vals):
        key = (round(val.real, 6), round(val.imag, 6))
        if key not in hashes:
            # Verify true distance > 1e-5 from existing roots
            hashes.add(key)
            roots_list.append(r)
            added += 1
    print(f"Loop {loop_i+1}: +{added} new roots -> total {len(roots_list)} / 440 ({time.time()-t0:.2f}s)")

Z_base = np.array(roots_list, dtype=np.complex128)
# Verify pairwise min distance
diffs = np.max(np.abs(Z_base[:, None, :] - Z_base[None, :, :]), axis=2)
np.fill_diagonal(diffs, np.inf)
print("Min pairwise L_inf distance among base roots:", np.min(diffs))

# NOW TRACK ALL 440 ROOTS TO BARTZOS'S EXACT PARAMETERS!!
# Use a complex arc sq(t) = (1-t)*sq_base + t*sq_bartzos + gamma * t*(1-t) to avoid any real discriminant on the way!
sq_bartzos = (BARTZOS_LENGTHS ** 2).astype(np.complex128)
gamma = (0.15 + 0.23j) * sq_bartzos
Z_curr = Z_base.copy()
N_TRACK = 120
for s in range(N_TRACK):
    t1 = s / N_TRACK
    t2 = (s + 1) / N_TRACK
    sq1 = (1 - t1) * sq_base + t1 * sq_bartzos + gamma * t1 * (1 - t1)
    sq2 = (1 - t2) * sq_base + t2 * sq_bartzos + gamma * t2 * (1 - t2)
    Z_curr, err = track_homotopy(Z_curr, sq1, sq2, n_steps=1)

Z_bartzos, err_b = newton_polish(Z_curr, sq_bartzos, steps=12, tol=1e-13)
good_b = err_b < 1e-10
print(f"Tracked to Bartzos: {np.sum(good_b)} / {len(Z_base)} converged (max err among good: {np.max(err_b[good_b]):.2e})")
Zb = Z_bartzos[good_b]
# Check distinctness at Bartzos
diffs_b = np.max(np.abs(Zb[:, None, :] - Zb[None, :, :]), axis=2)
np.fill_diagonal(diffs_b, np.inf)
print("Min pairwise distance at Bartzos:", np.min(diffs_b))

# Count REAL solutions at Bartzos!
# Recall x_k = (u_k + w_k)/2, y_k = (u_k - w_k)/(2i)!
# A solution is REAL iff Im(x_k) == 0 and Im(y_k) == 0 for all k, i.e., w_k == conj(u_k)!
X_free = 0.5 * (Zb[:, :7] + Zb[:, 7:])
Y_free = -0.5j * (Zb[:, :7] - Zb[:, 7:])
imag_norm = np.max(np.maximum(np.abs(X_free.imag), np.abs(Y_free.imag)), axis=1)
real_mask = imag_norm < 1e-8
print(f"Half-realizations REAL count: {np.sum(real_mask)} / {len(Zb)}  --> Total SE(2) REAL realizations = {2 * np.sum(real_mask)} / 880 !!")
print("Non-real imaginary norms:", np.sort(imag_norm[~real_mask]))
np.savez("l880_base_and_bartzos.npz", Z_base=Z_base, sq_base=sq_base, Z_bartzos=Z_bartzos, sq_bartzos=sq_bartzos)
