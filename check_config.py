import sys
sys.path.insert(0, "backend")

from core.config import settings

lines = [
    f"OLLAMA_MODEL    = {repr(settings.OLLAMA_MODEL)}",
    f"OLLAMA_BASE_URL = {repr(settings.OLLAMA_BASE_URL)}",
    f"NEO4J_URI       = {repr(settings.NEO4J_URI)}",
    f"NEO4J_USERNAME  = {repr(settings.NEO4J_USERNAME)}",
    f"NEO4J_PASSWORD  = {'(set, len=' + str(len(settings.NEO4J_PASSWORD)) + ')' if settings.NEO4J_PASSWORD else '(EMPTY!)'}",
]

for line in lines:
    print(line)
