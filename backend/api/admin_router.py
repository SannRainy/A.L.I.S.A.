"""
Admin Router — API endpoints untuk Super Admin Dashboard TVJP.
Semua endpoint memerlukan admin_id yang di-verify rolenya.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from services.supabase_service import SupabaseService
import os
import csv
import io
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# ── Data pipeline path ────────────────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PIPELINE_DIR = os.path.join(BACKEND_DIR, "data_pipeline")

# ── Neo4j graph engine (optional) ─────────────────────────────────────
graph = None
try:
    from services.graph_engine import GraphEngine
    graph = GraphEngine()
except Exception:
    pass


# ── Auth guard ─────────────────────────────────────────────────────────
async def verify_admin(admin_id: str):
    """Verifikasi bahwa user_id adalah admin."""
    if not admin_id:
        raise HTTPException(status_code=401, detail="Admin ID diperlukan")
    profile = await SupabaseService.get_user_profile(admin_id)
    if not profile or profile.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak: hanya admin")


# ═══════════════════════════════════════════════════════════════════════
# 1. USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

@router.get("/users")
async def get_all_users(admin_id: str):
    """Ambil semua user + demographics + Neo4j progress."""
    await verify_admin(admin_id)
    users = await SupabaseService.get_all_profiles()

    # Enrich dengan Neo4j mastery data secara concurrent
    async def enrich_user_neo4j(u: dict):
        u["neo4j_stats"] = {
            "vocab_learned": 0,
            "grammar_learned": 0,
            "kanji_mastered": 0,
        }
        if graph:
            try:
                mastery = await asyncio.to_thread(graph.get_student_mastery_path, u["id"])
                u["neo4j_stats"]["vocab_learned"] = sum(
                    1 for n in mastery if str(n.get("type", "")).lower() == "vocab"
                )
                u["neo4j_stats"]["grammar_learned"] = sum(
                    1 for n in mastery if str(n.get("type", "")).lower() == "grammar"
                )
                u["neo4j_stats"]["kanji_mastered"] = sum(
                    1 for n in mastery if str(n.get("type", "")).lower() == "kanji"
                )
            except Exception as e:
                logger.warning(f"Could not get Neo4j stats for {u['id']}: {e}")

    await asyncio.gather(*(enrich_user_neo4j(u) for u in users))

    # Tambahkan quest scores
    all_quests = await SupabaseService.get_all_quest_scores()
    quest_by_user = {}
    for q in all_quests:
        uid = q.get("user_id")
        if uid not in quest_by_user:
            quest_by_user[uid] = []
        quest_by_user[uid].append(q)

    for u in users:
        user_quests = quest_by_user.get(u["id"], [])
        u["quest_count"] = len(user_quests)
        u["quest_avg_score"] = (
            round(sum(q["score"] for q in user_quests) / len(user_quests), 1)
            if user_quests
            else 0
        )

    return users


@router.get("/users/{user_id}/detail")
async def get_user_detail(user_id: str, admin_id: str):
    """Ambil detail lengkap satu user."""
    await verify_admin(admin_id)
    profile = await SupabaseService.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")

    quests = await SupabaseService.get_user_achievements(user_id)
    mastery_path = []
    if graph:
        try:
            mastery_path = graph.get_student_mastery_path(user_id)
        except Exception:
            pass

    return {
        "profile": profile,
        "quests": quests,
        "mastery_path": mastery_path,
    }


# ═══════════════════════════════════════════════════════════════════════
# 2. DATA PIPELINE MANAGEMENT (CSV CRUD)
# ═══════════════════════════════════════════════════════════════════════

@router.get("/csv-files")
async def list_csv_files(admin_id: str):
    """Daftar semua file CSV di data_pipeline."""
    await verify_admin(admin_id)
    files = []
    for f in sorted(os.listdir(DATA_PIPELINE_DIR)):
        if f.endswith(".csv"):
            path = os.path.join(DATA_PIPELINE_DIR, f)
            stat = os.stat(path)
            # Count rows
            with open(path, "r", encoding="utf-8") as fh:
                row_count = sum(1 for _ in fh) - 1  # minus header
            files.append({
                "name": f,
                "size_bytes": stat.st_size,
                "row_count": max(row_count, 0),
                "type": "nodes" if f.startswith("nodes_") else "edges" if f.startswith("edges_") else "other",
            })
    return files


@router.get("/csv/{filename}")
async def read_csv_file(filename: str, admin_id: str):
    """Baca isi file CSV sebagai JSON array."""
    await verify_admin(admin_id)

    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = os.path.join(DATA_PIPELINE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)

    return {"filename": filename, "headers": headers, "rows": rows}


class CsvUpdateRequest(BaseModel):
    admin_id: str
    headers: list
    rows: list


@router.put("/csv/{filename}")
async def update_csv_file(filename: str, request: CsvUpdateRequest):
    """Overwrite isi file CSV dari data JSON."""
    await verify_admin(request.admin_id)

    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = os.path.join(DATA_PIPELINE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")

    # Backup original
    backup_path = path + ".bak"
    try:
        with open(path, "r", encoding="utf-8") as f:
            original = f.read()
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original)
    except Exception:
        pass

    # Write new data
    try:
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=request.headers, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for row in request.rows:
                writer.writerow(row)
        return {"status": "success", "message": f"{filename} berhasil diperbarui ({len(request.rows)} rows)"}
    except Exception as e:
        # Restore backup
        if os.path.exists(backup_path):
            with open(backup_path, "r", encoding="utf-8") as f:
                with open(path, "w", encoding="utf-8") as out:
                    out.write(f.read())
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan: {e}")


@router.post("/csv/upload")
async def upload_csv(admin_id: str, file: UploadFile = File(...)):
    """Upload file CSV baru ke data_pipeline."""
    await verify_admin(admin_id)

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Hanya file CSV yang diterima")

    safe_name = file.filename.replace("..", "").replace("/", "").replace("\\", "")
    path = os.path.join(DATA_PIPELINE_DIR, safe_name)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    # Count rows
    rows = content.decode("utf-8").strip().split("\n")
    row_count = len(rows) - 1

    return {"status": "success", "filename": safe_name, "row_count": row_count}


# ═══════════════════════════════════════════════════════════════════════
# 3. NEO4J INGEST
# ═══════════════════════════════════════════════════════════════════════

@router.post("/ingest")
async def trigger_ingest(admin_id: str):
    """Trigger ingest_n5.py untuk upload CSV ke Neo4j."""
    await verify_admin(admin_id)

    ingest_script = os.path.join(DATA_PIPELINE_DIR, "ingest_n5.py")
    if not os.path.exists(ingest_script):
        raise HTTPException(status_code=404, detail="ingest_n5.py tidak ditemukan")

    try:
        import sys
        process = await asyncio.create_subprocess_exec(
            sys.executable, ingest_script,
            cwd=BACKEND_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)

        return {
            "status": "success" if process.returncode == 0 else "error",
            "return_code": process.returncode,
            "output": stdout.decode("utf-8", errors="replace"),
            "errors": stderr.decode("utf-8", errors="replace"),
        }
    except asyncio.TimeoutError:
        return {"status": "error", "output": "", "errors": "Timeout: proses melebihi 120 detik"}
    except Exception as e:
        logger.error(f"Ingest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════
# 4. ANALYTICS
# ═══════════════════════════════════════════════════════════════════════

@router.get("/analytics")
async def get_analytics(admin_id: str):
    """Ambil statistik agregat untuk survey/laporan."""
    await verify_admin(admin_id)

    users = await SupabaseService.get_all_profiles()
    quests = await SupabaseService.get_all_quest_scores()
    chat_stats = await SupabaseService.get_chat_stats()

    # Demographics breakdown
    gender_dist = {}
    country_dist = {}
    purpose_dist = {}
    level_dist = {}
    age_groups = {"<18": 0, "18-22": 0, "23-30": 0, "31-40": 0, "40+": 0, "N/A": 0}
    total_xp = 0

    for u in users:
        if u.get("role") == "admin":
            continue  # Exclude admin from survey

        g = u.get("gender", "prefer_not_to_say") or "prefer_not_to_say"
        gender_dist[g] = gender_dist.get(g, 0) + 1

        c = u.get("country", "N/A") or "N/A"
        country_dist[c] = country_dist.get(c, 0) + 1

        p = u.get("study_purpose", "N/A") or "N/A"
        purpose_dist[p] = purpose_dist.get(p, 0) + 1

        lv = u.get("japanese_level", "N/A") or "N/A"
        level_dist[lv] = level_dist.get(lv, 0) + 1

        age = u.get("age")
        if age is None:
            age_groups["N/A"] += 1
        elif age < 18:
            age_groups["<18"] += 1
        elif age <= 22:
            age_groups["18-22"] += 1
        elif age <= 30:
            age_groups["23-30"] += 1
        elif age <= 40:
            age_groups["31-40"] += 1
        else:
            age_groups["40+"] += 1

        total_xp += u.get("xp", 0) or 0

    student_count = sum(1 for u in users if u.get("role") != "admin")

    # Quest stats
    quest_scores = [q["score"] for q in quests if q.get("score") is not None]

    # Neo4j global stats
    kg_stats = {"total_vocab": 0, "total_kanji": 0, "total_grammar": 0}
    if graph:
        try:
            with graph.driver.session() as s:
                for label, key in [("Vocab", "total_vocab"), ("Kanji", "total_kanji"), ("Grammar", "total_grammar")]:
                    result = s.run(f"MATCH (n:{label}) RETURN count(n) AS c")
                    kg_stats[key] = result.single()["c"]
        except Exception:
            pass

    return {
        "total_students": student_count,
        "demographics": {
            "gender": gender_dist,
            "age_groups": age_groups,
            "country": country_dist,
            "study_purpose": purpose_dist,
            "japanese_level": level_dist,
        },
        "engagement": {
            "avg_xp": round(total_xp / max(student_count, 1), 1),
            "total_quests_taken": len(quests),
            "avg_quest_score": round(sum(quest_scores) / max(len(quest_scores), 1), 1) if quest_scores else 0,
            **chat_stats,
        },
        "knowledge_graph": kg_stats,
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. EXPORT DATA
# ═══════════════════════════════════════════════════════════════════════

@router.get("/export/users")
async def export_users(admin_id: str, format: str = "json"):
    """Export semua data user (untuk lampiran skripsi/survey)."""
    await verify_admin(admin_id)
    users = await SupabaseService.get_all_profiles()

    if format == "csv":
        if not users:
            return {"csv": ""}
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=users[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for u in users:
            writer.writerow(u)
        return {"csv": output.getvalue(), "count": len(users)}

    return {"data": users, "count": len(users)}

@router.get("/kg-data")
async def get_kg_data(admin_id: str):
    """Ambil semua node dan relasi untuk visualisasi Knowledge Graph."""
    await verify_admin(admin_id)

    if not graph:
        return {"nodes": [], "links": []}

    try:
        with graph.driver.session() as s:
            # Mengambil semua nodes
            nodes_result = s.run("MATCH (n) RETURN id(n) AS id, labels(n) AS labels, properties(n) AS props")
            nodes = []
            for record in nodes_result:
                props = record["props"]
                name = props.get("name", props.get("text", props.get("id", str(record["id"]))))
                nodes.append({
                    "id": record["id"],
                    "labels": record["labels"],
                    "name": name,
                    "props": props
                })
                
            # Mengambil semua relasi
            edges_result = s.run("MATCH (n)-[r]->(m) RETURN id(n) AS source, id(m) AS target, type(r) AS type, properties(r) AS props")
            links = []
            for record in edges_result:
                links.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["type"],
                    "props": record["props"]
                })
                
            return {"nodes": nodes, "links": links}
    except Exception as e:
        logger.error(f"KG data error: {e}")
        return {"nodes": [], "links": [], "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════
# 6. AI MODEL SWITCHER & PLAYGROUND (CCP)
# ═══════════════════════════════════════════════════════════════════════

class ModelSelectRequest(BaseModel):
    model_name: str
    admin_id: str

class PureChatRequest(BaseModel):
    query: str
    history: Optional[list] = None
    admin_id: str

@router.get("/models")
async def get_models(admin_id: str):
    """Daftar model .gguf di folder models/ dan model HF Cloud, serta kembalikan model yang sedang aktif."""
    await verify_admin(admin_id)
    
    # Folder models berada di root backend
    models_dir = os.path.join(BACKEND_DIR, "models")
    available_models = []
    
    if os.path.exists(models_dir):
        for f in os.listdir(models_dir):
            if f.endswith(".gguf"):
                available_models.append(f)
                
    # Dapatkan path model aktif
    from services.llm_agent import get_active_model_path, HF_CLOUD_MODEL_ID
    active_path = await get_active_model_path()
    if active_path.startswith("hf_cloud:"):
        active_model = active_path
    else:
        active_model = os.path.basename(active_path)
        
    # Tambahkan HF Cloud model ke daftar model tersedia
    available_models.append(HF_CLOUD_MODEL_ID)
    
    return {
        "available_models": sorted(available_models),
        "active_model": active_model
    }

class TestHfRequest(BaseModel):
    admin_id: str

@router.post("/models/test-hf")
async def test_hf_connection(request: TestHfRequest):
    """Mengetes koneksi ke HuggingFace Cloud Inference API."""
    await verify_admin(request.admin_id)
    from services.llm_agent import test_hf_cloud_connection
    res = await test_hf_cloud_connection()
    return res

@router.post("/models/select")
async def select_model(request: ModelSelectRequest):
    """Ganti model aktif ke model .gguf baru dan load ke memori."""
    await verify_admin(request.admin_id)
    
    from services.llm_agent import switch_model_async
    try:
        await switch_model_async(request.model_name)
        return {
            "status": "success",
            "message": f"Model berhasil diganti ke {request.model_name} dan dimuat ke VRAM/RAM."
        }
    except Exception as e:
        logger.error(f"Error switching model to {request.model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/chat")
async def pure_chat(request: PureChatRequest):
    """Playground chat (CCP Mode) - Streaming langsung ke model tanpa RAG/DB log/TTS."""
    await verify_admin(request.admin_id)
    
    from api.chat_router import llm_agent
    from fastapi.responses import StreamingResponse
    
    history_data = request.history or []
    
    return StreamingResponse(
        llm_agent.stream_pure_response(
            query=request.query,
            history=[{"role": m.get("role"), "content": m.get("content")} for m in history_data]
        ),
        media_type="text/event-stream"
    )


# ═══════════════════════════════════════════════════════════════════════
# 6. KG EDITOR & A/B TEST MANAGER
# ═══════════════════════════════════════════════════════════════════════

class AddNodeRequest(BaseModel):
    node_type: str  # 'Vocab', 'Grammar', 'Kanji', 'Topic'
    node_id: str
    properties: dict


class ABTestGroupRequest(BaseModel):
    user_id: str
    test_name: str
    group_label: str  # 'control', 'treatment_a', 'treatment_b'


@router.post("/kg-node")
async def add_kg_node(admin_id: str, req: AddNodeRequest):
    """Tambah/edit node materi di Neo4j langsung."""
    await verify_admin(admin_id)
    if not graph:
        raise HTTPException(status_code=503, detail="Graph engine tidak tersedia.")

    props_str = ", ".join([f"n.{k} = ${k}" for k in req.properties.keys()])
    cypher = f"MERGE (n:{req.node_type} {{id: $node_id}}) SET {props_str} RETURN n"

    try:
        with graph.driver.session() as session:
            session.run(cypher, node_id=req.node_id, **req.properties)
        return {
            "status": "success",
            "message": f"Node {req.node_type} '{req.node_id}' berhasil ditambahkan/diperbarui."
        }
    except Exception as e:
        logger.error(f"Error adding Neo4j node: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/kg-node/{node_type}/{node_id}")
async def delete_kg_node(admin_id: str, node_type: str, node_id: str):
    """Hapus node materi di Neo4j beserta relasinya."""
    await verify_admin(admin_id)
    if not graph:
        raise HTTPException(status_code=503, detail="Graph engine tidak tersedia.")

    # Prevent SQL/Cypher Injection by whitelist
    allowed_types = {"Vocab", "Grammar", "Kanji", "Topic"}
    if node_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipe node tidak valid.")

    cypher = f"MATCH (n:{node_type} {{id: $node_id}}) DETACH DELETE n"

    try:
        with graph.driver.session() as session:
            session.run(cypher, node_id=node_id)
        return {
            "status": "success",
            "message": f"Node '{node_id}' berhasil dihapus dari Knowledge Graph."
        }
    except Exception as e:
        logger.error(f"Error deleting Neo4j node: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test")
async def assign_ab_test_group(admin_id: str, req: ABTestGroupRequest):
    """Tugaskan user ke grup A/B testing tertentu."""
    await verify_admin(admin_id)
    try:
        from core.supabase_client import supabase
        supabase.table("ab_test_groups").upsert({
            "user_id": req.user_id,
            "test_name": req.test_name,
            "group_label": req.group_label
        }).execute()
        return {
            "status": "success",
            "message": f"User '{req.user_id}' ditugaskan ke grup '{req.group_label}' pada test '{req.test_name}'."
        }
    except Exception as e:
        logger.error(f"Error assigning A/B test group: {e}")
        raise HTTPException(status_code=500, detail=str(e))
