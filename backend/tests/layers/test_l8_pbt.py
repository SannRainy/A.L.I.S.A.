"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     TVJP – LAYER 8 · PROPERTY-BASED FUZZ TESTING  (Pilar 3 / Skripsi)       ║
║     Sistem Virtual Tutor Bahasa Jepang Berbasis Knowledge Graph              ║
║                                                                              ║
║  Metode: Property-Based Testing (PBT) / Automated Fuzzing for NLP            ║
║  Engine: Hypothesis (Claessen & Hughes, QuickCheck 2000 — Python port)       ║
║  Referensi Jurnal: Scopus Q1 — "Automated Fuzzing for NLP Components"        ║
║                                                                              ║
║  Properti yang Diuji (Invariant Specification):                               ║
║    P-01 · Crash Safety          – romaji generator tidak pernah crash        ║
║    P-01b· Crash Safety Katakana – katakana tidak pernah crash                ║
║    P-02 · Output Type Invariant – output selalu bertipe str (digabung P-01)  ║
║    P-03 · Empty Input Invariant – input kosong/whitespace → output kosong    ║
║    P-04 · ASCII Output Safety   – output Hiragana murni selalu ASCII         ║
║    P-05 · SM-2 EF Floor        – EF tidak pernah turun di bawah 1.3         ║
║    P-06 · SM-2 Interval Positive– interval review selalu ≥ 1 hari            ║
║    P-07 · BKT Boundary         – belief selalu dalam [0.001, 0.999]          ║
║    P-07b· BKT Extreme Input    – nilai ekstrem p=0.0, p=1.0 tidak crash      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Cara Menjalankan:
    pip install hypothesis
    python -m pytest backend/tests/test_pbt_layer8.py -v
    python backend/tests/test_pbt_layer8.py          (standalone)
