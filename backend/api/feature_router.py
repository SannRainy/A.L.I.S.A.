"""
Feature Router — New API endpoints for all upgraded features.
SRS, Learning Path, Placement Test, Streak, Grammar Checker, Reading, Writing, Analytics.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
import logging

from services.srs_service import SRSService
from services.streak_service import StreakService
from services.placement_data import get_placement_questions, calculate_placement_result
from services.grammar_checker import GrammarCheckerService
from services.reading_data import get_reading_passages, get_passage_by_id
from services.bkt_engine import BKTEngine
from core.supabase_client import supabase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["features"])

# Try to get graph engine
graph = None
try:
    from services.graph_engine import GraphEngine
    graph = GraphEngine()
    logger.info("✅ GraphEngine available for feature router")
except Exception as e:
    logger.warning(f"⚠️ GraphEngine not available: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ══════════════════════════════════════════════════════════════════════════════

class SRSReviewRequest(BaseModel):
    user_id: str
    node_id: str
    node_type: str
    quality: int  # 0-5 SM-2 quality


class PlacementAnswerItem(BaseModel):
    question_id: str
    user_answer: str
    is_correct: bool


class PlacementSubmitRequest(BaseModel):
    user_id: str
    answers: List[PlacementAnswerItem]


class GrammarCheckRequest(BaseModel):
    user_id: str
    text: str


class ReadingSubmitRequest(BaseModel):
    user_id: str
    passage_id: str
    unknown_words: List[str]
    comprehension_answers: List[dict]


class WritingSubmitRequest(BaseModel):
    user_id: str
    prompt: str
    user_text: str


class DailyGoalsUpdateRequest(BaseModel):
    vocab_target: Optional[int] = None
    grammar_target: Optional[int] = None
    review_target: Optional[int] = None
    study_minutes_target: Optional[int] = None


# ══════════════════════════════════════════════════════════════════════════════
# SRS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/srs/due/{user_id}")
async def get_srs_due_items(user_id: str, limit: int = 20):
    """Get items due for review (next_review <= now)."""
    try:
        items = await SRSService.get_due_items(user_id, limit)
        return {"status": "success", "items": items, "count": len(items)}
    except Exception as e:
        logger.error(f"get_srs_due_items error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/srs/review")
async def record_srs_review(req: SRSReviewRequest):
    """Record a review and update SRS schedule using SM-2."""
    try:
        result = await SRSService.record_review(
            req.user_id, req.node_id, req.node_type, req.quality
        )

        # Update graph engine status based on quality
        if graph and req.quality >= 4:
            status = "MASTERED"
        elif graph and req.quality >= 2:
            status = "LEARNED"
        elif graph:
            status = "STRUGGLING"
        else:
            status = None

        if graph and status:
            graph.update_node_status(req.user_id, req.node_id, status)

        # Log activity for streak
        await StreakService.log_activity(
            req.user_id, items_reviewed=1, xp_earned=5 if req.quality >= 3 else 2
        )

        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"record_srs_review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/srs/stats/{user_id}")
async def get_srs_stats(user_id: str):
    """Get SRS statistics for dashboard."""
    try:
        stats = await SRSService.get_srs_stats(user_id)
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"get_srs_stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/srs/forecast/{user_id}")
async def get_srs_forecast(user_id: str, days: int = 7):
    """Get review workload forecast for next N days."""
    try:
        forecast = await SRSService.get_retention_forecast(user_id, days)
        return {"status": "success", "forecast": forecast}
    except Exception as e:
        logger.error(f"get_srs_forecast error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# LEARNING PATH ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/learning-path/{user_id}")
async def get_learning_path(user_id: str, level: str = "N5"):
    """Generate personalized learning path using topological sort."""
    if not graph:
        raise HTTPException(status_code=503, detail="Graph engine not available")

    try:
        path = graph.generate_learning_path(user_id, level)
        return {
            "status": "success",
            "path": path,
            "total_nodes": len(path),
            "level": level,
        }
    except Exception as e:
        logger.error(f"get_learning_path error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kg/student-view/{user_id}")
async def get_kg_student_view(user_id: str):
    """Get full Knowledge Graph data for interactive visualization."""
    if not graph:
        raise HTTPException(status_code=503, detail="Graph engine not available")

    try:
        data = graph.get_kg_student_view(user_id)
        return {"status": "success", "graph": data}
    except Exception as e:
        logger.error(f"get_kg_student_view error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kg/shortest-path/{user_id}/{target_node_id}")
async def get_shortest_path(user_id: str, target_node_id: str):
    """Find shortest learning path from current position to target node."""
    if not graph:
        raise HTTPException(status_code=503, detail="Graph engine not available")

    try:
        path = graph.get_shortest_path(user_id, target_node_id)
        return {"status": "success", "path": path, "length": len(path)}
    except Exception as e:
        logger.error(f"get_shortest_path error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kg/seed-prerequisites")
async def seed_prerequisite_edges():
    """Admin: Seed PREREQUISITE_OF edges in Neo4j."""
    if not graph:
        raise HTTPException(status_code=503, detail="Graph engine not available")

    try:
        graph.ensure_prerequisite_edges()
        return {"status": "success", "message": "Prerequisites seeded successfully"}
    except Exception as e:
        logger.error(f"seed_prerequisite_edges error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# PLACEMENT TEST ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/placement/questions")
async def get_placement_test_questions():
    """Get all placement test questions."""
    questions = get_placement_questions()
    return {"status": "success", "questions": questions, "total": len(questions)}


@router.post("/placement/submit")
async def submit_placement_test(req: PlacementSubmitRequest):
    """Submit placement test and calculate level placement."""
    try:
        # Calculate result
        answers_data = [
            {
                "question_id": a.question_id,
                "user_answer": a.user_answer,
                "is_correct": a.is_correct,
            }
            for a in req.answers
        ]
        result = calculate_placement_result(answers_data)

        # Save to Supabase
        placement_data = {
            "user_id": req.user_id,
            "total_score": result["total_score"],
            "total_questions": result["total_questions"],
            "estimated_level": result["estimated_level"],
            "category_scores": result["category_scores"],
            "placed_nodes": result.get("mastered_levels", []),
        }

        # Upsert (update if exists, insert if not)
        supabase.table("placement_results").upsert(placement_data).execute()

        # Update profile
        supabase.table("profiles").update({
            "placement_completed": True
        }).eq("id", req.user_id).execute()

        # Auto-mark mastered levels in graph if available
        if graph and result.get("mastered_levels"):
            for level_id in result["mastered_levels"]:
                # Mark quest level nodes as MASTERED
                # (Implementation depends on quest_data structure)
                pass

        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"submit_placement_test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/placement/result/{user_id}")
async def get_placement_result(user_id: str):
    """Get user's placement test result."""
    try:
        resp = supabase.table("placement_results") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()

        if not resp.data:
            return {"status": "not_taken", "result": None}

        return {"status": "success", "result": resp.data[0]}
    except Exception as e:
        logger.error(f"get_placement_result error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# STREAK & DAILY GOALS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/streak/{user_id}")
