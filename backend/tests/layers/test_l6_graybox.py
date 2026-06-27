# -*- coding: utf-8 -*-
"""
TVJP – LAYER 6 · GRAY-BOX TESTING  (Pilar 1: Data Architecture & Schema Verification)
======================================================================================
Metode  : Gray-Box Data Architecture Testing
Referensi: IEEE Std 829-2008; Pressman & Maxim (2015)

Kasus Uji:
  G-01  SRS Payload Schema Validation
  G-02  Chat History Chronological Ordering Inversion
  G-03  Retention Forecast Struct Array Validation
  G-04  Admin Dashboard Aggregator Formulas Consistency
"""

import os, sys, time, unittest
from datetime import date

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path: sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, SRSService, SupabaseService,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 6 · GRAY-BOX TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L6_GrayBox(TVJPBaseTest):
    """Berlabel Gray-Box Testing – Mengetahui sebagian skema data internal server."""
    LAYER = "Gray-Box"

    def test_G01_srs_payload_schema(self):
        """[G-01] Validasi Atribut Field Wajib Tabel SRS."""
        desc = "Gray-Box: Mencocokkan skema field kirim data dengan struktur tabel srs_items."
        inputs = "Fungsi rekam review dipicu"
        expected = "Field terverifikasi: ['interval_days', 'next_review', 'node_id', 'repetitions']"
        try:
            mock_db.data = [{"user_id": "u1", "node_id": "n1", "node_type": "vocab", "repetitions": 1, "easiness_factor": 2.5, "interval_days": 1}]
            res = self.run_async(SRSService.record_review("u1", "n1", "vocab", 4))
            required_fields = {"node_id", "next_review", "interval_days", "repetitions"}
            missing = required_fields - set(res.keys())
            self.assertFalse(missing)
            self.log_result("Data Architecture", "Payload Database Schema Validation", desc, inputs, expected, f"Field terverifikasi: {sorted(list(required_fields))}", "PASSED")
        except Exception as e:
            self.log_result("Data Architecture", "Payload Database Schema Validation", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_G02_chat_history_ordering(self):
        """[G-02] Restrukturisasi Urutan Kronologis Pesan Riwayat Chat."""
        desc = "Gray-Box: Memastikan susunan data terbalik bawaan Supabase (desc) di-reverse kembali."
        inputs = "2 entri chat log ditarik dari DB"
        expected = "Index 0: 'Genki?' (Reversed)"
        try:
            mock_db.data = [{"role": "user", "content": "Konnichiwa"}, {"role": "assistant", "content": "Genki?"}]
            hist = self.run_async(SupabaseService.get_chat_history("u1", limit=2))
            self.assertEqual(hist[0]["content"], "Genki?")
            self.log_result("Data Architecture", "Chronological Messaging Orders", desc, inputs, expected, f"Index 0: '{hist[0]['content']}' (Reversed)", "PASSED")
        except Exception as e:
            self.log_result("Data Architecture", "Chronological Messaging Orders", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_G03_retention_forecast_structure(self):
        """[G-03] Validasi Struktur Skema Grafik Ramalan Retensi Memori."""
        desc = "Gray-Box: Memastikan fungsi ramalan menghasilkan array teratur berpasangan."
        inputs = "Request forecast durasi 3 hari"
        expected = "Forecast Days = 3 (Array Valid)"
        try:
            today = date.today()
            mock_db.data = [{"next_review": today.isoformat(), "interval_days": 1}]
            forecast = self.run_async(SRSService.get_retention_forecast("u1", days=3))
            self.assertEqual(len(forecast), 3)
            self.log_result("Data Architecture", "Forecast Struct Array Validation", desc, inputs, expected, f"Forecast Days = {len(forecast)} (Array Valid)", "PASSED")
        except Exception as e:
            self.log_result("Data Architecture", "Forecast Struct Array Validation", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_G04_admin_analytics_aggregation(self):
        """[G-04] Konsistensi Rumus Agregasi Statistik Dashboard Admin."""
        desc = "Gray-Box: Validasi penghitungan formula akumulasi log pesan admin."
        inputs = "3 log sampel: u1/discovery, u1/quiz, u2/discovery"
        expected = "Total = 3 | ActiveUsers = 2"
        try:
            mock_db.data = [{"user_id": "u1", "mode": "discovery"}, {"user_id": "u1", "mode": "quiz"}, {"user_id": "u2", "mode": "discovery"}]
            stats = self.run_async(SupabaseService.get_chat_stats())
            self.assertEqual(stats["total_messages"], 3); self.assertEqual(stats["active_users"], 2)
            self.log_result("Data Architecture", "Admin Dashboard Aggregator Formulas", desc, inputs, expected, f"Total = {stats['total_messages']} | ActiveUsers = {stats['active_users']}", "PASSED")
        except Exception as e:
            self.log_result("Data Architecture", "Admin Dashboard Aggregator Formulas", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 6 · GRAY-BOX TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: Data Architecture Verification  ·  Gray-Box Schemas'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  Gray-Box Data Architecture Testing"))
    print(_row(f"  {'Kasus Uji':<12}  4 skenario skema data (G-01 s.d. G-04)"))
    print(_row(f"  {'Komponen':<12}  Data Architecture · SRS · SupabaseService"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 6 · GRAY-BOX TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    runner.run(loader.loadTestsFromTestCase(Test_L6_GrayBox))
    print_layer_summary(ALL_RESULTS, "LAYER 6 · GRAY-BOX TESTING", time.perf_counter() - t0)
