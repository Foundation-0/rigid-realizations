#!/usr/bin/env python3
"""
Verification and Must-Fail Negative Control Suite for L880 and G160 Certificates.
Follows the Foundation-0 Repository Standard: verifies positive proofs AND ensures that
violating any mathematical hypothesis (disjointness, contraction, inclusion, Heronian
distance exactness, orientation, or Laman sparsity) causes immediate rejection.
"""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from verify_l880_krawczyk import DEFAULT_CERT, verify_certificate_dict
from verify_l880_independent import run_independent_box_verification, verify_laman_graph
from verify_capco_laman import compute_c2
from verify_bartzos_baselines import verify_bartzos_l880_868, verify_bartzos_g160_132


class TestRigidRealizationCertificates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DEFAULT_CERT, "r", encoding="utf-8") as fh:
            cls.base_cert = json.load(fh)

    def test_01_primary_l880_880_krawczyk(self):
        res = verify_certificate_dict(self.base_cert)
        self.assertEqual(res["verified_boxes"], 440)
        self.assertEqual(res["verified_SE2_realizations"], 880)
        self.assertLess(res["max_contraction_kappa_approx"], 0.001)
        self.assertLess(res["max_krawczyk_inclusion_ratio_approx"], 0.001)

    def test_02_independent_l880_880_interval_verifier(self):
        res = run_independent_box_verification(DEFAULT_CERT)
        self.assertEqual(res["independent_interval_boxes_verified"], 440)
        self.assertEqual(res["total_SE2_real_realizations"], 880)
        self.assertEqual(res["laman_subgraph_subsets_checked"], 1012)
        self.assertLess(res["worst_interval_inclusion_ratio"], 0.001)

    def test_03_combinatorial_capco_upper_bound_c2_equals_880(self):
        edges = [tuple(e) for e in self.base_cert["edges"]]
        self.assertEqual(compute_c2(edges), 880)

    def test_04_bartzos_baselines_868_and_132(self):
        r868 = verify_bartzos_l880_868()
        self.assertEqual(r868["verified_SE2_realizations"], 868)
        r132 = verify_bartzos_g160_132()
        self.assertEqual(r132["verified_SE3_realizations"], 132)

    # --- MUST-FAIL NEGATIVE CONTROLS ---
    def test_05_negative_control_overlapping_boxes_rejected(self):
        bad = copy.deepcopy(self.base_cert)
        bad["centers_num"][439] = list(bad["centers_num"][0])
        with self.assertRaises(ValueError):
            verify_certificate_dict(bad)

    def test_06_negative_control_touching_boundary_boxes_rejected(self):
        bad = copy.deepcopy(self.base_cert)
        # Shift box 1 to lie at exact l_inf distance 2*r from box 0 (touching boundary)
        two_r = 2 * (1 << (bad["center_scale_exp2"] - bad["box_radius_exp2"]))
        bad["centers_num"][1] = list(bad["centers_num"][0])
        bad["centers_num"][1][0] += two_r
        with self.assertRaises(ValueError):
            verify_certificate_dict(bad)

    def test_07_negative_control_non_contractive_preconditioner_rejected(self):
        bad = copy.deepcopy(self.base_cert)
        bad["preconds_num"][0] = [[0] * 14 for _ in range(14)]
        with self.assertRaises(ValueError):
            verify_certificate_dict(bad)

    def test_08_negative_control_perturbed_pinned_edge_rejected(self):
        bad = copy.deepcopy(self.base_cert)
        bad["edge_lengths"][4] = "1/1"  # breaks exact Heronian distance on (2, 7)
        with self.assertRaises(ValueError):
            verify_certificate_dict(bad)

    def test_09_negative_control_wrong_orientation_triangle_rejected(self):
        bad = copy.deepcopy(self.base_cert)
        # Negate y_3: preserves all 3 pinned edge lengths identically in Q, but flips orientation <= 0!
        x3_s, y3_s = bad["pinned_vertices"]["3"]
        bad["pinned_vertices"]["3"] = [x3_s, "-" + y3_s]
        with self.assertRaises(ValueError):
            verify_certificate_dict(bad)

    def test_10_negative_control_non_laman_graph_rejected(self):
        # Replace edge (9, 10) with (2, 10) duplicate or overconstrained K4 subgraph {1, 4, 8, 9}
        overconstrained = [
            (1, 4), (1, 8), (1, 9), (4, 8), (4, 9), (8, 9),  # K4 on 4 vertices: 6 > 2*4 - 3 = 5!
            (2, 3), (2, 7), (2, 10), (3, 7), (3, 9),
            (5, 7), (5, 8), (5, 10), (6, 7), (6, 8), (6, 9),
        ]
        with self.assertRaises(ValueError):
            verify_laman_graph(10, overconstrained)


    def test_11_sha256_manifest_integrity(self):
        import hashlib
        manifest = ROOT / "SHA256SUMS"
        self.assertTrue(manifest.exists(), "SHA256SUMS manifest missing")
        lines = [ln.strip() for ln in manifest.read_text(encoding="utf-8").splitlines() if ln.strip()]
        self.assertGreaterEqual(len(lines), 12)
        for ln in lines:
            expected_hash, rel_path = ln.split("  ", 1)
            target = ROOT / rel_path
            self.assertTrue(target.exists(), f"Missing file in manifest: {rel_path}")
            actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            self.assertEqual(actual_hash, expected_hash, f"SHA-256 mismatch on {rel_path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
