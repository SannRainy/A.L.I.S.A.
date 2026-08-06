import os
import sys
import time
from neo4j import GraphDatabase

# Make sure we can import core.config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from core.config import settings

def migrate_aura_to_local(aura_uri: str, aura_user: str, aura_pass: str):
    local_uri = settings.NEO4J_URI
    local_user = settings.NEO4J_USERNAME
    local_pass = settings.NEO4J_PASSWORD

    print("==================================================")
    print(" NEO4J MIGRATION TOOL: AURA -> LOCAL")
    print("==================================================")
    print(f" Source (Aura) : {aura_uri} (user: {aura_user})")
    print(f" Target (Local): {local_uri} (user: {local_user})")
    print("--------------------------------------------------")

    print("[1/4] Connecting to Neo4j Aura...")
    aura_driver = GraphDatabase.driver(aura_uri, auth=(aura_user, aura_pass))
    aura_driver.verify_connectivity()
    print("[OK] Connected to Aura!")

    print("[2/4] Connecting to Local Neo4j...")
    local_driver = GraphDatabase.driver(local_uri, auth=(local_user, local_pass))
    local_driver.verify_connectivity()
    print("[OK] Connected to Local Neo4j!")

    start_time = time.time()

    with aura_driver.session() as source_session, local_driver.session() as target_session:
        # 1. Transfer Constraints & Indexes
        print("\nCreating Constraints on Local Neo4j...")
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vocab) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (k:Kanji) REQUIRE k.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Grammar) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:POS) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rule) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sentence) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ka:Kana) REQUIRE ka.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:ErrorPattern) REQUIRE e.id IS UNIQUE",
        ]
        for c in constraints:
            target_session.run(c)
        print("[OK] Constraints created.")

        # 2. Extract & Transfer Nodes
        print("\nFetching all Nodes from Aura...")
        nodes_result = source_session.run("MATCH (n) RETURN labels(n) AS labels, properties(n) AS props")
        nodes_data = [record.data() for record in nodes_result]
        print(f"Found {len(nodes_data)} nodes in Aura.")

        print("Ingesting Nodes to Local...")
        batch_size = 500
        for i in range(0, len(nodes_data), batch_size):
            batch = nodes_data[i:i + batch_size]
            for item in batch:
                labels = ":".join(item["labels"])
                props = item["props"]
                if not labels:
                    continue
                node_id = props.get("id")
                if node_id:
                    cypher = f"MERGE (n:{labels} {{id: $node_id}}) SET n = $props"
                    target_session.run(cypher, node_id=node_id, props=props)
                else:
                    cypher = f"CREATE (n:{labels}) SET n = $props"
                    target_session.run(cypher, props=props)

        print(f"[OK] Transferred {len(nodes_data)} Nodes.")

        # 3. Extract & Transfer Relationships
        print("\nFetching all Relationships from Aura...")
        rel_result = source_session.run("""
            MATCH (a)-[r]->(b)
            RETURN labels(a) AS a_labels, a.id AS a_id,
                   type(r) AS rel_type, properties(r) AS rel_props,
                   labels(b) AS b_labels, b.id AS b_id
        """)
        rels_data = [record.data() for record in rel_result]
        print(f"Found {len(rels_data)} relationships in Aura.")

        print("Ingesting Relationships to Local...")
        for r in rels_data:
            a_label = r["a_labels"][0] if r["a_labels"] else ""
            b_label = r["b_labels"][0] if r["b_labels"] else ""
            rel_type = r["rel_type"]
            a_id = r["a_id"]
            b_id = r["b_id"]

            if a_label and b_label and a_id and b_id:
                cypher = f"""
                    MATCH (a:{a_label} {{id: $a_id}})
                    MATCH (b:{b_label} {{id: $b_id}})
                    MERGE (a)-[r:{rel_type}]->(b)
                    SET r += $rel_props
                """
                target_session.run(cypher, a_id=a_id, b_id=b_id, rel_props=r["rel_props"])

        print(f"[OK] Transferred {len(rels_data)} Relationships.")

    aura_driver.close()
    local_driver.close()
    elapsed = round(time.time() - start_time, 2)
    print("\n==================================================")
    print(f" MIGRATION COMPLETE in {elapsed}s!")
    print("==================================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate Neo4j Aura to Local Neo4j")
    parser.add_argument("--aura-uri", required=True, help="Neo4j Aura URI (e.g. neo4j+s://xxxx.databases.neo4j.io)")
    parser.add_argument("--aura-user", default="neo4j", help="Neo4j Aura Username")
    parser.add_argument("--aura-password", required=True, help="Neo4j Aura Password")

    args = parser.parse_args()
    migrate_aura_to_local(args.aura_uri, args.aura_user, args.aura_password)
