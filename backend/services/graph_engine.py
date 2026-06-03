import asyncio
import logging
import uuid
from neo4j import GraphDatabase
from core.config import settings

log = logging.getLogger(__name__)


class GraphEngine:
    # ──────────────────────────────────────────────────────────────────────────
    # Lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        self.driver.verify_connectivity()
        self.ensure_indexes()

    def ensure_indexes(self):
        """Buat indeks agar query pada node utama tetap cepat seiring pertumbuhan data."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Note)    ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Note)    ON (n.created_at)",
            "CREATE INDEX IF NOT EXISTS FOR (s:Student) ON (s.id)",
            "CREATE INDEX IF NOT EXISTS FOR (v:Vocab)   ON (v.id)",
            "CREATE INDEX IF NOT EXISTS FOR (v:Vocab)   ON (v.level)",
            "CREATE INDEX IF NOT EXISTS FOR (g:Grammar) ON (g.id)",
            "CREATE INDEX IF NOT EXISTS FOR (g:Grammar) ON (g.level)",
            "CREATE INDEX IF NOT EXISTS FOR (k:Kanji)   ON (k.id)",
            "CREATE INDEX IF NOT EXISTS FOR (k:Kanji)   ON (k.level)",
            "CREATE INDEX IF NOT EXISTS FOR (t:Topic)   ON (t.id)",
        ]
        with self.driver.session() as session:
            for cypher in indexes:
                session.run(cypher)
        log.info("✅ Neo4j Indexes ensured.")

    def close(self):
        if self.driver:
            self.driver.close()

    # ──────────────────────────────────────────────────────────────────────────
    # Topic Queries
    # ──────────────────────────────────────────────────────────────────────────

    def get_starting_topic(self) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Topic)
                RETURN t.id AS id, t.name AS name, t.category AS category
                ORDER BY t.id ASC
                LIMIT 1
            """)
            rec = result.single()
            return dict(rec) if rec else None

    def get_next_topic(self, current_topic_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Topic {id: $current_topic_id})
                MATCH (next:Topic)
                WHERE next.id > t.id
                RETURN next.id AS id, next.name AS name, next.category AS category
                ORDER BY next.id ASC
                LIMIT 1
            """, current_topic_id=current_topic_id)
            rec = result.single()
            return dict(rec) if rec else None

    def get_topic_learning(self, topic_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Topic {id: $topic_id})
                OPTIONAL MATCH (v:Vocab)-[:BELONGS_TO_TOPIC]->(t)
                OPTIONAL MATCH (g:Grammar)-[:BELONGS_TO_TOPIC]->(t)
                RETURN t.id AS topic_id,
                       t.name AS topic_name,
                       t.category AS topic_category,
                       collect(DISTINCT {
                           id: v.id,
                           romaji: v.romaji,
                           indonesian_meaning: v.indonesian_meaning
                       }) AS vocabulary,
                       collect(DISTINCT {
                           id: g.id,
                           name: g.name,
                           level: g.level
                       }) AS grammar
            """, topic_id=topic_id)
            rec = result.single()
            return dict(rec) if rec else None

    def get_topic_by_name(self, name: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Topic)
                WHERE toLower(t.name) CONTAINS toLower($name)
                RETURN t.id AS id, t.name AS name, t.category AS category
                ORDER BY t.id ASC
                LIMIT 1
            """, name=name)
            rec = result.single()
            return dict(rec) if rec else None

    def get_recommended_topic(self, student_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Topic)
                WHERE NOT ((:Student {id: $student_id})-[:LEARNED]->(t))
                RETURN t.id AS id, t.name AS name, t.category AS category
                ORDER BY t.id
                LIMIT 1
            """, student_id=student_id)
            rec = result.single()
            return dict(rec) if rec else None

    # ──────────────────────────────────────────────────────────────────────────
    # Vocab Queries
    # ──────────────────────────────────────────────────────────────────────────

    def get_vocab_detail(self, word: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:Vocab)
                WHERE v.id = $word OR v.romaji = $word
                OPTIONAL MATCH (v)-[:WRITTEN_IN]->(k:Kanji)
                OPTIONAL MATCH (v)-[:BELONGS_TO_TOPIC]->(t:Topic)
                OPTIONAL MATCH (v)-[:HAS_POS]->(p:POS)
                OPTIONAL MATCH (v)-[:SPELLED_WITH]->(ka:Kana)
                RETURN v.id AS id,
                       v.romaji AS romaji,
                       v.indonesian_meaning AS indonesian_meaning,
                       v.level AS level,
                       collect(DISTINCT {
                           id: k.id,
                           onyomi: k.onyomi,
                           kunyomi: k.kunyomi,
                           arti: k.arti
                       }) AS kanji,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics,
                       collect(DISTINCT {id: p.id, name: p.name, japanese_term: p.japanese_term}) AS pos,
                       collect(DISTINCT ka.id) AS kana_spelling
                LIMIT 1
            """, word=word)
            rec = result.single()
            return dict(rec) if rec else None

    def get_vocab_by_topic(self, topic_id: str, limit: int = 10) -> list[dict]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:Vocab)-[:BELONGS_TO_TOPIC]->(t:Topic {id: $topic_id})
                RETURN v.id AS id,
                       v.romaji AS romaji,
                       v.indonesian_meaning AS indonesian_meaning
                LIMIT toInteger($limit)
            """, topic_id=topic_id, limit=limit)
            return [dict(r) for r in result]

    def get_related_vocab(self, word: str) -> list[dict]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:Vocab)
                WHERE v.id = $word OR v.romaji = $word
                MATCH (v)-[:BELONGS_TO_TOPIC]->(t:Topic)<-[:BELONGS_TO_TOPIC]-(related:Vocab)
                WHERE related.id <> v.id
                RETURN DISTINCT related.id AS id,
                                related.romaji AS romaji,
                                related.indonesian_meaning AS indonesian_meaning
                LIMIT 8
            """, word=word)
            return [dict(r) for r in result]

    def search_vocab_multi(self, tokens: list[str], limit: int = 10) -> list[dict]:
        """Fuzzy search vocab — dipertahankan untuk kompatibilitas internal."""
        if not tokens:
            return []
        with self.driver.session() as session:
            result = session.run("""
                UNWIND $tokens AS token
                MATCH (v:Vocab)
                WHERE toLower(v.id) CONTAINS toLower(token)
                   OR toLower(v.romaji) CONTAINS toLower(token)
                   OR toLower(v.indonesian_meaning) CONTAINS toLower(token)
                OPTIONAL MATCH (v)-[:BELONGS_TO_TOPIC]->(t:Topic)
                OPTIONAL MATCH (v)-[:WRITTEN_IN]->(k:Kanji)
                RETURN DISTINCT
                       v.id AS id,
                       v.romaji AS romaji,
                       v.indonesian_meaning AS indonesian_meaning,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics,
                       collect(DISTINCT k.id) AS kanji_chars
                LIMIT toInteger($limit)
            """, tokens=tokens, limit=limit)
            return [dict(r) for r in result]

    def search_vocab_rich(self, tokens: list[str], limit: int = 5) -> list[dict]:
        """
        Fuzzy search vocab dengan data lengkap:
        - Kanji detail (onyomi, kunyomi, arti) bukan hanya id
        - POS (kelas kata)
        - Contoh kalimat (max 2)
        Dipakai oleh get_full_context sebagai pengganti search_vocab_multi untuk RAG.
        """
        if not tokens:
            return []
        with self.driver.session() as session:
            result = session.run("""
                UNWIND $tokens AS token
                MATCH (v:Vocab)
                WHERE toLower(v.id) CONTAINS toLower(token)
                   OR toLower(v.romaji) CONTAINS toLower(token)
                   OR toLower(v.indonesian_meaning) CONTAINS toLower(token)
                OPTIONAL MATCH (v)-[:BELONGS_TO_TOPIC]->(t:Topic)
                OPTIONAL MATCH (v)-[:WRITTEN_IN]->(k:Kanji)
                OPTIONAL MATCH (v)-[:HAS_POS]->(p:POS)
                OPTIONAL MATCH (v)<-[:CONTAINS_VOCAB]-(s:Sentence)
                RETURN DISTINCT
                       v.id AS id,
                       v.romaji AS romaji,
                       v.indonesian_meaning AS indonesian_meaning,
                       v.level AS level,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics,
                       collect(DISTINCT {
                           id: k.id,
                           onyomi: k.onyomi,
                           kunyomi: k.kunyomi,
                           arti: k.arti
                       }) AS kanji,
                       collect(DISTINCT p.name) AS pos,
                       collect(DISTINCT {
                           text: s.japanese_text,
                           meaning: s.indonesian_translation
                       })[..2] AS examples
                LIMIT toInteger($limit)
            """, tokens=tokens, limit=limit)
            return [dict(r) for r in result]

    def get_exact_node(self, word: str) -> dict | None:
        """
        Exact-match lookup terhadap semua node materi (Vocab, Grammar, Kanji, Topic)
        berdasarkan id, romaji, atau name — case-insensitive.

        Dipanggil SEBELUM fuzzy search agar query spesifik ("taberu", "は", "食べる")
        langsung mengembalikan data penuh tanpa noise dari fuzzy match.
        """
        with self.driver.session() as session:
            # ── Coba Vocab dulu (paling umum ditanya) ─────────────────────────
            result = session.run("""
                MATCH (v:Vocab)
                WHERE toLower(v.id) = toLower($word)
                   OR toLower(v.romaji) = toLower($word)
                OPTIONAL MATCH (v)-[:WRITTEN_IN]->(k:Kanji)
                OPTIONAL MATCH (v)-[:BELONGS_TO_TOPIC]->(t:Topic)
                OPTIONAL MATCH (v)-[:HAS_POS]->(p:POS)
                OPTIONAL MATCH (v)<-[:CONTAINS_VOCAB]-(s:Sentence)
                RETURN 'Vocab' AS node_type,
                       v.id AS id,
                       v.romaji AS romaji,
                       v.indonesian_meaning AS indonesian_meaning,
                       v.level AS level,
                       collect(DISTINCT {
                           id: k.id, onyomi: k.onyomi,
                           kunyomi: k.kunyomi, arti: k.arti
                       }) AS kanji,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics,
                       collect(DISTINCT p.name) AS pos,
                       collect(DISTINCT {
                           text: s.japanese_text,
                           meaning: s.indonesian_translation
                       })[..2] AS examples
                LIMIT 1
            """, word=word)
            rec = result.single()
            if rec:
                return dict(rec)

            # ── Coba Grammar ───────────────────────────────────────────────────
            result = session.run("""
                MATCH (g:Grammar)
                WHERE toLower(g.id) = toLower($word)
                   OR toLower(g.name) = toLower($word)
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r:Rule)
                OPTIONAL MATCH (g)-[:HAS_COMMON_ERROR]->(e:ErrorPattern)
                OPTIONAL MATCH (g)<-[:APPLIES_GRAMMAR]-(s:Sentence)
                OPTIONAL MATCH (g)-[:BELONGS_TO_TOPIC]->(t:Topic)
                RETURN 'Grammar' AS node_type,
                       g.id AS id,
                       g.name AS name,
                       g.level AS level,
                       collect(DISTINCT r.description) AS rules,
                       collect(DISTINCT e.description) AS common_errors,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics,
                       collect(DISTINCT {
                           text: s.japanese_text,
                           meaning: s.indonesian_translation
                       })[..2] AS examples
                LIMIT 1
            """, word=word)
            rec = result.single()
            if rec:
                return dict(rec)

            # ── Coba Kanji ─────────────────────────────────────────────────────
            result = session.run("""
                MATCH (k:Kanji)
                WHERE k.id = $word
                OPTIONAL MATCH (k)<-[:WRITTEN_IN]-(v:Vocab)<-[:CONTAINS_VOCAB]-(s:Sentence)
                RETURN 'Kanji' AS node_type,
                       k.id AS id,
                       k.onyomi AS onyomi,
                       k.kunyomi AS kunyomi,
                       k.arti AS arti,
                       k.strokes AS strokes,
                       k.level AS level,
                       k.description AS description,
                       collect(DISTINCT {
                           text: s.japanese_text,
                           meaning: s.indonesian_translation
                       })[..2] AS examples
                LIMIT 1
            """, word=word)
            rec = result.single()
            return dict(rec) if rec else None

    def get_random_vocab(self, level: str = "N5", limit: int = 5) -> list[dict]:
        """Ambil sejumlah kosakata secara acak berdasarkan level."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:Vocab {level: $level})
                OPTIONAL MATCH (v)<-[:CONTAINS_VOCAB]-(s:Sentence)
                RETURN v.id AS id,
                       v.romaji AS romaji,
                       v.indonesian_meaning AS indonesian_meaning,
                       collect(DISTINCT {text: s.japanese_text, meaning: s.indonesian_translation})[..2] AS examples
                ORDER BY rand()
                LIMIT toInteger($limit)
            """, level=level, limit=limit)
            return [dict(r) for r in result]

    # ──────────────────────────────────────────────────────────────────────────
    # Grammar Queries
    # ──────────────────────────────────────────────────────────────────────────

    def get_grammar_detail(self, grammar_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Grammar {id: $grammar_id})
                OPTIONAL MATCH (g)-[:USES_VOCAB]->(v:Vocab)
                OPTIONAL MATCH (g)-[:BELONGS_TO_TOPIC]->(t:Topic)
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r:Rule)
                OPTIONAL MATCH (g)-[:HAS_COMMON_ERROR]->(e:ErrorPattern)
                RETURN g.id AS id,
                       g.name AS name,
                       g.level AS level,
                       collect(DISTINCT {id: r.id, description: r.description}) AS rules,
                       collect(DISTINCT {id: e.id, description: e.description}) AS common_errors,
                       collect(DISTINCT {id: v.id, romaji: v.romaji, indonesian_meaning: v.indonesian_meaning}) AS vocab,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics
            """, grammar_id=grammar_id)
            rec = result.single()
            return dict(rec) if rec else None

    def get_all_grammar_patterns(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Grammar)
                RETURN g.id AS id,
                       g.name AS name,
                       g.level AS level
                ORDER BY g.id
            """)
            return [dict(r) for r in result]

    def search_grammar_by_keywords(self, tokens: list[str], limit: int = 5) -> list[dict]:
        """
        Filter grammar berdasarkan keyword pada id, name, atau deskripsi rule-nya.
        Menggunakan WITH clause agar OPTIONAL MATCH tidak di-force menjadi MATCH wajib.
        """
        if not tokens:
            return []
        with self.driver.session() as session:
            result = session.run("""
                UNWIND $tokens AS token
                MATCH (g:Grammar)
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r:Rule)
                WITH g, r, token
                WHERE toLower(g.id) CONTAINS toLower(token)
                   OR toLower(g.name) CONTAINS toLower(token)
                   OR (r IS NOT NULL AND toLower(r.description) CONTAINS toLower(token))
                RETURN DISTINCT
                       g.id AS id,
                       g.name AS name,
                       g.level AS level
                LIMIT toInteger($limit)
            """, tokens=tokens, limit=limit)
            return [dict(r) for r in result]

    def search_grammar_rich(self, tokens: list[str], limit: int = 3) -> list[dict]:
        """
        Fuzzy search grammar dengan data lengkap:
        - Rule descriptions (aturan pemakaian)
        - Common errors (kesalahan umum)
        - Contoh kalimat (max 2)
        Dipakai oleh get_full_context untuk RAG.
        """
        if not tokens:
            return []
        with self.driver.session() as session:
            result = session.run("""
                UNWIND $tokens AS token
                MATCH (g:Grammar)
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r:Rule)
                WITH g, r, token
                WHERE toLower(g.id) CONTAINS toLower(token)
                   OR toLower(g.name) CONTAINS toLower(token)
                   OR (r IS NOT NULL AND toLower(r.description) CONTAINS toLower(token))
                WITH DISTINCT g, token
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r2:Rule)
                OPTIONAL MATCH (g)-[:HAS_COMMON_ERROR]->(e:ErrorPattern)
                OPTIONAL MATCH (g)<-[:APPLIES_GRAMMAR]-(s:Sentence)
                OPTIONAL MATCH (g)-[:BELONGS_TO_TOPIC]->(t:Topic)
                RETURN DISTINCT
                       g.id AS id,
                       g.name AS name,
                       g.level AS level,
                       collect(DISTINCT r2.description) AS rules,
                       collect(DISTINCT e.description) AS common_errors,
                       collect(DISTINCT {id: t.id, name: t.name}) AS topics,
                       collect(DISTINCT {
                           text: s.japanese_text,
                           meaning: s.indonesian_translation
                       })[..2] AS examples
                LIMIT toInteger($limit)
            """, tokens=tokens, limit=limit)
            return [dict(r) for r in result]

    def get_random_grammar(self, level: str = "N5", limit: int = 3) -> list[dict]:
        """Ambil sejumlah tata bahasa secara acak berdasarkan level."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Grammar {level: $level})
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r:Rule)
                OPTIONAL MATCH (g)<-[:APPLIES_GRAMMAR]-(s:Sentence)
                RETURN g.id AS id,
                       g.name AS name,
                       g.level AS level,
                       collect(DISTINCT r.description) AS rules,
                       collect(DISTINCT {text: s.japanese_text, meaning: s.indonesian_translation})[..2] AS examples
                ORDER BY rand()
                LIMIT toInteger($limit)
            """, level=level, limit=limit)
            return [dict(r) for r in result]

    def get_quest_correction_context(self, grammar_id: str) -> dict | None:
        """
        Ambil data lengkap Grammar node untuk koreksi quest:
        - Rules (aturan pemakaian)
        - Common Errors (kesalahan umum siswa)
        - Example Sentences (contoh kalimat)
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Grammar)
                WHERE g.id = $grammar_id OR g.name = $grammar_id
                OPTIONAL MATCH (g)-[:HAS_RULE]->(r:Rule)
                OPTIONAL MATCH (g)-[:HAS_COMMON_ERROR]->(e:ErrorPattern)
                OPTIONAL MATCH (g)<-[:APPLIES_GRAMMAR]-(s:Sentence)
                RETURN g.id AS id,
                       g.name AS name,
                       g.level AS level,
                       collect(DISTINCT r.description) AS rules,
                       collect(DISTINCT e.description) AS common_errors,
                       collect(DISTINCT {
                           text: s.japanese_text,
                           romaji: s.romaji,
                           meaning: s.indonesian_translation
                       })[..3] AS examples
                LIMIT 1
            """, grammar_id=grammar_id)
            rec = result.single()
            return dict(rec) if rec else None

    # ──────────────────────────────────────────────────────────────────────────
    # Kanji Queries
    # ──────────────────────────────────────────────────────────────────────────

    def get_random_kanji(self, level: str = "N5", limit: int = 3) -> list[dict]:
        """
        Ambil sejumlah kanji secara acak berdasarkan level.

        Strategi dual-path untuk contoh kalimat (tanpa tambah latency —
        semua dalam satu Cypher query menggunakan COALESCE pada list):
          Path A (via Vocab)  : Kanji <-[:WRITTEN_IN]- Vocab <-[:CONTAINS_VOCAB]- Sentence
          Path B (direct edge): Kanji <-[:CONTAINS_KANJI]- Sentence
        Path B adalah direct edge yang ditambahkan oleh enrich_kanji_sentences.py
        sebagai fallback ketika jalur via Vocab tidak tersedia.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (k:Kanji {level: $level})
                OPTIONAL MATCH (k)<-[:WRITTEN_IN]-(v:Vocab)<-[:CONTAINS_VOCAB]-(sv:Sentence)
                OPTIONAL MATCH (sk:Sentence)-[:CONTAINS_KANJI]->(k)
                WITH k,
                     collect(DISTINCT {text: sv.japanese_text, meaning: sv.indonesian_translation}) AS via_vocab,
                     collect(DISTINCT {text: sk.japanese_text, meaning: sk.indonesian_translation}) AS via_direct
                RETURN k.id AS id,
                       k.onyomi AS onyomi,
                       k.kunyomi AS kunyomi,
                       k.arti AS arti,
                       k.strokes AS strokes,
                       k.frequency AS frequency,
                       k.description AS description,
                       CASE
                         WHEN size(via_vocab) > 0 THEN via_vocab[..2]
                         ELSE via_direct[..2]
                       END AS examples
                ORDER BY rand()
                LIMIT toInteger($limit)
            """, level=level, limit=limit)
            return [dict(r) for r in result]

    # ──────────────────────────────────────────────────────────────────────────
    # Student Progress
    # ──────────────────────────────────────────────────────────────────────────

    def update_student_progress(self, student_id: str, topic_id: str):
        with self.driver.session() as session:
            session.run("""
                MERGE (s:Student {id: $student_id})
                MATCH (t:Topic {id: $topic_id})
                MERGE (s)-[:LEARNED]->(t)
                SET s.last_topic_id = $topic_id,
                    s.updated_at = timestamp()
            """, student_id=student_id, topic_id=topic_id)

    def update_node_status(self, student_id: str, node_id: str, status: str):
        """
        Update relasi status (LEARNED | MASTERED | STRUGGLING) antara Student dan node materi.

        Strategi satu-session:
          1. MERGE student agar ada.
          2. MATCH node materi (Vocab / Grammar / Kanji).
          3. Hapus semua relasi status lama.
          4. Buat relasi status baru menggunakan CASE → applycount trick
             (tidak bisa pakai parameter sebagai nama relasi di Cypher,
              jadi tetap pakai 3 branch tapi dalam satu WITH yang efisien).
        """
        valid_statuses = {"LEARNED", "MASTERED", "STRUGGLING"}
        if status not in valid_statuses:
            log.warning(f"update_node_status: status '{status}' tidak valid, diabaikan.")
            return

        with self.driver.session() as session:
            # Hapus relasi status lama (semua tipe) dalam satu query
            session.run("""
                MATCH (s:Student {id: $student_id})
                MATCH (n) WHERE n.id = $node_id AND (n:Vocab OR n:Grammar OR n:Kanji)
                OPTIONAL MATCH (s)-[r:LEARNED|MASTERED|STRUGGLING]->(n)
                DELETE r
            """, student_id=student_id, node_id=node_id)

            # Buat relasi baru — 3 branch aman tanpa f-string injection
            if status == "LEARNED":
                session.run("""
                    MERGE (s:Student {id: $student_id})
                    MATCH (n) WHERE n.id = $node_id AND (n:Vocab OR n:Grammar OR n:Kanji)
                    MERGE (s)-[:LEARNED]->(n)
                """, student_id=student_id, node_id=node_id)
            elif status == "MASTERED":
                session.run("""
                    MERGE (s:Student {id: $student_id})
                    MATCH (n) WHERE n.id = $node_id AND (n:Vocab OR n:Grammar OR n:Kanji)
                    MERGE (s)-[:MASTERED]->(n)
                """, student_id=student_id, node_id=node_id)
            elif status == "STRUGGLING":
                session.run("""
                    MERGE (s:Student {id: $student_id})
                    MATCH (n) WHERE n.id = $node_id AND (n:Vocab OR n:Grammar OR n:Kanji)
                    MERGE (s)-[:STRUGGLING]->(n)
                """, student_id=student_id, node_id=node_id)

    def get_student_progress(self, student_id: str) -> dict | None:
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {id: $student_id})
                OPTIONAL MATCH (s)-[:LEARNED]->(t:Topic)
                OPTIONAL MATCH (s)-[:MASTERED]->(m)
                RETURN s.last_topic_id AS last_topic,
                       collect(DISTINCT t.id) AS learned_topics,
                       count(DISTINCT m) AS mastered_count
            """, student_id=student_id)
            rec = result.single()
            return dict(rec) if rec else None

    def get_student_mastery_path(self, student_id: str) -> list[dict]:
        """
        Ambil riwayat relasi mastery Student.
        Catatan: relasi tidak memiliki properti updated_at secara default,
        sehingga ordering berdasarkan label relasi dan id node (deterministic).
        LIMIT dinaikkan ke 500 agar mencakup semua kanji N5 (104) + vocab + grammar.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {id: $student_id})-[r:LEARNED|MASTERED|STRUGGLING]->(n)
                WHERE n:Vocab OR n:Kanji OR n:Grammar OR n:Topic
                RETURN n.id AS id,
                       COALESCE(n.romaji, n.name, n.id) AS label,
                       labels(n)[0] AS type,
                       type(r) AS status
                ORDER BY type(r), n.id
                LIMIT 500
            """, student_id=student_id)
            return [dict(r) for r in result]

    def ensure_and_master_kanji(self, student_id: str, kanji_ids: list[str]):
        """
        MERGE-create node Kanji jika belum ada, lalu tandai sebagai MASTERED.
        Ini penting karena kanji dari Dojo mungkin belum ada di Neo4j
        (belum diingested dari nodes_kanji.csv), sehingga MATCH biasa
        akan gagal diam-diam tanpa error.
        """
        with self.driver.session() as session:
            # Batch: satu query untuk semua kanji dalam set
            session.run("""
                MERGE (s:Student {id: $student_id})
                WITH s
                UNWIND $kanji_ids AS kid
                MERGE (k:Kanji {id: kid})
                ON CREATE SET k.level = 'N5', k.created_at = timestamp()
                OPTIONAL MATCH (s)-[r:LEARNED|MASTERED|STRUGGLING]->(k)
                DELETE r
                WITH s, k
                MERGE (s)-[:MASTERED]->(k)
            """, student_id=student_id, kanji_ids=kanji_ids)
        log.info(f"ensure_and_master_kanji: {len(kanji_ids)} kanji di-MASTERED untuk student '{student_id}'")

    # ──────────────────────────────────────────────────────────────────────────
    # Quest & Daily Mission
    # ──────────────────────────────────────────────────────────────────────────

    def get_quest_materials(self, student_id: str, limit: int = 3) -> list[dict]:
        """Ambil materi (Vocab/Grammar) yang belum MASTERED untuk diujikan."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n) WHERE (n:Vocab OR n:Grammar)
                WHERE NOT EXISTS {
                    MATCH (:Student {id: $student_id})-[:MASTERED]->(n)
                }
                OPTIONAL MATCH (n)<-[:CONTAINS_VOCAB|APPLIES_GRAMMAR]-(s:Sentence)
                RETURN labels(n)[0] AS type,
                       n.id AS id,
                       n.romaji AS romaji,
                       n.indonesian_meaning AS indonesian_meaning,
                       n.name AS name,
                       n.level AS level,
                       collect(DISTINCT {text: s.japanese_text, meaning: s.indonesian_translation})[..1] AS examples
                ORDER BY rand()
                LIMIT toInteger($limit)
            """, student_id=student_id, limit=limit)
            return [dict(r) for r in result]

    def get_daily_missions(self, student_id: str) -> list[dict]:
        """
        Ambil materi yang perlu direview: STRUGGLING diprioritaskan, lalu LEARNED.
        Relasi tidak memiliki properti updated_at, sehingga ordering berdasarkan
        prioritas status saja.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Student {id: $student_id})-[r:STRUGGLING|LEARNED]->(n)
                WHERE n:Vocab OR n:Grammar OR n:Kanji
                WITH n, r,
                     CASE WHEN type(r) = 'STRUGGLING' THEN 100 ELSE 50 END AS priority
                RETURN n.id AS id,
                       COALESCE(n.romaji, n.name, n.id) AS label,
                       labels(n)[0] AS type,
                       type(r) AS status,
                       priority
                ORDER BY priority DESC, n.id ASC
                LIMIT 3
            """, student_id=student_id)
            return [dict(r) for r in result]

    # ──────────────────────────────────────────────────────────────────────────
    # Wiki Note
    # ──────────────────────────────────────────────────────────────────────────

    def add_wiki_note_node(self, student_id: str, content: str, references: list[str] | None = None):
        """
        Membuat node :Note dan menghubungkannya ke Student serta node materi referensi.

        Dua run() dalam satu session agar Note id tersedia untuk MATCH referensi
        tanpa perlu membuka koneksi baru.
        """
        note_id = str(uuid.uuid4())
        with self.driver.session() as session:
            session.run("""
                MERGE (s:Student {id: $student_id})
                CREATE (n:Note {
                    id: $note_id,
                    content: $content,
                    created_at: timestamp()
                })
                MERGE (s)-[:WROTE]->(n)
            """, student_id=student_id, content=content, note_id=note_id)

            if references:
                session.run("""
                    MATCH (n:Note {id: $note_id})
                    MATCH (ref)
                    WHERE ref.id IN $refs OR ref.name IN $refs
                    MERGE (n)-[:REFERENCES]->(ref)
                """, note_id=note_id, refs=references)

    # ──────────────────────────────────────────────────────────────────────────
    # Node Existence Check (dipakai oleh DBOrchestrator)
    # ──────────────────────────────────────────────────────────────────────────

    def node_exists(self, node_id: str) -> bool:
        """
        Cek apakah suatu node materi (Vocab | Grammar | Kanji | Topic) ada di graph.
        Lebih efisien daripada memanggil get_vocab_detail + get_grammar_detail + get_topic_by_name
        secara berurutan.
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.id = $node_id
                  AND (n:Vocab OR n:Grammar OR n:Kanji OR n:Topic)
                RETURN count(n) > 0 AS exists
                LIMIT 1
            """, node_id=node_id)
            rec = result.single()
            return bool(rec["exists"]) if rec else False

    # ──────────────────────────────────────────────────────────────────────────
    # Context Helper
    # ──────────────────────────────────────────────────────────────────────────

    def _find_topic_from_tokens(self, tokens: list[str]) -> dict | None:
        for token in tokens:
            t = self.get_topic_by_name(token)
            if t:
                return t
        return None

    async def get_full_context(self, tokens: list[str], student_id: str) -> dict:
        """
        Pipeline multi-tahap untuk mengambil konteks Neo4J yang akurat:

        Tahap 1 — Exact Match (paralel per token):
          Coba cocokkan setiap token secara tepat ke node Vocab/Grammar/Kanji.
          Jika ada yang cocok, gunakan data penuh node tersebut.

        Tahap 2 — Rich Fuzzy Search (paralel):
          search_vocab_rich  : vocab + kanji detail + POS + contoh kalimat
          search_grammar_rich: grammar + rules + common errors + contoh kalimat
          topic search       : cari topik yang relevan dari token
          recommendation     : topik berikutnya yang belum dipelajari

        Hasil kedua tahap digabung dengan deduplication berdasarkan id.
        """
        # ── Tahap 1: Exact match setiap token secara paralel ──────────────────
        exact_futures = [asyncio.to_thread(self.get_exact_node, t) for t in tokens[:5]]
        exact_results_raw = await asyncio.gather(*exact_futures, return_exceptions=True)

        exact_vocab:   list[dict] = []
        exact_grammar: list[dict] = []
        exact_kanji:   list[dict] = []
        seen_exact: set = set()
        for r in exact_results_raw:
            if not r or isinstance(r, Exception):
                continue
            nid = r.get("id")
            if not nid or nid in seen_exact:
                continue
            seen_exact.add(nid)
            nt = r.get("node_type", "")
            if nt == "Vocab":
                exact_vocab.append(r)
            elif nt == "Grammar":
                exact_grammar.append(r)
            elif nt == "Kanji":
                exact_kanji.append(r)

        # ── Tahap 2: Rich fuzzy search (paralel) ──────────────────────────────
        vocab_future          = asyncio.to_thread(self.search_vocab_rich,    tokens, 5)
        grammar_future        = asyncio.to_thread(self.search_grammar_rich,  tokens, 3)
        topic_future          = asyncio.to_thread(self._find_topic_from_tokens, tokens)
        recommendation_future = asyncio.to_thread(self.get_recommended_topic, student_id)

        fuzzy_vocab, fuzzy_grammar, topic_hit, recommendation = await asyncio.gather(
            vocab_future, grammar_future, topic_future, recommendation_future
        )

        # ── Merge & deduplicate (exact match lebih diprioritaskan) ─────────────
        def _merge(exact: list, fuzzy: list) -> list:
            seen: set = set(e["id"] for e in exact)
            merged = list(exact)
            for item in fuzzy:
                if item.get("id") not in seen:
                    seen.add(item["id"])
                    merged.append(item)
            return merged

        return {
            "vocab":          _merge(exact_vocab, fuzzy_vocab),
            "grammar":        _merge(exact_grammar, fuzzy_grammar),
            "kanji":          exact_kanji,
            "topic":          topic_hit,
            "recommendation": recommendation,
        }