"""

import unittest
import sys
import os
import time

# ─────────────────────────────────────────────────────────────────────────────
# PATH SETUP (konsisten dengan test_automation_suite.py)
# ─────────────────────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir   = os.path.dirname(current_dir)
backend_dir = os.path.dirname(tests_dir)
root_dir    = os.path.dirname(backend_dir)

for _p in (backend_dir, root_dir, tests_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ─────────────────────────────────────────────────────────────────────────────
# HYPOTHESIS IMPORT CHECK
# ─────────────────────────────────────────────────────────────────────────────
try:
    from hypothesis import given, settings, HealthCheck
    from hypothesis import strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    print("\n[WARNING] Library 'hypothesis' tidak ditemukan.")
    print("  Jalankan: pip install hypothesis")
    print("  Semua test Layer 8 akan di-SKIP otomatis.\n")

# ─────────────────────────────────────────────────────────────────────────────
# ANSI CONSOLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False

def _c(code, text): return f"\033[{code}m{text}\033[0m" if _ANSI else text
def green(t):   return _c("32;1", t)
def red(t):     return _c("31;1", t)
def yellow(t):  return _c("33;1", t)
def cyan(t):    return _c("36;1", t)
def dim(t):     return _c("2", t)
def bold(t):    return _c("1", t)

W = 86

def _hline(): return "╔" + "═" * (W - 2) + "╗"
def _bline(): return "╚" + "═" * (W - 2) + "╝"
def _mline(): return "╠" + "═" * (W - 2) + "╣"
def _row(t):
    inner = W - 4
    return f"║ {t:<{inner}} ║"

# ─────────────────────────────────────────────────────────────────────────────
# SERVICE IMPORTS dengan try-except dua path (sama seperti test_automation_suite.py)
# ─────────────────────────────────────────────────────────────────────────────
try:
    from services.romaji_utils import generate_romaji_hybrid
    from services.srs_service  import SRSService
    from services.bkt_engine   import BKTEngine
    SERVICES_AVAILABLE = True
except ImportError:
    try:
        from backend.services.romaji_utils import generate_romaji_hybrid
        from backend.services.srs_service  import SRSService
        from backend.services.bkt_engine   import BKTEngine
        SERVICES_AVAILABLE = True
    except ImportError:
        SERVICES_AVAILABLE = False
        print("[ERROR] Service modules tidak dapat diimpor. Pastikan PYTHONPATH benar.\n")
        # Dummy stubs agar test dapat didefinisikan (akan di-skip saat dijalankan)
        def generate_romaji_hybrid(x): return ""
        class SRSService:
            @staticmethod
            def calculate_sm2(q, r, ef, i): return {"easiness_factor": 2.5, "interval_days": 1, "repetitions": 0}
        class BKTEngine:
            def update_belief(self, p, c, params): return 0.5

# ─────────────────────────────────────────────────────────────────────────────
# KARAKTER JEPANG UNTUK FUZZING
# ─────────────────────────────────────────────────────────────────────────────
# Hiragana: cakupan penuh U+3041–U+3096
HIRAGANA = (
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほ"
    "まみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでど"
    "ばびぶべぼぱぴぷぺぽぁぃぅぇぉゃゅょっ"
)
# Katakana: cakupan penuh U+30A1–U+30F6
KATAKANA = (
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホ"
    "マミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデド"
    "バビブベボパピプペポァィゥェォャュョッ"
)

# Strategi Hypothesis
_hira_strategy  = st.text(alphabet=HIRAGANA, min_size=1, max_size=80)
_kata_strategy  = st.text(alphabet=KATAKANA, min_size=1, max_size=80)
_blank_strategy = st.one_of(st.just(""), st.text(alphabet=" \t\n\u3000", min_size=1, max_size=20))

# ─────────────────────────────────────────────────────────────────────────────
# RESULT ACCUMULATOR
# ─────────────────────────────────────────────────────────────────────────────
ALL_PBT_RESULTS: list[dict] = []
_pbt_counter = 0
_T0 = time.perf_counter()

def _log_pbt(prop_id: str, name: str, examples_run: int, status: str, note: str = ""):
    """Catat satu properti ke ALL_PBT_RESULTS dan cetak ke konsol."""
    global _pbt_counter
    _pbt_counter += 1

    ALL_PBT_RESULTS.append({
        "no":       _pbt_counter,
        "id":       prop_id,
        "name":     name,
        "examples": examples_run,
        "status":   status,
        "note":     note,
    })

    badge   = f"[PBT LAYER 8]     "
    st_icon = "✔ PASSED " if status == "PASSED" else (
              "✖ FAILED " if status == "FAILED" else
              "⊘ SKIPPED")
    st_col  = (green if status == "PASSED" else (red if status == "FAILED" else yellow))(st_icon)
    eg_info = dim(f"~{examples_run:>4} examples")
    id_col  = cyan(f"PBT:{prop_id:<7}")
    name_col = bold(f"{name:<34}")
    print(f"  {st_col}  {badge}  {id_col}  {name_col}  {eg_info}")
    if note:
        print(f"           {dim(note[:70])}")


# ═════════════════════════════════════════════════════════════════════════════
#  P-01 + P-02 + P-03 + P-04 · ROMAJI GENERATOR — CRASH SAFETY & TYPE INVARIANTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L8_RomajiGenerator(unittest.TestCase):
    """
    Property-Based Fuzz Testing — generate_romaji_hybrid().
    Referensi kode: backend/services/romaji_utils.py  baris 23-140

    Invariants:
      P-01  Crash Safety (Hiragana) — tidak pernah raise Exception
      P-01b Crash Safety (Katakana) — sama, untuk Katakana
      P-02  Output Type  — output selalu bertipe str (terintegrasi dalam P-01)
      P-03  Empty Input  — input kosong/whitespace → output ""
      P-04  ASCII Output — output Hiragana → selalu pure ASCII
    """

    # ── P-01 + P-02 ──────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P01_crash_safety_and_type_hiragana(self):
        """[P-01/P-02] generate_romaji_hybrid() tidak crash & selalu kembalikan str — Hiragana."""
        examples_run = 0

        @given(_hira_strategy)
        @settings(max_examples=300, deadline=None,
                  suppress_health_check=[HealthCheck.too_slow])
        def _run(jp):
            nonlocal examples_run
            examples_run += 1
            try:
                out = generate_romaji_hybrid(jp)
                assert isinstance(out, str), \
                    f"P-02 VIOLATED: output bukan str untuk '{jp[:20]}'"
            except AssertionError:
                raise
            except Exception as exc:
                raise AssertionError(
                    f"P-01 VIOLATED: {type(exc).__name__} — '{jp[:20]}'"
                ) from exc

        try:
            _run()
            _log_pbt("P-01/02", "Crash Safety + Type (Hiragana)",
                     examples_run, "PASSED",
                     "romaji tidak crash dan selalu bertipe str untuk input Hiragana")
        except AssertionError as e:
            _log_pbt("P-01/02", "Crash Safety + Type (Hiragana)",
                     examples_run, "FAILED", str(e))
            raise

    # ── P-01b ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P01b_crash_safety_katakana(self):
        """[P-01b] generate_romaji_hybrid() tidak crash untuk semua input Katakana."""
        examples_run = 0

        @given(_kata_strategy)
        @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
        def _run(jp):
            nonlocal examples_run
            examples_run += 1
            try:
                out = generate_romaji_hybrid(jp)
                assert isinstance(out, str)
            except AssertionError:
                raise
            except Exception as exc:
                raise AssertionError(
                    f"P-01b VIOLATED: {type(exc).__name__} — '{jp[:20]}'"
                ) from exc

        try:
            _run()
            _log_pbt("P-01b", "Crash Safety (Katakana)",
                     examples_run, "PASSED",
                     "aman untuk semua variasi input Katakana")
        except AssertionError as e:
            _log_pbt("P-01b", "Crash Safety (Katakana)",
                     examples_run, "FAILED", str(e))
            raise

    # ── P-03 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P03_empty_input_invariant(self):
        """[P-03] Input kosong/whitespace → output string kosong.
        Referensi: romaji_utils.py baris 29-30 — guard clause."""
        examples_run = 0

        @given(_blank_strategy)
        @settings(max_examples=100)
        def _run(blank):
            nonlocal examples_run
            examples_run += 1
            out = generate_romaji_hybrid(blank)
            assert out == "", \
                f"P-03 VIOLATED: input {repr(blank)} → '{out}' (bukan '')"

        try:
            _run()
            _log_pbt("P-03", "Empty Input Invariant",
                     examples_run, "PASSED",
                     "guard clause baris 29-30 berfungsi untuk semua varian blank input")
        except AssertionError as e:
            _log_pbt("P-03", "Empty Input Invariant",
                     examples_run, "FAILED", str(e))
            raise

    # ── P-04 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P04_ascii_output_safety(self):
        """[P-04] Output Hiragana murni selalu berupa string ASCII bersih.
        Penting: output dikirim ke TTS engine yang hanya menerima ASCII."""
        examples_run = 0
        violations   = []

        @given(_hira_strategy)
        @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
        def _run(jp):
            nonlocal examples_run
            examples_run += 1
            out = generate_romaji_hybrid(jp)
            if out and not out.isascii():
                violations.append((jp[:25], out[:25]))

        _run()

        if violations:
            _log_pbt("P-04", "ASCII Output Safety",
                     examples_run, "FAILED",
                     f"Non-ASCII pada {len(violations)} kasus: {violations[:2]}")
            self.fail(
                f"P-04 VIOLATED: {len(violations)} kasus menghasilkan output non-ASCII. "
                f"Contoh: {violations[:2]}"
            )
        else:
            _log_pbt("P-04", "ASCII Output Safety",
                     examples_run, "PASSED",
                     "100% Hiragana input → ASCII output bersih")


# ═════════════════════════════════════════════════════════════════════════════
#  P-05 + P-06 · SM-2 ALGORITHM — MATHEMATICAL INVARIANTS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L8_SM2Invariants(unittest.TestCase):
    """
    Property-Based Fuzz Testing — SRSService.calculate_sm2().
    Referensi kode: backend/services/srs_service.py  baris 22-58

    Invariants:
      P-05  EF Floor    — easiness_factor selalu ≥ 1.3  (baris 52)
      P-06  Interval +  — interval_days selalu ≥ 1       (baris 39/41/43/48)
    """

    # ── P-05 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P05_sm2_ef_floor_invariant(self):
        """[P-05] SM-2 EF Floor: easiness_factor selalu ≥ 1.3 untuk SEMUA kombinasi input.
        Diuji juga terhadap quality di luar range resmi [0,5] (nilai -50 s/d +50).
        Referensi: srs_service.py baris 52 — 'new_ef = max(1.3, new_ef)'"""
        examples_run = 0
        violations   = []

        @given(
            quality     = st.integers(min_value=-50,  max_value=50),
            repetitions = st.integers(min_value=0,    max_value=100),
            ef          = st.floats(min_value=0.5,    max_value=10.0,
                                    allow_nan=False,  allow_infinity=False),
            interval    = st.integers(min_value=1,    max_value=365),
        )
        @settings(max_examples=500, suppress_health_check=[HealthCheck.too_slow])
        def _run(quality, repetitions, ef, interval):
            nonlocal examples_run
            examples_run += 1
            res = SRSService.calculate_sm2(quality, repetitions, ef, interval)
            if res["easiness_factor"] < 1.3:
                violations.append({
                    "q": quality, "rep": repetitions,
                    "ef_in": round(ef, 3), "ef_out": res["easiness_factor"]
                })

        _run()

        if violations:
            _log_pbt("P-05", "SM-2 EF Floor Invariant",
                     examples_run, "FAILED",
                     f"EF < 1.3 pada {len(violations)} kasus: {violations[:1]}")
            self.fail(f"P-05 VIOLATED: {violations[0]}")
        else:
            _log_pbt("P-05", "SM-2 EF Floor Invariant",
                     examples_run, "PASSED",
                     f"EF ≥ 1.3 terjaga di semua {examples_run} kombinasi")

    # ── P-06 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P06_sm2_interval_always_positive(self):
        """[P-06] SM-2 Interval Positivity: interval_days selalu ≥ 1 hari.
        interval negatif/0 akan menjadwalkan review di masa lalu → bug kritis."""
        examples_run = 0
        violations   = []

        @given(
            quality     = st.integers(min_value=0,  max_value=5),
            repetitions = st.integers(min_value=0,  max_value=50),
            ef          = st.floats(min_value=1.3,  max_value=5.0,
                                    allow_nan=False, allow_infinity=False),
            interval    = st.integers(min_value=1,  max_value=365),
        )
        @settings(max_examples=400)
        def _run(quality, repetitions, ef, interval):
            nonlocal examples_run
            examples_run += 1
            res = SRSService.calculate_sm2(quality, repetitions, ef, interval)
            if res["interval_days"] < 1:
                violations.append({
                    "q": quality, "rep": repetitions,
                    "interval_out": res["interval_days"]
                })

        _run()

        if violations:
            _log_pbt("P-06", "SM-2 Interval Positivity",
                     examples_run, "FAILED",
                     f"interval < 1 pada {len(violations)} kasus: {violations[:1]}")
            self.fail(f"P-06 VIOLATED: {violations[0]}")
        else:
            _log_pbt("P-06", "SM-2 Interval Positivity",
                     examples_run, "PASSED",
                     f"interval_days ≥ 1 terjaga di semua {examples_run} kombinasi")


# ═════════════════════════════════════════════════════════════════════════════
#  P-07 · BKT ENGINE — PROBABILITY BOUNDARY INVARIANT
# ═════════════════════════════════════════════════════════════════════════════
class Test_L8_BKTInvariants(unittest.TestCase):
    """
    Property-Based Fuzz Testing — BKTEngine.update_belief().

    Invariants:
      P-07  BKT Boundary     — output selalu dalam [0.001, 0.999]
      P-07b BKT Extreme Input — input p=0.0 dan p=1.0 tidak menghasilkan NaN/crash
    """

    def setUp(self):
        if SERVICES_AVAILABLE:
            self.bkt    = BKTEngine()
            self.params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}

    # ── P-07 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P07_bkt_belief_boundary_invariant(self):
        """[P-07] BKT Boundary: update_belief() selalu menghasilkan nilai dalam [0.001, 0.999].
        Mencakup semua kombinasi p ∈ [0.0, 1.0] dan correct ∈ {True, False}."""
        examples_run = 0
        violations   = []

        @given(
            p       = st.floats(min_value=0.0, max_value=1.0,
                                allow_nan=False, allow_infinity=False),
            correct = st.booleans(),
        )
        @settings(max_examples=500)
        def _run(p, correct):
            nonlocal examples_run
            examples_run += 1
            out = self.bkt.update_belief(p, correct, self.params)
            if not (0.001 <= out <= 0.999):
                violations.append({"p_in": p, "correct": correct, "p_out": out})

        _run()

        if violations:
            _log_pbt("P-07", "BKT Boundary Invariant",
                     examples_run, "FAILED",
                     f"Keluar [0.001,0.999] pada {len(violations)} kasus: {violations[:1]}")
            self.fail(f"P-07 VIOLATED: {violations[0]}")
        else:
            _log_pbt("P-07", "BKT Boundary Invariant",
                     examples_run, "PASSED",
                     f"[0.001,0.999] terjaga untuk semua {examples_run} kombinasi")

    # ── P-07b ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(HYPOTHESIS_AVAILABLE and SERVICES_AVAILABLE,
                         "Hypothesis atau service tidak tersedia")
    def test_P07b_bkt_extreme_boundary_inputs(self):
        """[P-07b] BKT Extreme Input Safety: p=0.0 dan p=1.0 tidak menghasilkan NaN/Inf/crash.
        Edge-case: nilai sentinel 0.0 dan 1.0 rawan division-by-zero di rumus Bayesian."""
        examples_run = 0
        EXTREMES = [0.0, 1.0, 0.001, 0.999, 0.5]

        @given(correct=st.booleans())
        @settings(max_examples=30)
        def _run(correct):
            nonlocal examples_run
            for p in EXTREMES:
                examples_run += 1
                out = self.bkt.update_belief(p, correct, self.params)
                self.assertIsInstance(out, (int, float),
                    f"P-07b: output bukan numerik untuk p={p}")
                self.assertFalse(
                    out != out,  # NaN check: NaN != NaN adalah True
                    f"P-07b: NaN terdeteksi untuk p={p}, correct={correct}"
                )
                self.assertGreaterEqual(out, 0.001,
                    f"P-07b: output {out} < 0.001 untuk p={p}")
                self.assertLessEqual(out, 0.999,
                    f"P-07b: output {out} > 0.999 untuk p={p}")

        try:
            _run()
            _log_pbt("P-07b", "BKT Extreme Input Safety",
                     examples_run, "PASSED",
                     f"p=0.0, p=1.0 dan nilai boundary aman untuk {examples_run} kombinasi")
        except AssertionError as e:
            _log_pbt("P-07b", "BKT Extreme Input Safety",
                     examples_run, "FAILED", str(e))
            raise


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY PRINTER
# ─────────────────────────────────────────────────────────────────────────────
def _print_pbt_summary(elapsed: float):
    import re
    total   = len(ALL_PBT_RESULTS)
    passed  = sum(1 for r in ALL_PBT_RESULTS if r["status"] == "PASSED")
    failed  = sum(1 for r in ALL_PBT_RESULTS if r["status"] == "FAILED")
    skipped = sum(1 for r in ALL_PBT_RESULTS if r["status"] == "SKIPPED")
    rate    = passed / total * 100 if total else 0
    ok      = failed == 0

    print()
    print(cyan("╔" + "═" * (W - 2) + "╗"))
    print(f"║ {cyan(bold('LAYER 8 · PROPERTY-BASED FUZZ TESTING — RINGKASAN HASIL')):^{W-4}} ║")
    print(cyan("╠" + "═" * (W - 2) + "╣"))

    rows = [
        ("Total Properti Diuji",     bold(str(total))),
        ("Passed",                   green(f"✔  {passed}")),
        ("Failed",                   red(f"✖  {failed}") if failed else dim("0")),
        ("Skipped",                  yellow(f"⊘  {skipped}") if skipped else dim("0")),
        ("Pass Rate",                (green if ok else red)(f"{rate:.1f}%")),
        ("Waktu Eksekusi",           f"{elapsed:.3f}s"),
        ("Status Kelayakan Pilar 3", green("● VALID — Non-Deterministic Testing OK") if ok
                                     else red(f"● CACAT — {failed} properti dilanggar")),
    ]
    for label, value in rows:
        val_c   = re.sub(r'\033\[[0-9;]*m', '', str(value))
        padding = (W - 4) - len(label) - len(val_c)
        print(f"║ {label}{' ' * max(0, padding)}{value} ║")

    print(cyan("╠" + "═" * (W - 2) + "╣"))
    print(f"║ {cyan(bold('Detail Hasil per Properti:')):<{W-4}} ║")
    for r in ALL_PBT_RESULTS:
        col   = green if r["status"] == "PASSED" else (red if r["status"] == "FAILED" else yellow)
        icon  = "✔" if r["status"] == "PASSED" else ("✖" if r["status"] == "FAILED" else "⊘")
        line  = f"  {col(icon)}  {r['id']:<12}  {r['name']:<36}  {dim(str(r['examples']) + ' ex')}"
        line_c = re.sub(r'\033\[[0-9;]*m', '', line)
        pad   = (W - 4) - len(line_c)
        print(f"║ {line}{' ' * max(0, pad)} ║")
    print(cyan("╚" + "═" * (W - 2) + "╝"))


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    try:
        print()
        print(cyan("╔" + "═" * (W - 2) + "╗"))
        print(f"║ {cyan(bold('TVJP  –  LAYER 8 · PROPERTY-BASED FUZZ TESTING')):^{W-4}} ║")
        print(f"║ {dim('Pilar 3: Non-Deterministic & Robustness Testing  ·  Hypothesis Engine'):^{W-4}} ║")
        print(f"║ {dim('Referensi: Claessen & Hughes QuickCheck ICFP 2000  |  Hypothesis 2024'):^{W-4}} ║")
        print(cyan("╠" + "═" * (W - 2) + "╣"))
        print(_row(f"  {'Library':<12}  Hypothesis — Search-Based Automated Input Generation"))
        print(_row(f"  {'Properti':<12}  9 invariant (P-01 – P-07b) · ~1500 test examples otomatis"))
        print(_row(f"  {'Komponen':<12}  romaji_utils.py · srs_service.py · bkt_engine.py"))
        print(cyan("╚" + "═" * (W - 2) + "╝"))
        print(dim("  STATUS         [PBT LAYER 8]         ID            NAMA PROPERTI                    EXAMPLES"))
        print(dim("  " + "─" * (W - 2)))
    except (UnicodeEncodeError, ValueError, OSError):
        pass


def tearDownModule():
    try:
        _print_pbt_summary(time.perf_counter() - _T0)
    except (ValueError, OSError):
        pass  # pytest closes stdout during teardown — silently skip


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT STANDALONE
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))

    setUpModule()
    t0 = time.perf_counter()
    for cls in [Test_L8_RomajiGenerator, Test_L8_SM2Invariants, Test_L8_BKTInvariants]:
        runner.run(loader.loadTestsFromTestCase(cls))
    _print_pbt_summary(time.perf_counter() - t0)
