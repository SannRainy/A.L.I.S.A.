# -*- coding: utf-8 -*-
"""
TVJP – LAYER 1 · AUTOMATED UNIT TESTING  (Pilar 1: Structural & Logical Verification)
========================================================================================
Metode  : Automated Unit Testing with Mock Isolation
Referensi: IEEE Std 829-2008; ISTQB Foundation 2024

Kasus Uji:
  U-01  BKTEngine — CAT Difficulty Selection
  U-02  BKTEngine — Bayesian Belief Update
  U-03  BKTEngine — Sequential Mastery Computation
  U-04  BKTEngine — Information Gain Node Selection
  U-05  BKTEngine — Difficulty Estimation
  U-06  LLMAgent  — Quiz Intent Detection
  U-07  LLMAgent  — Grammar Keyword Extraction
  U-08  LLMAgent  — JP Text Normalization
  U-09  LLMAgent  — TTS Text Filter
  U-10  GrammarChecker — Morphology Tokenization
  U-11  GrammarChecker — Text Metrics
  U-12  GrammarChecker — Double Particle Detection
  U-13  SRSService — SM-2 Algorithm Pure Math
"""

import os, sys, time, unittest
from unittest.mock import MagicMock

# ── PATH untuk import _shared ─────────────────────────────────────────────────
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)
if os.path.dirname(_DIR) not in sys.path:
    sys.path.insert(0, os.path.dirname(_DIR))

from _shared import (
    make_base_class, print_layer_summary, safe_print,
    mock_db, BKTEngine, LLMAgent, GrammarCheckerService, SRSService,
    _is_quiz_request, _extract_grammar_keywords, _normalize_jp_text,
    green, red, cyan, dim, bold, W, _hline, _mline, _bline, _row,
    STATUS_ICON, LAYER_BADGE, BOX_V,
)

print = safe_print

