#!/usr/bin/env python3
"""Tests for the L2288 certificate: it is accepted, and each kind of corruption is rejected.

The corrupted cases keep only the first 20 boxes so that each run takes about one second. Every case runs twice,
normally and under python3 -O, because a proof step that is a bare assert would pass under -O.
"""
import copy
import json
from fractions import Fraction as Fr
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CERT = ROOT / "results" / "l2288-all-2288-real" / "l2288_certificate.json"
INDEPENDENT = ROOT / "scripts" / "verify_l2288_independent.py"
EXACT = ROOT / "scripts" / "verify_l2288_exact.py"
CODE = "18120782205838348"


def run(script, path, optimize, *extra):
    cmd = [sys.executable, "-I"] + (["-O"] if optimize else []) + [str(script), str(path)] + list(extra)
    return subprocess.run(cmd, capture_output=True, text=True)


class TestL2288Certificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, "r", encoding="utf-8") as fh:
            cls.cert = json.load(fh)
        cls.tmp = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def cases(self):
        d = self.cert
        out = {}

        def start():
            c = copy.deepcopy(d)
            c["centers"] = c["centers"][:20]
            return c

        c = start(); c["centers"][3][5] += 2 ** (c["center_scale_exp2"] - 30); out["shifted centre"] = c
        c = start(); c["sq_lengths"][0] = str(Fr(c["sq_lengths"][0]) + Fr(1, 10 ** 6)); out["changed length"] = c
        c = start(); c["centers"].append(list(c["centers"][7])); out["duplicate box"] = c
        c = start(); c["pinned"]["10"][0] = str(Fr(c["pinned"]["10"][0]) + Fr(1, 10 ** 9)); out["pinned vertex moved"] = c
        c = start(); c["edges"][0] = [1, 3]; out["edge replaced"] = c
        return out

    def write(self, name, cert):
        p = Path(self.tmp.name) / (name.replace(" ", "_") + ".json")
        p.write_text(json.dumps(cert), encoding="utf-8")
        return p

    def test_01_full_certificate_accepted_by_independent_checker(self):
        r = run(INDEPENDENT, CERT, True, CODE, "2288")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("count matches the expected 2288", r.stdout)

    def test_02_unchanged_prefix_is_accepted_by_both_checkers(self):
        c = copy.deepcopy(self.cert)
        c["centers"] = c["centers"][:20]
        p = self.write("control", c)
        for script in (INDEPENDENT, EXACT):
            for opt in (False, True):
                r = run(script, p, opt)
                self.assertEqual(r.returncode, 0, f"{script.name} -O={opt}: {r.stdout}{r.stderr}")

    def test_03_each_corruption_is_rejected_with_and_without_optimisation(self):
        for name, c in self.cases().items():
            p = self.write(name, c)
            for script in (INDEPENDENT, EXACT):
                for opt in (False, True):
                    r = run(script, p, opt)
                    self.assertNotEqual(r.returncode, 0, f"{script.name} -O={opt} accepted: {name}")

    def test_04_wrong_expected_count_is_rejected(self):
        c = copy.deepcopy(self.cert)
        c["centers"] = c["centers"][:20]
        p = self.write("short", c)
        r = run(INDEPENDENT, p, True, CODE, "2288")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
