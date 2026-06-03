import sys
sys.path.insert(0, "backend")

# Cek path yang digunakan
from pathlib import Path
env_path = Path("backend/core/config.py").resolve().parent.parent / ".env"
print("Expected .env path:", env_path)
print("File exists:", env_path.exists())

# Baca raw
with open(env_path, "rb") as f:
    raw = f.read()
print("File size:", len(raw), "bytes")
print("First 50 bytes hex:", raw[:50].hex())
print()
print("Content (lossy ascii):")
for line in raw.decode("utf-8").splitlines():
    print("  |", line)

print()
# Cek dotenv langsung
from dotenv import dotenv_values
vals = dotenv_values(env_path)
print("dotenv_values result:")
for k, v in vals.items():
    if "PASSWORD" in k or "PASS" in k:
        print(f"  {k} = (set, len={len(v)})")
    else:
        print(f"  {k} = {v!r}")
