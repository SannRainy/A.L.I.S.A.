import logging
from services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class DBOrchestrator:
    def __init__(self, graph_engine):
        self.graph = graph_engine

    async def process_sync_event(self, student_id: str, updates: dict):
        """
        Orkestrasi Atomic Update:
        1. Validasi keberadaan node materi di Graph (Integrity Check via node_exists).
        2. Update Neo4j (update_node_status / add_wiki_note_node).
        3. Update Supabase hanya jika step 2 sukses penuh.

        Perbaikan: validasi kini menggunakan GraphEngine.node_exists() — satu query
        MATCH tunggal ke semua label relevan, jauh lebih efisien daripada 3 panggilan
        get_vocab_detail + get_grammar_detail + get_topic_by_name.
        """
        sb  = updates.get("supabase", {})
        n4j = updates.get("neo4j", [])

        graph_success = True
        if self.graph:
            for action in n4j:
                act_type = action.get("action")
                try:
                    if act_type == "UPDATE_STATUS":
                        target_id = action.get("target_node", "")
                        if not target_id:
                            logger.warning("[DB_ORCHESTRATOR] target_node kosong, dilewati.")
                            graph_success = False
                            continue

                        # ── Integrity check (satu query, semua label) ──
                        if not self.graph.node_exists(target_id):
                            logger.warning(
                                f"[DB_ORCHESTRATOR] Node '{target_id}' tidak ada di Graph. "
                                "Update status dilewati, XP tidak diberikan."
                            )
                            graph_success = False
                            continue

                        self.graph.update_node_status(student_id, target_id, action.get("type", "LEARNED"))

                    elif act_type == "CREATE_WIKI_NOTE":
                        self.graph.add_wiki_note_node(
                            student_id,
                            action.get("content", ""),
                            action.get("references", []),
                        )
                except Exception as e:
                    logger.error(f"[DB_ORCHESTRATOR] Neo4j Sync Error: {e}")
                    graph_success = False

        # Supabase hanya diproses jika tidak ada kegagalan kritis Neo4j
        if graph_success or not n4j:
            try:
                action_label = sb.get("action_label")
                if action_label:
                    await SupabaseService.update_user_stats(student_id, action_label)

                achievement = sb.get("achievement_unlocked")
                if achievement:
                    await SupabaseService.add_achievement(student_id, achievement)
            except Exception as e:
                logger.error(f"[DB_ORCHESTRATOR] Supabase Sync Error: {e}")
        else:
            logger.warning(
                "[DB_ORCHESTRATOR] Graph sync gagal atau ID invalid. "
                "Pemberian XP Supabase dibatalkan (Atomic Sync)."
            )
