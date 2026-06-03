with open(r"C:\Users\satya\OneDrive\Desktop\TVJP\.env", "rb") as f:
    raw = f.read()

print("First 20 bytes (hex):", raw[:20].hex())
print("Content:")
print(raw.decode("utf-8", errors="replace"))
