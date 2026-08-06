from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "A.L.I.S.A. (Adaptive Language Intelligent Symbolic Assistant)"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = ""
    NEO4J_PASSWORD: str = ""

    # Local LLM (Llama.cpp)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "alisa-tutor:latest"
    UNSLOTH_MODEL_PATH: str = "models/Qwen3-4B-Instruct-2507-Q4_K_M.gguf"
    UNSLOTH_MAX_SEQ_LENGTH: int = 4096

    # HuggingFace Cloud
    HF_TOKEN: str = ""
    HF_MODEL_REPO: str = "Qwen/Qwen3-4B-Instruct-2507"

    # Whisper STT — path ke model lokal.
    # Download sekali dengan: python backend/utils/download_whisper.py
    WHISPER_MODEL_PATH: str = "models/kotoba-whisper-v1.0-faster"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
