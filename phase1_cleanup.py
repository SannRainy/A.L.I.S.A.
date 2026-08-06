"""
Phase 1 Cleanup Script — A.L.I.S.A / TVJP Codebase
====================================================
Menghapus komentar debug/catatan sementara dari file Python dan Svelte/JS.
Menstandarisasi section dividers dan whitespace berlebih.
"""
import os
import re
import shutil
from pathlib import Path
from typing import Tuple, List

ROOT = Path(r"C:\Users\satya\OneDrive\Desktop\TVJP")
BACKUP_DIR = ROOT / "_cleanup_backup"

SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", "venv-backend",
    ".svelte-kit", "build", "trt_cache", "dist", ".pytest_cache",
    ".hypothesis", "_cleanup_backup", "temp", "tests", "data_pipeline",
    "Style-Bert-VITS2", "SKRIPSI 2026", "ALISA Sticker", "brain", "scratch",
}

PY_FILES = [
    "backend/main.py",
    "backend/services/llm_agent.py",
    "backend/services/graph_engine.py",
    "backend/services/srs_service.py",
    "backend/services/streak_service.py",
    "backend/services/supabase_service.py",
    "backend/services/voice_service.py",
    "backend/services/warmup_service.py",
    "backend/services/bkt_engine.py",
    "backend/services/grammar_checker.py",
    "backend/services/romaji_utils.py",
    "backend/api/chat_router.py",
    "backend/api/admin_router.py",
    "backend/api/feature_router.py",
    "backend/core/config.py",
    "backend/core/supabase_client.py",
    "backend/logic/db_orchestrator.py",
]

SVELTE_JS_FILES = [
    "frontend/src/routes/+page.svelte",
    "frontend/src/routes/+layout.svelte",
    "frontend/src/routes/admin/+page.svelte",
    "frontend/src/routes/admin/AiModelsTab.svelte",
    "frontend/src/routes/admin/AnalyticsTab.svelte",
    "frontend/src/routes/admin/DataPipelineTab.svelte",
    "frontend/src/routes/admin/IngestTab.svelte",
    "frontend/src/routes/admin/UsersTab.svelte",
    "frontend/src/components/Achievement.svelte",
    "frontend/src/components/AchievementBadges.svelte",
    "frontend/src/components/DiscoveryMode.svelte",
    "frontend/src/components/EquippedEmblems.svelte",
    "frontend/src/components/ExamEngine.svelte",
    "frontend/src/components/KanjiFlashcard.svelte",
    "frontend/src/components/KanjiStudyMode.svelte",
    "frontend/src/components/MasteryPath.svelte",
    "frontend/src/components/PlacementTest.svelte",
    "frontend/src/components/Profile.svelte",
    "frontend/src/components/QuestEngine.svelte",
    "frontend/src/components/QuestMap.svelte",
    "frontend/src/components/QuestMode.svelte",
    "frontend/src/components/QuestResult.svelte",
    "frontend/src/components/RadarChart.svelte",
    "frontend/src/components/ReadingMode.svelte",
    "frontend/src/components/SRSReview.svelte",
    "frontend/src/components/VoiceMode.svelte",
    "frontend/src/lib/furigana.js",
    "frontend/src/lib/sfx_manager.js",
    "frontend/src/lib/supabase.js",
    "frontend/src/lib/vrm_controller.js",
    "frontend/src/stores/auth_store.js",
    "frontend/src/stores/chat_store.js",
    "frontend/src/stores/profile_store.js",
    "frontend/src/stores/theme_store.js",
]

# ── Python comment cleaning ───────────────────────────────────────────────

# Patterns untuk komentar yang HARUS dihapus (debug/noise/catatan dev):
PY_REMOVE_PATTERNS = [
    # Debug/TODO/FIXME/HACK markers
    re.compile(r'^\s*#\s*(TODO|FIXME|HACK|XXX|TEMP|BUG|WORKAROUND)[\s:].+$', re.I),
    # Komentar "DEBUG" inline
    re.compile(r'^\s*#\s*[Dd][Ee][Bb][Uu][Gg][:\s].+$'),
    # Komentar "test" yang tidak informatif
    re.compile(r'^\s*#\s*[Tt]est[:\s].+$'),
    # Komentar catatan pribadi dengan kata "coba", "check this", "lihat ini"
    re.compile(r'^\s*#\s*(coba|check this|lihat ini|perhatikan ini|ini perlu).+$', re.I),
    # Commented-out code blocks (baris yang dimulai # + valid python keywords)
    re.compile(r'^\s*#\s*(import|from|def |class |return|if |for |while |print\(|logger\.).+$'),
]

