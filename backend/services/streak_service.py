"""
Streak Service — Daily study tracking & streak management
"""
import logging
from datetime import date, timedelta, datetime, timezone
from typing import Optional
from core.supabase_client import supabase

logger = logging.getLogger(__name__)


class StreakService:
    """Manage daily study streaks and goals."""

    @staticmethod
    async def log_activity(
        user_id: str,
        study_minutes: int = 0,
        items_reviewed: int = 0,
        quests_completed: int = 0,
        xp_earned: int = 0,
    ) -> dict:
        """Log or update today's study activity."""
        try:
            today = date.today().isoformat()

            # Check if entry exists for today
            resp = supabase.table("study_streaks") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("study_date", today) \
                .execute()

            if resp.data and len(resp.data) > 0:
                existing = resp.data[0]
                supabase.table("study_streaks").update({
                    "study_minutes": existing.get("study_minutes", 0) + study_minutes,
                    "items_reviewed": existing.get("items_reviewed", 0) + items_reviewed,
                    "quests_completed": existing.get("quests_completed", 0) + quests_completed,
                    "xp_earned": existing.get("xp_earned", 0) + xp_earned,
                }).eq("id", existing["id"]).execute()
            else:
                supabase.table("study_streaks").insert({
                    "user_id": user_id,
                    "study_date": today,
                    "study_minutes": study_minutes,
                    "items_reviewed": items_reviewed,
                    "quests_completed": quests_completed,
                    "xp_earned": xp_earned,
                }).execute()

            # Update streak count
            streak_info = await StreakService.update_streak(user_id)
            return streak_info
        except Exception as e:
            logger.error(f"StreakService log_activity error: {e}")
            return {"streak_days": 0}

    @staticmethod
    async def update_streak(user_id: str) -> dict:
        """Calculate and update current streak from study_streaks table."""
        try:
            resp = supabase.table("study_streaks") \
                .select("study_date") \
                .eq("user_id", user_id) \
                .order("study_date", desc=True) \
                .limit(365) \
                .execute()

            dates = sorted(
                [row["study_date"] for row in (resp.data or [])],
                reverse=True,
            )

            if not dates:
                return {"streak_days": 0, "longest_streak": 0}

            # Calculate current streak
            streak = 0
            today = date.today()
            check_date = today

            for d in dates:
                study_date = date.fromisoformat(d) if isinstance(d, str) else d
                if study_date == check_date:
                    streak += 1
                    check_date -= timedelta(days=1)
                elif study_date == check_date - timedelta(days=1):
                    # Allow one-day gap tolerance (yesterday counts too)
                    check_date = study_date
                    streak += 1
                    check_date -= timedelta(days=1)
                else:
                    break

            # Get existing longest streak
            profile_resp = supabase.table("profiles") \
                .select("longest_streak") \
                .eq("id", user_id) \
                .execute()
            longest = (profile_resp.data[0].get("longest_streak", 0)
                      if profile_resp.data else 0)
            longest = max(longest, streak)

            # Update profile
            supabase.table("profiles").update({
                "streak_days": streak,
                "last_active_date": today.isoformat(),
                "longest_streak": longest,
            }).eq("id", user_id).execute()

            return {
                "streak_days": streak,
                "longest_streak": longest,
                "last_active_date": today.isoformat(),
            }
        except Exception as e:
            logger.error(f"StreakService update_streak error: {e}")
            return {"streak_days": 0, "longest_streak": 0}

    @staticmethod
    async def get_streak_calendar(user_id: str, days: int = 90) -> list[dict]:
        """Get study activity for calendar heatmap (GitHub-style)."""
        try:
            start_date = (date.today() - timedelta(days=days)).isoformat()
            resp = supabase.table("study_streaks") \
                .select("study_date, study_minutes, items_reviewed, xp_earned") \
                .eq("user_id", user_id) \
                .gte("study_date", start_date) \
                .order("study_date", desc=False) \
                .execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"StreakService get_calendar error: {e}")
            return []

    @staticmethod
    async def get_daily_goals(user_id: str) -> dict:
        """Get user's daily goals configuration."""
        try:
            resp = supabase.table("daily_goals") \
                .select("*") \
                .eq("user_id", user_id) \
                .execute()

            if resp.data and len(resp.data) > 0:
                return resp.data[0]

            # Create default goals
            defaults = {
                "user_id": user_id,
                "vocab_target": 10,
                "grammar_target": 2,
                "review_target": 5,
                "study_minutes_target": 15,
            }
            supabase.table("daily_goals").insert(defaults).execute()
            return defaults
        except Exception as e:
            logger.error(f"StreakService get_daily_goals error: {e}")
            return {
                "vocab_target": 10,
                "grammar_target": 2,
                "review_target": 5,
                "study_minutes_target": 15,
            }

    @staticmethod
    async def update_daily_goals(user_id: str, goals: dict) -> dict:
        """Update user's daily goals."""
        try:
            allowed = {"vocab_target", "grammar_target", "review_target", "study_minutes_target"}
            payload = {k: v for k, v in goals.items() if k in allowed}

            if not payload:
                return {"status": "no_change"}

            resp = supabase.table("daily_goals") \
                .select("id") \
                .eq("user_id", user_id) \
                .execute()

            if resp.data:
                supabase.table("daily_goals") \
                    .update(payload) \
                    .eq("user_id", user_id) \
                    .execute()
            else:
                supabase.table("daily_goals") \
                    .insert({"user_id": user_id, **payload}) \
                    .execute()

            return {"status": "success", **payload}
        except Exception as e:
            logger.error(f"StreakService update_daily_goals error: {e}")
            return {"status": "error", "message": str(e)}

    @staticmethod
    async def get_today_progress(user_id: str) -> dict:
        """Get today's progress against daily goals."""
        try:
            today = date.today().isoformat()

            # Get today's activity
            activity_resp = supabase.table("study_streaks") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("study_date", today) \
                .execute()

            activity = activity_resp.data[0] if activity_resp.data else {
                "study_minutes": 0,
                "items_reviewed": 0,
                "quests_completed": 0,
                "xp_earned": 0,
            }

            # Get goals
            goals = await StreakService.get_daily_goals(user_id)

            return {
                "activity": activity,
                "goals": goals,
                "completion": {
                    "review_pct": min(100, round(
                        (activity.get("items_reviewed", 0) / max(goals.get("review_target", 5), 1)) * 100
                    )),
                    "minutes_pct": min(100, round(
                        (activity.get("study_minutes", 0) / max(goals.get("study_minutes_target", 15), 1)) * 100
                    )),
                },
            }
        except Exception as e:
            logger.error(f"StreakService get_today_progress error: {e}")
            return {"activity": {}, "goals": {}, "completion": {}}
