# -*- coding: utf-8 -*-
"""
TVJP – LAYER 2 · INTEGRATION TESTING  (Pilar 1: Module Pipeline Verification)
===============================================================================
Metode  : Automated Integration Testing — Cross-Module Pipeline
Referensi: IEEE Std 829-2008; Pressman & Maxim (2015)

Kasus Uji:
  I-01  SRS Engine ↔ Supabase Update Pipeline
  I-02  LLM Translation ↔ TTS Filter Pipeline
  I-03  Grammar Tokenizer ↔ LLM Prompt Builder
  I-04  Streak Goals ↔ Progress Calculator
  I-05  Voice STT ↔ Translation Module
"""

import os, sys, time, unittest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import date

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path: sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, LLMAgent, GrammarCheckerService, SRSService, StreakService, VoiceService,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 2 · INTEGRATION TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L2_Integration(TVJPBaseTest):
    """Integration Testing – Pipeline Lintasan Modul."""
    LAYER = "Integration"

    def setUp(self):
        super().setUp()
        self.agent = LLMAgent(graph=MagicMock())
        self.gc    = GrammarCheckerService()
        self.vs    = VoiceService()

    def test_I01_srs_review_pipeline(self):
        """[I-01] SM-2 Engine ↔ Supabase Update."""
        desc = "Menguji jembatan kirim data: Rumus SM-2 di-push masuk ke DB Supabase."
        inputs = "user_id='u1', node_id='n1', quality=4"
        expected = "Repetisi baru = 2"
        try:
            mock_db.data = [{"user_id":"u1","node_id":"n1","node_type":"vocab","repetitions":1,"easiness_factor":2.5,"interval_days":1}]
            res = self.run_async(SRSService.record_review("u1","n1","vocab",4))
            self.assertEqual(res["repetitions"], 2)
            self.log_result("SRS ↔ Supabase", "Review Update Pipeline", desc, inputs, expected, f"Repetisi baru = {res['repetitions']}", "PASSED")
        except Exception as e:
            self.log_result("SRS ↔ Supabase", "Review Update Pipeline", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_I02_llm_translation_to_tts(self):
        """[I-02] LLM Output Trans ↔ Filter Saluran Suara."""
        desc = "Menguji pipeline data bersih dari layer translasi LLM ke input modul suara."
        inputs = "Teks Indonesia → Translate Mock → Clean Filter"
        expected = "Filtered: '私は好き'"
        try:
            self.agent.translate_and_romaji_user_llm = AsyncMock(return_value={"jp": "JP: **私は好き**", "romaji": "Watashi wa suki"})
            res      = self.run_async(self.agent.translate_and_romaji_user_llm("Saya suka"))
            filtered = self.agent._prepare_tts_text(res["jp"])
            self.assertEqual(filtered, "私は好き")
            self.log_result("LLM → TTS", "Translation Pipeline", desc, inputs, expected, f"Filtered: '{filtered}'", "PASSED")
        except Exception as e:
            self.log_result("LLM → TTS", "Translation Pipeline", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_I03_grammar_checker_to_llm_prompt(self):
        """[I-03] Token Morfologi ↔ Struktur Prompter JSON."""
        desc = "Menguji penyusunan otomatis token kata mentah menjadi prompt JSON LLM."
        inputs = "'go' → tokenize → build prompt"
        expected = "Prompt memuat JSON (Len > 0)"
        try:
            tokens = self.gc.tokenize("go")
            prompt = self.gc.build_llm_prompt("go", tokens)
            self.assertIn("JSON", prompt)
            self.log_result("Grammar → LLM", "Prompt Builder Pipeline", desc, inputs, expected, f"Prompt memuat JSON (Len={len(prompt)} chars)", "PASSED")
        except Exception as e:
            self.log_result("Grammar → LLM", "Prompt Builder Pipeline", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_I04_streak_goals_to_progress(self):
        """[I-04] Target Konfigurasi ↔ Hitungan Pencapaian."""
        desc = "Menguji sinkronisasi limit target harian dengan progres belajar."
        inputs = "reviewed=5, target=5"
        expected = "Progress review_pct = 100%"
        try:
            mock_db.data = [{"study_date": date.today().isoformat(),"study_minutes":15,"items_reviewed":5,"quests_completed":1,"xp_earned":20}]
            with patch("backend.services.streak_service.StreakService.get_daily_goals", new_callable=AsyncMock) as mg:
                mg.return_value = {"vocab_target":10,"grammar_target":2,"review_target":5,"study_minutes_target":15}
                prog = self.run_async(StreakService.get_today_progress("u1"))
            self.assertEqual(prog["completion"]["review_pct"], 100)
            self.log_result("Streak ↔ Progress", "Goal Calculation Pipeline", desc, inputs, expected, f"Progress review_pct = {prog['completion']['review_pct']}%", "PASSED")
        except Exception as e:
            self.log_result("Streak ↔ Progress", "Goal Calculation Pipeline", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_I05_voice_stt_to_translation(self):
        """[I-05] Transkripsi Audio STT ↔ Modul Translator Suara."""
        desc = "Menguji aliran data audio Whisper transkrip masuk ke translator bahasa."
        inputs = "WAV File → Text → Translator"
        expected = "Trans: 'こんにちは' | Romaji: 'Konnichiwa'"
        try:
            self.vs.transcribe_audio = AsyncMock(return_value="こんにちは")
            transcript = self.run_async(self.vs.transcribe_audio("a.wav"))
            with patch("deep_translator.GoogleTranslator.translate", return_value="Halo"):
                trans_res = self.run_async(self.vs.translate_and_romaji_user(transcript))
            self.assertIn("jp", trans_res)
            self.log_result("Voice ↔ Trans", "Speech Translation Pipeline", desc, inputs, expected, f"Trans: '{trans_res.get('jp')}' | Romaji: '{trans_res.get('romaji')}'", "PASSED")
        except Exception as e:
            self.log_result("Voice ↔ Trans", "Speech Translation Pipeline", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 2 · INTEGRATION TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: Module Pipeline Verification  ·  Cross-Module Data Flow'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  Automated Integration Testing — Cross-Module Pipeline"))
    print(_row(f"  {'Kasus Uji':<12}  5 skenario alur (I-01 s.d. I-05)"))
    print(_row(f"  {'Komponen':<12}  SRS · LLM · Grammar · Streak · Voice"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 2 · INTEGRATION TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    runner.run(loader.loadTestsFromTestCase(Test_L2_Integration))
    print_layer_summary(ALL_RESULTS, "LAYER 2 · INTEGRATION TESTING", time.perf_counter() - t0)
