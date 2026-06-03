"""verify_enrichment.py - Cek hasil enrichment di Neo4j"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from neo4j import GraphDatabase

driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD))
driver.verify_connectivity()

with driver.session() as session:
    r1 = session.run("MATCH (s:Sentence) RETURN count(s) AS total").single()
    r2 = session.run("MATCH ()-[:CONTAINS_KANJI]->() RETURN count(*) AS total").single()
    r3 = session.run("""
        MATCH (k:Kanji {level: 'N5'})
        OPTIONAL MATCH (s1:Sentence)-[:CONTAINS_KANJI]->(k)
        OPTIONAL MATCH (k)<-[:WRITTEN_IN]-(v:Vocab)<-[:CONTAINS_VOCAB]-(s2:Sentence)
        WITH k, count(DISTINCT s1) + count(DISTINCT s2) AS total_examples
        WHERE total_examples = 0
        RETURN count(k) AS kanji_tanpa_contoh
    """).single()

    print(f"Total Sentence node     : {r1['total']}")
    print(f"Total CONTAINS_KANJI    : {r2['total']}")
    print(f"Kanji N5 tanpa contoh   : {r3['kanji_tanpa_contoh']} dari 103")

    # List kanji yang masih kosong (jika ada)
    if r3['kanji_tanpa_contoh'] > 0:
        missing = session.run("""
            MATCH (k:Kanji {level: 'N5'})
            OPTIONAL MATCH (s1:Sentence)-[:CONTAINS_KANJI]->(k)
            OPTIONAL MATCH (k)<-[:WRITTEN_IN]-(v:Vocab)<-[:CONTAINS_VOCAB]-(s2:Sentence)
            WITH k, count(DISTINCT s1) + count(DISTINCT s2) AS total_examples
            WHERE total_examples = 0
            RETURN k.id AS kanji, k.arti AS arti
            ORDER BY k.id
        """)
        print("\nKanji yang masih belum punya contoh:")
        for r in missing:
            print(f"  - {r['kanji']} ({r['arti']})")

driver.close()
print("\n[DONE] Verifikasi selesai.")
