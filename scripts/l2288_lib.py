"""Isotropic 16x16 evaluator and Newton polisher for 11-vertex L2288 (GKT code 18120782205838348)."""
import numpy as np


def decode_msb(n: int, code: int):
    m_pairs = n * (n - 1) // 2
    pairs = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)]
    return [pairs[k] for k in range(m_pairs) if (code >> (m_pairs - 1 - k)) & 1]


EDGES11 = decode_msb(11, 18120782205838348)
VA, VB, VC = 3, 9, 10
IDX_AB = EDGES11.index((3, 9))
IDX_AC = EDGES11.index((3, 10))
IDX_BC = EDGES11.index((9, 10))

FREE11 = [v for v in range(1, 12) if v not in (VA, VB, VC)]
V11_MAP = {v: i for i, v in enumerate(FREE11)}
REM_E11 = [idx for idx in range(19) if idx not in (IDX_AB, IDX_AC, IDX_BC)]

_A11_F = [V11_MAP.get(EDGES11[i][0], -1) for i in REM_E11]
_B11_F = [V11_MAP.get(EDGES11[i][1], -1) for i in REM_E11]
_A11_P = [EDGES11[i][0] if EDGES11[i][0] not in V11_MAP else -1 for i in REM_E11]
_B11_P = [EDGES11[i][1] if EDGES11[i][1] not in V11_MAP else -1 for i in REM_E11]


def get_pinned11(sq):
    sab, sac, sbc = sq[IDX_AB], sq[IDX_AC], sq[IDX_BC]
    Lab = np.sqrt(sab)
    xc = (sab + sac - sbc) / (2.0 * Lab)
    yc = np.sqrt(sac - xc * xc)
    u = {VA: 0.0 + 0j, VB: Lab + 0j, VC: xc + 1j * yc}
    w = {VA: 0.0 + 0j, VB: Lab + 0j, VC: xc - 1j * yc}
    return u, w


def eval_FJ11(Z, sq):
    B = Z.shape[0]
    up, wp = get_pinned11(sq)
    F = np.zeros((B, 16), dtype=np.complex128)
    J = np.zeros((B, 16, 16), dtype=np.complex128)
    for eq_i, e_i in enumerate(REM_E11):
        ia, ib = _A11_F[eq_i], _B11_F[eq_i]
        ua = Z[:, ia] if ia >= 0 else up[_A11_P[eq_i]]
        wa = Z[:, 8 + ia] if ia >= 0 else wp[_A11_P[eq_i]]
        ub = Z[:, ib] if ib >= 0 else up[_B11_P[eq_i]]
        wb = Z[:, 8 + ib] if ib >= 0 else wp[_B11_P[eq_i]]
        du, dw = ua - ub, wa - wb
        F[:, eq_i] = du * dw - sq[e_i]
        if ia >= 0:
            J[:, eq_i, ia] = dw
            J[:, eq_i, 8 + ia] = du
        if ib >= 0:
            J[:, eq_i, ib] = -dw
            J[:, eq_i, 8 + ib] = -du
    return F, J


def polish11(Z, sq, steps=7, tol=1e-13):
    Zc = Z.copy()
    for _ in range(steps):
        F, J = eval_FJ11(Zc, sq)
        err = np.max(np.abs(F), axis=1)
        if len(err) == 0 or np.max(err) < tol:
            return Zc, err
        try:
            Zc = Zc - np.linalg.solve(J, F[..., None])[..., 0]
        except np.linalg.LinAlgError:
            break
    F, _ = eval_FJ11(Zc, sq)
    return Zc, np.max(np.abs(F), axis=1)
