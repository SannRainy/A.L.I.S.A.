"""
Grammar Checker Service — Japanese sentence analysis using pykakasi + LLM
Provides morphological analysis and error detection for user-written Japanese text.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import pykakasi (already in requirements)
try:
    import pykakasi
    _kakasi = pykakasi.kakasi()
    HAS_KAKASI = True
except ImportError:
    _kakasi = None
    HAS_KAKASI = False
    logger.warning("pykakasi not available — grammar checker will use LLM-only mode")


class GrammarCheckerService:
    """Analyze Japanese text for grammar errors and provide corrections."""

    @staticmethod
    def tokenize(text: str) -> list[dict]:
        """
        Tokenize Japanese text using pykakasi.
        Returns list of {original, reading, romaji, type}.
        """
        if not HAS_KAKASI or not text.strip():
            return []

        try:
            result = _kakasi.convert(text)
            tokens = []
            for item in result:
                tokens.append({
                    "original": item.get("orig", ""),
                    "reading": item.get("hira", ""),
                    "romaji": item.get("hepburn", ""),
                    "type": item.get("kana", ""),  # Katakana/Hiragana/Kanji/ASCII
                })
            return tokens
        except Exception as e:
            logger.error(f"Tokenize error: {e}")
            return []

    @staticmethod
    def basic_analysis(text: str) -> dict:
        """
        Basic morphological analysis of Japanese text.
        Returns token breakdown and basic stats.
        """
        tokens = GrammarCheckerService.tokenize(text)

        # Count character types
        kanji_count = sum(1 for t in tokens if any('一' <= c <= '鿿' for c in t["original"]))
        hiragana_count = sum(1 for t in tokens if any('぀' <= c <= 'ゟ' for c in t["original"]))
        katakana_count = sum(1 for t in tokens if any('゠' <= c <= 'ヿ' for c in t["original"]))

        return {
            "tokens": tokens,
            "token_count": len(tokens),
            "char_count": len(text),
            "kanji_count": kanji_count,
            "hiragana_tokens": hiragana_count,
            "katakana_tokens": katakana_count,
        }

    @staticmethod
    def detect_common_errors(text: str) -> list[dict]:
        """
        Rule-based detection of common N5 grammar errors.
        Returns list of {type, position, message, suggestion}.
        """
        errors = []

        # Check common particle errors
        particle_rules = [
            {
                "wrong": "が食べる",
                "type": "particle_error",
                "message": "Biasanya kata kerja 食べる (taberu) berpasangan dengan objek menggunakan partikel を (o), bukan が (ga) untuk kalimat aktif.",
                "suggestion": "を食べる"
            },
            {
                "wrong": "は食べる",
                "type": "particle_error",
                "message": "Gunakan partikel を (o) untuk menandai objek makanan dari kata kerja 食べる (taberu).",
                "suggestion": "を食べる"
            },
            {
                "wrong": "を行く",
                "type": "particle_error",
                "message": "Kata kerja 行く (iku) menunjukkan arah pergerakan dan berpasangan dengan partikel に (ni) atau へ (e), bukan を (o).",
                "suggestion": "に行く"
            },
            {
                "wrong": "で行く",
                "type": "particle_error",
                "message": "Untuk menyatakan pergi ke suatu tempat, gunakan partikel に (ni) atau へ (e), bukan で (de).",
                "suggestion": "に行く"
            },
        ]

        for rule in particle_rules:
            if rule["wrong"] in text:
                pos = text.index(rule["wrong"])
                errors.append({
                    "type": rule["type"],
                    "position": pos,
                    "message": rule["message"],
                    "suggestion": text.replace(rule["wrong"], rule["suggestion"])
                })

        # Check for missing です/ます (politeness)
        if text.endswith("だ") and not text.endswith("んだ"):
            errors.append({
                "type": "register",
                "message": "文末の「だ」はカジュアルです。丁寧語では「です」を使いましょう。",
                "suggestion": text[:-1] + "desu",
            })

        # Check double particles
        double_particles = ["はは", "がが", "をを", "にに", "でで"]
        for dp in double_particles:
            if dp in text:
                pos = text.index(dp)
                errors.append({
                    "type": "particle_error",
                    "position": pos,
                    "message": f"助詞「{dp[0]}」が重複しています。",
                    "suggestion": text[:pos] + dp[0] + text[pos + 2:],
                })

        return errors

    @staticmethod
    def detect_correct_grammar_points(text: str) -> list[dict]:
        """
        Detect correct N5 grammar patterns in the text to explain why it is correct.
        """
        detected = []
        
        patterns = [
            {
                "pattern": "は",
                "name": "Partikel は (wa)",
                "explanation": "Berfungsi sebagai penanda topik utama dalam kalimat. Menunjukkan tentang apa kalimat tersebut dibahas.",
                "example": "私は学生です (Saya adalah siswa)"
            },
            {
                "pattern": "が",
                "name": "Partikel が (ga)",
                "explanation": "Berfungsi sebagai penanda subjek utama pelaku tindakan, keberadaan (ada/arimasu/imasu), atau kata sifat yang dirasakan.",
                "example": "水がほしいです (Ingin air)"
            },
            {
                "pattern": "を",
                "name": "Partikel を (o/wo)",
                "explanation": "Berfungsi sebagai penanda objek langsung yang dikenai tindakan oleh kata kerja transitif.",
                "example": "本を読む (Membaca buku)"
            },
            {
                "pattern": "に",
                "name": "Partikel に (ni)",
                "explanation": "Menunjukkan arah/tujuan perpindahan (ke), titik spesifik waktu (pada jam/hari), atau penerima tindakan (kepada).",
                "example": "日本に行く (Pergi ke Jepang)"
            },
            {
                "pattern": "で",
                "name": "Partikel で (de)",
                "explanation": "Menunjukkan tempat terjadinya suatu aktivitas (di), atau alat/kendaraan/cara yang digunakan untuk melakukan sesuatu.",
                "example": "図書館で勉強する (Belajar di perpustakaan)"
            },
            {
                "pattern": "です",
                "name": "Kopula です (desu)",
                "explanation": "Digunakan di akhir kalimat kata benda atau kata sifat untuk menyatakan pernyataan bentuk sopan (polite copula).",
                "example": "日本語は面白いです (Bahasa Jepang menarik)"
            },
            {
                "pattern": "ます",
                "name": "Bentuk ます (masu)",
                "explanation": "Merupakan akhiran kata kerja bentuk sopan (Keigo) untuk menunjukkan tindakan di masa sekarang/depan secara sopan.",
                "example": "食べます (Makan)"
            },
            {
                "pattern": "の",
                "name": "Partikel の (no)",
                "explanation": "Berfungsi menghubungkan kata benda dengan kata benda lainnya untuk menyatakan kepemilikan, asal, atau klasifikasi.",
                "example": "私の本 (Buku saya)"
            },
            {
                "pattern": "と",
                "name": "Partikel と (to)",
                "explanation": "Digunakan untuk menggabungkan kata benda secara sejajar dengan arti 'dan', atau menyatakan pelaku bersama 'dengan'.",
                "example": "友達と遊ぶ (Bermain dengan teman)"
            },
            {
                "pattern": "も",
                "name": "Partikel も (mo)",
                "explanation": "Berarti 'juga' atau 'pun', digunakan untuk menyamakan subjek/objek dengan yang telah disebutkan sebelumnya.",
                "example": "私も学生です (Saya juga siswa)"
            },
            {
                "pattern": "から",
                "name": "Partikel から (kara)",
                "explanation": "Menunjukkan titik awal dari waktu atau tempat (mulai dari/sejak), atau menyatakan sebab-akibat (karena).",
                "example": "インドネシアから来ました (Datang dari Indonesia)"
            },
            {
                "pattern": "まで",
                "name": "Partikel まで (made)",
                "explanation": "Menunjukkan titik batas akhir dari waktu atau lokasi tempat perpindahan (sampai/hingga).",
                "example": "学校まで行く (Pergi sampai sekolah)"
            }
        ]
        
        for item in patterns:
            if item["pattern"] in text:
                detected.append(item)
                
        return detected

    @staticmethod
    def build_llm_prompt(text: str, tokens: list[dict]) -> str:
        """
        Build a prompt for LLM-based grammar checking.
        Used when deeper analysis is needed beyond rule-based checks.
        """
        token_info = ", ".join([f"{t['original']}({t['romaji']})" for t in tokens[:20]])

        return f"""以下の日本語テキストを分析してください。

テキスト: 「{text}」
トークン: {token_info}

以下の形式でJSON回答してください:
{{
  "is_correct": true/false,
  "overall_score": 0-100,
  "errors": [
    {{
      "type": "particle/conjugation/word_order/register",
      "original": "間違い部分",
      "correction": "正しい形",
      "explanation_id": "インドネシア語の説明",
      "explanation_jp": "日本語の説明"
    }}
  ],
  "corrected_text": "修正後の全文",
  "level_assessment": "N5/N4/N3"
}}"""
