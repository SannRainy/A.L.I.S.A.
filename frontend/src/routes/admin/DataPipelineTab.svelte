<script>
    import { onMount } from "svelte";

    export let user;
    export let API;

    let csvFiles = [];
    let editingCsv = null;
    let csvData = null;
    let editHeaders = [];
    let editRows = [];
    let csvSaving = false;
    let loading = true;

    onMount(async () => {
        await loadCsvFiles();
    });

    async function loadCsvFiles() {
        loading = true;
        try {
            const res = await fetch(`${API}/csv-files?admin_id=${user.id}`);
            csvFiles = await res.json();
        } catch (e) {
            console.error("Gagal memuat daftar CSV:", e);
        } finally {
            loading = false;
        }
    }

    async function loadCsvContent(filename) {
        try {
            const res = await fetch(
                `${API}/csv/${filename}?admin_id=${user.id}`,
            );
            csvData = await res.json();
            editingCsv = filename;
            editHeaders = [...csvData.headers];
            editRows = csvData.rows.map((r) => ({ ...r }));
        } catch (e) {
            console.error("Gagal memuat konten CSV:", e);
        }
    }

    let notificationModal = null; // { type: 'success' | 'error', title, message }
    let showIngestModal = false;

    async function saveCsv() {
        csvSaving = true;
        try {
            const res = await fetch(`${API}/csv/${editingCsv}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    admin_id: user.id,
                    headers: editHeaders,
                    rows: editRows,
                }),
            });
            const data = await res.json();
            if (res.ok) {
                notificationModal = {
                    type: "success",
                    title: "Berhasil Disimpan! 🎉",
                    message: `Berkas CSV ${editingCsv} telah berhasil diperbarui dan disimpan.`,
                };
                await loadCsvFiles();
                editingCsv = null;
                csvData = null;
            } else {
                notificationModal = {
                    type: "error",
                    title: "Gagal Menyimpan ❌",
                    message: data.detail || "Terjadi kesalahan saat menyimpan berkas CSV.",
                };
            }
        } catch (e) {
            notificationModal = {
                type: "error",
                title: "Gagal Menyimpan ❌",
                message: e.message,
            };
        } finally {
            csvSaving = false;
        }
    }

    function addRow() {
        const newRow = {};
        editHeaders.forEach((h) => (newRow[h] = ""));
        editRows = [...editRows, newRow];
    }

    function deleteRow(idx) {
        editRows = editRows.filter((_, i) => i !== idx);
    }

    // Integrated Neo4j Ingestion
    let ingestRunning = false;
    let ingestResult = null;

    async function triggerIngest() {
        ingestRunning = true;
        ingestResult = null;
        showIngestModal = false;
        try {
            const res = await fetch(`${API}/ingest?admin_id=${user.id}`, {
                method: "POST",
            });
            ingestResult = await res.json();
        } catch (e) {
            ingestResult = { status: "error", output: "", errors: e.message };
        } finally {
            ingestRunning = false;
            showIngestModal = true;
        }
    }
</script>

{#if editingCsv && csvData}
    <div class="tab-header">
        <h2>✏️ Editing: {editingCsv}</h2>
        <div class="tab-actions">
            <button
                class="btn-secondary"
                on:click={() => {
                    editingCsv = null;
                    csvData = null;
                }}>← Kembali</button
            >
            <button class="btn-add" on:click={addRow}>+ Tambah Baris</button>
            <button
                class="btn-save"
                on:click={saveCsv}
                disabled={csvSaving}
            >
                {csvSaving ? "Menyimpan..." : "💾 Simpan"}
            </button>
        </div>
    </div>
    <div class="table-wrap custom-scroll">
        <table class="admin-table csv-table">
            <thead>
                <tr>
                    <th class="th-num">#</th>
                    {#each editHeaders as h}
                        <th>{h}</th>
                    {/each}
                    <th class="th-act">🗑</th>
                </tr>
            </thead>
            <tbody>
                {#each editRows as row, i}
                    <tr>
                        <td class="td-num">{i + 1}</td>
                        {#each editHeaders as h}
                            <td>
                                <input
                                    class="csv-cell"
                                    bind:value={editRows[i][h]}
                                />
                            </td>
                        {/each}
                        <td class="td-act">
                            <button
                                class="btn-del"
                                on:click={() => deleteRow(i)}
                            >×</button>
                        </td>
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
{:else}
    <div class="tab-header">
        <h2>📁 Data Pipeline Files & Ingest</h2>
    </div>

    <!-- Integrated Ingest Panel -->
    <div class="ingest-card">
        <div class="ingest-card-info">
            <span class="ingest-icon-badge">🔄</span>
            <div>
                <h4>Ingest Data ke Neo4j Knowledge Graph</h4>
                <p>Membaca seluruh berkas CSV di folder <code>data_pipeline/</code> lalu meng-upload/sinkronisasi relasi ke Neo4j database.</p>
                <p class="warn-txt">⚠️ Proses ini bersifat MERGE & Sync yang aman dijalankan berulang kali.</p>
            </div>
        </div>
        <button
            class="btn-ingest"
            on:click={triggerIngest}
            disabled={ingestRunning}
        >
            {ingestRunning ? "⏳ Sedang Ingest..." : "🚀 Jalankan Ingest Neo4j"}
        </button>
    </div>

    <div class="section-divider">
        <span>Daftar Berkas CSV ({csvFiles.length})</span>
    </div>

    {#if loading}
        <div class="csv-loading">
            <div class="admin-spinner"></div>
            <p>Memuat daftar berkas CSV...</p>
        </div>
    {:else}
        <div class="csv-grid custom-scroll">
            {#each csvFiles as f}
                <button
                    class="csv-card"
                    on:click={() => loadCsvContent(f.name)}
                >
                    <div class="csv-icon">
                        {f.type === "nodes"
                            ? "🟢"
                            : f.type === "edges"
                              ? "🔗"
                              : "📄"}
                    </div>
                    <div class="csv-info">
                        <h4>{f.name}</h4>
                        <p>
                            {f.row_count} rows • {(
                                f.size_bytes / 1024
                            ).toFixed(1)} KB
                        </p>
                    </div>
                    <span class="csv-badge">{f.type}</span>
                </button>
            {/each}
        </div>
    {/if}
{/if}

<!-- ── Custom UI Modal: Notifikasi Simpan CSV ── -->
{#if notificationModal}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
    <div
        class="admin-modal-backdrop"
        role="presentation"
        on:click={() => (notificationModal = null)}
    >
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div
            class="admin-modal-card"
            role="dialog"
            aria-modal="true"
            on:click|stopPropagation
        >
            <div class="admin-modal-icon {notificationModal.type}">
                {notificationModal.type === "success" ? "✅" : "❌"}
            </div>
            <h3 class="admin-modal-title">{notificationModal.title}</h3>
            <p class="admin-modal-message">{notificationModal.message}</p>
            <button
                class="btn-modal-close"
                on:click={() => (notificationModal = null)}
            >
                Tutup
            </button>
        </div>
    </div>
{/if}

<!-- ── Custom UI Modal: Pop Up Output Ingest Neo4j ── -->
{#if showIngestModal && ingestResult}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
    <div
        class="admin-modal-backdrop"
        role="presentation"
        on:click={() => (showIngestModal = false)}
    >
        <!-- svelte-ignore a11y-click-events-have-key-events -->
        <!-- svelte-ignore a11y-no-static-element-interactions -->
        <div
            class="admin-modal-card ingest-modal-card"
            class:ingest-modal-error={ingestResult.status === "error"}
            role="dialog"
            aria-modal="true"
            on:click|stopPropagation
        >
            <div class="ingest-modal-header">
                <div class="ingest-modal-title-group">
                    <span class="ingest-modal-badge-icon">
                        {ingestResult.status === "success" ? "🚀" : "❌"}
                    </span>
                    <h3>
                        {ingestResult.status === "success"
                            ? "Ingest Selesai dengan Sukses!"
                            : "Ingest Gagal"}
                    </h3>
                </div>
                <button
                    class="btn-modal-x"
                    on:click={() => (showIngestModal = false)}>×</button
                >
            </div>

            <div class="ingest-modal-body custom-scroll">
                <pre
                    class="ingest-modal-log">{ingestResult.output || ""}{ingestResult.errors
                        ? "\n--- ERRORS ---\n" + ingestResult.errors
                        : ""}</pre>
            </div>

            <div class="ingest-modal-footer">
                <button
                    class="btn-modal-primary"
                    on:click={() => (showIngestModal = false)}
                >
                    Mengerti & Tutup
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    /* ── Custom Pop Up Modals ── */
    .admin-modal-backdrop {
        position: fixed;
        inset: 0;
        z-index: 99999;
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(8px);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        animation: fadeInModal 0.2s ease-out;
    }

    .admin-modal-card {
        background: #ffffff;
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 24px;
        padding: 28px;
        width: 100%;
        max-width: 440px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        text-align: center;
        animation: popUpModal 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    :global(body.dark) .admin-modal-card {
        background: #1e293b;
        border-color: rgba(255, 255, 255, 0.12);
        color: #f8fafc;
    }

    .admin-modal-icon {
        font-size: 42px;
        margin-bottom: 12px;
        line-height: 1;
    }
    .admin-modal-title {
        font-size: 19px;
        font-weight: 900;
        margin-bottom: 8px;
        color: #0f172a;
    }
    :global(body.dark) .admin-modal-title {
        color: #f8fafc;
    }
    .admin-modal-message {
        font-size: 13px;
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 24px;
    }
    :global(body.dark) .admin-modal-message {
        color: #94a3b8;
    }
    .btn-modal-close {
        width: 100%;
        padding: 13px 20px;
        background: #6366f1;
        color: #ffffff;
        border: none;
        border-radius: 14px;
        font-size: 13px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-modal-close:hover {
        background: #4f46e5;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }

    /* Ingest Output Pop Up Modal */
    .ingest-modal-card {
        max-width: 650px;
        text-align: left;
        display: flex;
        flex-direction: column;
        max-height: 85vh;
        padding: 24px;
    }
    .ingest-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 14px;
        border-bottom: 1px solid #e2e8f0;
    }
    :global(body.dark) .ingest-modal-header {
        border-color: rgba(255, 255, 255, 0.1);
    }
    .ingest-modal-title-group {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ingest-modal-badge-icon {
        font-size: 22px;
    }
    .ingest-modal-header h3 {
        font-size: 16px;
        font-weight: 900;
        color: #0f172a;
        margin: 0;
    }
    :global(body.dark) .ingest-modal-header h3 {
        color: #f8fafc;
    }
    .btn-modal-x {
        background: transparent;
        border: none;
        font-size: 24px;
        font-weight: 700;
        color: #94a3b8;
        cursor: pointer;
        padding: 0 6px;
        line-height: 1;
        border-radius: 6px;
    }
    .btn-modal-x:hover {
        color: #0f172a;
        background: #f1f5f9;
    }
    :global(body.dark) .btn-modal-x:hover {
        color: #ffffff;
        background: rgba(255, 255, 255, 0.1);
    }
    .ingest-modal-body {
        flex: 1;
        overflow-y: auto;
        margin-bottom: 18px;
    }
    .ingest-modal-log {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 11.5px;
        line-height: 1.6;
        white-space: pre-wrap;
        color: #047857;
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 14px;
        padding: 16px;
        max-height: 380px;
        overflow-y: auto;
        margin: 0;
    }
    .ingest-modal-card.ingest-modal-error .ingest-modal-log {
        color: #991b1b;
        background: #fef2f2;
        border-color: #fecaca;
    }
    :global(body.dark) .ingest-modal-log {
        color: #a7f3d0;
        background: rgba(6, 78, 59, 0.25);
        border-color: rgba(16, 185, 129, 0.3);
    }
    :global(body.dark) .ingest-modal-card.ingest-modal-error .ingest-modal-log {
        color: #fca5a5;
        background: rgba(153, 27, 27, 0.25);
        border-color: rgba(239, 68, 68, 0.3);
    }
    .ingest-modal-footer {
        display: flex;
        justify-content: flex-end;
    }
    .btn-modal-primary {
        padding: 12px 24px;
        background: #10b981;
        color: #ffffff;
        border: none;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 800;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-modal-primary:hover {
        background: #059669;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
    }
    .ingest-modal-card.ingest-modal-error .btn-modal-primary {
        background: #ef4444;
    }
    .ingest-modal-card.ingest-modal-error .btn-modal-primary:hover {
        background: #dc2626;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.35);
    }

    @keyframes fadeInModal {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes popUpModal {
        from { opacity: 0; transform: scale(0.92); }
        to { opacity: 1; transform: scale(1); }
    }
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
    .tab-actions {
        display: flex;
        gap: 8px;
    }
    
    /* Buttons */
    .btn-secondary,
    .btn-add,
    .btn-save {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-secondary {
        background: rgba(255, 255, 255, 0.06);
        color: rgba(255, 255, 255, 0.6);
    }
    .btn-add {
        background: rgba(34, 197, 94, 0.1);
        color: #86efac;
        border-color: rgba(34, 197, 94, 0.2);
    }
    .btn-save {
        background: rgba(99, 102, 241, 0.8);
        color: #fff;
        border: none;
    }
    .btn-save:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    .btn-del {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border-radius: 6px;
        cursor: pointer;
        width: 22px;
        height: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    .btn-del:hover {
        background: rgba(239, 68, 68, 0.8);
        color: #fff;
        border-color: transparent;
    }

    /* Table & Editors */
    .table-wrap {
        overflow: auto;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        flex-grow: 1;
        background: rgba(255, 255, 255, 0.01);
    }
    .admin-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        background: rgba(255, 255, 255, 0.02);
    }
    .admin-table th {
        position: sticky;
        top: 0;
        z-index: 10;
        padding: 12px 14px;
        text-align: left;
        font-weight: 800;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255, 255, 255, 0.4);
        background: #161233;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        white-space: nowrap;
    }
    .admin-table td {
        padding: 10px 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        white-space: nowrap;
        color: rgba(255, 255, 255, 0.7);
    }
    .csv-cell {
        background: transparent;
        border: none;
        color: #fff;
        width: 100%;
        padding: 6px;
        font-family: inherit;
        font-size: 12px;
        outline: none;
        border-radius: 4px;
        transition: background 0.15s;
    }
    .csv-cell:focus {
        background: rgba(255, 255, 255, 0.05);
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.1);
    }
    .th-num {
        width: 40px;
        text-align: center !important;
    }
    .th-act {
        width: 50px;
        text-align: center !important;
    }
    .td-num {
        text-align: center;
        color: rgba(255, 255, 255, 0.3) !important;
    }
    .td-act {
        text-align: center;
    }

    /* Grid layout */
    .csv-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 16px;
        overflow-y: auto;
        flex-grow: 1;
    }
    .csv-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 16px;
        cursor: pointer;
        text-align: left;
        transition: all 0.2s;
        position: relative;
        overflow: hidden;
    }
    .csv-card:hover {
        background: rgba(99, 102, 241, 0.05);
        border-color: rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }
    .csv-icon {
        font-size: 24px;
    }
    .csv-info h4 {
        margin: 0;
        font-size: 13px;
        font-weight: 700;
        color: #fff;
    }
    .csv-info p {
        margin: 4px 0 0;
        font-size: 11px;
        color: rgba(255, 255, 255, 0.45);
    }
    .csv-badge {
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 9px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: rgba(255, 255, 255, 0.05);
        padding: 3px 6px;
        border-radius: 4px;
        color: rgba(255, 255, 255, 0.6);
    }
    .csv-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        color: rgba(255, 255, 255, 0.5);
        gap: 12px;
    }
    .admin-spinner {
        width: 28px;
        height: 28px;
        border: 3px solid rgba(99, 102, 241, 0.2);
        border-top-color: #6366f1;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Integrated Ingest Card */
    .ingest-card {
        background: rgba(99, 102, 241, 0.05);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        gap: 20px;
        flex-shrink: 0;
    }
    .ingest-card-info {
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }
    .ingest-icon-badge {
        font-size: 24px;
        background: rgba(99, 102, 241, 0.15);
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .ingest-card-info h4 {
        margin: 0;
        font-size: 14px;
        font-weight: 800;
        color: #fff;
    }
    .ingest-card-info p {
        margin: 4px 0 0;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.6);
        line-height: 1.5;
    }
    .ingest-card-info .warn-txt {
        color: #fbbf24;
        font-size: 11px;
        font-weight: 600;
        margin-top: 6px;
    }
    .btn-ingest {
        padding: 12px 24px;
        background: #6366f1;
        color: #fff;
        border: none;
        border-radius: 10px;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        white-space: nowrap;
    }
    .btn-ingest:hover:not(:disabled) {
        background: #4f46e5;
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.4);
    }
    .btn-ingest:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Ingest Result Box */
    .ingest-result-box {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        flex-shrink: 0;
    }
    .ingest-result-box.ingest-error {
        background: rgba(239, 68, 68, 0.08);
        border-color: rgba(239, 68, 68, 0.3);
    }
    .ingest-result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-size: 13px;
        font-weight: 700;
        color: #065f46;
    }
    :global(body.dark) .ingest-result-header {
        color: #34d399;
    }
    .ingest-result-box.ingest-error .ingest-result-header {
        color: #991b1b;
    }
    :global(body.dark) .ingest-result-box.ingest-error .ingest-result-header {
        color: #f87171;
    }
    .btn-close-result {
        background: transparent;
        border: none;
        color: #047857;
        font-size: 20px;
        font-weight: 800;
        cursor: pointer;
        opacity: 0.7;
    }
    :global(body.dark) .btn-close-result {
        color: rgba(255, 255, 255, 0.6);
    }
    .btn-close-result:hover {
        opacity: 1;
    }
    .ingest-result-box pre {
        margin: 0;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 11px;
        line-height: 1.5;
        white-space: pre-wrap;
        color: #047857;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 8px;
        padding: 12px;
        max-height: 220px;
        overflow-y: auto;
    }
    .ingest-result-box.ingest-error pre {
        color: #991b1b;
        background: rgba(254, 242, 242, 0.9);
        border-color: rgba(239, 68, 68, 0.2);
    }
    :global(body.dark) .ingest-result-box pre {
        color: #a7f3d0;
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(16, 185, 129, 0.3);
    }
    :global(body.dark) .ingest-result-box.ingest-error pre {
        color: #fca5a5;
        background: rgba(15, 23, 42, 0.6);
        border-color: rgba(239, 68, 68, 0.3);
    }

    /* Section divider */
    .section-divider {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: rgba(255, 255, 255, 0.35);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 8px;
        flex-shrink: 0;
    }
</style>
