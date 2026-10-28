# L880 unresolved roots

The [primary paper, section 4.1](https://arxiv.org/html/1811.12800v1#S4.SS1) reports 868 numerical real solutions but retains a verified lower bound of 860. It describes small triangle-inequality violations in the distance-system solutions. That observation does not classify the remaining candidates as real, nonreal, coincident or artifacts.

Acquire the original distance-system roots and the source archive before any classification. Preserve precision, solver version, root IDs and the original constraints. Replay with higher precision, test the triangle inequalities with outward enclosures, then attempt independent box certification. Nearby lengths need a bounded, seeded search and a separate log for every failed or unresolved root.

The diagnostic records scale-dependent numerical quantities only. It never discards a candidate or infers completeness.