async def get_streak_info(user_id: str):
    """Get current streak information."""
    try:
        streak_info = await StreakService.update_streak(user_id)
        return {"status": "success", "streak": streak_info}
    except Exception as e:
        logger.error(f"get_streak_info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/streak/calendar/{user_id}")
async def get_streak_calendar(user_id: str, days: int = 90):
    """Get study activity calendar for heatmap."""
    try:
        calendar = await StreakService.get_streak_calendar(user_id, days)
        return {"status": "success", "calendar": calendar}
    except Exception as e:
        logger.error(f"get_streak_calendar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-goals/{user_id}")
async def get_daily_goals(user_id: str):
    """Get user's daily goals configuration."""
    try:
        goals = await StreakService.get_daily_goals(user_id)
        return {"status": "success", "goals": goals}
    except Exception as e:
        logger.error(f"get_daily_goals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/daily-goals/{user_id}")
async def update_daily_goals(user_id: str, req: DailyGoalsUpdateRequest):
    """Update user's daily goals."""
    try:
        goals_dict = req.dict(exclude_none=True)
        result = await StreakService.update_daily_goals(user_id, goals_dict)
        return result
    except Exception as e:
        logger.error(f"update_daily_goals error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-goals/progress/{user_id}")
async def get_today_progress(user_id: str):
    """Get today's progress against daily goals."""
    try:
        progress = await StreakService.get_today_progress(user_id)
        return {"status": "success", "progress": progress}
    except Exception as e:
        logger.error(f"get_today_progress error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# GRAMMAR CHECKER ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/grammar/check")