# Patterns untuk komentar SECTION DIVIDER yang perlu distandarisasi
PY_SECTION_PATTERNS = [
    # ── Section ─── (berbagai variasi) → standar bersih
    re.compile(r'^\s*#\s*[─━═\-=]{4,}\s*(.+?)\s*[─━═\-=]*\s*$'),
    re.compile(r'^\s*#\s*[═]{3,}\s*(.+?)\s*[═]*\s*$'),
]

# Inline comments yang harus dihapus (komentar di akhir baris code)
PY_INLINE_REMOVE = [
    # "# Fixed: ..."
    re.compile(r'\s*#\s*Fixed:\s*.+$'),
    # "# Deprecated: ..."
    re.compile(r'\s*#\s*Deprecated:\s*.+$'),
    # Debug print hints
    re.compile(r'\s*#\s*(jangan lupa hapus|remove this|delete this|sementara).+$', re.I),
    # "# In production, ..." (sisa catatan dev)
    re.compile(r'\s*#\s*In production[,\s].+$', re.I),
]

def clean_python_line(line: str, prev_was_blank: bool) -> Tuple[str | None, bool]:
    """
    Proses satu baris Python.
    Returns: (cleaned_line | None, is_blank)
    None = baris ini harus dihapus sepenuhnya.
    """
    stripped = line.rstrip('\r\n')
    rstripped = stripped.rstrip()

    # Cek apakah baris ini hanya komentar (dimulai dengan #)
    if re.match(r'^\s*#', stripped):
        content = stripped.strip()

        # Hapus patterns yang noise
        for pat in PY_REMOVE_PATTERNS:
            if pat.match(stripped):
                return None, False

        # Standarisasi section divider: hanya variasi ASCII/unicode decoration
        if re.match(r'^\s*#\s*[─━═\-=_]{8,}', content):
            # Hanya pertahankan jika ada teks label di dalamnya
            m = re.match(r'^\s*#\s*[─━═\-=_]{4,}\s*(.+?)\s*[─━═\-=_]*\s*$', content)
            if m and len(m.group(1).strip()) > 2:
                return f"# {m.group(1).strip()}\n", False
            else:
                # Pure decoration line — hapus
                return None, False

        return line, False

    # Baris bukan komentar — bersihkan inline comment noise
    for pat in PY_INLINE_REMOVE:
        rstripped = pat.sub('', rstripped)

    # Kembalikan dengan line ending asli
    ending = '\n'
    return rstripped + ending, len(rstripped.strip()) == 0


def clean_python_file(content: str) -> str:
    lines = content.split('\n')
    result = []
    prev_blank = False
    consecutive_blanks = 0

    for raw_line in lines:
        line = raw_line + '\n' if not raw_line.endswith('\n') else raw_line
        cleaned, is_blank = clean_python_line(line, prev_blank)

        if cleaned is None:
            # Baris dihapus — jika sebelumnya tidak blank, jangan tambahkan blank extra
            continue

        if is_blank or cleaned.strip() == '':
            consecutive_blanks += 1
            if consecutive_blanks <= 2:  # Maksimal 2 blank lines berturut-turut
                result.append('\n')
        else:
            consecutive_blanks = 0
            result.append(cleaned)

        prev_blank = is_blank

    # Gabungkan dan trim trailing whitespace
    final = ''.join(result)
    # Hapus trailing blank lines di akhir file, biarkan 1 newline
    final = final.rstrip() + '\n'
    return final


# ── Svelte/JS comment cleaning ────────────────────────────────────────────

JS_REMOVE_INLINE = [
    # // TODO
    re.compile(r'^\s*//\s*(TODO|FIXME|HACK|XXX|TEMP|BUG)[\s:].+$', re.I),
    # // Debug
    re.compile(r'^\s*//\s*[Dd]ebug[:\s].+$'),
    # // Test:
    re.compile(r'^\s*//\s*[Tt]est[:\s].+$'),
    # // console.log( — komentar tentang console.log
    re.compile(r'^\s*//\s*console\.log.+$'),
    # // coba / check / sementara
    re.compile(r'^\s*//\s*(coba|check this|lihat ini|sementara|jangan lupa).+$', re.I),
]

