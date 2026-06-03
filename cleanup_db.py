from neo4j import GraphDatabase
import os

uri = "bolt://localhost:7687"
user = "neo4j"
password = "tvjp08052004"

driver = GraphDatabase.driver(uri, auth=(user, password))
with driver.session() as session:
    print("🧹 Cleaning up database... Deleting all nodes and relationships.")
    session.run("MATCH (n) DETACH DELETE n")
    print("✨ Database is now clean!")
driver.close()
