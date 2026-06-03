"""Quick test: can we reach Neo4j Aura?"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from neo4j import GraphDatabase
from core.config import settings

# 1. Cek apa yang dibaca pydantic-settings
loaded_pw = settings.NEO4J_PASSWORD
print(f"URI      : {settings.NEO4J_URI}")
print(f"USERNAME : {settings.NEO4J_USERNAME}")
print(f"PASSWORD (loaded)  : [{loaded_pw}]")
print(f"PASSWORD (len)     : {len(loaded_pw)}")

# 2. Bandingkan raw dari file
with open(".env", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("NEO4J_PASSWORD"):
            raw_pw = line.strip().split("=", 1)[1]
            print(f"PASSWORD (raw .env): [{raw_pw}]")
            print(f"PASSWORD (raw len) : {len(raw_pw)}")
            print(f"MATCH: {loaded_pw == raw_pw}")
            break

# 3. Test koneksi dengan password dari settings
print("\n--- Test 1: Koneksi via settings ---")
try:
    driver = GraphDatabase.driver(
        settings.NEO4J_URI,
        auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
    )
    driver.verify_connectivity()
    print("SUCCESS!")
    driver.close()
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

# 4. Test koneksi dengan password quoted di .env
print("\n--- Test 2: Koneksi via hardcoded raw password ---")
try:
    driver2 = GraphDatabase.driver(
        "neo4j+s://4e15c291.databases.neo4j.io",
        auth=("neo4j", raw_pw),
    )
    driver2.verify_connectivity()
    print("SUCCESS!")
    driver2.close()
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")
