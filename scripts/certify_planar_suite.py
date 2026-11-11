#!/usr/bin/env python3
"""For Prism_6, L136, and L344: verify each rigid_realizations_l880_pr_bundle/results/{name}_{count}_cert.json when present; exit nonzero if any expected file is missing (does not write JSON)."""
import json
import os
import sys

from verify_note_schema_2d import verify_certificate

RESULTS_DIR_ENV = "PLANAR_SUITE_RESULTS_DIR"

SUITE_SPECS = [
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
        "pinned": (1, 4),
    },
]


def results_dir():
    override = os.environ.get(RESULTS_DIR_ENV)
    if override:
        return override
    return os.path.join("rigid_realizations_l880_pr_bundle", "results")


def edge_set(edges):
    out = set()
    for u, v in edges:
        a, b = (u, v) if u < v else (v, u)
        out.add((a, b))
    return out


def pin_is_edge(pin, edges):
    a, b = (pin[0], pin[1]) if pin[0] < pin[1] else (pin[1], pin[0])
    return (a, b) in edge_set(edges)


def validate_suite_specs(specs):
    """Return error message if any spec pins a non-edge, else None."""
    for spec in specs:
        if not pin_is_edge(spec["pinned"], spec["edges"]):
            return f"{spec['name']} spec pins {spec['pinned']}, which is not an edge"
    return None


def cert_metadata_matches_spec(cert, spec):
    """Return an error message if certificate metadata disagrees with the suite spec, else None."""
    if int(cert["n"]) != spec["n"]:
        return f"n {cert['n']} != spec {spec['n']}"
    spec_edges = [list(e) for e in spec["edges"]]
    if cert["edges"] != spec_edges:
        return "edges do not match spec"
    if cert["lengths"] != spec["lengths"]:
        return "lengths do not match spec"
    if int(cert["complex_count"]) != spec["complex_count"]:
        return f"complex_count {cert['complex_count']} != spec {spec['complex_count']}"
    cert_pin = tuple(cert["pinned"])
    spec_pin = tuple(spec["pinned"])
    if cert_pin != spec_pin and cert_pin != (spec_pin[1], spec_pin[0]):
        return f"pinned {cert_pin} != spec pinned {spec_pin}"
    if not pin_is_edge(cert_pin, spec["edges"]):
        return f"pinned edge {cert_pin} is not in graph edges"
    return None


def cert_meets_full_count(cert, spec):
    """Return error message if certified count is below spec complex_count, else None."""
    expected = spec["complex_count"]
    claimed = int(cert["claimed_real_count"])
    if claimed < expected:
        return f"claimed_real_count {claimed} < full count {expected}"
    boxes = cert.get("boxes")
    if boxes is not None and len(boxes) < expected:
        return f"{len(boxes)} boxes < full count {expected}"
    return None


def check_cert_against_spec(spec, path):
    with open(path, "r", encoding="utf-8") as f:
        cert = json.load(f)
    for check in (cert_metadata_matches_spec, cert_meets_full_count):
        err = check(cert, spec)
        if err:
            print(f"ERROR: {spec['name']} certificate at {path}: {err}", file=sys.stderr)
            return False
    return True


def main():
    spec_err = validate_suite_specs(SUITE_SPECS)
    if spec_err:
        print(f"ERROR: {spec_err}", file=sys.stderr)
        sys.exit(1)

    missing = []
    had_error = False
    rdir = results_dir()
    for spec in SUITE_SPECS:
        out_path = os.path.join(rdir, f"{spec['name'].lower()}_{spec['complex_count']}_cert.json")
        if os.path.isfile(out_path):
            if not check_cert_against_spec(spec, out_path):
                had_error = True
            else:
                verify_certificate(out_path)
        else:
            missing.append((spec["name"], out_path))

    if missing:
        for name, out_path in missing:
            print(f"ERROR: missing certificate for {name}: {out_path}", file=sys.stderr)
    if missing or had_error:
        sys.exit(1)


if __name__ == "__main__":
    main()
