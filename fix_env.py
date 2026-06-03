env_content = """# === NEO4J CONFIG ===
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tvjp08052004

# === OLLAMA (LOCAL LLM) CONFIG ===
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=alisa-tutor:latest

# === APP CONFIG ===
PROJECT_NAME=TVJP - Japanese Virtual Tutor
"""

# Tulis dengan encoding UTF-8 tanpa BOM
with open(r"C:\Users\satya\OneDrive\Desktop\TVJP\.env", "w", encoding="utf-8", newline="\n") as f:
    f.write(env_content)

print("OK: .env ditulis ulang tanpa BOM")

# Verifikasi
with open(r"C:\Users\satya\OneDrive\Desktop\TVJP\.env", "rb") as f:
    first3 = f.read(3)
print("First 3 bytes:", first3.hex(), "(harus bukan 'efbbbf')")
