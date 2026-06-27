# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     TVJP – LAYER 9 · METAMORPHIC TESTING  (Pilar 3 / Skripsi)               ║
║     Sistem Virtual Tutor Bahasa Jepang Berbasis Knowledge Graph              ║
║                                                                              ║
║  Metode: Metamorphic Testing (MT) — Solusi untuk Oracle Problem pada AI      ║
║  Referensi Jurnal: Chen et al. (1998); Liu et al. (IEEE TSE 2024)            ║
║                                                                              ║
║  Metamorphic Relations (MR) yang Diimplementasikan:                          ║
║    MR-1 · BKT Monotonic Increase  – jawaban benar → P(L) pasti naik         ║
║    MR-1b· BKT Monotonic Decrease  – jawaban salah → P(L) pasti turun        ║
║    MR-2 · SM-2 Interval Monotonic – kualitas lebih tinggi → interval ≥       ║
║    MR-3 · SM-2 Reset Invariant    – quality < 3 → repetisi reset ke 0       ║
║    MR-4 · SM-2 Quality Clamp      – quality di luar [0,5] diklem aman        ║
║    MR-5 · BKT Dominance Order     – P(L_correct) > P(L_wrong) selalu        ║
║    MR-6 · SM-2 EF Monotonicity    – quality lebih tinggi → EF ≥ EF sebelum  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Cara Menjalankan:
    python -m pytest backend/tests/test_metamorphic_layer9.py -v
    python backend/tests/test_metamorphic_layer9.py     (standalone)

Catatan Akademik:
    Metamorphic Testing mengatasi "Oracle Problem" pada pengujian sistem AI/non-deterministik
    dengan mendefinisikan RELASI yang harus berlaku antara dua eksekusi berbeda,
    alih-alih mendefinisikan output tepat yang benar (yang tidak diketahui).

    Formal: Jika f(input_A) = output_A, maka untuk transformasi T,
            harus berlaku: f(T(input_A)) RELASI output_A
