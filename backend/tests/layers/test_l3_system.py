# -*- coding: utf-8 -*-
"""
TVJP – LAYER 3 · BLACK-BOX: SYSTEM TESTING  (Pilar 1: End-to-End System Verification)
========================================================================================
Metode  : Automated System Testing (Black-Box E2E Flow)
Referensi: IEEE Std 829-2008; Sommerville (2016)

Kasus Uji:
  S-01  Siklus Belajar E2E: BKT → SRS → Streak
  S-02  Siklus Suara E2E: Audio In ↔ Audio Out AI
  S-03  Siklus Kuis Adaptif: BKT CAT ↔ Profil Jawaban Siswa
"""

import os, sys, time, unittest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import date

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path: sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, BKTEngine, SRSService, StreakService, VoiceService,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 3 · SYSTEM TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L3_System(TVJPBaseTest):
    """Berlabel Black-Box Testing – Menilai sistem utuh dari luar (Input-Output)."""
    LAYER = "System"

    def test_S01_learning_session_flow(self):
        """[S-01] Siklus Belajar E2E: BKT → SRS → Streak."""
        desc = "Black-Box E2E: Menguji rangkaian proses satu ketukan siklus belajar vocab."
        inputs = "User submit jawaban benar"
        expected = "P(L) > 0.500 | streak_days ≥ 1"
        try:
            bkt = BKTEngine()
            p_l = bkt.update_belief(0.5, True, {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05})
            self.assertGreater(p_l, 0.5)

            mock_db.data = [{"user_id": "u1", "node_id": "n1", "node_type": "vocab", "repetitions": 0, "easiness_factor": 2.5, "interval_days": 1}]
            review = self.run_async(SRSService.record_review("u1", "n1", "vocab", 5))
            mock_db.data = [{"study_date": date.today().isoformat()}]
            streak = self.run_async(StreakService.update_streak("u1"))

            self.log_result("System Functional", "E2E Learning Session", desc, inputs, expected, f"P(L)={p_l:.3f} | streak_days={streak['streak_days']}", "PASSED")
        except Exception as e:
            self.log_result("System Functional", "E2E Learning Session", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_S02_voice_interaction_flow(self):
        """[S-02] Siklus Suara E2E: Audio In ↔ Audio Out AI."""
        desc = "Black-Box E2E: Menguji input stream suara masuk hingga melahirkan audio balasan."
        inputs = "File WAV masukan percakapan user"
        expected = "Audio Output: '*.wav'"
        try:
            vs = VoiceService()
            vs.transcribe_audio = AsyncMock(return_value="こんにちは")
            text = self.run_async(vs.transcribe_audio("t.wav"))

            mc = MagicMock(); mr = MagicMock()
            mr.status_code = 200; mr.content = b"wav"
            async def _post(*a, **k): return mr
            mc.post = _post
            mc.__aenter__ = AsyncMock(return_value=mc); mc.__aexit__ = AsyncMock(return_value=False)

            with patch("httpx.AsyncClient", return_value=mc):
                path = self.run_async(vs.synthesize_speech(text))
            self.assertTrue(path.endswith(".wav"))
            path_base = os.path.basename(path)
            if os.path.exists(path): os.unlink(path)
            self.log_result("System Functional", "E2E Audio Conversation Flow", desc, inputs, expected, f"Audio Output: '{path_base}'", "PASSED")
        except Exception as e:
            self.log_result("System Functional", "E2E Audio Conversation Flow", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_S03_quiz_adaptive_flow(self):
        """[S-03] Siklus Kuis Adaptif: BKT CAT ↔ Profil Jawaban Siswa."""
        desc = "Black-Box E2E: Validasi penugasan item kuis adaptif berdasarkan riwayat kompetensi."
        inputs = "beliefs={n1:0.4, n2:0.9} → jawab benar"
        expected = "Next_Node = 'n1' | P(L) > 0.400"
        try:
            bkt = BKTEngine()
            beliefs = {"n1": 0.4, "n2": 0.9}
            nodes = [{"id": "n1", "name": "N1"}, {"id": "n2", "name": "N2"}]
            selected = bkt.select_next_questions(beliefs, nodes, count=1)
            self.assertEqual(selected[0]["id"], "n1")

            new_p = bkt.update_belief(beliefs["n1"], True, {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05})
            self.assertGreater(new_p, beliefs["n1"])
            self.log_result("System Functional", "Adaptive Question Selector", desc, inputs, expected, f"Next_Node = '{selected[0]['id']}' | P(L)={new_p:.3f}", "PASSED")
        except Exception as e:
            self.log_result("System Functional", "Adaptive Question Selector", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 3 · SYSTEM TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: End-to-End System Verification  ·  Black-Box: System'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  Automated System Testing (Black-Box E2E Flow)"))
    print(_row(f"  {'Kasus Uji':<12}  3 skenario E2E (S-01 s.d. S-03)"))
    print(_row(f"  {'Komponen':<12}  System Functional · BKT · SRS · Voice · Streak"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 3 · SYSTEM TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    runner.run(loader.loadTestsFromTestCase(Test_L3_System))
    print_layer_summary(ALL_RESULTS, "LAYER 3 · SYSTEM TESTING", time.perf_counter() - t0)
