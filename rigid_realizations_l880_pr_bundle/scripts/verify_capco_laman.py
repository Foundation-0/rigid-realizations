#!/usr/bin/env python3
"""
Standalone Pure-Python Combinatorial Verifier for Complex Realization Counts c_2(G)
Implementing Proposition 2.10, Lemmas 2.18-2.19, and Theorem 4.7 of:
  Capco, Gallet, Grasegger, Koutschan, Lubbes & Schicho (2018),
  "The number of realizations of a Laman graph", SIAGA 2(1), 95-125 (arXiv:1701.05500v2).

Uses ONLY Python's standard library. Proves combinatorially from first principles that
c_2(L880) = Lam(L880, L880) = 880, establishing the sharp upper bound r_2(L880) <= 880.
"""
from functools import lru_cache
import time


def _canonicalize_graph(edges):
    """
    Given a tuple of edges (u, v) representing a multigraph without isolated vertices,
    relabel vertices canonically by first appearance in sorted edge order?
    Wait: in a bigraph B = (G, H), edge i of G is paired with edge i of H!
    So biedge bijection MUST be preserved when canonicalizing (G, H).
    """
    pass


def _components_and_dim(num_verts, endpts):
    """
    endpts: tuple of (u, v) for each biedge in 0..m-1, with 0 <= u <= v < num_verts.
    Note: isolated vertices do not affect dim(G) = |V| - |CC(G)|!
    Wait: let's verify! If an isolated vertex v is added to G, |V| increases by 1 AND
    |CC(G)| increases by 1, so |V| - |CC(G)| is INVARIANT under isolated vertices!
    Even better: dim(G) equals the rank of the cycle matroid (spanning forest size)!
    """
    parent = list(range(num_verts))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    rank = 0
    has_loop = False
    for u, v in endpts:
        if u == v:
            has_loop = True
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            rank += 1
    return rank, has_loop


def _find_bridges(num_verts, endpts):
    """Return a bitmask of biedge indices that are bridges in the multigraph."""
    m = len(endpts)
    adj = [[] for _ in range(num_verts)]
    for idx, (u, v) in enumerate(endpts):
        if u != v:
            adj[u].append((v, idx))
            adj[v].append((u, idx))

    tin = [-1] * num_verts
    low = [-1] * num_verts
    timer = 0
    bridge_mask = 0

    for start in range(num_verts):
        if tin[start] != -1 or not adj[start]:
            continue
        # Iterative DFS to avoid recursion limit and stay fast
        stack = [(start, -1, 0)]
        tin[start] = low[start] = timer
        timer += 1
        while stack:
            u, p_edge, it = stack[-1]
            if it < len(adj[u]):
                v, e_idx = adj[u][it]
                stack[-1] = (u, p_edge, it + 1)
                if e_idx == p_edge:
                    continue
                if tin[v] != -1:
                    if tin[v] < low[u]:
                        low[u] = tin[v]
                else:
                    tin[v] = low[v] = timer
                    timer += 1
                    stack.append((v, e_idx, 0))
            else:
                stack.pop()
                if stack:
                    pu, _, _ = stack[-1]
                    if low[u] < low[pu]:
                        low[pu] = low[u]
                    if low[u] > tin[pu]:
                        bridge_mask |= (1 << p_edge)
    return bridge_mask


def _contract(num_verts, endpts, mask_to_contract, m):
    """
    Compute quotient graph G / M on remaining biedges E \\ M (where mask_to_contract marks M).
    Returns (new_num_verts, tuple_of_remaining_endpts, has_loop).
    """
    parent = list(range(num_verts))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(m):
        if (mask_to_contract >> i) & 1:
            u, v = endpts[i]
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv

    remap = {}
    nxt = 0
    rem = []
    for i in range(m):
        if not ((mask_to_contract >> i) & 1):
            ru, rv = find(endpts[i][0]), find(endpts[i][1])
            if ru == rv:
                return 0, (), True
            if ru not in remap:
                remap[ru] = nxt
                nxt += 1
            if rv not in remap:
                remap[rv] = nxt
                nxt += 1
            a, b = remap[ru], remap[rv]
            rem.append((a, b) if a < b else (b, a))
    return nxt, tuple(rem), False


def _delete(endpts, mask_to_delete, m):
    """
    Compute deletion graph G \\ M on remaining biedges E \\ M (dropping isolated vertices).
    Returns (new_num_verts, tuple_of_remaining_endpts).
    """
    remap = {}
    nxt = 0
    rem = []
    for i in range(m):
        if not ((mask_to_delete >> i) & 1):
            u, v = endpts[i]
            if u not in remap:
                remap[u] = nxt
                nxt += 1
            if v not in remap:
                remap[v] = nxt
                nxt += 1
            a, b = remap[u], remap[v]
            rem.append((a, b) if a < b else (b, a))
    return nxt, tuple(rem)


