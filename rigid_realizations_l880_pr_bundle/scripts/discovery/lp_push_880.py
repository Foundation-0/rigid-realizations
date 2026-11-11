import time
import numpy as np
from scipy.optimize import linprog
from l880_lib import EDGES, eval_F_and_J, newton_polish, count_distinct_and_real

ck = np.load("fast_climb_best.npz")
Z_cur = ck["Z"]
delta_cur = ck["delta"]
sq_cur = ((1.0 + delta_cur) ** 2).astype(np.complex128)

def fast_move_adaptive(Z_start, sq_start, sq_end):
    F0, J0 = eval_F_and_J(Z_start, sq_start)
    F1, _ = eval_F_and_J(Z_start, sq_end)
    try:
        Zp = Z_start - np.linalg.solve(J0, (F1 - F0)[..., None])[..., 0]
        Zp, err = newton_polish(Zp, sq_end, steps=6, tol=1e-13)
        tot, nr, imm = count_distinct_and_real(Zp, err, tol_sep=1e-7)
        if tot == 440:
            return Zp, tot, nr, imm
    except np.linalg.LinAlgError:
        pass
    # Complex detour arc (12 steps) so fold crossings split cleanly into two real roots!
    rng = np.random.default_rng(99991)
    diff = sq_end - sq_start
    dnorm = np.linalg.norm(diff)
    gamma = 1j * 0.4 * max(dnorm, 1e-5) * rng.uniform(0.7, 1.3, size=17) * rng.choice([-1.0, 1.0], size=17)
    Zc = Z_start.copy()
    for s in range(12):
        t0, t1 = s / 12.0, (s + 1) / 12.0
        s0 = (1 - t0) * sq_start + t0 * sq_end + gamma * (4 * t0 * (1 - t0))
        s1 = (1 - t1) * sq_start + t1 * sq_end + gamma * (4 * t1 * (1 - t1))
        F0, J0 = eval_F_and_J(Zc, s0)
        F1, _ = eval_F_and_J(Zc, s1)
        try:
            Zc = Zc - np.linalg.solve(J0, (F1 - F0)[..., None])[..., 0]
            for _ in range(2):
                Fc, Jc = eval_F_and_J(Zc, s1)
                Zc = Zc - np.linalg.solve(Jc, Fc[..., None])[..., 0]
        except np.linalg.LinAlgError:
            return Zc, -1, -1, None
    Zc, err = newton_polish(Zc, sq_end, steps=8, tol=1e-13)
    tot, nr, imm = count_distinct_and_real(Zc, err, tol_sep=1e-7)
    return Zc, tot, nr, imm

def compute_all_dZ_dsq(Z, sq):
    """Exact sensitivity dZ/dsq for ALL 440 roots simultaneously in ~4ms!"""
    B = Z.shape[0]
    F0, J0 = eval_F_and_J(Z, sq)
    eps = 1e-8
    dF = np.zeros((B, 14, 17), dtype=np.complex128)
    for p in range(17):
        sp = sq.copy(); sp[p] += eps
        sm = sq.copy(); sm[p] -= eps
        Fp, _ = eval_F_and_J(Z, sp)
        Fm, _ = eval_F_and_J(Z, sm)
        dF[:, :, p] = (Fp - Fm) / (2.0 * eps)
    dZ = -np.linalg.solve(J0, dF)  # (440, 14, 17)
    return dZ

t0 = time.time()
tot, nr_cur, imm_cur = count_distinct_and_real(Z_cur, np.zeros(440), tol_sep=1e-7)
print(f"Loaded checkpoint: REAL = {2*nr_cur} / 880, pair |Im| = {np.sort(imm_cur[imm_cur>=1e-7])[::2]}")

best_nr = nr_cur
best_Z = Z_cur.copy()
best_sq = sq_cur.copy()

