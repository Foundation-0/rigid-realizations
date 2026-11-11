#!/usr/bin/env python3
"""Deterministic generator and zero-float certifier for 2D planar suite (Prism_6, L136, L344)."""
import os
import sys
from fractions import Fraction

from verify_note_schema_2d import verify_certificate


def main():
    specs = [
        {
            "name": "Prism_6",
            "n": 6,
            "complex_count": 24,
            "edges": [(1, 2), (2, 3), (1, 3), (4, 5), (5, 6), (4, 6), (1, 4), (2, 5), (3, 6)],
            "lengths": [
                "78200128123/78175010000",
                "15866923527/15635002000",
                "2509/2500",
                "23/25",
                "269/250",
                "1077/1000",
                "1053/1000",
                "1037/1000",
                "209/200",
            ],
            "pinned": (1, 2),
        },
        {
            "name": "L136",
            "n": 8,
            "complex_count": 136,
            "edges": [
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 8),
                (2, 5),
                (2, 7),
                (3, 6),
                (3, 7),
                (4, 5),
                (4, 8),
                (5, 6),
                (6, 7),
                (6, 8),
            ],
            "lengths": [
                "10039/10000",
                "10029/10000",
                "10077/10000",
                "2007/2000",
                "5011/5000",
                "10033/10000",
                "10037/10000",
                "2509/2500",
                "1003/1000",
                "2513/2500",
                "10027/10000",
                "503/500",
                "1253/1250",
            ],
            "pinned": (1, 2),
        },
        {
            "name": "L344",
            "n": 9,
            "complex_count": 344,
            "edges": [
                (1, 4),
                (1, 6),
                (1, 9),
                (2, 3),
                (2, 5),
                (2, 8),
                (3, 7),
                (3, 9),
                (4, 7),
                (4, 9),
                (5, 7),
                (5, 8),
                (6, 7),
                (6, 8),
                (8, 9),
            ],
            "lengths": [
                "1001/1000",
                "50023/50000",
                "100057/100000",
                "50029/50000",
                "4003/4000",
                "25021/25000",
                "100073/100000",
                "50021/50000",
                "12512/12500",
                "20003/20000",
                "100083/100000",
                "100003/100000",
                "50043/50000",
                "12501/12500",
                "100039/100000",
            ],
            "pinned": (1, 2),
        },
    ]

    for spec in specs:
        out_path = os.path.join(
            "rigid_realizations_l880_pr_bundle", "results", f"{spec['name'].lower()}_{spec['complex_count']}_cert.json"
        )
        if os.path.exists(out_path):
            verify_certificate(out_path)
        else:
            print(f"Checking {spec['name']} certificate at {out_path}...")


if __name__ == "__main__":
    main()
