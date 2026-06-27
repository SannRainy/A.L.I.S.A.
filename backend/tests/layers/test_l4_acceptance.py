# -*- coding: utf-8 -*-
"""
TVJP – LAYER 4 · BLACK-BOX: ACCEPTANCE TESTING  (Pilar 1: User Acceptance Verification)
=========================================================================================
Metode  : Automated Acceptance Testing (UAT Scenarios)
Referensi: IEEE Std 829-2008; Black (2009)

Kasus Uji:
  A-01  Learner Sees Appropriate Difficulty Allocation
  A-02  Learner Streak Motivation Tracker
  A-03  Gamification XP and Level Scaling
  A-04  Actionable Grammar Error Feedback
"""

import os, sys, time, unittest
from datetime import date, timedelta

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path: sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, BKTEngine, StreakService, SupabaseService, GrammarCheckerService,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 4 · ACCEPTANCE TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L4_Acceptance(TVJPBaseTest):
    """Berlabel Black-Box Testing – Pengujian berbasis skenario penerimaan pelajar (UAT)."""
    LAYER = "Acceptance"

    def test_A01_learner_sees_correct_difficulty(self):
        """[A-01] UAT: Pengalokasian Level Kesulitan Siswa Pemula."""
        desc = "UAT: Pelajar dengan tingkat mastery rendah wajib menerima soal tipe 'easy'."
        inputs = "Profil kompetensi kognitif siswa P(L) = 0.2"
        expected = "Label kesulitan = 'easy'"
        try:
            bkt = BKTEngine()
            diff = bkt.compute_cat_difficulty(p_mastered=0.2)
            self.assertEqual(diff, "easy")
            self.log_result("User Acceptance", "Appropriate Difficulty Allocation", desc, inputs, expected, f"Label kesulitan = '{diff}'", "PASSED")
        except Exception as e:
            self.log_result("User Acceptance", "Appropriate Difficulty Allocation", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_A02_learner_streak_motivation(self):
        """[A-02] UAT: Retensi Motivasi Belajar Lewat Sistem Streak."""
        desc = "UAT: Memastikan sistem mencatat kalender belajar harian secara mutakhir."
        inputs = "Aktivitas belajar hari ini dan kemarin berturut-turut"
        expected = "streak_days = 2"
        try:
            today = date.today()
            mock_db.data = [{"study_date": today.isoformat()}, {"study_date": (today - timedelta(days=1)).isoformat()}]
            info = self.run_async(StreakService.update_streak("u1"))
            self.assertGreaterEqual(info["streak_days"], 2)
            self.log_result("User Acceptance", "Streak Tracker Motivation", desc, inputs, expected, f"streak_days = {info['streak_days']}", "PASSED")
        except Exception as e:
            self.log_result("User Acceptance", "Streak Tracker Motivation", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_A03_learner_xp_and_leveling(self):
        """[A-03] UAT: Insentif Gamifikasi Poin dan Level Up Akun."""
        desc = "UAT: Mekanisme kenaikan level otomatis ketika tabungan XP menembus threshold."
        inputs = "XP awal = 95, pemicu aksi master (+10 XP)"
        expected = "XP = 105 | Level = 2"
        try:
            mock_db.data = [{"xp": 95, "level": 1}]
            self.run_async(SupabaseService.update_user_stats("u1", "VOCAB_MASTERED"))
            payload = mock_db.data
            self.assertEqual(payload["xp"], 105)
            self.assertEqual(payload["level"], 2)
            self.log_result("User Acceptance", "Gamification XP Scaling", desc, inputs, expected, f"XP = {payload['xp']} | Level = {payload['level']}", "PASSED")
        except Exception as e:
            self.log_result("User Acceptance", "Gamification XP Scaling", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_A04_grammar_error_feedback(self):
        """[A-04] UAT: Umpan Balik Koreksi Tata Bahasa."""
        desc = "UAT: Pesan notifikasi kekeliruan struktur kalimat harus komunikatif."
        inputs = "Pola kalimat salah ketik partikel kembar ('私はりんごをを食べる')"
        expected = "Error feedback terstruktur ('助詞...')"
        try:
            gc = GrammarCheckerService()
            errs = gc.detect_common_errors("私はりんごをを食べる")
            self.assertGreater(len(errs), 0)
            msg = errs[0]["message"]
            self.log_result("User Acceptance", "Actionable Grammar Feedback", desc, inputs, expected, f"Error feedback: '{msg[:25]}…'", "PASSED")
        except Exception as e:
            self.log_result("User Acceptance", "Actionable Grammar Feedback", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 4 · ACCEPTANCE TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: User Acceptance Verification  ·  Black-Box: UAT'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  Automated Acceptance Testing (UAT Scenarios)"))
    print(_row(f"  {'Kasus Uji':<12}  4 skenario penerimaan (A-01 s.d. A-04)"))
    print(_row(f"  {'Komponen':<12}  User Acceptance · BKT · Streak · Gamification · Grammar"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 4 · ACCEPTANCE TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    runner.run(loader.loadTestsFromTestCase(Test_L4_Acceptance))
    print_layer_summary(ALL_RESULTS, "LAYER 4 · ACCEPTANCE TESTING", time.perf_counter() - t0)
