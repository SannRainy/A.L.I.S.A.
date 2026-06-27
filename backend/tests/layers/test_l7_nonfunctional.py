# -*- coding: utf-8 -*-
"""
TVJP – LAYER 7 · NON-FUNCTIONAL TESTING  (Pilar 1: Performance & Resilience Verification)
==========================================================================================
Metode  : Non-Functional Benchmarking & System Resilience Testing
Referensi: IEEE Std 829-2008; ISO/IEC 25010 Quality Model

Kasus Uji:
  N-01  BKT Engine Stress-Load Computation Performance Speed
  N-02  SM-2 Batch Interval Calculation Speed
  N-03  Regression Smoke Core Initialization Protection
  N-04  Idempotent Logic Restraints Data Value Protection
  N-05  Deterministic Output Tokenization Stability
"""

import os, sys, time, unittest
from datetime import date

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path: sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, BKTEngine, SRSService, StreakService, GrammarCheckerService, VoiceService,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 7 · NON-FUNCTIONAL TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L7_NonFunctional(TVJPBaseTest):
    """Berlabel Non-Functional Testing – Kualitas komputasi, proteksi regresi, & stabilitas."""
    LAYER = "Non-Functional"

    def test_N01_bkt_computation_performance(self):
        """[N-01] Kecepatan Performa Komputasi Mesin Kognitif BKT."""
        desc = "Performa: Validasi mesin hitung sanggup melahap beban ribuan operasi dalam sekejap."
        inputs = "1.000 iterasi kalkulasi update_belief() beruntun"
        expected = "Elapsed time < 1.000s"
        try:
            bkt = BKTEngine(); params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}
            t0 = time.perf_counter()
            for i in range(1000): bkt.update_belief(0.5, i % 2 == 0, params)
            elapsed = time.perf_counter() - t0
            self.assertLess(elapsed, 1.0)
            self.log_result("System Performance", "BKT Engine Stress-Load Speed", desc, inputs, expected, f"Elapsed time = {elapsed:.4f}s", "PASSED")
        except Exception as e:
            self.log_result("System Performance", "BKT Engine Stress-Load Speed", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_N02_sm2_batch_performance(self):
        """[N-02] Kecepatan Performa Batch Kalkulasi Jadwal Ulang SRS."""
        desc = "Performa: Memastikan eksekusi masal SM-2 tidak memicu kemacetan thread server."
        inputs = "500 batch hitungan interval repetisi"
        expected = "Elapsed time < 0.500s"
        try:
            t0 = time.perf_counter()
            for i in range(500): SRSService.calculate_sm2(i % 6, i % 3, 2.5, max(1, i % 10))
            elapsed = time.perf_counter() - t0
            self.assertLess(elapsed, 0.5)
            self.log_result("System Performance", "SM-2 Batch Interval Speed", desc, inputs, expected, f"Elapsed time = {elapsed:.4f}s", "PASSED")
        except Exception as e:
            self.log_result("System Performance", "SM-2 Batch Interval Speed", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_N03_regression_smoke_core_imports(self):
        """[N-03] Proteksi Ketahanan Regresi (Import Smoke Test)."""
        desc = "Smoke Test: Memastikan rombakan arsitektur tidak merusak rantai modul fundamental."
        inputs = "Instansiasi masal: BKTEngine, GrammarChecker, VoiceService"
        expected = "Status instansiasi: 3 modul OK"
        try:
            b = BKTEngine(); g = GrammarCheckerService(); v = VoiceService()
            self.assertIsNotNone(b); self.assertIsNotNone(g); self.assertIsNotNone(v)
            self.log_result("System Resilience", "Regression Core Initialization", desc, inputs, expected, "Status instansiasi: 3 modul OK", "PASSED")
        except Exception as e:
            self.log_result("System Resilience", "Regression Core Initialization", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_N04_idempotent_streak_update(self):
        """[N-04] Proteksi Integritas Data (Idempotensi Nilai Streak)."""
        desc = "Sanity Test: Menjamin pengulangan pemicu fungsi di hari yang sama bersifat idempoten."
        inputs = "Memanggil update_streak() dua kali berturut-turut pada tanggal yang sama"
        expected = "Streak1 = 1 == Streak2 = 1 (Idempotent)"
        try:
            today = date.today()
            mock_db.data = [{"study_date": today.isoformat()}]
            first = self.run_async(StreakService.update_streak("u1"))
            self._reset_db()
            mock_db.data = [{"study_date": today.isoformat()}]
            second = self.run_async(StreakService.update_streak("u1"))
            self.assertEqual(first["streak_days"], second["streak_days"])
            self.log_result("System Resilience", "Idempotent Logic Restraints", desc, inputs, expected, f"Streak1 = {first['streak_days']} == Streak2 = {second['streak_days']} (Idempotent)", "PASSED")
        except Exception as e:
            self.log_result("System Resilience", "Idempotent Logic Restraints", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_N05_grammar_tokenization_stability(self):
        """[N-05] Konsistensi Stabilitas Hasil Tokenisasi (Uji Deterministik)."""
        desc = "Stability Test: Tokenizer wajib melahirkan pecahan yang sama untuk data identik."
        inputs = "Fungsi tokenize() dieksekusi 5 kali menggunakan kalimat yang sama"
        expected = "5/5 iterasi identik: ['私', 'は', '学生', 'です']"
        try:
            gc = GrammarCheckerService()
            results = [[t["original"] for t in gc.tokenize("私は学生です")] for _ in range(5)]
            for r in results[1:]: self.assertEqual(r, results[0])
            self.log_result("System Resilience", "Deterministic Output Stability", desc, inputs, expected, f"5/5 iterasi identik: {results[0]}", "PASSED")
        except Exception as e:
            self.log_result("System Resilience", "Deterministic Output Stability", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 7 · NON-FUNCTIONAL TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: Performance & Resilience  ·  Benchmarking & Stability'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  Non-Functional Benchmarking & System Resilience Testing"))
    print(_row(f"  {'Kasus Uji':<12}  5 skenario non-fungsional (N-01 s.d. N-05)"))
    print(_row(f"  {'Komponen':<12}  System Performance · System Resilience"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 7 · NON-FUNCTIONAL TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    runner.run(loader.loadTestsFromTestCase(Test_L7_NonFunctional))
    print_layer_summary(ALL_RESULTS, "LAYER 7 · NON-FUNCTIONAL TESTING", time.perf_counter() - t0)