# console.log statements yang masih aktif (uncommented) — hapus dari kode
CONSOLE_LOG_RE = re.compile(r'^\s*console\.log\(.+$')

# Aktif console statements lainnya  
CONSOLE_WARN_ERROR_RE = re.compile(r'^\s*console\.(warn|error|debug|info|trace)\(.+$')

def clean_js_svelte_line(line: str) -> str | None:
    """
    Bersihkan satu baris JS/Svelte.
    Returns cleaned line or None (to delete).
    """
    stripped = line.rstrip('\r\n')

    # Hapus console.log yang aktif
    if CONSOLE_LOG_RE.match(stripped):
        return None

    # Hapus console.warn/error/debug/info aktif
    if CONSOLE_WARN_ERROR_RE.match(stripped):
        return None

    # Komentar satu baris //
    if re.match(r'^\s*//', stripped):
        for pat in JS_REMOVE_INLINE:
            if pat.match(stripped):
                return None

    return line


def clean_js_svelte_file(content: str) -> str:
    lines = content.split('\n')
    result = []
    consecutive_blanks = 0

    for raw_line in lines:
        line = raw_line + '\n' if not raw_line.endswith('\n') else raw_line
        cleaned = clean_js_svelte_line(line)

        if cleaned is None:
            continue

        if cleaned.strip() == '':
            consecutive_blanks += 1
            if consecutive_blanks <= 2:
                result.append('\n')
        else:
            consecutive_blanks = 0
            result.append(cleaned)

    final = ''.join(result)
    final = final.rstrip() + '\n'
    return final


# ── Main ──────────────────────────────────────────────────────────────────

def backup_file(path: Path):
    rel = path.relative_to(ROOT)
    backup = BACKUP_DIR / rel
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)


def process_file(rel_path: str, is_python: bool) -> dict:
    path = ROOT / rel_path
    if not path.exists():
        return {"file": rel_path, "status": "NOT_FOUND"}

    original = path.read_text(encoding="utf-8")

    if is_python:
        cleaned = clean_python_file(original)
    else:
        cleaned = clean_js_svelte_file(original)

    orig_lines = original.count('\n')
    clean_lines = cleaned.count('\n')
    removed = orig_lines - clean_lines

    if cleaned != original:
        backup_file(path)
        path.write_text(cleaned, encoding="utf-8")
        status = "CLEANED"
    else:
        status = "NO_CHANGE"

    return {
        "file": rel_path,
        "status": status,
        "original_lines": orig_lines,
        "cleaned_lines": clean_lines,
        "removed_lines": removed,
    }


def main():
    print("=" * 60)
    print("Phase 1 Cleanup — A.L.I.S.A / TVJP Codebase")
    print("=" * 60)
    print(f"Backup directory: {BACKUP_DIR}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print()

    results = []

    print("── Python Files ──────────────────────────────────")
    for rel in PY_FILES:
        r = process_file(rel, is_python=True)
        results.append(r)
        status = r["status"]
        if status == "CLEANED":
            print(f"  ✅ CLEANED  {rel}  (-{r['removed_lines']} lines)")
        elif status == "NO_CHANGE":
            print(f"  ○  NO CHANGE {rel}")
        else:
            print(f"  ❌ {status}   {rel}")

    print()
    print("── Svelte / JS Files ─────────────────────────────")
    for rel in SVELTE_JS_FILES:
        r = process_file(rel, is_python=False)
        results.append(r)
        status = r["status"]
        if status == "CLEANED":
            print(f"  ✅ CLEANED  {rel}  (-{r['removed_lines']} lines)")
        elif status == "NO_CHANGE":
            print(f"  ○  NO CHANGE {rel}")
        else:
            print(f"  ❌ {status}   {rel}")

    print()
    total_cleaned = sum(1 for r in results if r["status"] == "CLEANED")
    total_removed = sum(r.get("removed_lines", 0) for r in results if r["status"] == "CLEANED")
    print("=" * 60)
    print(f"SUMMARY: {total_cleaned} files cleaned, {total_removed} lines removed")
    print(f"Backup saved to: {BACKUP_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