# ── Per-layer hasil accumulator ───────────────────────────────────────────────
ALL_RESULTS: list[dict] = []
_counter = [0]
TVJPBaseTest = make_base_class(ALL_RESULTS, _counter)
_T0 = time.perf_counter()


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 1 · BKT ENGINE UNIT TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L1_BKTEngine(TVJPBaseTest):
    """White-Box Unit Testing – BKT Engine."""
    LAYER = "Unit"

    def setUp(self):
        super().setUp()
        self.bkt = BKTEngine()

    def test_U01_cat_difficulty_selection(self):
        """[U-01] compute_cat_difficulty() – label kesulitan adaptif."""
        desc = "Menguji penentuan kelas kesulitan CAT berdasarkan mastery P(L)."
        inputs = "p_mastered ∈ {0.85, 0.50, 0.20}"
        expected = "0.85→hard | 0.50→medium | 0.20→easy"
        try:
            for p, exp in [(0.85, "hard"), (0.50, "medium"), (0.20, "easy")]:
                with self.subTest(p=p):
                    self.assertEqual(self.bkt.compute_cat_difficulty(p_mastered=p), exp)
            self.log_result("BKT Engine", "CAT Difficulty Selection", desc, inputs, expected, "0.85→hard | 0.50→medium | 0.20→easy", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "CAT Difficulty Selection", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U02_bayesian_belief_update(self):
        """[U-02] update_belief() – hitungan probabilistik Bayesian."""
        desc = "Menguji pembaruan matematis P(L) dan restriksi boundary [0.001, 0.999]."
        inputs = "p_l=0.5, correct=T/F; boundary check"
        expected = "Benar→>0.5 | Salah→<0.5"
        try:
            params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}
            pc  = self.bkt.update_belief(0.5,   True,  params)
            pi  = self.bkt.update_belief(0.5,   False, params)
            phi = self.bkt.update_belief(0.999, True,  params)
            plo = self.bkt.update_belief(0.001, False, params)
            self.assertGreater(pc, 0.5);      self.assertLess(pi, 0.5)
            self.assertLessEqual(phi, 0.999); self.assertGreaterEqual(plo, 0.001)
            self.log_result("BKT Engine", "Bayesian Belief Update", desc, inputs, expected, f"Benar→{pc:.4f} | Salah→{pi:.4f}", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Bayesian Belief Update", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U03_sequential_mastery(self):
        """[U-03] compute_mastery() – akumulasi sekuens jawaban."""
        desc = "Menguji kalkulasi ketuntasan dari rangkaian data observasi runut."
        inputs = "obs=[T,T,T] dan obs=[F,F]"
        expected = "[T,T,T]→mastered=True | [F,F]→mastered=False"
        try:
            rp = self.bkt.compute_mastery([True, True, True], "vocab")
            rf = self.bkt.compute_mastery([False, False],     "vocab")
            self.assertTrue(rp["is_mastered"]); self.assertFalse(rf["is_mastered"])
            self.log_result("BKT Engine", "Sequential Mastery", desc, inputs, expected, f"[T,T,T]→mastered={rp['is_mastered']} | [F,F]→mastered={rf['is_mastered']}", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Sequential Mastery", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U04_information_gain_node_selection(self):
        """[U-04] select_next_questions() – entropi node tertinggi."""
        desc = "Menguji pemilihan soal dengan Information Gain (entropi mendekati ~0.5)."
        inputs = "beliefs={n1:0.5, n2:0.9, n3:0.1}, count=2"
        expected = "Node terpilih: ['n1', 'n3']"
        try:
            beliefs = {"n1": 0.5, "n2": 0.9, "n3": 0.1}
            nodes   = [{"id": k, "name": f"Node {k}"} for k in beliefs]
            sel     = self.bkt.select_next_questions(beliefs, nodes, count=2)
            ids     = [n["id"] for n in sel]
            self.assertIn("n1", ids); self.assertNotIn("n2", ids)
            self.log_result("BKT Engine", "IG Node Selection", desc, inputs, expected, f"Node terpilih: {ids}", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "IG Node Selection", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U05_difficulty_estimation(self):
        """[U-05] estimate_difficulty() – correct rate jawaban kolektif."""
        desc = "Menguji estimasi tingkat kesukaran item soal dari sekuens kolektif."
        inputs = "correct_rate ∈ {80%, 50%, 25%}"
        expected = "80%→easy | 50%→medium | 25%→hard"
        try:
            cases = [([True]*4+[False], "easy"), ([True,False]*2, "medium"), ([False]*3+[True], "hard")]
            for obs, exp in cases:
                with self.subTest(exp=exp):
                    self.assertEqual(self.bkt.estimate_difficulty(obs), exp)
            self.log_result("BKT Engine", "Difficulty Estimation", desc, inputs, expected, "80%→easy | 50%→medium | 25%→hard", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Difficulty Estimation", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 1 · LLM AGENT UNIT TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L1_LLMAgent(TVJPBaseTest):
    """White-Box Unit Testing – LLM Agent internal functions."""
    LAYER = "Unit"

    def setUp(self):
        super().setUp()
        self.agent = LLMAgent(graph=MagicMock())

    def test_U06_quiz_intent_detection(self):
        """[U-06] _is_quiz_request() – klasifikasi intent NLU kuis."""
        desc = "Menguji deteksi intent kuis dari text natural kalimat user."
        inputs = "Positif: 'latihan kuis' | Negatif: 'siapa dewa'"
        expected = "Positif→True | Negatif→False"
        try:
            pos = ["Berikan kuis JLPT N5", "latihan kuis"]
            neg = ["siapakah dewa kematian?", "apa itu haiku?"]
            for t in pos: self.assertTrue(_is_quiz_request(t))
            for t in neg: self.assertFalse(_is_quiz_request(t))
            self.log_result("LLM Agent", "Quiz Intent Detection", desc, inputs, expected, f"Positif={_is_quiz_request('latihan kuis')} | Negatif={_is_quiz_request('apa itu haiku?')}", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "Quiz Intent Detection", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U07_grammar_keyword_extraction(self):
        """[U-07] _extract_grammar_keywords() – parser token RAG."""
        desc = "Menguji ekstraksi pola grammar Jepang untuk pencarian pangkalan RAG."
        inputs = "'N5 Grammar ~てください'"
        expected = "Keywords=['てください']"
        try:
            kw = _extract_grammar_keywords("N5 Grammar ~てください")
            self.assertIn("てください", kw)
            self.log_result("LLM Agent", "Grammar Extraction", desc, inputs, expected, f"Keywords={kw}", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "Grammar Extraction", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U08_jp_text_normalization(self):
        """[U-08] _normalize_jp_text() – stripping whitespace Jepang."""
        desc = "Menguji pembersihan whitespace berlebih pada aksara Jepang."
        inputs = "'こんにちは   ！  '"
        expected = "Teks bersih: 'こんにちは'"
        try:
            out = _normalize_jp_text("こんにちは   ！   ")
            self.assertEqual(out, "こんにちは")
            self.log_result("LLM Agent", "JP Text Normalization", desc, inputs, expected, f"Teks bersih: '{out}'", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "JP Text Normalization", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U09_tts_text_filter(self):
        """[U-09] _prepare_tts_text() – stripping markdown & prefix."""
        desc = "Menguji pembersihan markdown dan prefix JP: sebelum dikirim ke TTS."
        inputs = "'JP: **りんgo**'"
        expected = "TTS filter: 'りんgo'"
        try:
            out = self.agent._prepare_tts_text("JP: **りんgo**")
            self.assertEqual(out, "りんgo")
            self.log_result("LLM Agent", "TTS Text Filter", desc, inputs, expected, f"TTS filter: '{out}'", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "TTS Text Filter", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 1 · GRAMMAR CHECKER + SRS UNIT TESTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L1_GrammarChecker(TVJPBaseTest):
    """White-Box Unit Testing – Grammar Checker & SRS pure math."""
    LAYER = "Unit"

    def setUp(self):
        super().setUp()
        self.gc = GrammarCheckerService()

    def test_U10_morphology_tokenization(self):
        """[U-10] tokenize() – pemecahan morfologi Pykakasi."""
        desc = "Menguji tokenisasi pecahan struktur kata terkecil kalimat Jepang."
        inputs = "'私は学生です'"
        expected = "Pecahan token mengandung '私' dan '学生'"
        try:
            tokens   = self.gc.tokenize("私は学生です")
            surfaces = [t["original"] for t in tokens]
            for s in ("私", "学生"):
                self.assertIn(s, surfaces)
            self.log_result("Grammar Checker", "Morphology Tokenization", desc, inputs, expected, f"Pecahan token: {surfaces}", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Morphology Tokenization", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U11_text_metrics(self):
        """[U-11] basic_analysis() – char dan token counters."""
        desc = "Menguji kalkulasi statistik kuantitatif dasar teks Jepang."
        inputs = "'私は日本語を勉強します'"
        expected = "char_count = 11"
        try:
            a = self.gc.basic_analysis("私は日本語を勉強します")
            self.assertEqual(a["char_count"], 11)
            self.log_result("Grammar Checker", "Text Metrics", desc, inputs, expected, f"char_count = {a['char_count']}", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Text Metrics", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U12_double_particle_detection(self):
        """[U-12] detect_common_errors() – rule-based ganda particle."""
        desc = "Menguji deteksi anomali penulisan partikel ganda berulang (grammar error)."
        inputs = "'私はりんごをを食べる'"
        expected = "Terdeteksi 'particle_error' | Saran: '私はりんごを食べる'"
        try:
            errs = self.gc.detect_common_errors("私はりんごをを食べる")
            types = [e["type"] for e in errs]
            self.assertIn("particle_error", types)
            sugg = errs[0]["suggestion"]
            self.log_result("Grammar Checker", "Double Particle Detect", desc, inputs, expected, f"Terdeteksi '{types[0]}' | Saran: '{sugg}'", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Double Particle Detect", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise

    def test_U13_sm2_algorithm(self):
        """[U-13] SRSService.calculate_sm2() – rumus matematis SM-2."""
        desc = "Validasi rumus pembagian interval memori murni algoritma SM-2."
        inputs = "Q=5 rep0 | Q=5 rep1"
        expected = "R0_Int=1 | R1_Int=6"
        try:
            r0 = SRSService.calculate_sm2(5, 0, 2.5, 1)
            r1 = SRSService.calculate_sm2(5, 1, 2.5, 1)
            self.assertEqual(r0["repetitions"], 1); self.assertEqual(r0["interval_days"], 1)
            self.assertEqual(r1["repetitions"], 2); self.assertEqual(r1["interval_days"], 6)
            self.log_result("SRS Service", "SM-2 Algorithmic Pure", desc, inputs, expected, f"R0_Int={r0['interval_days']} | R1_Int={r1['interval_days']}", "PASSED")
        except Exception as e:
            self.log_result("SRS Service", "SM-2 Algorithmic Pure", desc, inputs, expected, f"ERR: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    ALL_RESULTS.clear(); _counter[0] = 0
    print(f"\n{cyan(_hline())}")
    print(f"{BOX_V} {cyan(bold('TVJP  –  LAYER 1 · AUTOMATED UNIT TESTING')):^{W-4}} {BOX_V}")
    print(f"{BOX_V} {dim('Pilar 1: Structural & Logical Verification  ·  White-Box: Unit'):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    print(_row(f"  {'Metode':<12}  Automated Unit Testing with Mock Isolation"))
    print(_row(f"  {'Kasus Uji':<12}  13 unit (U-01 s.d. U-13)"))
    print(_row(f"  {'Komponen':<12}  BKTEngine · LLMAgent · GrammarChecker · SRSService"))
    print(cyan(_bline()))
    print(dim("  STATUS         [LAYER BADGE]         KOMPONEN             KASUS UJI                         AKTUAL"))
    print(dim("  " + "─" * (W - 2)))


def tearDownModule():
    try:
        print_layer_summary(ALL_RESULTS, "LAYER 1 · UNIT TESTING", time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE ENTRY
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    setUpModule()
    t0 = time.perf_counter()
    for cls in [Test_L1_BKTEngine, Test_L1_LLMAgent, Test_L1_GrammarChecker]:
        runner.run(loader.loadTestsFromTestCase(cls))
    print_layer_summary(ALL_RESULTS, "LAYER 1 · UNIT TESTING", time.perf_counter() - t0)
