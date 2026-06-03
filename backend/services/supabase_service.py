import logging
from typing import List, Dict, Any, Optional
from core.supabase_client import supabase

logger = logging.getLogger(__name__)
 
XP_ACTION_MAP = {
    "INTERACTION_BASIC": 5,
    "QUIZ_SUCCESS_N5": 15,
    "VOCAB_MASTERED": 10,
    "GRAMMAR_MASTERED": 20,
    "TOPIC_COMPLETED": 50,
    "DAILY_STREAK": 25
}

class SupabaseService:
    @staticmethod
    async def save_chat_log(user_id: str, role: str, content: str, mode: str = "discovery"):
        """Simpan chat log ke Supabase."""
        try:
            # Ensure profile exists due to Foreign Key constraint
            await SupabaseService.ensure_profile_exists(user_id)
            
            data = {
                "user_id": user_id,
                "role": role,
                "content": content,
                "mode": mode
            }
            # Menggunakan threading atau async wrapper jika client sync, 
            # tapi postgrest-py biasanya mendukung .execute()
            supabase.table("chat_logs").insert(data).execute()
        except Exception as e:
            logger.error(f"Failed to save chat log: {e}")

    @staticmethod
    async def get_chat_history(user_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Ambil riwayat chat terbaru untuk context LLM."""
        try:
            response = supabase.table("chat_logs")\
                .select("role, content")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            # Balik urutan agar kronologis (history[0] adalah tertua)
            history = response.data[::-1]
            return history
        except Exception as e:
            logger.error(f"Failed to fetch chat history: {e}")
            return []

    @staticmethod
    async def ensure_profile_exists(
        user_id: str,
        email: str = None,
        full_name: str = "User Baru",
        age: int = None,
        gender: str = "prefer_not_to_say",
        country: str = "Indonesia",
        study_purpose: str = None,
        japanese_level: str = "beginner",
    ):
        """Pastikan profile user ada di tabel profiles (untuk FK constraint). Sekarang dengan demographics."""
        try:
            profile = await SupabaseService.get_user_profile(user_id)
            if not profile:
                logger.info(f"Creating missing profile for user {user_id}")
                data = {
                    "id": user_id,
                    "username": email.split("@")[0] if email else f"user_{user_id[:8]}",
                    "email": email,
                    "full_name": full_name or "User Baru",
                    "age": age,
                    "gender": gender or "prefer_not_to_say",
                    "country": country or "Indonesia",
                    "study_purpose": study_purpose,
                    "japanese_level": japanese_level or "beginner",
                    "role": "student",
                    "xp": 0,
                    "level": 1,
                }
                supabase.table("profiles").insert(data).execute()
        except Exception as e:
            logger.error(f"Error in ensure_profile_exists: {e}")

    @staticmethod
    async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Ambil data profile user (XP, Level, etc)."""
        try:
            # Gunakan .execute() tanpa .single() untuk menghindari error 406 jika 0 rows
            response = supabase.table("profiles").select("*").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Failed to fetch user profile: {e}")
            return None

    @staticmethod
    async def update_user_stats(user_id: str, action_type: str, custom_xp: Optional[int] = None):
        """Update XP dan Level user berdasarkan tipe aksi (Internal Mapping atau Custom XP)."""
        try:
            xp_gain = custom_xp if custom_xp is not None else XP_ACTION_MAP.get(action_type, 5)
            profile = await SupabaseService.get_user_profile(user_id)
            if not profile:
                return

            new_xp = (profile.get("xp") or 0) + xp_gain
            new_level = (new_xp // 100) + 1 

            supabase.table("profiles").update({
                "xp": new_xp,
                "level": new_level
            }).eq("id", user_id).execute()
            
            logger.info(f"User {user_id} gained {xp_gain} XP from {action_type}")
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")

    @staticmethod
    async def save_wiki_note(user_id: str, content: str):
        """Simpan catatan wiki (Second Brain) ke Supabase."""
        try:
            data = {"user_id": user_id, "content": content}
            supabase.table("wiki_notes").insert(data).execute()
        except Exception as e:
            logger.error(f"Failed to save wiki note: {e}")

    @staticmethod
    async def add_achievement(user_id: str, achievement_name: str, description: str = ""):
        """Tambahkan achievement baru untuk user."""
        try:
            data = {
                "user_id": user_id, 
                "name": achievement_name, 
                "description": description
            }
            supabase.table("achievements").insert(data).execute()
        except Exception as e:
            logger.error(f"Failed to add achievement: {e}")

    @staticmethod
    async def update_quest_score(user_id: str, score: int, level_id: str):
        """
        Update score quest dan tambahkan ke completed_levels.
        """
        try:
            # 1. Update XP (Gunakan skor langsung sebagai XP gain agar lebih memuaskan)
            await SupabaseService.update_user_stats(user_id, "QUIZ_SUCCESS_N5", custom_xp=score)
            
            # 2. Log quest completion ke tabel user_quests
            data = {"user_id": user_id, "level_id": level_id, "score": score}
            supabase.table("user_quests").insert(data).execute()
            
            logger.info(f"Quest {level_id} completed by {user_id} with score {score}")
        except Exception as e:
            logger.error(f"Failed to update quest score: {e}")

    @staticmethod
    async def get_user_achievements(user_id: str) -> List[Dict[str, Any]]:
        """Ambil daftar quest yang sudah diselesaikan user."""
        try:
            response = supabase.table("user_quests")\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch user achievements: {e}")
            return []

    # ── Admin Methods ──────────────────────────────────────────────────
    @staticmethod
    async def get_all_profiles() -> List[Dict[str, Any]]:
        """Ambil SEMUA profiles (untuk admin dashboard)."""
        try:
            response = supabase.table("profiles")\
                .select("*")\
                .order("created_at", desc=False)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to fetch all profiles: {e}")
            return []

    @staticmethod
    async def get_all_quest_scores() -> List[Dict[str, Any]]:
        """Ambil SEMUA quest scores (untuk admin analytics)."""
        try:
            response = supabase.table("user_quests")\
                .select("*")\
                .order("created_at", desc=False)\
                .execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Failed to fetch all quest scores: {e}")
            return []

    @staticmethod
    async def get_chat_stats() -> Dict[str, Any]:
        """Ambil statistik chat_logs agregat."""
        try:
            response = supabase.table("chat_logs")\
                .select("user_id, mode, created_at")\
                .execute()
            logs = response.data or []
            total = len(logs)
            users = set(l["user_id"] for l in logs if l.get("user_id"))
            modes = {}
            for l in logs:
                m = l.get("mode", "discovery")
                modes[m] = modes.get(m, 0) + 1
            return {
                "total_messages": total,
                "active_users": len(users),
                "by_mode": modes,
            }
        except Exception as e:
            logger.error(f"Failed to fetch chat stats: {e}")
            return {"total_messages": 0, "active_users": 0, "by_mode": {}}

    @staticmethod
    async def update_profile_role(user_id: str, role: str):
        """Update role user (admin/student)."""
        try:
            supabase.table("profiles").update({"role": role}).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Failed to update role: {e}")

    @staticmethod
    async def update_user_profile(user_id: str, payload: dict) -> bool:
        """Update data profil user di Supabase."""
        try:
            supabase.table("profiles").update(payload).eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise e

