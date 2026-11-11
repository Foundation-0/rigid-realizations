"""3D G160 squared-distance evaluator and damped Newton polisher (no homotopy tracker or driver in this file)."""
import numpy as np

EDGES_G160 = [
    (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
    (2, 3), (2, 6), (2, 7), (2, 8),
    (3, 4), (3, 7),
    (4, 5), (4, 7),
    (5, 6), (5, 7), (5, 8),
    (6, 8),
    (7, 8),
]

BARTZOS_G160 = np.array([
    1.999, 1.568, 6.611, 4.402, 1.994, 1.426, 0.879, 10.536, 0.847,
    6.494, 10.447, 7.278, 11.993, 4.321, 11.239, 4.279, 0.398, 10.474,
], dtype=np.float64)

FREE_V3 = [4, 5, 6, 7, 8]
V3_MAP = {v: i for i, v in enumerate(FREE_V3)}
REM_E3 = [idx for idx, e in enumerate(EDGES_G160) if e not in [(1, 2), (1, 3), (2, 3)]]
_A3_FREE = [V3_MAP.get(EDGES_G160[i][0], -1) for i in REM_E3]
_B3_FREE = [V3_MAP.get(EDGES_G160[i][1], -1) for i in REM_E3]
_A3_PIN = [EDGES_G160[i][0] if EDGES_G160[i][0] not in V3_MAP else -1 for i in REM_E3]
_B3_PIN = [EDGES_G160[i][1] if EDGES_G160[i][1] not in V3_MAP else -1 for i in REM_E3]


def get_pinned_3d(sq):
    s12, s13, s23 = sq[0], sq[1], sq[5]
    L12 = np.sqrt(s12)
    x3 = (s12 + s13 - s23) / (2.0 * L12)
    y3 = np.sqrt(s13 - x3 * x3)
    return {
        1: np.array([0.0 + 0j, 0.0 + 0j, 0.0 + 0j]),
        2: np.array([L12, 0.0 + 0j, 0.0 + 0j]),
        3: np.array([x3, y3, 0.0 + 0j]),
    }


def eval_F_J_3d(Z, sq):
    B = Z.shape[0]
    pin = get_pinned_3d(sq)
    F = np.zeros((B, 15), dtype=np.complex128)
    J = np.zeros((B, 15, 15), dtype=np.complex128)
    for eq_i, e_idx in enumerate(REM_E3):
        ia, ib = _A3_FREE[eq_i], _B3_FREE[eq_i]
        pa = Z[:, 3 * ia : 3 * ia + 3] if ia >= 0 else pin[_A3_PIN[eq_i]][None, :]
        pb = Z[:, 3 * ib : 3 * ib + 3] if ib >= 0 else pin[_B3_PIN[eq_i]][None, :]
        d = pa - pb
        F[:, eq_i] = d[:, 0] ** 2 + d[:, 1] ** 2 + d[:, 2] ** 2 - sq[e_idx]
        if ia >= 0:
            J[:, eq_i, 3 * ia : 3 * ia + 3] = 2.0 * d
        if ib >= 0:
            J[:, eq_i, 3 * ib : 3 * ib + 3] = -2.0 * d
    return F, J


def polish_3d(Z, sq, steps=8, tol=1e-13):
    Zc = Z.copy()
    for _ in range(steps):
        F, J = eval_F_J_3d(Zc, sq)
        err = np.max(np.abs(F), axis=1)
        if len(err) == 0 or np.max(err) < tol:
            return Zc, err
        try:
            Zc = Zc - np.linalg.solve(J, F[..., None])[..., 0]
        except np.linalg.LinAlgError:
            break
    F, _ = eval_F_J_3d(Zc, sq)
    return Zc, np.max(np.abs(F), axis=1)