for it in range(150):
    if time.time() - t0 > 32.0:
        break
    X = 0.5 * (Z_cur[:, :7] + Z_cur[:, 7:])
    Y = -0.5j * (Z_cur[:, :7] - Z_cur[:, 7:])
    im2 = np.sum(X.imag**2 + Y.imag**2, axis=1)
    imm = np.max(np.maximum(np.abs(X.imag), np.abs(Y.imag)), axis=1)
    real_mask = imm < 1e-7
    nr = int(np.sum(real_mask))
    if nr == 440:
        print(f"\n*** EUREKA AT ITER {it} ({time.time()-t0:.2f}s): ALL 440 HALF-REALIZATIONS = 880 / 880 REAL REALIZATIONS ACHIEVED!! ***")
        best_nr, best_Z, best_sq = nr, Z_cur.copy(), sq_cur.copy()
        np.savez("SOLUTION_880.npz", Z=best_Z, sq=best_sq, lengths=np.sqrt(best_sq.real))
        break

    dZ = compute_all_dZ_dsq(Z_cur, sq_cur)
    dX = 0.5 * (dZ[:, :7, :] + dZ[:, 7:, :])
    dY = -0.5j * (dZ[:, :7, :] - dZ[:, 7:, :])

    # 1. Identify non-real conjugate pair representatives
    nr_idxs = np.where(~real_mask)[0]
    reps = []
    used = set()
    for i in nr_idxs:
        if i in used: continue
        reps.append(i)
        for j in nr_idxs:
            if np.max(np.abs(X[i] - np.conj(X[j]))) < 1e-4:
                used.add(j)

    # Gradients of im2 for each non-real pair: g_k of shape (17,)
    G_nr = []
    for r_i in reps:
        gk = 2.0 * np.sum(X[r_i, :, None].imag * dX[r_i].imag + Y[r_i, :, None].imag * dY[r_i].imag, axis=0)
        G_nr.append(gk)
    G_nr = np.array(G_nr)  # (n_pairs, 17)

    # 2. Identify close pairs of REAL roots that could collide if pushed together!
    real_idxs = np.where(real_mask)[0]
    Xr = X[real_idxs].real  # (nr, 7)
    Yr = Y[real_idxs].real  # (nr, 7)
    dist2_mat = np.sum((Xr[:, None, :] - Xr[None, :, :])**2 + (Yr[:, None, :] - Yr[None, :, :])**2, axis=2)
    np.fill_diagonal(dist2_mat, np.inf)
    # Find all unordered pairs (a, b) with dist2 < 0.20 (or top 80 closest real pairs!)
    tri_u, tri_v = np.triu_indices(len(real_idxs), k=1)
    pair_d2 = dist2_mat[tri_u, tri_v]
    close_order = np.argsort(pair_d2)[:90]

    A_ub = []
    b_ub = []
    for idx_c in close_order:
        ia = real_idxs[tri_u[idx_c]]
        ib = real_idxs[tri_v[idx_c]]
        D0 = pair_d2[idx_c]
        diff_X = X[ia].real - X[ib].real
        diff_Y = Y[ia].real - Y[ib].real
        d_diff_X = dX[ia].real - dX[ib].real
        d_diff_Y = dY[ia].real - dY[ib].real
        # grad of D(sq) = 2 * sum_v (diff_X * d_diff_X + diff_Y * d_diff_Y)
        h_ab = 2.0 * np.sum(diff_X[:, None] * d_diff_X + diff_Y[:, None] * d_diff_Y, axis=0)
        # Require D0 + h_ab @ d_sq >= 0.65 * D0  <=>  -h_ab @ d_sq <= 0.35 * D0
        # (And if D0 is very small, require h_ab @ d_sq >= 0 so it strictly separates!)
        rhs = 0.25 * D0 if D0 > 1e-3 else -0.05 * D0
        A_ub.append(-h_ab)
        b_ub.append(rhs)

    # Also keep mean(sq) approximately constant so scale doesn't blow up or collapse to 1:
    # Actually let scale float slightly inside [1.00002, 1.02]!
    for p in range(17):
        # sq_cur[p] + d_sq[p] >= 1.00004  => -d_sq[p] <= sq_cur[p] - 1.00004
        A_ub.append(-np.eye(17)[p])
        b_ub.append(float(sq_cur[p].real - 1.00004))
        # sq_cur[p] + d_sq[p] <= 1.02     => +d_sq[p] <= 1.02 - sq_cur[p]
        A_ub.append(np.eye(17)[p])
        b_ub.append(float(1.02 - sq_cur[p].real))

    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)

    # Alternate objective: target smallest-im2 pair, or sum of normalized gradients!
    mode = it % (len(reps) + 1)
    if mode < len(reps):
        c_obj = G_nr[mode] / (np.linalg.norm(G_nr[mode]) + 1e-30)
        # Also don't let other nonreal pairs blow up fast
    else:
        c_obj = np.sum(G_nr / (np.linalg.norm(G_nr, axis=1, keepdims=True) + 1e-30), axis=0)

    # Solve LP with box trust region
    step_accepted = False
    for tr in [6e-4, 2.5e-4, 1e-4, 4e-5, 1.5e-5, 5e-6]:
        res = linprog(c_obj, A_ub=A_ub, b_ub=b_ub, bounds=(-tr, tr), method="highs")
        if not res.success:
            continue
        d_sq = res.x
        if np.linalg.norm(d_sq) < 1e-12:
            continue
        # Also test overshooting 1.5x if a pair is right on the cusp of crossing 0!
        for mult in [1.0, 1.8]:
            sq_try = sq_cur + mult * d_sq
            if np.any(sq_try.real <= 1.00001):
                continue
            Zt, tot_t, nr_t, imm_t = fast_move_adaptive(Z_cur, sq_cur, sq_try)
            if tot_t != 440:
                continue
            Xt = 0.5 * (Zt[:, :7] + Zt[:, 7:])
            Yt = -0.5j * (Zt[:, :7] - Zt[:, 7:])
            im2_t = np.sum(Xt.imag**2 + Yt.imag**2, axis=1)
            cur_obj_val = float(np.sum(im2[~real_mask]))
            new_obj_val = float(np.sum(im2_t[imm_t >= 1e-7]))
            if nr_t > nr or (nr_t == nr and new_obj_val < cur_obj_val - 1e-7):
                if nr_t > nr:
                    print(f"*** [Iter {it:3d}, {time.time()-t0:.2f}s] LP BREAKTHROUGH!! REAL JUMPED {2*nr} -> {2*nr_t} / 880 !! rem |Im|={np.round(np.sort(imm_t[imm_t>=1e-7])[::2], 5)} ***")
                elif it % 5 == 0:
                    print(f"  [Iter {it:3d}, {time.time()-t0:.2f}s] REAL={2*nr_t}/880, sum_im2: {cur_obj_val:.5f} -> {new_obj_val:.5f}, pair |Im|={np.round(np.sort(imm_t[imm_t>=1e-7])[::2], 5)}, min_real_d2={pair_d2[close_order[0]]:.2e}")
                Z_cur, sq_cur = Zt, sq_try
                if nr_t > best_nr or (nr_t == best_nr):
                    best_nr, best_Z, best_sq = nr_t, Zt.copy(), sq_try.copy()
                step_accepted = True
                break
        if step_accepted:
            break

    if not step_accepted:
        print(f"[Iter {it:3d}] LP trust-region tight (REAL={2*nr}/880, pair |Im|={np.round(np.sort(imm[~real_mask])[::2], 5)}, min_real_d2={pair_d2[close_order[0]]:.2e}). Relaxing separation constraint slightly!")
        # Try a pure nullspace / slightly relaxed step
        A_rel = A_ub[:30]
        b_rel = np.maximum(b_ub[:30], 0.45 * pair_d2[close_order[:30]])
        res = linprog(c_obj, A_ub=A_rel, b_ub=b_rel, bounds=(-8e-5, 8e-5), method="highs")
        if res.success:
            sq_try = sq_cur + res.x
            Zt, tot_t, nr_t, imm_t = fast_move_adaptive(Z_cur, sq_cur, sq_try)
            if tot_t == 440 and nr_t >= nr:
                Z_cur, sq_cur = Zt, sq_try
                if nr_t > best_nr:
                    best_nr, best_Z, best_sq = nr_t, Zt.copy(), sq_try.copy()
                    print(f"*** [Iter {it:3d}] RELAXED LP BREAKTHROUGH!! REAL = {2*nr_t} / 880 !! ***")
                continue
        break

tot_f, nr_f, imm_f = count_distinct_and_real(best_Z, np.zeros(440), tol_sep=1e-7)
np.savez("lp_push_best.npz", Z=best_Z, sq=best_sq, lengths=np.sqrt(best_sq.real), nr=best_nr)
print(f"\nFinal status ({time.time()-t0:.2f}s): BEST REAL = {2*best_nr} / 880")
if best_nr < 440:
    print("Remaining pair |Im|:", np.sort(imm_f[imm_f >= 1e-7])[::2])