def _canon_bigraph(nv_g, g_edges, nv_h, h_edges):
    """Canonicalize biedge order and vertex labels for memoization."""
    # Sort biedges lexicographically by (g_edge, h_edge)? Wait: vertex labels depend on order!
    # Simple order-preserving relabeling after sorting by degree signature gives high cache hit rate.
    m = len(g_edges)
    deg_g = [0] * nv_g
    deg_h = [0] * nv_h
    for u, v in g_edges:
        deg_g[u] += 1
        deg_g[v] += 1
    for u, v in h_edges:
        deg_h[u] += 1
        deg_h[v] += 1
    order = sorted(
        range(m),
        key=lambda i: (
            min(deg_g[g_edges[i][0]], deg_g[g_edges[i][1]]),
            max(deg_g[g_edges[i][0]], deg_g[g_edges[i][1]]),
            min(deg_h[h_edges[i][0]], deg_h[h_edges[i][1]]),
            max(deg_h[h_edges[i][0]], deg_h[h_edges[i][1]]),
            g_edges[i],
            h_edges[i],
        ),
    )
    map_g = {}
    ng = 0
    new_g = []
    map_h = {}
    nh = 0
    new_h = []
    for idx in order:
        ug, vg = g_edges[idx]
        if ug not in map_g:
            map_g[ug] = ng; ng += 1
        if vg not in map_g:
            map_g[vg] = ng; ng += 1
        ag, bg = map_g[ug], map_g[vg]
        new_g.append((ag, bg) if ag < bg else (bg, ag))

        uh, vh = h_edges[idx]
        if uh not in map_h:
            map_h[uh] = nh; nh += 1
        if vh not in map_h:
            map_h[vh] = nh; nh += 1
        ah, bh = map_h[uh], map_h[vh]
        new_h.append((ah, bh) if ah < bh else (bh, ah))
    return ng, tuple(new_g), nh, tuple(new_h)


@lru_cache(maxsize=None)
def laman_bigraph(nv_g, g_edges, nv_h, h_edges):
    """Compute Lam(B) for a pseudo-Laman bigraph B = (G, H) via Capco et al. Theorem 4.7."""
    m = len(g_edges)
    if m == 0:
        return 0
    # Proposition 2.10: check loops and single-edge base case
    for i in range(m):
        if g_edges[i][0] == g_edges[i][1] or h_edges[i][0] == h_edges[i][1]:
            return 0
    if m == 1:
        # Both G and H have 1 non-loop edge -> Lam(B) = 1
        return 1

    dim_g, loop_g = _components_and_dim(nv_g, g_edges)
    dim_h, loop_h = _components_and_dim(nv_h, h_edges)
    if loop_g or loop_h or (dim_g + dim_h != m + 1):
        return 0

    # Lemmas 2.18 & 2.19: bridge reductions!
    bg = _find_bridges(nv_g, g_edges)
    bh = _find_bridges(nv_h, h_edges)
    if bg & bh:
        return 0  # Lemma 2.18: common bridge -> Lam(B) = 0
    only_bridge = bg ^ bh
    if only_bridge:
        # Lemma 2.19: delete all edges that are bridges in one graph? Wait:
        # Deleting one bridge might change bridges in the other graph! Delete ONE bridge at a time.
        lsb = only_bridge & -only_bridge
        ng2, ge2 = _delete(g_edges, lsb, m)
        nh2, he2 = _delete(h_edges, lsb, m)
        return laman_bigraph(*_canon_bigraph(ng2, ge2, nh2, he2))

    # Choose pivot biedge e_bar = 0 (say, incident to highest-multiplicity / parallel edge if present)
    e_bar = 0
    for i in range(m):
        if g_edges.count(g_edges[i]) > 1 or h_edges.count(h_edges[i]) > 1:
            e_bar = i
            break
    eb_mask = 1 << e_bar

    total = 0
    # Term 1: Lam(^{e_bar} B) = (G / {e_bar}, H \ {e_bar})
    ng1, ge1, lp1 = _contract(nv_g, g_edges, eb_mask, m)
    if not lp1:
        nh1, he1 = _delete(h_edges, eb_mask, m)
        total += laman_bigraph(*_canon_bigraph(ng1, ge1, nh1, he1))

    # Term 2: Lam(B^{e_bar}) = (G \ {e_bar}, H / {e_bar})
    nh2, he2, lp2 = _contract(nv_h, h_edges, eb_mask, m)
    if not lp2:
        ng2, ge2 = _delete(g_edges, eb_mask, m)
        total += laman_bigraph(*_canon_bigraph(ng2, ge2, nh2, he2))

    # Term 3: Sum over (M, N) with M union N = E, M intersect N = {e_bar}, |M| >= 2, |N| >= 2,
    # and BOTH ^{M}B and B^{N} pseudo-Laman and loop-free!
    # Notice:
    # ^{M}B = (G / M, H \ M) has |E \ M| = |N| - 1 biedges!
    # When is ^{M}B loop-free and pseudo-Laman?
    # 1) Loop-freeness of G / M means M is a CLOSED edge set (flat) in the cycle matroid of G!
    #    Wait: an edge e not in M becomes a loop in G / M iff its endpoints are connected in (V, M)!
    # 2) Pseudo-Laman of ^{M}B = (G / M, H \ M):
    #    dim(G / M) + dim(H \ M) == (m - |M|) + 1!
    # AND notice that N = (E \ M) union {e_bar} is UNIQUELY determined by M!
    # We can pre-filter valid M subsets or valid N subsets independently, or check ^{M}B first
    # and ONLY evaluate B^{N} when Lam(^{M}B) > 0!
    other_edges = [i for i in range(m) if i != e_bar]
    r_len = len(other_edges)  # m - 1
    full_mask = (1 << m) - 1

    # Iterate over non-empty proper subsets S of E \ {e_bar}:
    # M = S | eb_mask (so |M| = |S| + 1 >= 2), N = ((full_mask ^ M) | eb_mask) (so |N| = m - |S| >= 2)
    for sub in range(1, (1 << r_len) - 1):
        m_mask = eb_mask
        s_cnt = 0
        # Fast bit mapping
        tmp = sub
        while tmp:
            lsb = tmp & -tmp
            bit_idx = lsb.bit_length() - 1
            m_mask |= (1 << other_edges[bit_idx])
            s_cnt += 1
            tmp ^= lsb

        # Quick check on ^{M}B = (G / M, H \ M) before recursing:
        ng_m, ge_m, lp_m = _contract(nv_g, g_edges, m_mask, m)
        if lp_m:
            continue
        n_mask = (full_mask ^ m_mask) | eb_mask
        nh_n, he_n, lp_n = _contract(nv_h, h_edges, n_mask, m)
        if lp_n:
            continue

        nh_m, he_m = _delete(h_edges, m_mask, m)
        rem_m = m - (s_cnt + 1)
        dg_m, _ = _components_and_dim(ng_m, ge_m)
        dh_m, _ = _components_and_dim(nh_m, he_m)
        if dg_m + dh_m != rem_m + 1:
            continue

        ng_n, ge_n = _delete(g_edges, n_mask, m)
        rem_n = s_cnt
        dg_n, _ = _components_and_dim(ng_n, ge_n)
        dh_n, _ = _components_and_dim(nh_n, he_n)
        if dg_n + dh_n != rem_n + 1:
            continue

        val_m = laman_bigraph(*_canon_bigraph(ng_m, ge_m, nh_m, he_m))
        if val_m == 0:
            continue
        val_n = laman_bigraph(*_canon_bigraph(ng_n, ge_n, nh_n, he_n))
        if val_n:
            total += val_m * val_n

    return total


