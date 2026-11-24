#!/usr/bin/env python3
"""Tests for verify_l880_blind_recheck.py (issue 20): the L880 certificate is accepted, and each corruption is
rejected with a nonzero exit status, normally and under python3 -O."""
import copy
import json
from fractions import Fraction as Fr
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CERT = ROOT / "results" / "l880-all-880-real" / "l880_certificate.json"
SCRIPT = ROOT / "scripts" / "verify_l880_blind_recheck.py"


def run(path, optimize):
    cmd = [sys.executable, "-I"] + (["-O"] if optimize else []) + [str(SCRIPT), str(path)]
    return subprocess.run(cmd, capture_output=True, text=True)


class TestBlindRecheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, "r", encoding="utf-8") as fh:
            cls.cert = json.load(fh)
        cls.tmp = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def write(self, name, cert):
        p = Path(self.tmp.name) / (name.replace(" ", "_") + ".json")
        p.write_text(json.dumps(cert), encoding="utf-8")
        return p

    def short(self, k=20):
        c = copy.deepcopy(self.cert)
        c["centers_num"] = c["centers_num"][:k]
        c["certified_real_half_realizations"] = k
        c["certified_real_realizations_SE2"] = 2 * k
        c["complex_realizations_SE2"] = 2 * k
        return c

    def test_01_full_certificate_accepted(self):
        for opt in (False, True):
            r = run(CERT, opt)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("440 boxes", r.stdout)

    def test_02_unchanged_prefix_accepted(self):
        r = run(self.write("control", self.short()), True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_03_corruptions_rejected(self):
        cases = {}
        c = self.short(); c["centers_num"][3][5] += 2 ** (c["center_scale_exp2"] - 20); cases["shifted centre"] = c
        c = self.short(); c["edge_lengths"][0] = str(Fr(c["edge_lengths"][0]) + Fr(1, 10 ** 6)); cases["changed length"] = c
        c = self.short(); c["centers_num"].append(list(c["centers_num"][7]))
        c["certified_real_half_realizations"] = 21; c["certified_real_realizations_SE2"] = 42
        c["complex_realizations_SE2"] = 42; cases["duplicate box"] = c
        c = self.short(); c["pinned_vertices"]["3"][0] = str(Fr(c["pinned_vertices"]["3"][0]) + Fr(1, 10 ** 9)); cases["pinned vertex moved"] = c
        c = self.short(); c["edges"][0] = [1, 2]; cases["edge replaced"] = c
        c = self.short(); c["certified_real_realizations_SE2"] = 41; cases["claimed count wrong"] = c
        for name, cert in cases.items():
            p = self.write(name, cert)
            for opt in (False, True):
                r = run(p, opt)
                self.assertNotEqual(r.returncode, 0, f"-O={opt} accepted: {name}")


if __name__ == "__main__":
    unittest.main()
