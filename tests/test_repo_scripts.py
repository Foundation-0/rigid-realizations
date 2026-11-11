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


def run_certify_planar_suite(results_dir: Path, *, cwd=REPO_ROOT):
    env = {**os.environ, "PLANAR_SUITE_RESULTS_DIR": str(results_dir)}
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "certify_planar_suite.py")],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
    )


class TestPlanarSuiteAndSchema(unittest.TestCase):
    def test_certify_planar_suite_missing_exits_nonzero(self):
        """python3 scripts/certify_planar_suite.py exits 1 when certificate JSON files are absent."""
        with tempfile.TemporaryDirectory() as tmp:
            proc = run_certify_planar_suite(Path(tmp))
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
        from certify_planar_suite import SUITE_SPECS, cert_metadata_matches_spec

        spec = SUITE_SPECS[0]
        cert = {
            "n": spec["n"],
            "edges": [list(e) for e in spec["edges"]],
            "lengths": list(spec["lengths"]),
            "lengths_bad": True,
            "complex_count": spec["complex_count"],
            "pinned": list(spec["pinned"]),
        }
        cert["lengths"] = ["9/8"] * len(spec["lengths"])
        self.assertIn("lengths", cert_metadata_matches_spec(cert, spec))

        with tempfile.TemporaryDirectory() as tmp:
            bad_path = Path(tmp) / "prism_6_24_cert.json"
            payload = {
                "graph": "Prism_6",
                "dimension": 2,
                "n": spec["n"],
                "edges": [list(e) for e in spec["edges"]],
                "lengths": ["9/8"] * len(spec["lengths"]),
                "pinned": list(spec["pinned"]),
                "complex_count": spec["complex_count"],
                "claimed_real_count": spec["complex_count"],
                "boxes": [],
            }
            with open(bad_path, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            proc = run_certify_planar_suite(Path(tmp))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("lengths", proc.stderr)

    def test_suite_specs_pins_are_edges(self):
        sys.path.insert(0, str(SCRIPTS))
        from certify_planar_suite import SUITE_SPECS, validate_suite_specs

        self.assertIsNone(validate_suite_specs(SUITE_SPECS))
        bad = dict(SUITE_SPECS[2])
        bad["pinned"] = (1, 2)
        self.assertIn("not an edge", validate_suite_specs([bad]))

    def test_cert_pin_not_on_edge_rejected(self):
        sys.path.insert(0, str(SCRIPTS))
        from certify_planar_suite import SUITE_SPECS, cert_metadata_matches_spec

        l344 = SUITE_SPECS[2]
        self.assertEqual(l344["pinned"], (1, 4))
        cert = {
            "n": l344["n"],
            "edges": [list(e) for e in l344["edges"]],
            "lengths": list(l344["lengths"]),
            "complex_count": l344["complex_count"],
            "pinned": [1, 2],
            "claimed_real_count": l344["complex_count"],
        }
        err = cert_metadata_matches_spec(cert, l344)
        self.assertIsNotNone(err)
        self.assertIn("pinned", err)

    def test_certify_planar_suite_partial_count_exits_nonzero(self):
        sys.path.insert(0, str(SCRIPTS))
        from certify_planar_suite import SUITE_SPECS

        spec = SUITE_SPECS[0]
        with tempfile.TemporaryDirectory() as tmp:
            partial = Path(tmp) / "prism_6_24_cert.json"
            payload = {
                "graph": "Prism_6",
                "dimension": 2,
                "n": spec["n"],
                "edges": [list(e) for e in spec["edges"]],
                "lengths": list(spec["lengths"]),
                "pinned": list(spec["pinned"]),
                "complex_count": spec["complex_count"],
                "claimed_real_count": 22,
                "boxes": [],
            }
            with open(partial, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            proc = run_certify_planar_suite(Path(tmp))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("22", proc.stderr)
        self.assertIn("24", proc.stderr)


if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPTS))
    unittest.main(verbosity=2)