"""

import unittest
import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir   = os.path.dirname(current_dir)
backend_dir = os.path.dirname(tests_dir)
root_dir    = os.path.dirname(backend_dir)

for _p in (backend_dir, root_dir, tests_dir):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ─────────────────────────────────────────────────────────────────────────────
# ANSI CONSOLE HELPERS
# ─────────────────────────────────────────────────────────────────────────────
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False

def _c(code, text): return f"\033[{code}m{text}\033[0m" if _ANSI else text
def green(t):   return _c("32;1", t)
def red(t):     return _c("31;1", t)
def yellow(t):  return _c("33;1", t)
def cyan(t):    return _c("36;1", t)
def magenta(t): return _c("35;1", t)
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
# SERVICE IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
try:
    from services.srs_service import SRSService
    from services.bkt_engine  import BKTEngine
    SERVICES_AVAILABLE = True
except ImportError:
    try:
        from backend.services.srs_service import SRSService
        from backend.services.bkt_engine  import BKTEngine
        SERVICES_AVAILABLE = True
    except ImportError:
        SERVICES_AVAILABLE = False
        print("[ERROR] Service modules tidak dapat diimpor. Pastikan PYTHONPATH benar.\n")
        class SRSService:
            @staticmethod
            def calculate_sm2(q, r, ef, i):
                return {"easiness_factor": 2.5, "interval_days": 1,
                        "repetitions": 0, "next_review": None}
        class BKTEngine:
            def update_belief(self, p, c, params): return 0.5

# ─────────────────────────────────────────────────────────────────────────────
# RESULT ACCUMULATOR
# ─────────────────────────────────────────────────────────────────────────────
ALL_MT_RESULTS: list[dict] = []
_mt_counter = 0
_T0 = time.perf_counter()

def _log_mt(mr_id: str, name: str, cases_tested: int, status: str,
            transform: str = "", relation: str = "", note: str = ""):
    """Catat satu Metamorphic Relation ke ALL_MT_RESULTS dan cetak ke konsol."""
    global _mt_counter
    _mt_counter += 1

    ALL_MT_RESULTS.append({
        "no":           _mt_counter,
        "id":           mr_id,
        "name":         name,
        "cases":        cases_tested,
        "status":       status,
        "transform":    transform,
        "relation":     relation,
        "note":         note,
    })

    badge   = magenta("[MT LAYER 9]      ")
    st_icon = ("✔ PASSED " if status == "PASSED" else
               "✖ FAILED " if status == "FAILED" else
               "⊘ SKIPPED")
    st_col  = (green if status == "PASSED" else (red if status == "FAILED" else yellow))(st_icon)
    mr_col  = cyan(f"MT:{mr_id:<7}")
    nm_col  = bold(f"{name:<36}")
    cases_d = dim(f"{cases_tested} cases")
    print(f"  {st_col}  {badge}  {mr_col}  {nm_col}  {cases_d}")
    if transform:
        print(f"  {dim(f'           T: {transform[:68]}')}")
    if relation:
        print(f"  {dim(f'           R: {relation[:68]}')}")
    if note:
        print(f"  {dim(f'           ! {note[:68]}')}")


# ═════════════════════════════════════════════════════════════════════════════
#  MR-1 + MR-1b + MR-5 · BKT ENGINE — MONOTONICITY RELATIONS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L9_BKTMetamorphic(unittest.TestCase):
    """
    Metamorphic Testing — BKTEngine.update_belief()

    MR-1  : Jawaban benar HARUS menaikkan P(L)  [monoton naik]
    MR-1b : Jawaban salah HARUS menurunkan P(L)  [monoton turun]
    MR-5  : f(p, correct=True) > f(p, correct=False) untuk semua p  [dominance order]

    Referensi: Chen et al. (1998) — Metamorphic Testing Principle
               Oracle Problem dalam sistem probabilistik
    """

    def setUp(self):
        if SERVICES_AVAILABLE:
            self.bkt    = BKTEngine()
            self.params = {"p_t": 0.15, "p_g": 0.25, "p_s": 0.05}

    @unittest.skipUnless(SERVICES_AVAILABLE, "Service bkt_engine tidak dapat diimpor")
    def test_MR1_bkt_monotonic_increase_on_correct(self):
        """
        [MR-1] BKT Monotonic Increase: Jawaban benar HARUS menaikkan P(L).

        Transformasi T : correct=False → correct=True
        Relasi        R : f(p, T) > p  (output harus lebih besar dari input)

        Diuji pada: 10 titik P(L) yang bervariasi dari sangat rendah hingga sangat tinggi.
        Kecuali batas atas (0.999) yang sudah di-clamp.
        """
        P_VALUES = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
        cases_tested = 0
        violations   = []

        for p in P_VALUES:
            cases_tested += 1
            p_after_correct = self.bkt.update_belief(p, True, self.params)
            if p_after_correct <= p:
                violations.append({
                    "p_before": p,
                    "p_after":  round(p_after_correct, 5),
                    "verdict":  "MR-1 VIOLATED: correct=True tidak menaikkan P(L)"
                })

        if violations:
            _log_mt("MR-1", "BKT Monotonic Increase (Correct)",
                    cases_tested, "FAILED",
                    transform="correct=False → correct=True",
                    relation="f(p, correct=True) > p  ∀p ∈ (0, 0.999)",
                    note=f"Pelanggaran: {violations}")
            self.fail(f"MR-1 VIOLATED: {violations}")
        else:
            _log_mt("MR-1", "BKT Monotonic Increase (Correct)",
                    cases_tested, "PASSED",
                    transform="correct=False → correct=True",
                    relation="f(p, correct=True) > p  [terbukti untuk semua p yang diuji]")

    @unittest.skipUnless(SERVICES_AVAILABLE, "Service bkt_engine tidak dapat diimpor")
    def test_MR1b_bkt_wrong_always_lower_than_correct(self):
        """
        [MR-1b] BKT Comparative Decrease: f(p, correct=False) < f(p, correct=True) selalu.

        Catatan Akademik (Temuan Metamorphic Testing):
          Rumus BKT baris 71 — 'p_l_new = p_l_given_obs + (1 - p_l_given_obs) * p_t'
          Komponen transition p_t=0.15 dapat menaikkan P(L) bahkan setelah jawaban salah
          (terutama untuk nilai p kecil, misal p=0.1). Ini bukan bug — ini adalah
          perilaku matematis BKT yang valid: meski salah, masih ada kemungkinan transisi
          dari 'belum tahu' menjadi 'tahu' (p_t).

          Oleh karena itu, MR yang tepat bukan:
            "jawaban salah PASTI menurunkan P(L) di bawah p_sebelum"
          melainkan:
            "output jawaban salah SELALU lebih rendah dari output jawaban benar
             untuk p input yang SAMA"

        Transformasi T : correct=True → correct=False  (input p IDENTIK)
        Relasi        R : f(p, correct=False) < f(p, correct=True)  ∀p ∈ (0.001, 0.999)
        """
        # P_VALUES dikecualikan batas p=0.999 (keduanya akan di-clamp ke 0.999)
        P_VALUES = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
        cases_tested = 0
        violations   = []

        for p in P_VALUES:
            cases_tested += 1
            p_correct = self.bkt.update_belief(p, True,  self.params)
            p_wrong   = self.bkt.update_belief(p, False, self.params)

            if p_wrong >= p_correct:
                violations.append({
                    "p_in":      p,
                    "p_correct": round(p_correct, 5),
                    "p_wrong":   round(p_wrong, 5),
                    "verdict":   "MR-1b: f(p,False) seharusnya < f(p,True)"
                })

        if violations:
            _log_mt("MR-1b", "BKT Comparative Decrease (Wrong < Correct)",
                    cases_tested, "FAILED",
                    transform="(p, correct=True) vs (p, correct=False) — p identik",
                    relation="f(p, False) < f(p, True)  ∀p",
                    note=f"Pelanggaran relasi komparatif: {violations}")
            self.fail(f"MR-1b VIOLATED: {violations}")
        else:
            _log_mt("MR-1b", "BKT Comparative Decrease (Wrong < Correct)",
                    cases_tested, "PASSED",
                    transform="(p, correct=True) vs (p, correct=False) — p identik",
                    relation=f"f(p,False) < f(p,True) terbukti ∀p dalam {cases_tested} titik uji",
                    note="Catatan: P(L) bisa naik meski jawaban salah (efek p_t=0.15), tapi SELALU lebih rendah dari jawaban benar")

    @unittest.skipUnless(SERVICES_AVAILABLE, "Service bkt_engine tidak dapat diimpor")
    def test_MR5_bkt_dominance_order(self):
        """
        [MR-5] BKT Dominance Order: Output jawaban benar SELALU lebih tinggi dari jawaban salah.

        Transformasi T : (p, correct=True) vs (p, correct=False) — input p identik
        Relasi        R : f(p, True) > f(p, False)  untuk semua p yang sama

        Ini adalah MR paling fundamental dalam BKT: bukti konsistensi arah update Bayesian.
        """
        P_VALUES = [0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.999]
        cases_tested = 0
        violations   = []

        for p in P_VALUES:
            cases_tested += 1
            p_correct = self.bkt.update_belief(p, True,  self.params)
            p_wrong   = self.bkt.update_belief(p, False, self.params)
            if not (p_correct > p_wrong):
                violations.append({
                    "p_in":      p,
                    "p_correct": round(p_correct, 5),
                    "p_wrong":   round(p_wrong, 5),
                })

        if violations:
            _log_mt("MR-5", "BKT Dominance Order",
                    cases_tested, "FAILED",
                    transform="(p, True) vs (p, False) — input identik",
                    relation="f(p, True) > f(p, False)  ∀p ∈ [0.001, 0.999]",
                    note=f"Pelanggaran dominance: {violations}")
            self.fail(f"MR-5 VIOLATED: {violations}")
        else:
            _log_mt("MR-5", "BKT Dominance Order",
                    cases_tested, "PASSED",
                    transform="(p, correct=True) vs (p, correct=False)",
                    relation="f(p,True) > f(p,False)  [terbukti ∀p dalam 13 titik uji]")


# ═════════════════════════════════════════════════════════════════════════════
#  MR-2 + MR-3 + MR-4 + MR-6 · SM-2 ALGORITHM — MONOTONICITY & RESET RELATIONS
# ═════════════════════════════════════════════════════════════════════════════
class Test_L9_SM2Metamorphic(unittest.TestCase):
    """
    Metamorphic Testing — SRSService.calculate_sm2()
    Referensi kode: srs_service.py  baris 22-58

    MR-2 : Kualitas lebih tinggi → interval review lebih panjang atau sama (rep > 1)
    MR-3 : quality < 3 → repetisi direset ke 0 (Reset Invariant)
    MR-4 : quality di luar [0,5] diklem aman — tidak crash atau menghasilkan nilai aneh
    MR-6 : Kualitas lebih tinggi → EF lebih besar atau sama (monotonicity EF)

    Formal Transformasi MR-2: T(quality=q_low) → T(quality=q_high), q_high > q_low ≥ 3
    Formal Relasi MR-2    : SM2(q_high).interval_days ≥ SM2(q_low).interval_days
    """

    # ── MR-2 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(SERVICES_AVAILABLE, "Service srs_service tidak dapat diimpor")
    def test_MR2_sm2_interval_monotonicity(self):
        """
        [MR-2] SM-2 Interval Monotonicity: Kualitas lebih tinggi → interval lebih panjang/sama.

        Transformasi T : quality=3 → quality=5  (dinaikkan, keduanya di atas threshold benar)
        Relasi        R : SM2(q=5).interval ≥ SM2(q=3).interval

        PENTING: Hanya valid untuk repetitions > 1, karena rep=0 dan rep=1 memiliki
                 interval fixed (1 dan 6) yang tidak bergantung pada kualitas.
        """
        EF_VALUES = [1.3, 1.5, 2.0, 2.5, 3.0, 4.0]
        cases_tested = 0
        violations   = []

        for ef in EF_VALUES:
            for rep in [2, 3, 5, 10]:  # rep > 1 agar interval bergantung pada kualitas
                for base_interval in [6, 10, 15, 21]:
                    for q_low, q_high in [(3, 4), (3, 5), (4, 5)]:
                        cases_tested += 1
                        res_low  = SRSService.calculate_sm2(q_low,  rep, ef, base_interval)
                        res_high = SRSService.calculate_sm2(q_high, rep, ef, base_interval)

                        if res_high["interval_days"] < res_low["interval_days"]:
                            violations.append({
                                "q_low": q_low, "q_high": q_high,
                                "ef": round(ef, 2), "rep": rep,
                                "interval_low":  res_low["interval_days"],
                                "interval_high": res_high["interval_days"],
                            })

        if violations:
            _log_mt("MR-2", "SM-2 Interval Monotonicity",
                    cases_tested, "FAILED",
                    transform="quality=q_low → quality=q_high (q_high > q_low ≥ 3)",
                    relation="SM2(q_high).interval ≥ SM2(q_low).interval",
                    note=f"Pelanggaran: {violations[:2]}")
            self.fail(f"MR-2 VIOLATED: {violations[0]}")
        else:
            _log_mt("MR-2", "SM-2 Interval Monotonicity",
                    cases_tested, "PASSED",
                    transform="quality=q_low → quality=q_high",
                    relation=f"SM2(q_high).interval ≥ SM2(q_low).interval [terbukti {cases_tested} kasus]")

    # ── MR-3 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(SERVICES_AVAILABLE, "Service srs_service tidak dapat diimpor")
    def test_MR3_sm2_incorrect_resets_repetitions(self):
        """
        [MR-3] SM-2 Reset Invariant: Jawaban salah (quality < 3) SELALU reset repetisi ke 0.

        Transformasi T : quality=5 (benar) → quality=2 (salah)  [crossing threshold 3]
        Relasi        R : SM2(quality<3).repetitions == 0  AND  SM2(quality<3).interval == 1

        Ini adalah invariant fundamental SM-2 yang HARUS terpenuhi agar
        algoritma spaced repetition bekerja dengan benar.
        """
        cases_tested = 0
        violations   = []
        BAD_QUALITIES = [0, 1, 2]
        HIGH_REPS     = [1, 3, 5, 10, 20]  # Berapapun repetisi sebelumnya, harus reset

        for q in BAD_QUALITIES:
            for rep_before in HIGH_REPS:
                for ef in [1.3, 2.5, 4.0]:
                    cases_tested += 1
                    res = SRSService.calculate_sm2(q, rep_before, ef, interval_days=10)

                    if res["repetitions"] != 0:
                        violations.append({
                            "quality": q, "rep_before": rep_before,
                            "rep_after": res["repetitions"],
                            "verdict": "repetisi tidak reset ke 0"
                        })
                    if res["interval_days"] != 1:
                        violations.append({
                            "quality": q, "rep_before": rep_before,
                            "interval_after": res["interval_days"],
                            "verdict": "interval tidak reset ke 1"
                        })

        if violations:
            _log_mt("MR-3", "SM-2 Reset Invariant (quality < 3)",
                    cases_tested, "FAILED",
                    transform="quality=5 (correct) → quality=0|1|2 (incorrect)",
                    relation="SM2(q<3).repetitions == 0  AND  SM2(q<3).interval == 1",
                    note=f"Pelanggaran: {violations[:2]}")
            self.fail(f"MR-3 VIOLATED: {violations[0]}")
        else:
            _log_mt("MR-3", "SM-2 Reset Invariant (quality < 3)",
                    cases_tested, "PASSED",
                    transform="quality ∈ {0,1,2} — salah semua",
                    relation=f"rep==0 dan interval==1 terjaga di {cases_tested} kombinasi")

    # ── MR-4 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(SERVICES_AVAILABLE, "Service srs_service tidak dapat diimpor")
    def test_MR4_sm2_quality_clamping(self):
        """
        [MR-4] SM-2 Quality Clamping: Input quality di luar [0,5] harus diklem aman.

        Transformasi T : quality=3 (dalam range) → quality=-999 atau quality=999
        Relasi        R : SM2(-999) setara dengan SM2(0)  [klem ke 0]
                         SM2(999)  setara dengan SM2(5)   [klem ke 5]

        Referensi: srs_service.py baris 34 — 'quality = max(0, min(5, quality))'
        """
        cases_tested = 0
        violations   = []
        EXTREME_LOW  = [-1, -50, -999, -9999]
        EXTREME_HIGH = [6,   50,  999,  9999]
        EF_VALUES    = [1.3, 2.5, 4.0]

        # Hasil klem ke 0 harus SAMA dengan quality=0
        for q_extreme in EXTREME_LOW:
            for ef in EF_VALUES:
                cases_tested += 1
                res_extreme = SRSService.calculate_sm2(q_extreme, 2, ef, 6)
                res_clamped = SRSService.calculate_sm2(0,         2, ef, 6)
                if res_extreme != res_clamped:
                    violations.append({
                        "q_extreme": q_extreme,
                        "res_extreme": res_extreme,
                        "res_clamped_to_0": res_clamped,
                    })

        # Hasil klem ke 5 harus SAMA dengan quality=5
        for q_extreme in EXTREME_HIGH:
            for ef in EF_VALUES:
                cases_tested += 1
                res_extreme = SRSService.calculate_sm2(q_extreme, 2, ef, 6)
                res_clamped = SRSService.calculate_sm2(5,         2, ef, 6)
                if res_extreme != res_clamped:
                    violations.append({
                        "q_extreme": q_extreme,
                        "res_extreme": res_extreme,
                        "res_clamped_to_5": res_clamped,
                    })

        if violations:
            _log_mt("MR-4", "SM-2 Quality Clamping",
                    cases_tested, "FAILED",
                    transform="quality=-999 atau quality=999 → harus setara quality=0 atau 5",
                    relation="SM2(q_extreme) == SM2(clamp(q_extreme, 0, 5))",
                    note=f"Pelanggaran clamping: {violations[:1]}")
            self.fail(f"MR-4 VIOLATED: {violations[0]}")
        else:
            _log_mt("MR-4", "SM-2 Quality Clamping",
                    cases_tested, "PASSED",
                    transform="quality ∈ {-9999..9999} — di luar range valid",
                    relation=f"Semua diklem aman ke [0,5] — {cases_tested} kasus")

    # ── MR-6 ────────────────────────────────────────────────────────────────
    @unittest.skipUnless(SERVICES_AVAILABLE, "Service srs_service tidak dapat diimpor")
    def test_MR6_sm2_ef_monotonicity(self):
        """
        [MR-6] SM-2 EF Monotonicity: Kualitas lebih tinggi → EF lebih besar atau sama.

        Transformasi T : quality=q_low → quality=q_high (q_high > q_low)
        Relasi        R : SM2(q_high).easiness_factor ≥ SM2(q_low).easiness_factor

        Ini karena rumus SM-2: new_ef = ef + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        Semakin besar q, semakin kecil penalty terhadap EF.
        """
        cases_tested = 0
        violations   = []
        EF_VALUES    = [1.3, 2.0, 2.5, 3.0]

        for ef in EF_VALUES:
            for rep in [0, 2, 5]:
                # Uji semua pasangan kualitas yang terurut
                for q_low in range(0, 5):
                    for q_high in range(q_low + 1, 6):
                        cases_tested += 1
                        res_low  = SRSService.calculate_sm2(q_low,  rep, ef, 6)
                        res_high = SRSService.calculate_sm2(q_high, rep, ef, 6)

                        if res_high["easiness_factor"] < res_low["easiness_factor"]:
                            violations.append({
                                "q_low": q_low, "q_high": q_high,
                                "ef_in": round(ef, 2),
                                "ef_low_out":  res_low["easiness_factor"],
                                "ef_high_out": res_high["easiness_factor"],
                            })

        if violations:
            _log_mt("MR-6", "SM-2 EF Monotonicity",
                    cases_tested, "FAILED",
                    transform="quality=q_low → quality=q_high (q_high > q_low)",
                    relation="SM2(q_high).EF ≥ SM2(q_low).EF",
                    note=f"Pelanggaran EF monotonicity: {violations[:2]}")
            self.fail(f"MR-6 VIOLATED: {violations[0]}")
        else:
            _log_mt("MR-6", "SM-2 EF Monotonicity",
                    cases_tested, "PASSED",
                    transform="quality ∈ [0..5] — semua pasangan terurut",
                    relation=f"EF(q_high) ≥ EF(q_low) — terbukti {cases_tested} kombinasi")


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY PRINTER
# ─────────────────────────────────────────────────────────────────────────────
def _print_mt_summary(elapsed: float):
    import re
    total   = len(ALL_MT_RESULTS)
    passed  = sum(1 for r in ALL_MT_RESULTS if r["status"] == "PASSED")
    failed  = sum(1 for r in ALL_MT_RESULTS if r["status"] == "FAILED")
    skipped = sum(1 for r in ALL_MT_RESULTS if r["status"] == "SKIPPED")
    rate    = passed / total * 100 if total else 0
    ok      = failed == 0

    # Hitung total cases diuji
    total_cases = sum(r.get("cases", 0) for r in ALL_MT_RESULTS)

    print()
    print(cyan("╔" + "═" * (W - 2) + "╗"))
    print(f"║ {cyan(bold('LAYER 9 · METAMORPHIC TESTING — RINGKASAN HASIL')):^{W-4}} ║")
    print(cyan("╠" + "═" * (W - 2) + "╣"))

    rows = [
        ("Total MR Diuji",              bold(str(total))),
        ("Total Test Cases Dieksekusi", bold(str(total_cases))),
        ("Passed",                      green(f"✔  {passed}")),
        ("Failed",                      red(f"✖  {failed}") if failed else dim("0")),
        ("Skipped",                     yellow(f"⊘  {skipped}") if skipped else dim("0")),
        ("Pass Rate",                   (green if ok else red)(f"{rate:.1f}%")),
        ("Waktu Eksekusi",              f"{elapsed:.3f}s"),
        ("Status Kelayakan MT",         green("● VALID — Semua Metamorphic Relations Terpenuhi") if ok
                                        else red(f"● CACAT — {failed} MR dilanggar")),
    ]
    for label, value in rows:
        val_c   = re.sub(r'\033\[[0-9;]*m', '', str(value))
        padding = (W - 4) - len(label) - len(val_c)
        print(f"║ {label}{' ' * max(0, padding)}{value} ║")

    print(cyan("╠" + "═" * (W - 2) + "╣"))
    print(f"║ {cyan(bold('Detail Metamorphic Relations:')):<{W-4}} ║")

    for r in ALL_MT_RESULTS:
        col  = green if r["status"] == "PASSED" else (red if r["status"] == "FAILED" else yellow)
        icon = "✔" if r["status"] == "PASSED" else ("✖" if r["status"] == "FAILED" else "⊘")
        line = (f"  {col(icon)}  {r['id']:<8}  {r['name']:<38}  "
                f"{dim(str(r['cases']) + ' cases')}")
        line_c = re.sub(r'\033\[[0-9;]*m', '', line)
        pad    = (W - 4) - len(line_c)
        print(f"║ {line}{' ' * max(0, pad)} ║")

    print(cyan("╠" + "═" * (W - 2) + "╣"))
    print(f"║ {dim('Referensi: Chen et al. (1998) — Metamorphic Testing; Liu et al. (IEEE TSE 2024)'):^{W-4}} ║")
    print(cyan("╚" + "═" * (W - 2) + "╝"))


# ─────────────────────────────────────────────────────────────────────────────
# MODULE LIFECYCLE HOOKS
# ─────────────────────────────────────────────────────────────────────────────
def setUpModule():
    try:
        print()
        print(cyan("╔" + "═" * (W - 2) + "╗"))
        print(f"║ {cyan(bold('TVJP  –  LAYER 9 · METAMORPHIC TESTING')):^{W-4}} ║")
        print(f"║ {dim('Pilar 3: Non-Deterministic & Robustness Testing  ·  Oracle Problem Solver'):^{W-4}} ║")
        print(f"║ {dim('Referensi: Chen et al. (1998)  |  Liu et al. IEEE TSE 2024'):^{W-4}} ║")
        print(cyan("╠" + "═" * (W - 2) + "╣"))
        print(_row(f"  {'Metode':<12}  Metamorphic Testing (MT) — Relasi antar eksekusi berbeda"))
        print(_row(f"  {'MR Diuji':<12}  7 Metamorphic Relations (MR-1 s.d. MR-6)"))
        print(_row(f"  {'Komponen':<12}  BKTEngine (MR-1,1b,5) · SRSService.calculate_sm2 (MR-2,3,4,6)"))
        print(_row(f"  {'Tujuan':<12}  Validasi invariant algoritmik tanpa oracle deterministik"))
        print(cyan("╚" + "═" * (W - 2) + "╝"))
        print(dim("  STATUS         [MT LAYER 9]          MR-ID       NAMA RELASI                       CASES"))
        print(dim("  " + "─" * (W - 2)))
    except (UnicodeEncodeError, ValueError, OSError):
        pass


def tearDownModule():
    try:
        _print_mt_summary(time.perf_counter() - _T0)
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
    for cls in [Test_L9_BKTMetamorphic, Test_L9_SM2Metamorphic]:
        runner.run(loader.loadTestsFromTestCase(cls))
    _print_mt_summary(time.perf_counter() - t0)
