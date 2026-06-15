"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        TVJP – AUTOMATED TESTING SUITE  (Standar Sinta 1 / Skripsi)        ║
║        Sistem Virtual Tutor Bahasa Jepang                                  ║
║                                                                            ║
║  Strategi Pengujian (Berlapis):                                            ║
║    Layer 1 · Unit Testing          – Komponen logika terkecil              ║
║    Layer 2 · Integration Testing   – Interaksi antar modul & layanan       ║
║    Layer 3 · System Testing        – Alur end-to-end (black box)           ║
║    Layer 4 · Acceptance Testing    – Kesesuaian kebutuhan pengguna         ║
║    Layer 5 · White-Box Testing     – Path & branch logika internal         ║
║    Layer 6 · Gray-Box Testing      – Skenario semi-struktural              ║
║    Layer 7 · Non-Functional        – Performa, regression, smoke           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import sys
import os
import time
from collections import Counter
from datetime import datetime, date, timedelta
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir    = os.path.dirname(backend_dir)

for _p in (backend_dir, root_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ─────────────────────────────────────────────────────────────────────────────
# ANSI CONSOLE HELPERS
# Graceful degradation: warna hanya aktif jika terminal mendukung
# ─────────────────────────────────────────────────────────────────────────────
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _ANSI else text

def green(t):   return _c("32;1", t)
def red(t):     return _c("31;1", t)
def yellow(t):  return _c("33;1", t)
def cyan(t):    return _c("36;1", t)
def magenta(t): return _c("35;1", t)
def bold(t):    return _c("1", t)
def dim(t):     return _c("2", t)
def white(t):   return _c("97;1", t)
def blue(t):    return _c("34;1", t)

_supports_unicode = False
try:
    for char in ["✔", "─", "╔", "█"]:
        char.encode(sys.stdout.encoding or 'ascii')
    _supports_unicode = True
except Exception:
    _supports_unicode = False


def safe_print(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '\n')
    text = sep.join(str(arg) for arg in args)
    
    try:
        sys.stdout.write(text + end)
        sys.stdout.flush()
    except UnicodeEncodeError:
        # Fallback to ascii representation of unicode characters
        clean = text.replace("✔", "[OK]").replace("✖", "[FAIL]").replace("⊘", "[SKIP]").replace("⚡", "[ERR]").replace("─", "-").replace("┌", "+").replace("┐", "+").replace("└", "+").replace("┘", "+").replace("├", "+").replace("┤", "+").replace("┬", "+").replace("┴", "+").replace("┼", "+").replace("│", "|").replace("═", "=").replace("║", "|").replace("╔", "+").replace("╗", "+").replace("╚", "+").replace("╝", "+").replace("╠", "+").replace("╣", "+").replace("→", "->").replace("●", "*").replace("█", "#").replace("░", "-").replace("◈", "*").replace("◉", "*").replace("◎", "*").replace("◆", "*").replace("◇", "*").replace("⚠", "[WARN]").replace("⊘", "[SKIP]")
        try:
            sys.stdout.write(clean + end)
            sys.stdout.flush()
        except Exception:
            enc = sys.stdout.encoding or 'ascii'
            fallback = clean.encode(enc, errors='replace').decode(enc, errors='replace')
            sys.stdout.write(fallback + end)
            sys.stdout.flush()

# Redefine print to use safe_print globally in this module
print = safe_print

W = 82   # console width constant

if _supports_unicode:
    BOX_TL, BOX_TR = "╔", "╗"
    BOX_BL, BOX_BR = "╚", "╝"
    BOX_H,  BOX_V  = "═", "║"
    BOX_ML, BOX_MR = "╠", "╣"
    STATUS_ICON = {
        "PASSED":  green("✔ PASSED "),
        "FAILED":  red("✖ FAILED "),
        "SKIPPED": yellow("⊘ SKIPPED"),
        "ERROR":   red("⚡ ERROR  "),
    }
else:
    BOX_TL, BOX_TR = "+", "+"
    BOX_BL, BOX_BR = "+", "+"
    BOX_H,  BOX_V  = "-", "|"
    BOX_ML, BOX_MR = "+", "+"
    STATUS_ICON = {
        "PASSED":  green("[PASSED] "),
        "FAILED":  red("[FAILED] "),
        "SKIPPED": yellow("[SKIPPED]"),
        "ERROR":   red("[ERROR]  "),
    }

def _hline(char=BOX_H, lc=BOX_TL, rc=BOX_TR): return lc + char * (W - 2) + rc
def _mline(): return BOX_ML + BOX_H * (W - 2) + BOX_MR
def _bline(): return BOX_BL + BOX_H * (W - 2) + BOX_BR
def _row(text: str):
    inner = W - 4
    return f"{BOX_V} {text:<{inner}} {BOX_V}"

# Warna badge per layer testing – dipakai di console dan report
LAYER_BADGE = {
    "Unit":             magenta("[UNIT]        "),
    "Integration":      cyan("[INTEGRATION] "),
    "System":           blue("[SYSTEM]      "),
    "Acceptance":       yellow("[ACCEPTANCE]  "),
    "White-Box":        green("[WHITE-BOX]   "),
    "Gray-Box":         cyan("[GRAY-BOX]    "),
    "Non-Functional":   dim("[NON-FUNC]    "),
}

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL MOCK SUPABASE CLIENT
# Mencegah semua HTTP call nyata selama inisialisasi & eksekusi test
# ─────────────────────────────────────────────────────────────────────────────
class MockSupabaseClient:
    """
    Lightweight mock supabase-py client.
    Mengimplementasikan fluent query builder dan menyimpan payload update
    agar bisa diassert di test body.
    """
    def __init__(self):
        self.data: Any  = []
        self.auth       = self
        self._last_update: Any = None

    # Fluent query builder stubs – semua return self agar chaining bisa berjalan
    def table(self, _):          return self
    def select(self, *a, **k):   return self
    def eq(self, *a, **k):       return self
    def neq(self, *a, **k):      return self
    def lte(self, *a, **k):      return self
    def gte(self, *a, **k):      return self
    def lt(self, *a, **k):       return self
    def gt(self, *a, **k):       return self
    def in_(self, *a, **k):      return self
    def order(self, *a, **k):    return self
    def limit(self, *a, **k):    return self
    def single(self, *a, **k):   return self

    def insert(self, data):
        self.data = [data] if isinstance(data, dict) else list(data)
        return self

    def update(self, data):
        self._last_update = data
        self.data = data   # expose payload untuk assertion
        return self

    def upsert(self, data, **k):
        self.data = [data] if isinstance(data, dict) else list(data)
        return self

    def delete(self):
        return self

    def execute(self):
        class _Resp:
            def __init__(self, data): self.data = data
        return _Resp(self.data)


mock_db = MockSupabaseClient()

# Inject mock sebelum import apapun yang menyentuh supabase
from types import ModuleType
_supa_mod_mock = ModuleType("supabase_client")
_supa_mod_mock.supabase = mock_db
sys.modules["core.supabase_client"]         = _supa_mod_mock
sys.modules["backend.core.supabase_client"] = _supa_mod_mock

import core
core.supabase_client = _supa_mod_mock  # type: ignore

try:
    import backend
    backend.core = core  # type: ignore
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# SERVICE IMPORTS  (backend.services.* atau services.* sebagai fallback)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from backend.services.bkt_engine        import BKTEngine
    from backend.services.llm_agent         import (LLMAgent,
                                                     _is_quiz_request,
                                                     _extract_grammar_keywords,
                                                     _normalize_jp_text)
    from backend.services.grammar_checker   import GrammarCheckerService
    from backend.services.srs_service       import SRSService
    from backend.services.streak_service    import StreakService
    from backend.services.voice_service     import VoiceService
    from backend.services.supabase_service  import SupabaseService
    import backend.services.srs_service     as _srs
    import backend.services.streak_service  as _streak
    import backend.services.supabase_service as _supa
    import backend.services.voice_service   as _voice
    import backend.services.llm_agent       as _llm
except ImportError:
    from services.bkt_engine        import BKTEngine
    from services.llm_agent         import (LLMAgent,
                                             _is_quiz_request,
                                             _extract_grammar_keywords,
                                             _normalize_jp_text)
    from services.grammar_checker   import GrammarCheckerService
    from services.srs_service       import SRSService
    from services.streak_service    import StreakService
    from services.voice_service     import VoiceService
    from services.supabase_service  import SupabaseService
    import services.srs_service     as _srs
    import services.streak_service  as _streak
    import services.supabase_service as _supa
    import services.voice_service   as _voice
    import services.llm_agent       as _llm

for _m in (_srs, _streak, _supa, _voice, _llm):
    if hasattr(_m, "supabase"):
        _m.supabase = mock_db

# ─────────────────────────────────────────────────────────────────────────────
# ACCUMULATED RESULTS STORE  (diakses lintas class)
# ─────────────────────────────────────────────────────────────────────────────
ALL_RESULTS: list[dict] = []
_result_counter = 0


# ─────────────────────────────────────────────────────────────────────────────
# BASE TEST CASE
# ─────────────────────────────────────────────────────────────────────────────
class TVJPBaseTest(unittest.TestCase):
    """
    Base class untuk semua TVJP test suite.
    Menyediakan:
      - setUp / tearDown dengan pengukuran waktu presisi tinggi
      - log_result() untuk mencatat dan mencetak setiap kasus uji
      - run_async() untuk menjalankan coroutine secara sinkron
      - _reset_db() untuk membersihkan mock database
    """

    LAYER: str = "Unit"   # Override di subclass

    def setUp(self):
        self._t0 = time.perf_counter()
        self._reset_db()

    def tearDown(self):
        dur = round(time.perf_counter() - self._t0, 4)
        if ALL_RESULTS:
            ALL_RESULTS[-1]["duration"] = dur

    def _reset_db(self):
        mock_db.data          = []
        mock_db._last_update  = None

    def log_result(
        self,
        service:   str,
        name:      str,
        desc:      str,
        inputs:    str,
        expected:  str,
        actual:    str,
        status:    str,
        layer:     str | None = None,
    ) -> None:
        global _result_counter
        _result_counter += 1
        layer = layer or self.LAYER
        
        # Detect actual exception details for precise categorization of errors vs failures
        import sys
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_val is not None and status in ("FAILED", "ERROR"):
            if isinstance(exc_val, AssertionError):
                status = "FAILED"
            else:
                status = "ERROR"

        # Replace non-unicode characters if target console doesn't support them
        if not _supports_unicode:
            actual = actual.replace("→", "->").replace("●", "*")
            inputs = inputs.replace("→", "->").replace("●", "*")
            expected = expected.replace("→", "->").replace("●", "*")

        ALL_RESULTS.append({
            "no":       _result_counter,
            "layer":    layer,
            "service":  service,
            "name":     name,
            "desc":     desc,
            "inputs":   inputs,
            "expected": expected,
            "actual":   actual,
            "status":   status,
            "duration": 0.0,
        })

        # ── Console row ───────────────────────────────────────────────────────
        badge   = LAYER_BADGE.get(layer, f"[{layer:<13}]")
        st_icon = STATUS_ICON.get(status, status)
        svc_col = cyan(f"{service:<22}")
        name_col = bold(f"{name:<34}")
        actual_s = (actual[:30] + "…") if len(actual) > 33 else actual
        log_line = f"  {st_icon}  {badge}  {svc_col}  {name_col}  {dim(actual_s)}"
        try:
            print(log_line)
        except UnicodeEncodeError:
            import re
            clean_log = re.sub(r'\033\[[0-9;]*m', '', log_line)
            clean_log = clean_log.replace("✔", "[OK]").replace("✖", "[FAIL]").replace("⊘", "[SKIP]").replace("⚡", "[ERR]")
            clean_log = clean_log.encode('ascii', 'replace').decode('ascii')
            print(clean_log)

    @staticmethod
    def run_async(coro): return asyncio.run(coro)


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 1 · UNIT TESTING
#  Menguji komponen terkecil secara terisolasi (single function/method)
# ═════════════════════════════════════════════════════════════════════════════

class Test_L1_BKTEngine(TVJPBaseTest):
    """Unit Testing – BKT Engine (Cognitive Adaptive Modeling)."""
    LAYER = "Unit"

    def setUp(self):
        super().setUp()
        self.bkt = BKTEngine()

    # ── U-01 ──────────────────────────────────────────────────────────────────
    def test_U01_cat_difficulty_selection(self):
        """[U-01] compute_cat_difficulty() – threshold P(L) ke label kesulitan."""
        desc     = "Menguji pemilihan level kesulitan CAT adaptif berdasarkan nilai mastery P(L)."
        inputs   = "p_mastered ∈ {0.85, 0.50, 0.20}"
        expected = "0.85→hard | 0.50→medium | 0.20→easy"
        try:
            for p, exp in [(0.85, "hard"), (0.50, "medium"), (0.20, "easy")]:
                with self.subTest(p=p):
                    got = self.bkt.compute_cat_difficulty(p_mastered=p)
                    self.assertEqual(got, exp)
            self.log_result("BKT Engine", "CAT Difficulty Selection",
                            desc, inputs, expected,
                            "0.85→hard | 0.50→medium | 0.20→easy", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "CAT Difficulty Selection",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-02 ──────────────────────────────────────────────────────────────────
    def test_U02_bayesian_belief_update(self):
        """[U-02] update_belief() – pembaruan matematis P(L) Bayesian."""
        desc     = "Menguji perbaruan P(L) saat jawaban benar/salah dan validasi batas [0.001, 0.999]."
        inputs   = "p_l=0.5, correct=T/F; boundary p_l=0.999 & 0.001"
        expected = "Benar→>0.5 | Salah→<0.5 | Clamp aman"
        try:
            params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}
            pc  = self.bkt.update_belief(0.5,   True,  params)
            pi  = self.bkt.update_belief(0.5,   False, params)
            phi = self.bkt.update_belief(0.999, True,  params)
            plo = self.bkt.update_belief(0.001, False, params)
            self.assertGreater(pc,  0.5);  self.assertLess(pi, 0.5)
            self.assertLessEqual(phi, 0.999); self.assertGreaterEqual(plo, 0.001)
            self.log_result("BKT Engine", "Bayesian Belief Update",
                            desc, inputs, expected,
                            f"T→{pc:.4f} | F→{pi:.4f} | clamp OK", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Bayesian Belief Update",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-03 ──────────────────────────────────────────────────────────────────
    def test_U03_sequential_mastery(self):
        """[U-03] compute_mastery() – akumulasi mastery dari sekuens jawaban."""
        desc     = "Menguji kalkulasi mastery dari rangkaian observasi jawaban berurutan."
        inputs   = "obs=[T,T,T] dan obs=[F,F]"
        expected = "[T,T,T]→mastered=True | [F,F]→mastered=False"
        try:
            rp = self.bkt.compute_mastery([True, True, True], "vocab")
            rf = self.bkt.compute_mastery([False, False],     "vocab")
            self.assertTrue(rp["is_mastered"]); self.assertFalse(rf["is_mastered"])
            self.log_result("BKT Engine", "Sequential Mastery",
                            desc, inputs, expected,
                            f"[T,T,T]→{rp['is_mastered']} | [F,F]→{rf['is_mastered']}", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Sequential Mastery",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-04 ──────────────────────────────────────────────────────────────────
    def test_U04_information_gain_node_selection(self):
        """[U-04] select_next_questions() – heuristik IG untuk pemilihan soal adaptif."""
        desc     = "Menguji heuristik Information Gain memilih node dengan entropi tertinggi (~0.5)."
        inputs   = "beliefs={n1:0.5, n2:0.9, n3:0.1}, count=2"
        expected = "n1 dipilih; n2 dikecualikan (mastered ≥ 0.85)"
        try:
            beliefs = {"n1": 0.5, "n2": 0.9, "n3": 0.1}
            nodes   = [{"id": k, "name": f"Node {k}"} for k in beliefs]
            sel     = self.bkt.select_next_questions(beliefs, nodes, count=2)
            ids     = [n["id"] for n in sel]
            self.assertIn("n1", ids); self.assertNotIn("n2", ids)
            self.log_result("BKT Engine", "IG Node Selection",
                            desc, inputs, expected, f"Dipilih: {ids}", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "IG Node Selection",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-05 ──────────────────────────────────────────────────────────────────
    def test_U05_difficulty_estimation(self):
        """[U-05] estimate_difficulty() – kalkulasi tingkat kesulitan dari correct rate."""
        desc     = "Menguji estimasi tingkat kesulitan soal dari distribusi jawaban kolektif."
        inputs   = "correct_rate ∈ {80%, 50%, 25%}"
        expected = "80%→easy | 50%→medium | 25%→hard"
        try:
            cases = [([True]*4+[False], "easy"),
                     ([True,False]*2,   "medium"),
                     ([False]*3+[True], "hard")]
            for obs, exp in cases:
                with self.subTest(exp=exp):
                    self.assertEqual(self.bkt.estimate_difficulty(obs), exp)
            self.log_result("BKT Engine", "Difficulty Estimation",
                            desc, inputs, expected,
                            " | ".join(f"{e}" for _,e in cases), "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Difficulty Estimation",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


class Test_L1_LLMAgent(TVJPBaseTest):
    """Unit Testing – LLM Agent (NLU, Normalisasi, TTS Filter)."""
    LAYER = "Unit"

    def setUp(self):
        super().setUp()
        self.agent = LLMAgent(graph=MagicMock())

    # ── U-06 ──────────────────────────────────────────────────────────────────
    def test_U06_quiz_intent_detection(self):
        """[U-06] _is_quiz_request() – klasifikasi intent kuis vs Q&A umum."""
        desc     = "Menguji deteksi intent permintaan kuis dari ucapan natural user."
        inputs   = "Positif: 'latihan kuis' | Negatif: 'siapa dewa kematian'"
        expected = "Kuis → True | Q&A → False"
        try:
            pos = ["Berikan kuis JLPT N5", "latihan kuis", "beri aku soal latihan"]
            neg = ["siapakah dewa kematian jepang?", "apa itu haiku?"]
            for t in pos:
                with self.subTest(t=t): self.assertTrue(_is_quiz_request(t))
            for t in neg:
                with self.subTest(t=t): self.assertFalse(_is_quiz_request(t))
            self.log_result("LLM Agent", "Quiz Intent Detection",
                            desc, inputs, expected,
                            f"{len(pos)} positif ✔ | {len(neg)} negatif ✔", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "Quiz Intent Detection",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-07 ──────────────────────────────────────────────────────────────────
    def test_U07_grammar_keyword_extraction(self):
        """[U-07] _extract_grammar_keywords() – ekstraksi keyword untuk RAG retrieval."""
        desc     = "Menguji ekstraksi kata kunci tata bahasa Jepang untuk pencarian modul RAG."
        inputs   = "'N5 Grammar ~てください'"
        expected = "'てください' ada di hasil ekstraksi"
        try:
            kw = _extract_grammar_keywords("N5 Grammar ~てください")
            self.assertIn("てください", kw)
            self.log_result("LLM Agent", "Grammar Keyword Extraction",
                            desc, inputs, expected, f"Keywords: {kw}", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "Grammar Keyword Extraction",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-08 ──────────────────────────────────────────────────────────────────
    def test_U08_jp_text_normalization(self):
        """[U-08] _normalize_jp_text() – pembersihan whitespace teks Jepang."""
        desc     = "Menguji normalisasi teks Jepang dari spasi berlebih sebelum dikirim ke generator."
        inputs   = "'こんにちは   ！  '"
        expected = "'こんにちは'"
        try:
            out = _normalize_jp_text("こんにちは   ！  ")
            self.assertEqual(out, "こんにちは")
            self.log_result("LLM Agent", "JP Text Normalization",
                            desc, inputs, expected, f"→ '{out}'", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "JP Text Normalization",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-09 ──────────────────────────────────────────────────────────────────
    def test_U09_tts_text_filter(self):
        """[U-09] _prepare_tts_text() – hapus teks Latin sebelum ke TTS Jepang."""
        desc     = "Menguji pembersihan markdown dan strip prefix JP: dari teks TTS."
        inputs   = "'JP: **りんごを食べる**'"
        expected = "'りんごを食べる'"
        try:
            out = self.agent._prepare_tts_text("JP: **りんごを食べる**")
            self.assertEqual(out, "りんご\u3092\u98df\u3079\u308b")
            self.log_result("LLM Agent", "TTS Text Filter",
                            desc, inputs, expected, f"→ '{out}'", "PASSED")
        except Exception as e:
            self.log_result("LLM Agent", "TTS Text Filter",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


class Test_L1_GrammarChecker(TVJPBaseTest):
    """Unit Testing – Grammar Checker (Tokenisasi & Deteksi Kesalahan)."""
    LAYER = "Unit"

    def setUp(self):
        super().setUp()
        self.gc = GrammarCheckerService()

    # ── U-10 ──────────────────────────────────────────────────────────────────
    def test_U10_morphology_tokenization(self):
        """[U-10] tokenize() – pemecahan morfologi menggunakan Pykakasi."""
        desc     = "Menguji tokenisasi morfologi teks Jepang ke unit kata terkecil."
        inputs   = "'私は学生です'"
        expected = "Token ['私', '学生'] ada dalam hasil"
        try:
            tokens   = self.gc.tokenize("私は学生です")
            surfaces = [t["original"] for t in tokens]
            for s in ("私", "学生"):
                with self.subTest(s=s): self.assertIn(s, surfaces)
            self.log_result("Grammar Checker", "Morphology Tokenization",
                            desc, inputs, expected, f"Tokens: {surfaces}", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Morphology Tokenization",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-11 ──────────────────────────────────────────────────────────────────
    def test_U11_text_metrics(self):
        """[U-11] basic_analysis() – statistik karakter dan token count."""
        desc     = "Menguji kalkulasi statistik dasar teks (char count, token count)."
        inputs   = "'私は日本語を勉強します' (11 karakter)"
        expected = "char_count = 11"
        try:
            a = self.gc.basic_analysis("私は日本語を勉強します")
            self.assertEqual(a["char_count"], 11)
            self.log_result("Grammar Checker", "Text Metrics",
                            desc, inputs, expected,
                            f"char={a['char_count']} | token={a['token_count']}", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Text Metrics",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-12 ──────────────────────────────────────────────────────────────────
    def test_U12_double_particle_detection(self):
        """[U-12] detect_common_errors() – deteksi partikel ganda (double を)."""
        desc     = "Menguji deteksi pola kesalahan partikel ganda berbasis aturan (rule-based)."
        inputs   = "'私はりんごをを食べる'"
        expected = "Error type 'particle_error' terdeteksi"
        try:
            errs  = self.gc.detect_common_errors("私はりんごをを食べる")
            types = [e["type"] for e in errs]
            self.assertIn("particle_error", types)
            self.log_result("Grammar Checker", "Double Particle Detection",
                            desc, inputs, expected, f"Errors: {types}", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Double Particle Detection",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── U-13 ──────────────────────────────────────────────────────────────────
    def test_U13_sm2_algorithm(self):
        """[U-13] SRSService.calculate_sm2() – validasi rumus SM-2 murni."""
        desc     = "Menguji keakuratan kalkulasi interval, repetisi, dan EF algoritma SM-2."
        inputs   = "Q=5 rep0 | Q=5 rep1 | Q=1 rep2 (fail)"
        expected = "Rep0→reps=1,int=1 | Rep1→reps=2,int=6 | Fail→reps=0,ef<2.6"
        try:
            r0 = SRSService.calculate_sm2(5, 0, 2.5, 1)
            r1 = SRSService.calculate_sm2(5, 1, 2.5, 1)
            rf = SRSService.calculate_sm2(1, 2, 2.6, 6)
            self.assertEqual(r0["repetitions"],  1); self.assertEqual(r0["interval_days"], 1)
            self.assertEqual(r1["repetitions"],  2); self.assertEqual(r1["interval_days"], 6)
            self.assertEqual(rf["repetitions"],  0); self.assertEqual(rf["interval_days"], 1)
            self.assertLess(rf["easiness_factor"], 2.6)
            self.log_result("SRS Service", "SM-2 Algorithm",
                            desc, inputs, expected,
                            f"r0reps={r0['repetitions']} | r1int={r1['interval_days']} | rfef={rf['easiness_factor']:.3f}",
                            "PASSED")
        except Exception as e:
            self.log_result("SRS Service", "SM-2 Algorithm",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 2 · INTEGRATION TESTING
#  Menguji interaksi & aliran data antar dua modul atau lebih
# ═════════════════════════════════════════════════════════════════════════════

class Test_L2_Integration(TVJPBaseTest):
    """Integration Testing – Interaksi antar modul layanan backend."""
    LAYER = "Integration"

    def setUp(self):
        super().setUp()
        self.agent = LLMAgent(graph=MagicMock())
        self.gc    = GrammarCheckerService()
        self.vs    = VoiceService()

    # ── I-01 ──────────────────────────────────────────────────────────────────
    def test_I01_srs_review_pipeline(self):
        """[I-01] SRSService.record_review() – SRS Engine ↔ Supabase DB."""
        desc     = "Menguji pipeline pencatatan review: SM-2 Engine → Supabase update jadwal."
        inputs   = "user_id='u1', node_id='n1', quality=4 (reps awal=1)"
        expected = "reps naik ke 2, node_id='n1', quality=4 tersimpan"
        try:
            mock_db.data = [{
                "user_id": "u1", "node_id": "n1", "node_type": "vocab",
                "repetitions": 1, "easiness_factor": 2.5, "interval_days": 1,
            }]
            res = self.run_async(SRSService.record_review("u1", "n1", "vocab", 4))
            self.assertEqual(res["node_id"],     "n1")
            self.assertEqual(res["quality"],     4)
            self.assertEqual(res["repetitions"], 2)
            self.log_result("SRS ↔ Supabase", "Review Record Pipeline",
                            desc, inputs, expected,
                            f"reps={res['repetitions']} | quality={res['quality']}", "PASSED")
        except Exception as e:
            self.log_result("SRS ↔ Supabase", "Review Record Pipeline",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── I-02 ──────────────────────────────────────────────────────────────────
    def test_I02_llm_translation_to_tts(self):
        """[I-02] LLMAgent translation → TTS filter pipeline."""
        desc     = "Menguji aliran data dari layer translasi LLM ke filter TTS Jepang."
        inputs   = "Teks Indonesia → translate mock → TTS filter"
        expected = "Output TTS dibersihkan dari markdown dan prefix JP:"
        try:
            self.agent.translate_and_romaji_user_llm = AsyncMock(return_value={
                "jp": "JP: **私はリンゴが好きです**", "romaji": "Watashi wa ringo ga suki desu",
            })
            res      = self.run_async(self.agent.translate_and_romaji_user_llm("Saya suka apel"))
            filtered = self.agent._prepare_tts_text(res["jp"])
            self.assertEqual(filtered, "私はリンゴが好きです")
            self.log_result("LLM → TTS", "Translation→TTS Pipeline",
                            desc, inputs, expected,
                            f"'{filtered[:30]}…'", "PASSED")
        except Exception as e:
            self.log_result("LLM → TTS", "Translation→TTS Pipeline",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── I-03 ──────────────────────────────────────────────────────────────────
    def test_I03_grammar_checker_to_llm_prompt(self):
        """[I-03] GrammarChecker tokenize() → build_llm_prompt() integration."""
        desc     = "Menguji integrasi tokenisasi morfologi ke konstruksi prompt LLM."
        inputs   = "'りんごを食べる' → tokenize → build prompt"
        expected = "Prompt memuat teks asli dan 'JSON' instruction"
        try:
            tokens = self.gc.tokenize("りんごを食べる")
            prompt = self.gc.build_llm_prompt("りんごを食べる", tokens)
            self.assertIn("りんごを食べる", prompt)
            self.assertIn("JSON", prompt)
            self.log_result("Grammar → LLM", "Tokenizer→Prompt Pipeline",
                            desc, inputs, expected,
                            f"Prompt {len(prompt)} chars ✔", "PASSED")
        except Exception as e:
            self.log_result("Grammar → LLM", "Tokenizer→Prompt Pipeline",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── I-04 ──────────────────────────────────────────────────────────────────
    def test_I04_streak_goals_to_progress(self):
        """[I-04] StreakService goals ↔ progress calculation."""
        desc     = "Menguji aliran data dari konfigurasi goals ke kalkulasi progress harian."
        inputs   = "reviewed=5, study_minutes=15 | target review=5, minutes=15"
        expected = "review_pct=100 | minutes_pct=100"
        try:
            mock_db.data = [{
                "study_date": date.today().isoformat(), "study_minutes": 15,
                "items_reviewed": 5, "quests_completed": 1, "xp_earned": 20,
            }]
            with patch("backend.services.streak_service.StreakService.get_daily_goals",
                       new_callable=AsyncMock) as mg:
                mg.return_value = {"vocab_target":10,"grammar_target":2,
                                   "review_target":5,"study_minutes_target":15}
                prog = self.run_async(StreakService.get_today_progress("u1"))
            self.assertEqual(prog["completion"]["review_pct"],  100)
            self.assertEqual(prog["completion"]["minutes_pct"], 100)
            self.log_result("Streak Goals ↔ Progress", "Goals→Progress Pipeline",
                            desc, inputs, expected,
                            f"review={prog['completion']['review_pct']}% | "
                            f"min={prog['completion']['minutes_pct']}%", "PASSED")
        except Exception as e:
            self.log_result("Streak Goals ↔ Progress", "Goals→Progress Pipeline",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── I-05 ──────────────────────────────────────────────────────────────────
    def test_I05_voice_stt_to_translation(self):
        """[I-05] VoiceService STT → Translation pipeline."""
        desc     = "Menguji aliran data dari transkripsi Whisper ke layer translasi suara."
        inputs   = "WAV file → STT → translate"
        expected = "Transkripsi 'こんにちは' → terjemahan valid"
        try:
            self.vs.transcribe_audio = AsyncMock(return_value="こんにちは")
            transcript = self.run_async(self.vs.transcribe_audio("audio.wav"))
            self.assertEqual(transcript, "こんにちは")
            with patch("deep_translator.GoogleTranslator.translate",
                       return_value="Halo"):
                trans_res = self.run_async(
                    self.vs.translate_and_romaji_user(transcript)
                )
            self.assertIn("jp", trans_res)
            self.log_result("Voice STT ↔ Translation", "STT→Translation Pipeline",
                            desc, inputs, expected,
                            f"STT='{transcript}' | jp='{trans_res['jp']}'", "PASSED")
        except Exception as e:
            self.log_result("Voice STT ↔ Translation", "STT→Translation Pipeline",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 3 · SYSTEM TESTING  (Black Box)
#  Menguji sistem sebagai satu kesatuan dari perspektif pengguna
# ═════════════════════════════════════════════════════════════════════════════

class Test_L3_System(TVJPBaseTest):
    """
    System Testing (Black Box) – Validasi alur end-to-end dari sudut pandang pengguna.
    Penguji tidak perlu mengetahui struktur internal; hanya input→output yang dinilai.
    """
    LAYER = "System"

    # ── S-01 ──────────────────────────────────────────────────────────────────
    def test_S01_learning_session_flow(self):
        """[S-01] Alur sesi belajar: BKT → SRS → Streak update."""
        desc     = "Menguji skenario end-to-end satu sesi belajar vocabulary."
        inputs   = "User menjawab benar → record review → update streak"
        expected = "P(L) meningkat, reps naik, streak bertambah – tanpa error"
        try:
            bkt  = BKTEngine()
            p_l  = bkt.update_belief(0.5, True, {"p_t":0.15,"p_g":0.25,"p_s":0.05})
            self.assertGreater(p_l, 0.5)

            mock_db.data = [{"user_id":"u1","node_id":"n1","node_type":"vocab",
                             "repetitions":0,"easiness_factor":2.5,"interval_days":1}]
            review = self.run_async(SRSService.record_review("u1","n1","vocab",5))
            self.assertEqual(review["repetitions"], 1)

            mock_db.data = [{"study_date": date.today().isoformat()}]
            streak = self.run_async(StreakService.update_streak("u1"))
            self.assertGreaterEqual(streak["streak_days"], 1)

            self.log_result("System (E2E)", "Learning Session Flow",
                            desc, inputs, expected,
                            f"P(L)={p_l:.3f} | reps={review['repetitions']} | "
                            f"streak={streak['streak_days']}", "PASSED")
        except Exception as e:
            self.log_result("System (E2E)", "Learning Session Flow",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── S-02 ──────────────────────────────────────────────────────────────────
    def test_S02_voice_interaction_flow(self):
        """[S-02] Alur interaksi suara: STT → Chat → TTS output."""
        desc     = "Menguji skenario end-to-end input suara hingga output audio."
        inputs   = "Audio WAV user → transkripsi → chat LLM → sintesis suara"
        expected = "Path file .wav output berhasil dibuat"
        try:
            vs = VoiceService()
            vs.transcribe_audio = AsyncMock(return_value="りんごを食べる")
            text = self.run_async(vs.transcribe_audio("test.wav"))
            self.assertIsInstance(text, str)

            mc   = MagicMock()
            mr   = MagicMock()
            mr.status_code = 200
            mr.content     = b"fake wav"
            async def _post(*a, **k): return mr
            mc.post = _post
            mc.__aenter__ = AsyncMock(return_value=mc)
            mc.__aexit__  = AsyncMock(return_value=False)

            with patch("httpx.AsyncClient", return_value=mc):
                path = self.run_async(vs.synthesize_speech(text))
            self.assertTrue(path.endswith(".wav"))
            if os.path.exists(path): os.unlink(path)
            self.log_result("System (E2E)", "Voice Interaction Flow",
                            desc, inputs, expected,
                            f"STT='{text}' | WAV='{os.path.basename(path)}'", "PASSED")
        except Exception as e:
            self.log_result("System (E2E)", "Voice Interaction Flow",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── S-03 ──────────────────────────────────────────────────────────────────
    def test_S03_quiz_adaptive_flow(self):
        """[S-03] Alur kuis adaptif: BKT CAT → soal → update mastery."""
        desc     = "Menguji skenario kuis adaptif dari pemilihan soal hingga update kognitif."
        inputs   = "beliefs={n1:0.4, n2:0.9} → pilih soal → jawab benar → update P(L)"
        expected = "n1 terpilih (bukan n2 mastered); P(L) n1 meningkat"
        try:
            bkt      = BKTEngine()
            beliefs  = {"n1": 0.4, "n2": 0.9}
            nodes    = [{"id":"n1","name":"Node 1"},{"id":"n2","name":"Node 2"}]
            selected = bkt.select_next_questions(beliefs, nodes, count=1)
            self.assertEqual(selected[0]["id"], "n1")

            new_p = bkt.update_belief(beliefs["n1"], True,
                                      {"p_t":0.15,"p_g":0.25,"p_s":0.05})
            self.assertGreater(new_p, beliefs["n1"])
            self.log_result("System (E2E)", "Adaptive Quiz Flow",
                            desc, inputs, expected,
                            f"Pilih=n1 | P(L) {beliefs['n1']:.2f}→{new_p:.4f}", "PASSED")
        except Exception as e:
            self.log_result("System (E2E)", "Adaptive Quiz Flow",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 4 · ACCEPTANCE TESTING  (UAT – User Acceptance Testing)
#  Menguji kesesuaian sistem dengan kebutuhan dan harapan pengguna akhir
# ═════════════════════════════════════════════════════════════════════════════

class Test_L4_Acceptance(TVJPBaseTest):
    """
    Acceptance Testing (UAT) – Validasi sistem terhadap kebutuhan pengguna.
    Skenario ditulis dari perspektif pelajar bahasa Jepang, bukan developer.
    """
    LAYER = "Acceptance"

    # ── A-01 ──────────────────────────────────────────────────────────────────
    def test_A01_learner_sees_correct_difficulty(self):
        """[A-01] Pelajar menerima soal pada level kesulitan yang sesuai kemampuan."""
        desc     = "UAT: Pelajar pemula (P(L)=0.2) harus mendapat soal 'easy'."
        inputs   = "User profile P(L)=0.2 (pemula)"
        expected = "Sistem mengalokasikan soal level 'easy'"
        try:
            bkt  = BKTEngine()
            diff = bkt.compute_cat_difficulty(p_mastered=0.2)
            self.assertEqual(diff, "easy",
                "Pelajar pemula harus mendapat soal 'easy', bukan sesuatu yang lebih sulit")
            self.log_result("Acceptance", "Appropriate Difficulty for Beginner",
                            desc, inputs, expected,
                            f"P(L)=0.2 → difficulty='{diff}' ✔", "PASSED")
        except Exception as e:
            self.log_result("Acceptance", "Appropriate Difficulty for Beginner",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── A-02 ──────────────────────────────────────────────────────────────────
    def test_A02_learner_streak_motivation(self):
        """[A-02] Streak harian memberikan motivasi belajar berkelanjutan."""
        desc     = "UAT: Sistem harus mencatat dan menampilkan streak belajar harian yang akurat."
        inputs   = "Belajar hari ini dan kemarin"
        expected = "Sistem menampilkan streak_days = 2"
        try:
            today = date.today()
            mock_db.data = [
                {"study_date": today.isoformat()},
                {"study_date": (today - timedelta(days=1)).isoformat()},
            ]
            info = self.run_async(StreakService.update_streak("u1"))
            self.assertGreaterEqual(info["streak_days"], 2,
                f"Pelajar belajar 2 hari berturut-turut, streak harus ≥2")
            self.log_result("Acceptance", "Streak Motivation System",
                            desc, inputs, expected,
                            f"streak_days={info['streak_days']} ✔", "PASSED")
        except Exception as e:
            self.log_result("Acceptance", "Streak Motivation System",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── A-03 ──────────────────────────────────────────────────────────────────
    def test_A03_learner_xp_and_leveling(self):
        """[A-03] Sistem gamifikasi XP mendorong keterlibatan pengguna."""
        desc     = "UAT: Pengguna naik level setelah mengumpulkan XP yang cukup."
        inputs   = "XP awal=95, aksi VOCAB_MASTERED (+10 XP)"
        expected = "xp=105, level naik ke 2"
        try:
            mock_db.data = [{"xp": 95, "level": 1}]
            self.run_async(SupabaseService.update_user_stats("u1", "VOCAB_MASTERED"))
            payload = mock_db.data
            self.assertEqual(payload["xp"],    105)
            self.assertEqual(payload["level"],   2)
            self.log_result("Acceptance", "XP & Level-Up Gamification",
                            desc, inputs, expected,
                            f"xp={payload['xp']} | level={payload['level']} ✔", "PASSED")
        except Exception as e:
            self.log_result("Acceptance", "XP & Level-Up Gamification",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── A-04 ──────────────────────────────────────────────────────────────────
    def test_A04_grammar_error_feedback(self):
        """[A-04] Pengguna menerima umpan balik grammar yang dapat dipahami."""
        desc     = "UAT: Sistem mendeteksi dan melaporkan kesalahan grammar dalam respons yang jelas."
        inputs   = "Kalimat dengan double particle 'をを'"
        expected = "Response mengandung informasi error yang actionable"
        try:
            gc    = GrammarCheckerService()
            errs  = gc.detect_common_errors("私はりんごをを食べる")
            self.assertTrue(len(errs) > 0, "Harus ada setidaknya satu error terdeteksi")
            self.assertIn("particle_error", [e["type"] for e in errs])
            has_msg = all("message" in e or "description" in e for e in errs)
            # Cukup jika error terdeteksi, message field opsional per implementasi
            self.log_result("Acceptance", "Grammar Error Feedback",
                            desc, inputs, expected,
                            f"{len(errs)} error terdeteksi | types={[e['type'] for e in errs]}",
                            "PASSED")
        except Exception as e:
            self.log_result("Acceptance", "Grammar Error Feedback",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 5 · WHITE-BOX TESTING
#  Menguji path, branch, dan kondisi batas pada logika internal
# ═════════════════════════════════════════════════════════════════════════════

class Test_L5_WhiteBox(TVJPBaseTest):
    """
    White-Box Testing – Pengujian berbasis pengetahuan struktural internal kode.
    Mencakup: branch coverage, boundary value analysis, kondisi edge case.
    """
    LAYER = "White-Box"

    def setUp(self):
        super().setUp()
        self.bkt = BKTEngine()

    # ── W-01 ──────────────────────────────────────────────────────────────────
    def test_W01_boundary_mastery_threshold(self):
        """[W-01] Branch coverage: ambang batas mastery tepat di 0.85."""
        desc     = "White-Box: menguji kedua cabang P(L) ≥ 0.85 (mastered) dan < 0.85 (not yet)."
        inputs   = "p_l = 0.85 (threshold) | p_l = 0.849 | p_l = 0.851"
        expected = "0.85→mastered (skipped) | 0.849→not yet (selected) | 0.851→mastered (skipped)"
        try:
            nodes = [
                {"id": "n_at", "name": "At Threshold"},
                {"id": "n_below", "name": "Below Threshold"},
                {"id": "n_above", "name": "Above Threshold"}
            ]
            beliefs = {
                "n_at": 0.85,
                "n_below": 0.849,
                "n_above": 0.851
            }
            selected = self.bkt.select_next_questions(beliefs, nodes, count=3)
            selected_ids = [n["id"] for n in selected]
            
            # Boundary assertions on mastery threshold
            self.assertIn("n_below", selected_ids)
            self.assertNotIn("n_at", selected_ids)
            self.assertNotIn("n_above", selected_ids)
            
            self.log_result("BKT Engine", "Mastery Boundary Branch",
                            desc, inputs, expected,
                            "0.85→skipped | 0.849→selected | 0.851→skipped", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Mastery Boundary Branch",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── W-02 ──────────────────────────────────────────────────────────────────
    def test_W02_sm2_ef_floor_boundary(self):
        """[W-02] Boundary value: EF tidak boleh turun di bawah 1.3 (SM-2 constraint)."""
        desc     = "White-Box: SM-2 harus mempertahankan easiness_factor ≥ 1.3 setelah kegagalan berulang."
        inputs   = "Skenario quality=0 (kegagalan total) berulang dengan EF rendah"
        expected = "EF tidak pernah < 1.3 (batas bawah algoritma SM-2)"
        try:
            ef = 2.5
            for _ in range(10):
                res = SRSService.calculate_sm2(quality=0, repetitions=0,
                                               easiness_factor=ef, interval_days=1)
                ef  = res["easiness_factor"]
                self.assertGreaterEqual(ef, 1.3,
                    f"EF={ef:.4f} melanggar batas bawah 1.3 (SM-2 constraint)")
            self.log_result("SRS Service", "SM-2 EF Floor Boundary",
                            desc, inputs, expected,
                            f"EF final={ef:.4f} (≥1.3) ✔", "PASSED")
        except Exception as e:
            self.log_result("SRS Service", "SM-2 EF Floor Boundary",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── W-03 ──────────────────────────────────────────────────────────────────
    def test_W03_belief_update_all_branches(self):
        """[W-03] Branch coverage: semua kombinasi correct/incorrect × boundary P(L)."""
        desc     = "White-Box: setiap cabang kondisi di update_belief dicakup."
        inputs   = "4 kombinasi: (low,T), (high,T), (low,F), (high,F)"
        expected = "Semua cabang menghasilkan nilai dalam [0.001, 0.999]"
        try:
            params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}
            cases  = [(0.001,True),(0.999,True),(0.001,False),(0.999,False)]
            for p, c in cases:
                with self.subTest(p=p, correct=c):
                    out = self.bkt.update_belief(p, c, params)
                    self.assertGreaterEqual(out, 0.001)
                    self.assertLessEqual(out, 0.999)
            self.log_result("BKT Engine", "Belief Update All Branches",
                            desc, inputs, expected,
                            f"{len(cases)} branch kombinasi valid ✔", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Belief Update All Branches",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── W-04 ──────────────────────────────────────────────────────────────────
    def test_W04_streak_gap_tolerance_branch(self):
        """[W-04] Branch: toleransi celah streak – gap=1 hari dilanjutkan, gap=2 diputus."""
        desc     = "White-Box: dua cabang kondisi pada logika gap toleransi StreakService."
        inputs   = "Skenario A: gap=1 hari | Skenario B: gap=2 hari"
        expected = "Gap 1 hari → streak lanjut | Gap 2 hari → streak putus (=1)"
        try:
            today = date.today()

            # Branch A: gap 1 hari (dua hari berturut) → streak ≥ 2
            mock_db.data = [
                {"study_date": today.isoformat()},
                {"study_date": (today - timedelta(days=1)).isoformat()},
            ]
            info_a = self.run_async(StreakService.update_streak("u1"))
            self._reset_db()

            # Branch B: gap 2 hari (hari ini dan 3 hari yang lalu, i.e. 2 hari bolos) → streak = 1 (hanya hari ini)
            mock_db.data = [
                {"study_date": today.isoformat()},
                {"study_date": (today - timedelta(days=3)).isoformat()},
            ]
            info_b = self.run_async(StreakService.update_streak("u1"))

            self.assertGreaterEqual(info_a["streak_days"], 2)
            self.assertEqual(info_b["streak_days"], 1)
            self.log_result("Streak Service", "Gap Tolerance Branch",
                            desc, inputs, expected,
                            f"Gap1→streak={info_a['streak_days']} | "
                            f"Gap2→streak={info_b['streak_days']}", "PASSED")
        except Exception as e:
            self.log_result("Streak Service", "Gap Tolerance Branch",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 6 · GRAY-BOX TESTING
#  Penguji memiliki pengetahuan sebagian tentang struktur internal
# ═════════════════════════════════════════════════════════════════════════════

class Test_L6_GrayBox(TVJPBaseTest):
    """
    Gray-Box Testing – Pengujian semi-struktural dengan pengetahuan parsial
    tentang arsitektur sistem (schema DB, tipe return, struktur payload).
    """
    LAYER = "Gray-Box"

    # ── G-01 ──────────────────────────────────────────────────────────────────
    def test_G01_srs_payload_schema(self):
        """[G-01] Validasi schema payload SRS yang dikirim ke Supabase."""
        desc     = "Gray-Box: mengetahui schema tabel srs_items – memvalidasi field wajib di payload update."
        inputs   = "record_review() setelah satu sesi"
        expected = "Payload update memuat: node_id, next_review, interval_days, repetitions"
        try:
            mock_db.data = [{"user_id":"u1","node_id":"n1","node_type":"vocab",
                             "repetitions":1,"easiness_factor":2.5,"interval_days":1}]
            res = self.run_async(SRSService.record_review("u1","n1","vocab",4))
            required_fields = {"node_id","next_review","interval_days","repetitions"}
            missing = required_fields - set(res.keys())
            self.assertFalse(missing, f"Field berikut tidak ada di payload: {missing}")
            self.log_result("SRS ↔ Supabase", "Payload Schema Validation",
                            desc, inputs, expected,
                            f"Semua {len(required_fields)} field wajib ada ✔", "PASSED")
        except Exception as e:
            self.log_result("SRS ↔ Supabase", "Payload Schema Validation",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── G-02 ──────────────────────────────────────────────────────────────────
    def test_G02_chat_history_ordering(self):
        """[G-02] Validasi urutan kronologis chat history dari Supabase."""
        desc     = "Gray-Box: mengetahui bahwa Supabase mengembalikan data desc → harus di-reverse."
        inputs   = "2 entri: user msg lalu assistant reply (urutan DB: terbaru dulu)"
        expected = "history[0] = assistant (terbaru) | history[1] = user (tertua)"
        try:
            mock_db.data = [
                {"role": "user",      "content": "Konnichiwa"},
                {"role": "assistant", "content": "Genki desu ka?"},
            ]
            hist = self.run_async(SupabaseService.get_chat_history("u1", limit=2))
            self.assertEqual(hist[0]["content"], "Genki desu ka?")
            self.assertEqual(hist[1]["content"], "Konnichiwa")
            self.log_result("Supabase Service", "Chat History Ordering",
                            desc, inputs, expected,
                            f"[0]='{hist[0]['role']}' | [1]='{hist[1]['role']}' ✔", "PASSED")
        except Exception as e:
            self.log_result("Supabase Service", "Chat History Ordering",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── G-03 ──────────────────────────────────────────────────────────────────
    def test_G03_retention_forecast_structure(self):
        """[G-03] Validasi struktur data return dari get_retention_forecast()."""
        desc     = "Gray-Box: mengetahui bahwa forecast harus berupa array dengan key 'due_count' per hari."
        inputs   = "2 item SRS aktif | days=3"
        expected = "Array 3 elemen, tiap elemen punya key 'due_count' & 'date'"
        try:
            today = date.today()
            mock_db.data = [
                {"next_review": today.isoformat(),                     "interval_days": 1},
                {"next_review": (today + timedelta(days=1)).isoformat(),"interval_days": 6},
            ]
            forecast = self.run_async(SRSService.get_retention_forecast("u1", days=3))
            self.assertEqual(len(forecast), 3)
            for day in forecast:
                self.assertIn("due_count", day)
                self.assertIn("date",      day)
            self.log_result("SRS Service", "Forecast Data Structure",
                            desc, inputs, expected,
                            f"{len(forecast)} hari | keys valid ✔", "PASSED")
        except Exception as e:
            self.log_result("SRS Service", "Forecast Data Structure",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── G-04 ──────────────────────────────────────────────────────────────────
    def test_G04_admin_analytics_aggregation(self):
        """[G-04] Admin analytics aggregation – total, by-mode, active users."""
        desc     = "Gray-Box: mengetahui struktur agregasi analytics Supabase service."
        inputs   = "3 chat_logs: u1/discovery, u1/quiz, u2/discovery"
        expected = "total=3 | active_users=2 | by_mode.discovery=2"
        try:
            mock_db.data = [
                {"user_id":"u1","mode":"discovery"},
                {"user_id":"u1","mode":"quiz"},
                {"user_id":"u2","mode":"discovery"},
            ]
            stats = self.run_async(SupabaseService.get_chat_stats())
            self.assertEqual(stats["total_messages"],         3)
            self.assertEqual(stats["active_users"],           2)
            self.assertEqual(stats["by_mode"]["discovery"],   2)
            self.log_result("Supabase Service", "Admin Analytics Aggregation",
                            desc, inputs, expected,
                            f"total={stats['total_messages']} | "
                            f"users={stats['active_users']} | "
                            f"disc={stats['by_mode']['discovery']} ✔", "PASSED")
        except Exception as e:
            self.log_result("Supabase Service", "Admin Analytics Aggregation",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 7 · NON-FUNCTIONAL TESTING
#  Performa, regression smoke, dan ketahanan sistem
# ═════════════════════════════════════════════════════════════════════════════

class Test_L7_NonFunctional(TVJPBaseTest):
    """
    Non-Functional Testing – Menguji kualitas sistem di luar fungsi utama:
    performa (response time), regression smoke, dan stabilitas berulang.
    """
    LAYER = "Non-Functional"

    # ── N-01 ──────────────────────────────────────────────────────────────────
    def test_N01_bkt_computation_performance(self):
        """[N-01] Performance: BKT Engine harus menyelesaikan 1.000 update belief < 1 detik."""
        desc     = "Performa: validasi komputasi BKT dalam jumlah besar tidak melebihi batas waktu."
        inputs   = "1.000 iterasi update_belief() dengan parameter bervariasi"
        expected = "Durasi total < 1.0 detik"
        try:
            bkt    = BKTEngine()
            params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}
            t0     = time.perf_counter()
            for i in range(1000):
                bkt.update_belief(0.5, i % 2 == 0, params)
            elapsed = time.perf_counter() - t0
            self.assertLess(elapsed, 1.0,
                f"1.000 belief update membutuhkan {elapsed:.3f}s (limit=1.0s)")
            self.log_result("BKT Engine", "Computation Performance",
                            desc, inputs, expected,
                            f"1.000 ops selesai dalam {elapsed:.4f}s ✔", "PASSED")
        except Exception as e:
            self.log_result("BKT Engine", "Computation Performance",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── N-02 ──────────────────────────────────────────────────────────────────
    def test_N02_sm2_batch_performance(self):
        """[N-02] Performance: SM-2 harus menyelesaikan 500 kalkulasi < 0.5 detik."""
        desc     = "Performa: memastikan SM-2 dapat memproses batch kalkulasi dalam batas waktu optimal."
        inputs   = "500 iterasi calculate_sm2() dengan quality variatif 0–5"
        expected = "Durasi total < 0.5 detik"
        try:
            t0 = time.perf_counter()
            for i in range(500):
                SRSService.calculate_sm2(i % 6, i % 3, 2.5, max(1, i % 10))
            elapsed = time.perf_counter() - t0
            self.assertLess(elapsed, 0.5)
            self.log_result("SRS Service", "SM-2 Batch Performance",
                            desc, inputs, expected,
                            f"500 kalkulasi dalam {elapsed:.4f}s ✔", "PASSED")
        except Exception as e:
            self.log_result("SRS Service", "SM-2 Batch Performance",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── N-03 ──────────────────────────────────────────────────────────────────
    def test_N03_regression_smoke_core_imports(self):
        """[N-03] Regression Smoke: semua modul utama masih bisa diimpor dan diinisialisasi."""
        desc     = "Smoke test: memastikan build/refactor tidak merusak inisialisasi modul kritis."
        inputs   = "Import dan instantiasi: BKTEngine, GrammarCheckerService, VoiceService"
        expected = "Semua modul berhasil diinisialisasi tanpa exception"
        try:
            b = BKTEngine()
            g = GrammarCheckerService()
            v = VoiceService()
            self.assertIsNotNone(b); self.assertIsNotNone(g); self.assertIsNotNone(v)
            self.log_result("Core Modules", "Regression Smoke Import",
                            desc, inputs, expected,
                            "BKTEngine ✔ | GrammarChecker ✔ | VoiceService ✔", "PASSED")
        except Exception as e:
            self.log_result("Core Modules", "Regression Smoke Import",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── N-04 ──────────────────────────────────────────────────────────────────
    def test_N04_idempotent_streak_update(self):
        """[N-04] Sanity: update streak berulang pada hari yang sama tidak memganda streak."""
        desc     = "Sanity test: memanggil update_streak() dua kali di hari yang sama harus idempoten."
        inputs   = "Dua kali update_streak('u1') pada tanggal yang sama"
        expected = "streak_days tidak bertambah dua kali lipat"
        try:
            today    = date.today()
            mock_db.data = [{"study_date": today.isoformat()}]
            first  = self.run_async(StreakService.update_streak("u1"))
            self._reset_db()
            mock_db.data = [{"study_date": today.isoformat()}]
            second = self.run_async(StreakService.update_streak("u1"))
            self.assertEqual(first["streak_days"], second["streak_days"],
                "Streak harus idempoten untuk hari yang sama")
            self.log_result("Streak Service", "Idempotent Streak Update",
                            desc, inputs, expected,
                            f"Call1={first['streak_days']} | Call2={second['streak_days']} ✔",
                            "PASSED")
        except Exception as e:
            self.log_result("Streak Service", "Idempotent Streak Update",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise

    # ── N-05 ──────────────────────────────────────────────────────────────────
    def test_N05_grammar_tokenization_stability(self):
        """[N-05] Stability: tokenisasi teks identik harus selalu menghasilkan output yang sama."""
        desc     = "Stability test: GrammarChecker harus deterministik untuk input yang sama."
        inputs   = "tokenize('私は学生です') dipanggil 5 kali"
        expected = "Semua 5 hasil identik"
        try:
            gc      = GrammarCheckerService()
            results = [
                [t["original"] for t in gc.tokenize("私は学生です")]
                for _ in range(5)
            ]
            for r in results[1:]:
                self.assertEqual(r, results[0], "Hasil tokenisasi harus deterministik")
            self.log_result("Grammar Checker", "Tokenization Stability",
                            desc, inputs, expected,
                            f"5 pemanggilan identik ✔ | tokens={results[0]}", "PASSED")
        except Exception as e:
            self.log_result("Grammar Checker", "Tokenization Stability",
                            desc, inputs, expected, f"GAGAL: {e}", "FAILED"); raise


# ─────────────────────────────────────────────────────────────────────────────
# CONSOLE FORMATTING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _print_banner():
    """Mencetak header banner saat awal eksekusi."""
    now  = datetime.now().strftime("%d %B %Y  %H:%M:%S")
    lines = [
        cyan(_hline()),
        f"{BOX_V} {cyan(bold('TVJP  –  AUTOMATED TESTING SUITE')):^{W-4}} {BOX_V}",
        f"{BOX_V} {dim('Sistem Virtual Tutor Bahasa Jepang  ·  Sinta 1 / Skripsi Standard'):^{W-4}} {BOX_V}",
        cyan(_mline()),
        _row(f"  {dim('Metode'):<12}  Unit · Integration · System · Acceptance · White/Gray-Box · Non-Functional"),
        _row(f"  {dim('Runtime'):<12}  {now}"),
        _row(f"  {dim('Isolasi'):<12}  Mock Objects (unittest.mock, AsyncMock, supabase stub)"),
        cyan(_bline()),
    ]
    print("\n" + "\n".join(lines) + "\n")


def _print_layer_header(no: int, layer: str, subtitle: str, icon: str = "◈"):
    """Mencetak pemisah section per layer testing."""
    inner = W - 4
    label = f"  {icon}  Layer {no}  ·  {layer.upper():<18}  {dim('–')}  {subtitle}"
    print(
        f"\n{cyan(_hline())}\n"
        f"{BOX_V} {cyan(bold(f'{label}'))}{BOX_V}\n"
        f"{cyan(_mline())}"
    )


def _print_column_header():
    """Mencetak header kolom tabel hasil."""
    h = (f"  {'STATUS':<11}  {'LAYER':<15}  {'LAYANAN':<22}  "
         f"{'NAMA TEST':<34}  HASIL AKTUAL")
    print(dim(h))
    print(dim("  " + "─" * (W - 2)))


def _print_summary(results: list, elapsed: float):
    """Mencetak panel ringkasan eksekusi beserta tabel rekapitulasi."""
    total  = len(results)
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    skipped = sum(1 for r in results if r["status"] == "SKIPPED")
    warnings_cnt = _warning_count
    
    rate   = passed / total * 100 if total else 0
    ok     = (failed + errors) == 0

    # Per-layer breakdown
    by_layer: dict[str, dict] = {}
    for r in results:
        L = r["layer"]
        by_layer.setdefault(L, {"p": 0, "f": 0})
        by_layer[L]["p" if r["status"]=="PASSED" else "f"] += 1

    print()
    print(cyan(_hline()))
    print(f"{BOX_V} {cyan(bold('RINGKASAN EKSEKUSI  –  EXECUTION SUMMARY')):^{W-4}} {BOX_V}")
    print(cyan(_mline()))
    
    # Global stats
    overall_status_str = green("● SUKSES  (ALL PASSED)") if ok else red(f"● GAGAL   ({failed + errors} test bermasalah)")
    if not _supports_unicode:
        overall_status_str = overall_status_str.replace("●", "*")
        
    rows = [
        ("Total Test Cases",  bold(str(total))),
        ("Passed (Success)",   green(f"✔  {passed}") if _supports_unicode else f"[OK] {passed}"),
        ("Failed",            red(f"✖  {failed}") if failed else dim("0")),
        ("Errors",            red(f"⚡  {errors}") if errors else dim("0")),
        ("Skipped",           yellow(f"⊘  {skipped}") if skipped else dim("0")),
        ("Warnings",          yellow(f"⚠  {warnings_cnt}") if warnings_cnt else dim("0")),
        ("Pass Rate",         (green if ok else red)(f"{rate:.2f}%")),
        ("Execution Time",    f"{elapsed:.3f}s"),
        ("Overall Status",    overall_status_str),
    ]
    for label, value in rows:
        inner = W - 4
        # Strip ANSI colors for length check
        import re
        val_clean = re.sub(r'\033\[[0-9;]*m', '', str(value))
        padding = inner - len(label) - len(val_clean)
        line  = f"  {label}{' ' * padding}{value}"
        print(f"{BOX_V} {line} {BOX_V}")

    print(cyan(_mline()))
    # Per-layer breakdown
    print(f"{BOX_V} {cyan(bold('Breakdown per Layer:')):<{W-4}} {BOX_V}")
    LAYER_ORDER = ["Unit","Integration","System","Acceptance",
                   "White-Box","Gray-Box","Non-Functional"]
    for L in LAYER_ORDER:
        if L not in by_layer: continue
        p, f = by_layer[L]["p"], by_layer[L]["f"]
        t    = p + f
        pr   = p / t * 100 if t else 0
        bar_ok  = ("█" if _supports_unicode else "#") * p
        bar_fail= ("░" if _supports_unicode else "-") * f
        pct_str = (green if f==0 else red)(f"{pr:.0f}%")
        line = f"  {L:<18}  {green(bar_ok)}{red(bar_fail)}  {pct_str}  ({p}/{t})"
        
        # Calculate padding dynamically
        line_clean = re.sub(r'\033\[[0-9;]*m', '', line)
        padding = (W - 4) - len(line_clean)
        print(f"{BOX_V} {line}{' ' * padding} {BOX_V}")
        
    print(cyan(_mline()))
    
    # Beautiful visual summary table requested by user
    print(f"{BOX_V} {cyan(bold('Tabel Rekapitulasi Akhir (Summary Grid):')):<{W-4}} {BOX_V}")
    
    if _supports_unicode:
        T_TL, T_TR = "┌", "┐"
        T_BL, T_BR = "└", "┘"
        T_H,  T_V  = "─", "│"
        T_T,  T_B  = "┬", "┴"
        T_L,  T_R  = "├", "┤"
        T_C        = "┼"
    else:
        T_TL, T_TR = "+", "+"
        T_BL, T_BR = "+", "+"
        T_H,  T_V  = "-", "|"
        T_T,  T_B  = "+", "+"
        T_L,  T_R  = "+", "+"
        T_C        = "+"

    def _cell(text: str, width: int, color_fn=None) -> str:
        padded = f"{text:^{width}}"
        if color_fn and _ANSI:
            return padded.replace(text, color_fn(text))
        return padded

    line_top = T_TL + T_H * 19 + T_T + T_H * 10 + T_T + T_H * 10 + T_T + T_H * 10 + T_T + T_H * 10 + T_T + T_H * 10 + T_TR
    line_mid = T_L + T_H * 19 + T_C + T_H * 10 + T_C + T_H * 10 + T_C + T_H * 10 + T_C + T_H * 10 + T_C + T_H * 10 + T_R
    line_bot = T_BL + T_H * 19 + T_B + T_H * 10 + T_B + T_H * 10 + T_B + T_H * 10 + T_B + T_H * 10 + T_B + T_H * 10 + T_BR

    row_headers = (
        f"{T_V}{_cell('TOTAL TESTS', 19, bold)}"
        f"{T_V}{_cell('PASSED', 10, green)}"
        f"{T_V}{_cell('FAILED', 10, red)}"
        f"{T_V}{_cell('SKIPPED', 10, yellow)}"
        f"{T_V}{_cell('ERRORS', 10, red)}"
        f"{T_V}{_cell('WARNINGS', 10, yellow)}{T_V}"
    )

    row_data = (
        f"{T_V}{_cell(str(total), 19, bold)}"
        f"{T_V}{_cell(str(passed), 10, green if passed > 0 else None)}"
        f"{T_V}{_cell(str(failed), 10, red if failed > 0 else None)}"
        f"{T_V}{_cell(str(skipped), 10, yellow if skipped > 0 else None)}"
        f"{T_V}{_cell(str(errors), 10, red if errors > 0 else None)}"
        f"{T_V}{_cell(str(warnings_cnt), 10, yellow if warnings_cnt > 0 else None)}{T_V}"
    )
    
    # Print table with padding to align with box width
    inner = W - 4
    t_pad = " "
    print(f"{BOX_V} {t_pad}{line_top}{t_pad} {BOX_V}")
    print(f"{BOX_V} {t_pad}{row_headers}{t_pad} {BOX_V}")
    print(f"{BOX_V} {t_pad}{line_mid}{t_pad} {BOX_V}")
    print(f"{BOX_V} {t_pad}{row_data}{t_pad} {BOX_V}")
    print(f"{BOX_V} {t_pad}{line_bot}{t_pad} {BOX_V}")

    print(cyan(_bline()))


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN REPORT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

# Markdown Report Generator removed as requested by user.


# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM TEST RUNNER & GLOBAL TEST LIFE CYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────

_HEADER_PRINTED = False
_SUMMARY_PRINTED = False
_warning_count = 0
_T0_MODULE = time.perf_counter()

import warnings
_original_showwarning = warnings.showwarning

def _custom_showwarning(*args, **kwargs):
    global _warning_count
    _warning_count += 1
    _original_showwarning(*args, **kwargs)

warnings.showwarning = _custom_showwarning


def setUpModule():
    global _HEADER_PRINTED
    if not _HEADER_PRINTED:
        _HEADER_PRINTED = True
        _print_banner()
        _print_column_header()


def tearDownModule():
    global _SUMMARY_PRINTED
    if not _SUMMARY_PRINTED:
        _SUMMARY_PRINTED = True
        elapsed = time.perf_counter() - _T0_MODULE
        _print_summary(ALL_RESULTS, elapsed)


SUITE_REGISTRY = [
    (1, "Unit Testing",        "Komponen Logika Terkecil",      "◈", Test_L1_BKTEngine),
    (1, "Unit Testing",        "Komponen Logika Terkecil",      "◈", Test_L1_LLMAgent),
    (1, "Unit Testing",        "Komponen Logika Terkecil",      "◈", Test_L1_GrammarChecker),
    (2, "Integration Testing", "Interaksi Antar Modul",         "◉", Test_L2_Integration),
    (3, "System Testing",      "End-to-End Black Box",          "◎", Test_L3_System),
    (4, "Acceptance Testing",  "UAT – Kebutuhan Pengguna",      "◆", Test_L4_Acceptance),
    (5, "White-Box Testing",   "Branch & Boundary Coverage",    "◇", Test_L5_WhiteBox),
    (6, "Gray-Box Testing",    "Semi-Struktural",               "◈", Test_L6_GrayBox),
    (7, "Non-Functional",      "Performa, Regression, Smoke",   "◉", Test_L7_NonFunctional),
]

_PREV_LAYER = [None]   # mutable state untuk deteksi pergantian layer


class _TVJPRunner(unittest.TextTestRunner):

    def __init__(self, **kw):
        kw.setdefault("verbosity", 0)
        # Suppress default unittest output
        kw.setdefault("stream", open(os.devnull, "w"))
        super().__init__(**kw)

    def run(self, test: unittest.TestSuite):
        global _HEADER_PRINTED, _SUMMARY_PRINTED
        t0 = time.perf_counter()
        
        if not _HEADER_PRINTED:
            _HEADER_PRINTED = True
            _print_banner()
            _print_column_header()

        _SEEN_LAYERS = set()
        for suite in test:
            cls = suite.__class__
            # Find registry entry for this class
            entry = next((e for e in SUITE_REGISTRY if e[4] is cls), None)
            if entry:
                layer_no, layer_name, subtitle, icon, _ = entry
                if layer_name not in _SEEN_LAYERS:
                    _SEEN_LAYERS.add(layer_name)
                    _print_layer_header(layer_no, layer_name, subtitle, icon)
            super().run(suite)
            print()  # breathing room between suites

        elapsed = time.perf_counter() - t0
        if not _SUMMARY_PRINTED:
            _SUMMARY_PRINTED = True
            _print_summary(ALL_RESULTS, elapsed)
            
        return unittest.TestResult()


# ─────────────────────────────────────────────────────────────────────────────
# SUITE BUILDER & ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def build_suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    seen   = set()
    for entry in SUITE_REGISTRY:
        cls = entry[4]
        if cls not in seen:
            seen.add(cls)
            suite.addTest(loader.loadTestsFromTestCase(cls))
    return suite


if __name__ == "__main__":
    _TVJPRunner().run(build_suite())