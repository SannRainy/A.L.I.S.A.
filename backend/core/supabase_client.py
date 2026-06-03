import logging
from typing import Any
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)

class MockSupabaseClient:
    """Fallback client when Supabase credentials are not yet configured."""
    def __init__(self):
        logger.warning("Supabase URL or Key missing. Using MockSupabaseClient.")
        self.auth = self

    def sign_up(self, credentials: dict) -> Any:
        logger.info(f"[MockAuth] User signed up: {credentials.get('email')}")
        class MockUser:
            id = "mock-user-uuid-1234"
            email = credentials.get("email")
        class MockSignResponse:
            user = MockUser()
        return MockSignResponse()

    def table(self, table_name: str) -> Any:
        return self

    def insert(self, data: dict) -> Any:
        return self

    def select(self, fields: str) -> Any:
        return self

    def eq(self, column: str, value: Any) -> Any:
        return self
        
    def execute(self) -> Any:
        # Mock response format expected from Supabase
        logger.info("[MockSupabase] Executed query.")
        class MockResponse:
            data = []
            count = 0
        return MockResponse()

def get_supabase_client() -> Client | MockSupabaseClient:
    url = settings.SUPABASE_URL.strip()
    key = settings.SUPABASE_KEY.strip()
    
    # DEBUG: Cek apakah env terbaca (Gunakan logger agar pasti muncul)
    logger.info(f"DEBUG: Supabase URL from config: '{url}'")
    
    if url and key:
        try:
            return create_client(url, key)
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            return MockSupabaseClient()
    else:
        return MockSupabaseClient()

supabase = get_supabase_client()
