"""
SRS Service — SM-2 Spaced Repetition Algorithm
Manages review scheduling per item per user using Supabase srs_items table.
"""
import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Optional
from core.supabase_client import supabase

logger = logging.getLogger(__name__)


def _now_utc():
    return datetime.now(timezone.utc)


class SRSService:
    """SM-2 algorithm implementation for spaced repetition scheduling."""

    @staticmethod
    def calculate_sm2(
        quality: int,
        repetitions: int,
        easiness_factor: float,
        interval_days: int,
    ) -> dict:
        """
        SM-2 algorithm core.

        quality: 0-5 (0=complete blackout, 5=perfect recall)
        Returns dict with new repetitions, easiness_factor, interval_days.
        """
        quality = max(0, min(5, quality))

        if quality >= 3:
            # Correct response
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = 6
            else:
                new_interval = round(interval_days * easiness_factor)
            new_repetitions = repetitions + 1
        else:
            # Incorrect — reset
            new_repetitions = 0
            new_interval = 1

        # Update easiness factor (minimum 1.3)
        new_ef = easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(1.3, new_ef)

        return {
            "repetitions": new_repetitions,
            "easiness_factor": round(new_ef, 4),
            "interval_days": new_interval,
        }

    @staticmethod
    async def get_or_create_item(user_id: str, node_id: str, node_type: str) -> dict:
        """Get existing SRS item or create new one."""
        try:
            resp = supabase.table("srs_items") \
                .select("*") \
                .eq("user_id", user_id) \
                .eq("node_id", node_id) \
                .execute()

            if resp.data and len(resp.data) > 0:
                return resp.data[0]

            # Create new item
            new_item = {
                "user_id": user_id,
                "node_id": node_id,
                "node_type": node_type,
                "easiness_factor": 2.5,
                "interval_days": 1,
                "repetitions": 0,
                "next_review": _now_utc().isoformat(),
                "last_quality": None,
            }
            resp = supabase.table("srs_items").insert(new_item).execute()
            return resp.data[0] if resp.data else new_item
        except Exception as e:
            logger.error(f"SRS get_or_create_item error: {e}")
            return None

    @staticmethod
    async def record_review(user_id: str, node_id: str, node_type: str, quality: int) -> dict:
        """
        Record a review and update SRS schedule.
        quality: 0-5 (mapping from UI: again=1, hard=2, good=3, easy=5)
        """
        try:
            item = await SRSService.get_or_create_item(user_id, node_id, node_type)
            if not item:
                return {"error": "Failed to get SRS item"}

            result = SRSService.calculate_sm2(
                quality=quality,
                repetitions=item.get("repetitions", 0),
                easiness_factor=item.get("easiness_factor", 2.5),
                interval_days=item.get("interval_days", 1),
            )

            next_review = _now_utc() + timedelta(days=result["interval_days"])

            update_data = {
                "easiness_factor": result["easiness_factor"],
                "interval_days": result["interval_days"],
                "repetitions": result["repetitions"],
                "next_review": next_review.isoformat(),
                "last_reviewed": _now_utc().isoformat(),
                "last_quality": quality,
            }

            supabase.table("srs_items") \
                .update(update_data) \
                .eq("user_id", user_id) \
                .eq("node_id", node_id) \
                .execute()

            logger.info(
                f"SRS review: user={user_id}, node={node_id}, q={quality}, "
                f"next_review={next_review.date()}, interval={result['interval_days']}d"
            )

            return {
                "node_id": node_id,
                "quality": quality,
                "next_review": next_review.isoformat(),
                "interval_days": result["interval_days"],
                "easiness_factor": result["easiness_factor"],
                "repetitions": result["repetitions"],
            }
        except Exception as e:
            logger.error(f"SRS record_review error: {e}")
            return {"error": str(e)}

    @staticmethod
    async def get_due_items(user_id: str, limit: int = 20) -> list[dict]:
        """Get items due for review (next_review <= now)."""
        try:
            now_iso = _now_utc().isoformat()
            resp = supabase.table("srs_items") \
                .select("*") \
                .eq("user_id", user_id) \
                .lte("next_review", now_iso) \
                .order("next_review", desc=False) \
                .limit(limit) \
                .execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"SRS get_due_items error: {e}")
            return []

    @staticmethod
    async def get_srs_stats(user_id: str) -> dict:
        """Get SRS statistics for user dashboard."""
        try:
            resp = supabase.table("srs_items") \
                .select("*") \
                .eq("user_id", user_id) \
                .execute()

            items = resp.data or []
            now = _now_utc()

            due_count = sum(1 for i in items if i.get("next_review") and
                          datetime.fromisoformat(i["next_review"].replace("Z", "+00:00")) <= now)
            mature_count = sum(1 for i in items if i.get("interval_days", 0) >= 21)
            learning_count = sum(1 for i in items if 0 < i.get("interval_days", 0) < 21)

            return {
                "total_items": len(items),
                "due_now": due_count,
                "mature": mature_count,
                "learning": learning_count,
                "new": sum(1 for i in items if i.get("repetitions", 0) == 0),
            }
        except Exception as e:
            logger.error(f"SRS get_stats error: {e}")
            return {"total_items": 0, "due_now": 0, "mature": 0, "learning": 0, "new": 0}

    @staticmethod
    async def add_items_bulk(user_id: str, items: list[dict]) -> int:
        """
        Add multiple items to SRS in bulk.
        items: list of {"node_id": str, "node_type": str}
        """
        try:
            added = 0
            for item in items:
                existing = supabase.table("srs_items") \
                    .select("id") \
                    .eq("user_id", user_id) \
                    .eq("node_id", item["node_id"]) \
                    .execute()

                if not existing.data:
                    supabase.table("srs_items").insert({
                        "user_id": user_id,
                        "node_id": item["node_id"],
                        "node_type": item["node_type"],
                        "easiness_factor": 2.5,
                        "interval_days": 1,
                        "repetitions": 0,
                        "next_review": _now_utc().isoformat(),
                    }).execute()
                    added += 1
            return added
        except Exception as e:
            logger.error(f"SRS add_items_bulk error: {e}")
            return 0

    @staticmethod
    async def get_retention_forecast(user_id: str, days: int = 7) -> list[dict]:
        """
        Predict review workload for the next N days.
        Returns list of { date, due_count } for dashboard.
        """
        try:
            resp = supabase.table("srs_items") \
                .select("next_review, interval_days") \
                .eq("user_id", user_id) \
                .execute()

            items = resp.data or []
            now = _now_utc()
            forecast = []

            for day_offset in range(days):
                target_date = (now + timedelta(days=day_offset)).date()
                count = 0
                for item in items:
                    if item.get("next_review"):
                        review_date = datetime.fromisoformat(
                            item["next_review"].replace("Z", "+00:00")
                        ).date()
                        if review_date <= target_date:
                            count += 1
                forecast.append({
                    "date": target_date.isoformat(),
                    "due_count": count,
                })
            return forecast
        except Exception as e:
            logger.error(f"SRS retention_forecast error: {e}")
            return []