def compute_c2(edges_1based):
    """
    Compute the exact complex planar realization count c_2(G) modulo SE(2)
    for a Laman graph G with 1-indexed edges.
    By Proposition 2.11 of Capco et al. (2018), c_2(G) = Lam(G, G).
    """
    verts = sorted({u for e in edges_1based for u in e})
    vmap = {v: i for i, v in enumerate(verts)}
    ed = tuple((min(vmap[u], vmap[v]), max(vmap[u], vmap[v])) for u, v in edges_1based)
    nv = len(verts)
    return laman_bigraph(*_canon_bigraph(nv, ed, nv, ed))


if __name__ == "__main__":
    t0 = time.time()
    # Test benchmark Laman graphs from Capco et al. (2018) Table 2 & OEIS A306420:
    k3 = [(1, 2), (2, 3), (1, 3)]
    k4_e = [(1, 2), (2, 3), (1, 3), (2, 4), (3, 4)]
    prism6 = [(1, 2), (2, 3), (1, 3), (4, 5), (5, 6), (4, 6), (1, 4), (2, 5), (3, 6)]
    l880 = [
        (1, 4), (1, 8), (1, 10), (2, 3), (2, 7), (2, 10), (3, 7), (3, 9),
        (4, 8), (4, 9), (5, 7), (5, 8), (5, 10), (6, 7), (6, 8), (6, 9), (9, 10)
    ]
    assert compute_c2(k3) == 2, f"Expected 2, got {compute_c2(k3)}"
    assert compute_c2(k4_e) == 4, f"Expected 4, got {compute_c2(k4_e)}"
    assert compute_c2(prism6) == 24, f"Expected 24, got {compute_c2(prism6)}"
    c2_l880 = compute_c2(l880)
    dt = time.time() - t0
    print(f"Capco et al. Theorem 4.7 exact combinatorial verification:")
    print(f"  c_2(K_3)     = 2")
    print(f"  c_2(K_4 - e) = 4")
    print(f"  c_2(Prism_6) = 24")
    print(f"  c_2(L_880)   = {c2_l880}  (elapsed: {dt:.3f}s)")
    assert c2_l880 == 880, f"Expected 880, got {c2_l880}"
