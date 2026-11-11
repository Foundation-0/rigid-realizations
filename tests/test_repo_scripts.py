"""Tests for repository-root scripts (planar suite and NOTE.md schema verifier)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


class TestPlanarSuiteAndSchema(unittest.TestCase):
    def test_certify_planar_suite_missing_exits_nonzero(self):
        """python3 scripts/certify_planar_suite.py exits 1 when certificate JSON files are absent."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "certify_planar_suite.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("missing certificate", proc.stderr)

    def test_verify_note_schema_complex_count_mismatch(self):
        sys.path.insert(0, str(SCRIPTS))
        from verify_note_schema_2d import verify_certificate

        cert = {
            "graph": "triangle",
            "dimension": 2,
            "n": 3,
            "edges": [[1, 2], [1, 3], [2, 3]],
            "lengths": ["6", "5", "5"],
            "pinned": [1, 2],
            "unknowns": ["x3", "y3"],
            "boxes": [],
            "complex_count": 10,
            "claimed_real_count": 0,
            "made_by": "unittest",
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(cert, f)
            path = f.name
        self.addCleanup(os.unlink, path)
        with self.assertRaises(ValueError) as ctx:
            verify_certificate(path)
        self.assertIn("complex_count", str(ctx.exception))

    def test_certify_planar_suite_metadata_mismatch_exits_nonzero(self):
        sys.path.insert(0, str(SCRIPTS))
        from certify_planar_suite import cert_metadata_matches_spec

        spec_edges = [(1, 2), (2, 3), (1, 3), (4, 5), (5, 6), (4, 6), (1, 4), (2, 5), (3, 6)]
        spec = {
            "name": "Prism_6",
            "n": 6,
            "complex_count": 24,
            "edges": spec_edges,
            "lengths": ["1/1"] * 9,
        }
        cert = {
            "n": 6,
            "edges": [list(e) for e in spec_edges],
            "lengths": ["2/1"] * 9,
            "complex_count": 24,
        }
        self.assertIn("lengths", cert_metadata_matches_spec(cert, spec))

        results = REPO_ROOT / "rigid_realizations_l880_pr_bundle" / "results"
        results.mkdir(parents=True, exist_ok=True)
        bad_cert = results / "prism_6_24_cert.json"
        with open(bad_cert, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "graph": "Prism_6",
                    "dimension": 2,
                    "n": 6,
                    "edges": [list(e) for e in spec_edges],
                    "lengths": ["9/8"] * 9,
                    "pinned": [1, 2],
                    "complex_count": 24,
                    "claimed_real_count": 0,
                    "boxes": [],
                },
                f,
            )
        self.addCleanup(lambda: bad_cert.unlink(missing_ok=True))
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "certify_planar_suite.py")],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("metadata mismatch", proc.stderr)


if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPTS))
    unittest.main(verbosity=2)
