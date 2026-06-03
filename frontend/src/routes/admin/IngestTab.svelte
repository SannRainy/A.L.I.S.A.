<script>
    export let user;
    export let API;

    let ingestRunning = false;
    let ingestResult = null;

    async function triggerIngest() {
        ingestRunning = true;
        ingestResult = null;
        try {
            const res = await fetch(`${API}/ingest?admin_id=${user.id}`, {
                method: "POST",
            });
            ingestResult = await res.json();
        } catch (e) {
            ingestResult = { status: "error", output: "", errors: e.message };
        } finally {
            ingestRunning = false;
        }
    }
</script>

<div class="tab-header">
    <h2>🔄 Ingest Data ke Neo4j</h2>
</div>
<div class="ingest-panel custom-scroll">
    <div class="ingest-info">
        <p>
            Menjalankan <code>ingest_n5.py</code> akan membaca semua file CSV di <code>data_pipeline/</code> dan meng-upload ke Neo4j Knowledge Graph.
        </p>
        <p class="ingest-warn">
            ⚠️ Proses ini akan MERGE data (tidak menghapus yang lama). Aman dijalankan berulang kali.
        </p>
    </div>
    <button
        class="btn-ingest"
        on:click={triggerIngest}
        disabled={ingestRunning}
    >
        {ingestRunning
            ? "⏳ Proses sedang berjalan..."
            : "🚀 Jalankan Ingest Sekarang"}
    </button>

    {#if ingestResult}
        <div
            class="ingest-result"
            class:ingest-error={ingestResult.status === "error"}
        >
            <h4>
                {ingestResult.status === "success"
                    ? "✅ Berhasil!"
                    : "❌ Error"}
            </h4>
            <pre>{ingestResult.output || ""}{ingestResult.errors
                    ? "\n--- ERRORS ---\n" + ingestResult.errors
                    : ""}</pre>
        </div>
    {/if}
</div>

<style>
    .tab-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        flex-wrap: wrap;
        gap: 12px;
        flex-shrink: 0;
    }
    .tab-header h2 {
        font-size: 18px;
        font-weight: 900;
        margin: 0;
        color: #fff;
    }

    /* Ingest Panel */
    .ingest-panel {
        display: flex;
        flex-direction: column;
        gap: 20px;
        background: rgba(15, 13, 36, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 24px;
        flex-grow: 1;
        overflow-y: auto;
    }
    .ingest-info {
        font-size: 13px;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.7);
    }
    .ingest-info code {
        background: rgba(255, 255, 255, 0.08);
        padding: 2px 6px;
        border-radius: 4px;
        color: #a5b4fc;
        font-family: inherit;
        font-size: 12px;
    }
    .ingest-warn {
        color: #fbbf24;
        margin-top: 10px;
        font-weight: 600;
    }
    .btn-ingest {
        align-self: flex-start;
        padding: 12px 24px;
        background: #6366f1;
        color: #fff;
        border: none;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-ingest:hover:not(:disabled) {
        background: #4f46e5;
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.4);
    }
    .btn-ingest:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    .ingest-result {
        background: rgba(16, 185, 129, 0.05);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px;
        padding: 16px;
    }
    .ingest-result.ingest-error {
        background: rgba(239, 68, 68, 0.05);
        border-color: rgba(239, 68, 68, 0.2);
    }
    .ingest-result h4 {
        margin: 0 0 10px 0;
        font-size: 14px;
        font-weight: 800;
    }
    .ingest-result pre {
        margin: 0;
        font-family: monospace;
        font-size: 11px;
        white-space: pre-wrap;
        color: rgba(255, 255, 255, 0.8);
        max-height: 300px;
        overflow-y: auto;
    }
</style>
