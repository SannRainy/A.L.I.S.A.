# -*- coding: utf-8 -*-
"""
_shared.py — Infrastruktur Bersama untuk Semua Layer Testing TVJP
=================================================================
Diimpor oleh setiap file layer test. Berisi:
  · PATH setup
  · ANSI helpers + safe_print
  · BOX chars, STATUS_ICON, LAYER_BADGE
  · MockSupabaseClient + sys.modules patching
  · Service imports
  · make_base_class(results_list, counter_ref) — Factory Base Test
  · print_layer_summary() — Printer ringkasan per layer
"""

import sys
import os
import re
import time
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, date, timedelta
from collections import Counter
from typing import Any
from types import ModuleType

# ─────────────────────────────────────────────────────────────────────────────
# PATH SETUP
# ─────────────────────────────────────────────────────────────────────────────
_LAYERS_DIR  = os.path.dirname(os.path.abspath(__file__))   # backend/tests/layers/
_TESTS_DIR   = os.path.dirname(_LAYERS_DIR)                  # backend/tests/
_BACKEND_DIR = os.path.dirname(_TESTS_DIR)                   # backend/
_ROOT_DIR    = os.path.dirname(_BACKEND_DIR)                 # project root

for _p in (_BACKEND_DIR, _ROOT_DIR, _TESTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ─────────────────────────────────────────────────────────────────────────────
# ANSI CONSOLE HELPERS
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
    for _ch in ["✔", "─", "╔", "█"]:
        _ch.encode(sys.stdout.encoding or "ascii")
    _supports_unicode = True
except Exception:
    _supports_unicode = False

# ─────────────────────────────────────────────────────────────────────────────
# safe_print — Windows-safe UTF-8 output
# ─────────────────────────────────────────────────────────────────────────────
def safe_print(*args, **kwargs):
    sep  = kwargs.get("sep", " ")
    end  = kwargs.get("end", "\n")
    text = sep.join(str(a) for a in args)
    _SUBS = str.maketrans({
        "✔":"[OK]","✖":"[FAIL]","⊘":"[SKIP]","⚡":"[ERR]","─":"-","┌":"+",
        "┐":"+","└":"+","┘":"+","├":"+","┤":"+","┬":"+","┴":"+","┼":"+",
        "│":"|","═":"=","║":"|","╔":"+","╗":"+","╚":"+","╝":"+","╠":"+",
        "╣":"+","→":"->","●":"*","█":"#","░":"-","◈":"*","◉":"*","◎":"*",
        "◆":"*","◇":"*","⚠":"[WARN]",
    })
    try:
        sys.stdout.write(text + end)
        sys.stdout.flush()
    except UnicodeEncodeError:
        clean = text.translate(_SUBS)
        try:
            sys.stdout.write(clean + end)
            sys.stdout.flush()
        except Exception:
            enc      = sys.stdout.encoding or "ascii"
            fallback = clean.encode(enc, errors="replace").decode(enc, errors="replace")
            sys.stdout.write(fallback + end)
            sys.stdout.flush()

# ─────────────────────────────────────────────────────────────────────────────
# BOX CHARS + LAYOUT HELPERS
# ─────────────────────────────────────────────────────────────────────────────
W = 86

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

LAYER_BADGE = {
    "Unit":           magenta("[WHITE-BOX: UNIT]"),
    "Integration":    cyan("[INTEGRATION]     "),
    "System":         blue("[BLACK-BOX: SYS]  "),
    "Acceptance":     yellow("[BLACK-BOX: UAT]  "),
    "White-Box":      green("[WHITE-BOX: LOG]  "),
    "Gray-Box":       cyan("[GRAY-BOX]        "),
    "Non-Functional": dim("[NON-FUNCTIONAL]  "),
}

def _hline(char=None, lc=None, rc=None):
    char = char or BOX_H; lc = lc or BOX_TL; rc = rc or BOX_TR
    return lc + char * (W - 2) + rc

def _mline(): return BOX_ML + BOX_H * (W - 2) + BOX_MR
def _bline(): return BOX_BL + BOX_H * (W - 2) + BOX_BR

def _row(text: str) -> str:
    inner = W - 4
    return f"{BOX_V} {text:<{inner}} {BOX_V}"

# ─────────────────────────────────────────────────────────────────────────────
# MOCK SUPABASE CLIENT
# ─────────────────────────────────────────────────────────────────────────────
class MockSupabaseClient:
    def __init__(self):
        self.data: Any         = []
        self.auth              = self
        self._last_update: Any = None

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
        self.data = data
        return self

    def upsert(self, data, **k):
        self.data = [data] if isinstance(data, dict) else list(data)
        return self

    def delete(self): return self

    def execute(self):
        class _Resp:
            def __init__(self, d): self.data = d
        return _Resp(self.data)


mock_db = MockSupabaseClient()

_supa_mod_mock          = ModuleType("supabase_client")
_supa_mod_mock.supabase = mock_db
sys.modules["core.supabase_client"]         = _supa_mod_mock
sys.modules["backend.core.supabase_client"] = _supa_mod_mock

import core  # noqa: E402
core.supabase_client = _supa_mod_mock  # type: ignore

try:
    import backend  # noqa: E402
    backend.core = core  # type: ignore
except Exception:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# SERVICE IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
try:
    from backend.services.bkt_engine       import BKTEngine
    from backend.services.llm_agent        import (LLMAgent, _is_quiz_request,
                                                    _extract_grammar_keywords, _normalize_jp_text)
    from backend.services.grammar_checker  import GrammarCheckerService
    from backend.services.srs_service      import SRSService
    from backend.services.streak_service   import StreakService
    from backend.services.voice_service    import VoiceService
    from backend.services.supabase_service import SupabaseService
    import backend.services.srs_service      as _srs
    import backend.services.streak_service   as _streak
    import backend.services.supabase_service as _supa
    import backend.services.voice_service    as _voice
    import backend.services.llm_agent        as _llm
except ImportError:
    from services.bkt_engine       import BKTEngine
    from services.llm_agent        import (LLMAgent, _is_quiz_request,
                                            _extract_grammar_keywords, _normalize_jp_text)
    from services.grammar_checker  import GrammarCheckerService
    from services.srs_service      import SRSService
    from services.streak_service   import StreakService
    from services.voice_service    import VoiceService
    from services.supabase_service import SupabaseService
    import services.srs_service      as _srs
    import services.streak_service   as _streak
    import services.supabase_service as _supa
    import services.voice_service    as _voice
    import services.llm_agent        as _llm

for _m in (_srs, _streak, _supa, _voice, _llm):
    if hasattr(_m, "supabase"):
        _m.supabase = mock_db

# ─────────────────────────────────────────────────────────────────────────────
# BASE TEST CLASS FACTORY
# ─────────────────────────────────────────────────────────────────────────────
def make_base_class(results_list: list, counter_ref: list) -> type:
    """
    Factory — membuat TVJPBaseTest yang terikat ke results_list dan counter_ref lokal.

    Args:
        results_list : list kosong milik layer file (mutable reference)
        counter_ref  : list berisi 1 int [0] sebagai counter mutable
    Returns:
        Class TVJPBaseTest yang siap disubclass oleh kelas test layer
    """
    _sp = safe_print  # referensi lokal agar tidak hilang saat override print

    class TVJPBaseTest(unittest.TestCase):
        LAYER: str = "Unit"

        def setUp(self):
            self._t0 = time.perf_counter()
            self._reset_db()

        def tearDown(self):
            dur = round(time.perf_counter() - self._t0, 4)
            if results_list:
                results_list[-1]["duration"] = dur

        def _reset_db(self):
            mock_db.data         = []
            mock_db._last_update = None

        def log_result(
            self,
            service:  str,
            name:     str,
            desc:     str,
            inputs:   str,
            expected: str,
            actual:   str,
            status:   str,
            layer:    str | None = None,
        ) -> None:
            counter_ref[0] += 1
            layer = layer or self.LAYER

            exc_val = sys.exc_info()[1]
            if exc_val is not None and status in ("FAILED", "ERROR"):
                status = "FAILED" if isinstance(exc_val, AssertionError) else "ERROR"

            if not _supports_unicode:
                actual   = actual.replace("→", "->").replace("●", "*")
                inputs   = inputs.replace("→", "->").replace("●", "*")
                expected = expected.replace("→", "->").replace("●", "*")

            results_list.append({
                "no":       counter_ref[0],
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

            badge    = LAYER_BADGE.get(layer, f"[{layer:<17}]")
            st_icon  = STATUS_ICON.get(status, status)
            svc_col  = cyan(f"{service:<20}")
            name_col = bold(f"{name:<32}")
            actual_s = (actual[:25] + "…") if len(actual) > 28 else actual
            log_line = f"  {st_icon}  {badge}  {svc_col}  {name_col}  {dim(actual_s)}"
            try:
                _sp(log_line)
            except UnicodeEncodeError:
                clean = re.sub(r"\033\[[0-9;]*m", "", log_line)
                clean = clean.replace("✔","[OK]").replace("✖","[FAIL]")
                _sp(clean.encode("ascii", "replace").decode("ascii"))

        @staticmethod
        def run_async(coro): return asyncio.run(coro)

    return TVJPBaseTest


# ─────────────────────────────────────────────────────────────────────────────
# SHARED SUMMARY PRINTER
# ─────────────────────────────────────────────────────────────────────────────
def print_layer_summary(results: list, layer_title: str, elapsed: float):
    """Cetak kotak ringkasan hasil pengujian satu layer ke konsol."""
    total   = len(results)
    passed  = sum(1 for r in results if r["status"] == "PASSED")
    failed  = sum(1 for r in results if r["status"] == "FAILED")
    errors  = sum(1 for r in results if r["status"] == "ERROR")
    rate    = passed / total * 100 if total else 0
    ok      = (failed + errors) == 0
    _p      = safe_print

    _p()
    _p(cyan(_hline()))
    _p(f"{BOX_V} {cyan(bold(f'TVJP – {layer_title} — RINGKASAN HASIL')):^{W-4}} {BOX_V}")
    _p(cyan(_mline()))

    rows = [
        ("Total Kasus Uji", bold(str(total))),
        ("Passed",          green(f"✔  {passed}")),
        ("Failed",          red(f"✖  {failed}") if failed else dim("0")),
        ("Errors",          red(f"⚡  {errors}") if errors else dim("0")),
        ("Pass Rate",       (green if ok else red)(f"{rate:.2f}%")),
        ("Waktu Eksekusi",  f"{elapsed:.3f}s"),
        ("Status",          green("● VALID") if ok else red(f"● CACAT ({failed+errors} MALFUNGSI)")),
    ]
    for label, value in rows:
        val_c   = re.sub(r"\033\[[0-9;]*m", "", str(value))
        padding = (W - 4) - len(label) - len(val_c)
        _p(f"{BOX_V} {label}{' ' * max(0, padding)}{value} {BOX_V}")

    _p(cyan(_bline()))
