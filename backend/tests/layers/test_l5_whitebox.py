# -*- coding: utf-8 -*-
"""
TVJP – LAYER 5 · WHITE-BOX: LOGIKA INTERNAL & COVERAGE  (Pilar 1: Structural Coverage)
========================================================================================
Metode  : White-Box Logic & Branch Boundary Testing
Referensi: Myers et al. (2011); IEEE Std 829-2008

Kasus Uji:
  W-01  Boundary Mastery Threshold (Limit Desimal 0.85)
  W-02  SM-2 EF Floor Boundary Restraint (Floor 1.3)
  W-03  Belief Update Full Matrix Branch Coverage
  W-04  Streak Gap Tolerance Absence Forgiveness Branch
"""

import os, sys, time, unittest
from datetime import date, timedelta

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path: sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, BKTEngine, SRSService, StreakService,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 5 · WHITE-BOX TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L5_WhiteBox(TVJPBaseTest):
    """Berlabel White-Box Testing – Menembak langsung struktur kode internal & nilai batas."""
    LAYER = "White-Box"

    def setUp(self):
        super().setUp()
        self.bkt = BKTEngine()

    def test_W01_boundary_mastery_threshold(self):
        """[W-01] Percabangan Kondisi Batas Kelulusan Desimal 0.85."""
        desc = "White-Box: Menguji ketepatan branch if-else di angka limit desimal presisi."
        inputs = "p_l bernilai limit kaku: 0.85, 0.849, 0.851"
        expected = "Node terpilih: ['n_below']"
        try:
            nodes = [{"id": "n_at"}, {"id": "n_below"}, {"id": "n_above"}]
            beliefs = {"n_at": 0.85, "n_below": 0.849, "n_above": 0.851}
            selected = self.bkt.select_next_questions(beliefs, nodes, count=3)
            selected_ids = [n["id"] for n in selected]
            self.assertIn("n_below", selected_ids)
            self.assertNotIn("n_at", selected_ids)
            self.log_result("Structural Logics", "Boundary Precision Branch", desc, inputs, expected, f"Node terpilih: {selected_ids}", "PASSED")
        except Exception as e:
            self.log_result("Structural Logics", "Boundary Precision Branch", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_W02_sm2_ef_floor_boundary(self):
        """[W-02] Restriksi Batas Bawah Nilai EF Rumus SM-2."""
        desc = "White-Box: Memastikan variabel Easiness Factor terkunci aman di nilai minimal 1.3."
        inputs = "Simulasi eror salah menjawab kuis berturut-turut sebanyak 10 kali"
        expected = "Easiness Factor Floor = 1.30"
        try:
            ef = 2.5
            for _ in range(10):
                res = SRSService.calculate_sm2(0, 0, ef, 1)
                ef = res["easiness_factor"]
                self.assertGreaterEqual(ef, 1.3)
            self.log_result("Structural Logics", "SM-2 Algorithmic Constraint", desc, inputs, expected, f"Easiness Factor Floor = {ef:.2f}", "PASSED")
        except Exception as e:
            self.log_result("Structural Logics", "SM-2 Algorithmic Constraint", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_W03_belief_update_all_branches(self):
        """[W-03] Cakupan Kombinasi Cabang Logika Bayesian Update."""
        desc = "White-Box: Menguji ketersediaan jalur alternatif matematika kognitif."
        inputs = "4 variasi matrix silang: (low/high) x (benar/salah)"
        expected = "Matrix outcomes dalam clamp aman [0.001, 0.999]"
        try:
            params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}
            cases = [(0.001, True), (0.999, True), (0.001, False), (0.999, False)]
            outs = []
            for p, c in cases:
                with self.subTest(p=p, correct=c):
                    out = self.bkt.update_belief(p, c, params)
                    self.assertGreaterEqual(out, 0.001); self.assertLessEqual(out, 0.999)
                    outs.append(round(out, 3))
            self.log_result("Structural Logics", "Full Probability Branch Coverage", desc, inputs, expected, f"Matrix outcomes: {outs}", "PASSED")
        except Exception as e:
            self.log_result("Structural Logics", "Full Probability Branch Coverage", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_W04_streak_gap_tolerance_branch(self):
        """[W-04] Jalur Toleransi Hari Bolos (Gap Logic)."""
        desc = "White-Box: Validasi percabangan if-else pengampunan masa absen siswa."
        inputs = "Kasus A: Bolos 1 hari | Kasus B: Bolos 2 hari"
        expected = "Gap1 (Toleransi) = 2 | Gap2 (Reset) = 1"
        try:
            today = date.today()
            mock_db.data = [{"study_date": today.isoformat()}, {"study_date": (today - timedelta(days=1)).isoformat()}]
            info_a = self.run_async(StreakService.update_streak("u1"))
            self._reset_db()
            mock_db.data = [{"study_date": today.isoformat()}, {"study_date": (today - timedelta(days=3)).isoformat()}]
            info_b = self.run_async(StreakService.update_streak("u1"))
            self.assertGreaterEqual(info_a["streak_days"], 2); self.assertEqual(info_b["streak_days"], 1)
            self.log_result("Structural Logics", "Gap Absence Forgiveness Branch", desc, inputs, expected, f"Gap1 (Toleransi) = {info_a['streak_days']} | Gap2 (Reset) = {info_b['streak_days']}", "PASSED")
        except Exception as e:
            self.log_result("Structural Logics", "Gap Absence Forgiveness Branch", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 5 · WHITE-BOX LOGIC TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: Structural Coverage  ·  White-Box Logics & Boundaries'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  White-Box Logic & Branch Boundary Testing"))
    print(_row(f"  {'Kasus Uji':<12}  4 skenario cabang (W-01 s.d. W-04)"))
    print(_row(f"  {'Komponen':<12}  Structural Logics · BKT · SRS · Streak"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 5 · WHITE-BOX LOGIC TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    runner.run(loader.loadTestsFromTestCase(Test_L5_WhiteBox))
    print_layer_summary(ALL_RESULTS, "LAYER 5 · WHITE-BOX LOGIC TESTING", time.perf_counter() - t0)
