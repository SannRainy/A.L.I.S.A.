import csv
import os
import sys
from neo4j import GraphDatabase

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class N5GraphIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_csv(self, filename):
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            print(f"Warning: {filename} not found at {path}")
            return []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def ingest_data(self):
        with self.driver.session() as session:
            print("Setting up constraints...")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vocab) REQUIRE v.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (k:Kanji) REQUIRE k.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:Grammar) REQUIRE g.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:POS) REQUIRE p.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rule) REQUIRE r.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sentence) REQUIRE s.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (ka:Kana) REQUIRE ka.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:ErrorPattern) REQUIRE e.id IS UNIQUE")

            # Nodes
            self._ingest_nodes(session, "nodes_vocabulary.csv", "Vocab", "vocab_id", {
                "romaji": "row.romaji",
                "indonesian_meaning": "row.indonesian_meaning",
                "level": "row.level"
            })
            
            # Special case for Kanji with new fields
            kanji_data = self.load_csv("nodes_kanji.csv")
            if kanji_data:
                print(f"Ingesting {len(kanji_data)} Kanji nodes...")
                session.run("""
                    UNWIND $data AS row
                    MERGE (k:Kanji {id: row.kanji_id})
                    SET k.onyomi = row.onyomi,
                        k.kunyomi = row.kunyomi,
                        k.arti = row.arti,
                        k.level = row.level,
                        k.strokes = toInteger(row.strokes),
                        k.frequency = toInteger(row.frequency),
                        k.description = row.description
                """, data=kanji_data)

            self._ingest_nodes(session, "nodes_grammar.csv", "Grammar", "grammar_id", {
                "name": "row.name",
                "level": "row.level"
            })

            self._ingest_nodes(session, "nodes_topic.csv", "Topic", "topic_id", {
                "name": "row.name",
                "category": "row.category"
            })

            self._ingest_nodes(session, "nodes_pos.csv", "POS", "pos_id", {
                "name": "row.name",
                "japanese_term": "row.japanese_term"
            })

            self._ingest_nodes(session, "nodes_rule.csv", "Rule", "rule_id", {
                "description": "row.description",
                "rule_type": "row.rule_type"
            })

            self._ingest_nodes(session, "nodes_sentence.csv", "Sentence", "sentence_id", {
                "japanese_text": "row.japanese_text",
                "romaji": "row.romaji",
                "indonesian_translation": "row.indonesian_translation",
                "level": "row.level"
            })

            self._ingest_nodes(session, "nodes_kana.csv", "Kana", "kana_id", {
                "character": "row.character",
                "type": "row.type",
                "romaji": "row.romaji"
            })

            self._ingest_nodes(session, "nodes_error_pattern.csv", "ErrorPattern", "error_id", {
                "description": "row.description",
                "level": "row.level"
            })

            # Edges
            self._ingest_edges(session, "edges_grammar_rule.csv", "Grammar", "grammar_id", "Rule", "rule_id", "HAS_RULE")
            self._ingest_edges(session, "edges_grammar_topic.csv", "Grammar", "grammar_id", "Topic", "topic_id", "BELONGS_TO_TOPIC")
            self._ingest_edges(session, "edges_grammar_vocab.csv", "Grammar", "grammar_id", "Vocab", "vocab_id", "USES_VOCAB")
            self._ingest_edges(session, "edges_vocab_kanji.csv", "Vocab", "vocab_id", "Kanji", "kanji_id", "WRITTEN_IN")
            self._ingest_edges(session, "edges_vocab_pos.csv", "Vocab", "vocab_id", "POS", "pos_id", "HAS_POS")
            self._ingest_edges(session, "edges_vocab_topic.csv", "Vocab", "vocab_id", "Topic", "topic_id", "BELONGS_TO_TOPIC")
            self._ingest_edges(session, "edges_vocal_rule.csv", "Vocab", "vocab_id", "Rule", "rule_id", "HAS_PHONETIC_RULE")
            self._ingest_edges(session, "edges_sentence_vocab.csv", "Sentence", "sentence_id", "Vocab", "vocab_id", "CONTAINS_VOCAB")
            self._ingest_edges(session, "edges_sentence_grammar.csv", "Sentence", "sentence_id", "Grammar", "grammar_id", "APPLIES_GRAMMAR")
            self._ingest_edges(session, "edges_vocab_kana.csv", "Vocab", "vocab_id", "Kana", "kana_id", "SPELLED_WITH")
            self._ingest_edges(session, "edges_grammar_error.csv", "Grammar", "grammar_id", "ErrorPattern", "error_id", "HAS_COMMON_ERROR")

            # Special Edge: Vocab Relation
            rel_data = self.load_csv("edges_vocab_relation.csv")
            if rel_data:
                print("Ingesting Vocab relations...")
                session.run("""
                    UNWIND $data AS row
                    WITH row WHERE row.relationship_type = 'ANTONYM_OF'
                    MATCH (v1:Vocab {id: row.vocab_id_1})
                    MATCH (v2:Vocab {id: row.vocab_id_2})
                    MERGE (v1)-[:ANTONYM_OF]->(v2)
                """, data=rel_data)
                session.run("""
                    UNWIND $data AS row
                    WITH row WHERE row.relationship_type = 'SYNONYM_OF'
                    MATCH (v1:Vocab {id: row.vocab_id_1})
                    MATCH (v2:Vocab {id: row.vocab_id_2})
                    MERGE (v1)-[:SYNONYM_OF]->(v2)
                """, data=rel_data)

            print("Knowledge Graph N5 berhasil di-ingest (FULL GRAPH via Python-side loading)")

    def _ingest_nodes(self, session, filename, label, id_col, attr_map):
        data = self.load_csv(filename)
        if not data: return
        print(f"Ingesting {len(data)} {label} nodes...")
        
        set_clauses = [f"n.{k} = row.{k}" for k in attr_map.keys()]
        query = f"""
            UNWIND $data AS row
            MERGE (n:{label} {{id: row.{id_col}}})
            SET {', '.join(set_clauses)}
        """
        session.run(query, data=data)

    def _ingest_edges(self, session, filename, from_label, from_col, to_label, to_col, rel_type):
        data = self.load_csv(filename)
        if not data: return
        print(f"Ingesting {len(data)} edges: {from_label}-[:{rel_type}]->{to_label}...")
        
        query = f"""
            UNWIND $data AS row
            MATCH (a:{from_label} {{id: row.{from_col}}})
            MATCH (b:{to_label} {{id: row.{to_col}}})
            MERGE (a)-[:{rel_type}]->(b)
        """
        session.run(query, data=data)

def run_ingestion():
    """
    FIX: Credentials sekarang dibaca dari .env (melalui core.config.settings)
    dengan fallback ke hardcoded values jika modul tidak tersedia
    (misal: dijalankan standalone tanpa venv backend).
    """
    try:
        # Tambahkan parent dir ke path agar bisa import core.config
        backend_dir = os.path.dirname(BASE_DIR)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from core.config import settings
        uri = settings.NEO4J_URI
        user = settings.NEO4J_USERNAME
        password = settings.NEO4J_PASSWORD
        print(f"📋 Menggunakan kredensial dari .env (URI: {uri})")
    except Exception:
        # Fallback jika dijalankan standalone
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "tvjp08052004"
        print(f"⚠️ Tidak bisa import settings, menggunakan fallback credentials (URI: {uri})")

    ingestor = N5GraphIngestor(uri, user, password)
    ingestor.ingest_data()
    ingestor.close()

if __name__ == "__main__":
    run_ingestion()