async def check_grammar(req: GrammarCheckRequest):
    """Analyze Japanese text for grammar errors."""
    try:
        # Basic analysis
        analysis = GrammarCheckerService.basic_analysis(req.text)

        # Rule-based error detection
        errors = GrammarCheckerService.detect_common_errors(req.text)

        # Calculate score (100 - 10 per error, min 0)
        score = max(0, 100 - len(errors) * 10)

        # Detect correct grammar points
        detected_points = GrammarCheckerService.detect_correct_grammar_points(req.text)

        # Save to database
        check_data = {
            "user_id": req.user_id,
            "input_text": req.text,
            "analysis": {
                "tokens": analysis["tokens"],
                "stats": {
                    "token_count": analysis["token_count"],
                    "char_count": analysis["char_count"],
                    "kanji_count": analysis["kanji_count"],
                },
                "errors": errors,
                "detected_points": detected_points,
            },
            "score": score,
        }
        supabase.table("grammar_checks").insert(check_data).execute()

        return {
            "status": "success",
            "analysis": analysis,
            "errors": errors,
            "score": score,
            "detected_points": detected_points,
        }
    except Exception as e:
        logger.error(f"check_grammar error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/grammar/history/{user_id}")
async def get_grammar_history(user_id: str, limit: int = 10):
    """Get user's grammar check history."""
    try:
        resp = supabase.table("grammar_checks") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {"status": "success", "history": resp.data or []}
    except Exception as e:
        logger.error(f"get_grammar_history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# READING COMPREHENSION ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/reading/passages")
async def get_reading_passages_list(level: Optional[str] = None):
    """Get list of reading passages, optionally filtered by level."""
    try:
        passages = get_reading_passages(level)
        # Don't send full text in list view
        passages_list = [
            {
                "id": p["id"],
                "level": p["level"],
                "title": p["title"],
                "translation": p["translation"],
                "question_count": len(p.get("questions", [])),
            }
            for p in passages
        ]
        return {"status": "success", "passages": passages_list}
    except Exception as e:
        logger.error(f"get_reading_passages_list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading/passage/{passage_id}")
async def get_reading_passage_detail(passage_id: str):
    """Get full reading passage with annotations and questions."""
    try:
        passage = get_passage_by_id(passage_id)
        if not passage:
            raise HTTPException(status_code=404, detail="Passage not found")

        return {"status": "success", "passage": passage}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_reading_passage_detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reading/submit")
async def submit_reading_session(req: ReadingSubmitRequest):
    """Submit reading comprehension session results."""
    try:
        # Calculate comprehension score
        passage = get_passage_by_id(req.passage_id)
        if not passage:
            raise HTTPException(status_code=404, detail="Passage not found")

        total_questions = len(passage.get("questions", []))
        correct_answers = sum(
            1 for ans in req.comprehension_answers if ans.get("is_correct")
        )
        comprehension_score = (
            round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
        )

        # Save to database
        session_data = {
            "user_id": req.user_id,
            "passage_id": req.passage_id,
            "unknown_words": req.unknown_words,
            "comprehension_score": comprehension_score,
        }
        supabase.table("reading_sessions").insert(session_data).execute()

        # Log activity
        await StreakService.log_activity(
            req.user_id, study_minutes=5, xp_earned=comprehension_score // 10
        )

        return {
            "status": "success",
            "comprehension_score": comprehension_score,
            "correct": correct_answers,
            "total": total_questions,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"submit_reading_session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading/history/{user_id}")
