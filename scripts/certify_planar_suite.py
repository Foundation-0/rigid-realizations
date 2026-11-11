#!/usr/bin/env python3
"""For Prism_6, L136, and L344: verify each rigid_realizations_l880_pr_bundle/results/{name}_{count}_cert.json when present; exit nonzero if any expected file is missing (does not write JSON)."""
import os
import sys

from verify_note_schema_2d import verify_certificate

RESULTS = os.path.join("rigid_realizations_l880_pr_bundle", "results")

CERT_FILES = {
    "Prism_6": os.path.join(RESULTS, "prism_6_24_cert.json"),
    "L136": os.path.join(RESULTS, "l136_136_cert.json"),
    "L344": os.path.join(RESULTS, "l344_344_cert.json"),
}


def main():
    missing = []
    for name, out_path in CERT_FILES.items():
        if os.path.isfile(out_path):
            verify_certificate(out_path)
        else:
            missing.append((name, out_path))
    if missing:
        for name, out_path in missing:
            print(f"ERROR: missing certificate for {name}: {out_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