async def get_reading_history(user_id: str, limit: int = 10):
    """Get user's reading session history."""
    try:
        resp = supabase.table("reading_sessions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {"status": "success", "history": resp.data or []}
    except Exception as e:
        logger.error(f"get_reading_history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ══════════════════════════════════════════════════════════════════════════════
# WRITING PRACTICE ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/writing/submit")
async def submit_writing(req: WritingSubmitRequest):
    """Submit writing practice and get feedback."""
    try:
        # Use grammar checker for analysis
        analysis = GrammarCheckerService.basic_analysis(req.user_text)
        errors = GrammarCheckerService.detect_common_errors(req.user_text)

        # Calculate overall score
        base_score = max(0, 100 - len(errors) * 10)
        length_bonus = min(20, len(analysis["tokens"]) // 2)  # Bonus for longer text
        overall_score = min(100, base_score + length_bonus)

        # Save to database
        writing_data = {
            "user_id": req.user_id,
            "prompt": req.prompt,
            "user_text": req.user_text,
            "grammar_feedback": {
                "tokens": analysis["tokens"],
                "errors": errors,
                "stats": {
                    "token_count": analysis["token_count"],
                    "char_count": analysis["char_count"],
                    "kanji_count": analysis["kanji_count"],
                },
            },
            "overall_score": overall_score,
        }
        supabase.table("writing_submissions").insert(writing_data).execute()

        # Log activity
        await StreakService.log_activity(
            req.user_id, study_minutes=10, xp_earned=overall_score // 5
        )

        return {
            "status": "success",
            "overall_score": overall_score,
            "feedback": {
                "errors": errors,
                "stats": analysis,
                "suggestions": [
                    "Use more varied vocabulary" if analysis["token_count"] < 20 else "Good vocabulary variety!",
                    "Include kanji where appropriate" if analysis["kanji_count"] < 3 else "Nice kanji usage!",
                ],
            },
        }
    except Exception as e:
        logger.error(f"submit_writing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/writing/history/{user_id}")
async def get_writing_history(user_id: str, limit: int = 10):
    """Get user's writing submission history."""
    try:
        resp = supabase.table("writing_submissions") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {"status": "success", "history": resp.data or []}
    except Exception as e:
        logger.error(f"get_writing_history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/writing/prompts")
async def get_writing_prompts(level: str = "beginner"):
    """Get daily writing prompts based on level."""
    prompts = {
        "beginner": [
            "自己紹介をしてください。(Perkenalkan diri Anda)",
            "好きな食べ物について書いてください。(Tulis tentang makanan favorit)",
            "週末の予定を書いてください。(Tulis rencana akhir pekan)",
        ],
        "intermediate": [
            "日本の文化について知っていることを書いてください。",
            "将来の夢について書いてください。",
            "最近読んだ本について書いてください。",
        ],
        "advanced": [
            "環境問題について意見を述べてください。",
            "技術の進歩が社会に与える影響について書いてください。",
            "伝統と近代化のバランスについて論じてください。",
        ],
    }

    return {
        "status": "success",
        "prompts": prompts.get(level, prompts["beginner"]),
        "level": level,
    }


# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/analytics/student/{user_id}")
async def get_student_analytics(user_id: str):
    """Get comprehensive learning analytics for student."""
    try:
        # Streak data
        streak_info = await StreakService.update_streak(user_id)
        calendar = await StreakService.get_streak_calendar(user_id, 30)

        # SRS stats
        srs_stats = await SRSService.get_srs_stats(user_id)

        # Study time from streaks
        total_study_minutes = sum(day.get("study_minutes", 0) for day in calendar)
        total_items_reviewed = sum(day.get("items_reviewed", 0) for day in calendar)

        # Recent activity
        activity_resp = supabase.table("study_streaks") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("study_date", desc=True) \
            .limit(30) \
            .execute()

        recent_activity = activity_resp.data or []

        return {
            "status": "success",
            "analytics": {
                "streak": streak_info,
                "srs": srs_stats,
                "study_summary": {
                    "total_minutes_30d": total_study_minutes,
                    "total_reviews_30d": total_items_reviewed,
                    "avg_minutes_per_day": round(total_study_minutes / 30, 1),
                },
                "recent_activity": recent_activity,
            },
        }
    except Exception as e:
        logger.error(f"get_student_analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
