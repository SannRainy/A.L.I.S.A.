<script>
    import { onMount, onDestroy } from "svelte";

    export let user;
    export let API;

    let analytics = null;
    let kgData = null;
    let rawKgData = null;
    let kgLoading = false;
    let graphContainer;
    let myGraph;
    let nodeCounts = {};
    let linkCounts = {};
    let kgFullscreen = false;

    const labelColors = {
        ErrorPattern: "#10b981",
        Grammar: "#f59e0b",
        Kana: "#93c5fd",
        Kanji: "#3b82f6",
        POS: "#f97316",
        Rule: "#b45309",
        Sentence: "#4b5563",
        Student: "#a855f7",
        Topic: "#ec4899",
        Vocab: "#ef4444",
        Default: "#6366f1",
    };

    onMount(async () => {
        await loadAnalytics();
    });

    onDestroy(() => {
        if (myGraph) {
            myGraph = null;
        }
    });

    async function loadAnalytics() {
        try {
            const res = await fetch(`${API}/analytics?admin_id=${user.id}`);
            analytics = await res.json();

            kgLoading = true;
            try {
                const kgRes = await fetch(
                    `${API}/kg-data?admin_id=${user.id}`,
                );
                rawKgData = await kgRes.json();

                nodeCounts = {};
                linkCounts = {};
                if (rawKgData && rawKgData.nodes) {
                    rawKgData.nodes.forEach((n) => {
                        const lbl =
                            n.labels && n.labels.length ? n.labels[0] : "Node";
                        nodeCounts[lbl] = (nodeCounts[lbl] || 0) + 1;
                    });
                    rawKgData.links.forEach((l) => {
                        linkCounts[l.type] = (linkCounts[l.type] || 0) + 1;
                    });
                }
            } catch (e) {
                console.error("Failed to load KG data", e);
            }
            kgLoading = false;
        } catch (e) {
            console.error("Failed to load analytics:", e);
        }
    }

    function toggleFullscreen() {
        kgFullscreen = !kgFullscreen;
        setTimeout(() => {
            if (myGraph && graphContainer) {
                myGraph.width(graphContainer.clientWidth);
                myGraph.height(graphContainer.clientHeight);
                myGraph.zoomToFit(400, 40);
            }
        }, 50);
    }

    function handleKeydown(e) {
        if (e.key === 'Escape' && kgFullscreen) {
            toggleFullscreen();
        }
    }

    async function exportUsers(format) {
        try {
            const res = await fetch(
                `${API}/export/users?admin_id=${user.id}&format=${format}`,
            );
            const data = await res.json();
            if (format === "csv") {
                const blob = new Blob([data.csv], { type: "text/csv" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "tvjp_users_export.csv";
                a.click();
                URL.revokeObjectURL(url);
            } else {
                const blob = new Blob([JSON.stringify(data.data, null, 2)], {
                    type: "application/json",
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "tvjp_users_export.json";
                a.click();
                URL.revokeObjectURL(url);
            }
        } catch (e) {
            alert("Export failed: " + e.message);
        }
    }

    $: if (rawKgData && graphContainer && !kgLoading) {
        if (!myGraph && typeof window !== "undefined") {
            import("force-graph")
                .then((module) => {
                    const ForceGraph = module.default;
                    if (!myGraph && graphContainer) {
                        kgData = JSON.parse(JSON.stringify(rawKgData));
                        myGraph = ForceGraph()(graphContainer)
                            .graphData(kgData)
                            .nodeLabel((n) => {
                                let html = `<div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px; font-size: 11px; z-index: 1000; position: relative;">`;
                                html += `<strong style="font-size:12px; color:#fff;">${n.labels && n.labels.length > 0 ? n.labels[0] : "Node"}: ${n.name || ""}</strong><br/>`;
                                if (n.props) {
                                    for (const [k, v] of Object.entries(
                                        n.props,
                                    )) {
                                        if (k !== "name")
                                            html += `<span style="color: #a5b4fc">${k}</span>: ${v}<br/>`;
                                    }
                                }
                                html += `</div>`;
                                return html;
                            })
                            .linkLabel((l) => {
                                let html = `<div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px; font-size: 11px;">`;
                                html += `<strong style="font-size:12px; color:#fff;">${l.type}</strong><br/>`;
                                if (l.props) {
                                    for (const [k, v] of Object.entries(
                                        l.props,
                                    )) {
                                        html += `<span style="color: #a5b4fc">${k}</span>: ${v}<br/>`;
                                    }
                                }
                                html += `</div>`;
                                return html;
                            })
                            .nodeColor((n) => {
                                const lbl =
                                    n.labels && n.labels.length > 0
                                        ? n.labels[0]
                                        : "Default";
                                return labelColors[lbl] || labelColors.Default;
                            })
                            .nodeCanvasObjectMode(() => "after")
                            .nodeCanvasObject((node, ctx, globalScale) => {
                                if (globalScale >= 0.6) {
                                    const label = node.name || node.id || "";
                                    const fontSize = 14 / globalScale;
                                    ctx.font = `${fontSize}px Inter, sans-serif`;
                                    ctx.textAlign = "center";
                                    ctx.textBaseline = "middle";
                                    
                                    ctx.lineWidth = 3 / globalScale;
                                    ctx.strokeStyle = "#0c0a1d";
                                    ctx.strokeText(label, node.x, node.y + 18 / globalScale);
                                    
                                    ctx.fillStyle = "rgba(255, 255, 255, 1)";
                                    ctx.fillText(label, node.x, node.y + 18 / globalScale);
                                }
                            })
                            .linkDirectionalArrowLength(4)
                            .linkDirectionalArrowRelPos(1)
                            .linkCanvasObjectMode(() => "after")
                            .linkCanvasObject((link, ctx, globalScale) => {
                                if (globalScale < 0.8) return;
                                const fontSize = 11 / globalScale;
                                const LABEL = link.type;
                                ctx.font = `${fontSize}px Inter, sans-serif`;
                                ctx.textAlign = "center";
                                ctx.textBaseline = "middle";
                                const start = link.source;
                                const end = link.target;
                                if (
                                    typeof start !== "object" ||
                                    typeof end !== "object"
                                )
                                    return;
                                const x = start.x + (end.x - start.x) / 2;
                                const y = start.y + (end.y - start.y) / 2;

                                const bckgDimensions = [
                                    ctx.measureText(LABEL).width + 6 / globalScale,
                                    fontSize + 4 / globalScale,
                                ];
                                ctx.fillStyle = "rgba(12, 10, 29, 0.85)";
                                ctx.fillRect(
                                    x - bckgDimensions[0] / 2,
                                    y - bckgDimensions[1] / 2,
                                    ...bckgDimensions,
                                );

                                ctx.fillStyle = "rgba(165, 180, 252, 0.9)";
                                ctx.fillText(LABEL, x, y);
                            })
                            .backgroundColor("#0c0a1d")
                            .linkColor(() => "rgba(165, 180, 252, 0.25)")
                            .nodeRelSize(12)
                            .enableZoomInteraction(true)
                            .enableNodeDrag(true);

                        myGraph.d3Force("link").distance(100);
                        myGraph.d3Force("charge").strength(-400).distanceMax(300);
                        if (myGraph.d3Force("center")) {
                            myGraph.d3Force("center").strength(0.05);
                        }

                        myGraph.onEngineStop(() => {
                            if (myGraph && !myGraph.hasZoomedToFit) {
                                myGraph.zoomToFit(600, 40);
                                myGraph.hasZoomedToFit = true;
                            }
                        });

                        setTimeout(() => {
                            if (graphContainer && myGraph)
                                myGraph.width(graphContainer.clientWidth);
                        }, 50);

                        const resizeObserver = new ResizeObserver((entries) => {
                            for (let entry of entries) {
                                if (myGraph) {
                                    myGraph.width(entry.contentRect.width);
                                }
                            }
                        });
                        resizeObserver.observe(graphContainer);
                    }
                })
                .catch((err) =>
                    console.error("Failed to load force-graph:", err),
                );
        }
    }

    function processStats(data, formatter = (x) => x) {
        if (!data) return [];
        return Object.entries(data)
            .filter(([k, v]) => {
                if (!k || k === "N/A" || k === "None" || k === "prefer_not_to_say") return false;
                const label = formatter(k);
                return label !== "—" && label !== "N/A" && label !== "-";
            })
            .sort((a, b) => b[1] - a[1]);
    }

    function genderLabel(g) {
        return (
            { male: "Laki-laki", female: "Perempuan", prefer_not_to_say: "—" }[
                g
            ] || g
        );
    }
    function purposeLabel(p) {
        return (
            {
                akademik: "Akademik",
                kerja: "Kerja",
                hobi: "Hobi",
                wisata: "Wisata",
                lainnya: "Lainnya",
            }[p] ||
            p ||
            "—"
        );
    }
    function levelLabel(l) {
        return (
            { beginner: "Pemula", basic: "Dasar", intermediate: "Menengah" }[
                l
            ] ||
            l ||
            "—"
        );
    }
</script>

<svelte:window on:keydown={handleKeydown} />

<div class="tab-header">
    <h2>📊 Analytics & Survey Data</h2>
    <div class="tab-actions">
        <button class="btn-export" on:click={() => exportUsers("csv")}>
            📥 Export All Data
        </button>
    </div>
</div>

{#if analytics}
    <div class="analytics-grid custom-scroll">
        <!-- Summary Cards -->
        <div class="stat-card stat-primary">
            <span class="stat-num">{analytics.total_students}</span>
            <span class="stat-label">Total Students</span>
        </div>
        <div class="stat-card">
            <span class="stat-num">{analytics.engagement?.avg_xp || 0}</span>
            <span class="stat-label">Rata-rata XP</span>
        </div>
        <div class="stat-card">
            <span class="stat-num">{analytics.engagement?.total_quests_taken || 0}</span>
            <span class="stat-label">Total Quest</span>
        </div>
        <div class="stat-card">
            <span class="stat-num">{analytics.engagement?.total_messages || 0}</span>
            <span class="stat-label">Total Chat</span>
        </div>

        <!-- Demographics -->
        <div class="chart-card">
            <h4>👤 Distribusi Gender</h4>
            <div class="dist-bars">
                {#each processStats(analytics.demographics?.gender, genderLabel) as [k, v]}
                    <div class="dist-row">
                        <span class="dist-label">{genderLabel(k)}</span>
                        <div class="dist-bar-bg">
                            <div
                                class="dist-bar-fill"
                                style="width: {Math.min((v / Math.max(analytics.total_students, 1)) * 100, 100)}%"
                            ></div>
                        </div>
                        <span class="dist-val">{v}</span>
                    </div>
                {/each}
            </div>
        </div>

        <div class="chart-card">
            <h4>🎂 Distribusi Umur</h4>
            <div class="dist-bars">
                {#each processStats(analytics.demographics?.age_groups) as [k, v]}
                    <div class="dist-row">
                        <span class="dist-label">{k}</span>
                        <div class="dist-bar-bg">
                            <div
                                class="dist-bar-fill bar-blue"
                                style="width: {Math.min((v / Math.max(analytics.total_students, 1)) * 100, 100)}%"
                            ></div>
                        </div>
                        <span class="dist-val">{v}</span>
                    </div>
                {/each}
            </div>
        </div>

        <div class="chart-card">
            <h4>🌏 Negara</h4>
            <div class="dist-bars">
                {#each processStats(analytics.demographics?.country) as [k, v]}
                    <div class="dist-row">
                        <span class="dist-label">{k}</span>
                        <div class="dist-bar-bg">
                            <div
                                class="dist-bar-fill bar-green"
                                style="width: {Math.min((v / Math.max(analytics.total_students, 1)) * 100, 100)}%"
                            ></div>
                        </div>
                        <span class="dist-val">{v}</span>
                    </div>
                {/each}
            </div>
        </div>

        <div class="chart-card">
            <h4>🎯 Tujuan Belajar</h4>
            <div class="dist-bars">
                {#each processStats(analytics.demographics?.study_purpose, purposeLabel) as [k, v]}
                    <div class="dist-row">
                        <span class="dist-label">{purposeLabel(k)}</span>
                        <div class="dist-bar-bg">
                            <div
                                class="dist-bar-fill bar-amber"
                                style="width: {Math.min((v / Math.max(analytics.total_students, 1)) * 100, 100)}%"
                            ></div>
                        </div>
                        <span class="dist-val">{v}</span>
                    </div>
                {/each}
            </div>
        </div>

        <!-- KG Stats -->
        <div class="chart-card chart-wide">
            <h4>🧠 Knowledge Graph</h4>
            <div class="kg-stats">
                <div class="kg-item">
                    <span class="kg-num">{analytics.knowledge_graph?.total_vocab || 0}</span>
                    <span>Vocab</span>
                </div>
                <div class="kg-item">
                    <span class="kg-num">{analytics.knowledge_graph?.total_kanji || 0}</span>
                    <span>Kanji</span>
                </div>
                <div class="kg-item">
                    <span class="kg-num">{analytics.knowledge_graph?.total_grammar || 0}</span>
                    <span>Grammar</span>
                </div>
            </div>
        </div>

        <!-- KG Interactive Visualization -->
        <div
            class="chart-card chart-wide"
            class:kg-fullscreen={kgFullscreen}
            style="position:relative;"
        >
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 14px;">
                <h4 style="margin:0;">🌐 Interactive Knowledge Graph (Neo4j)</h4>
            </div>
            <div class="kg-container">
                {#if kgLoading}
                    <div class="kg-loading">
                        <div class="admin-spinner"></div>
                        <p>Memuat Graph Data...</p>
                    </div>
                {:else if rawKgData && rawKgData.nodes && rawKgData.nodes.length > 0}
                    <div class="kg-stats-inline">
                        <span>Nodes: <strong>{rawKgData.nodes.length}</strong></span>
                        <span>Relationships: <strong>{rawKgData.links.length}</strong></span>
                    </div>
                    <div class="force-graph-wrapper" bind:this={graphContainer}></div>

                    <div class="kg-zoom-controls">
                        <button on:click={toggleFullscreen} title={kgFullscreen ? 'Keluar Fullscreen (ESC)' : 'Fullscreen'}>
                            {#if kgFullscreen}
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                                </svg>
                            {:else}
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3.75v4.5m0-4.5h4.5m-4.5 0L9 9M3.75 20.25v-4.5m0 4.5h4.5m-4.5 0L9 15M20.25 3.75h-4.5m4.5 0v4.5m0-4.5L15 9m5.25 11.25h-4.5m4.5 0v-4.5m0 4.5L15 15" />
                                </svg>
                            {/if}
                        </button>
                    </div>

                    <div class="kg-legend-overlay custom-scroll">
                        <div class="legend-section">
                            <strong>Nodes</strong>
                            <div class="legend-items">
                                {#each Object.entries(nodeCounts) as [lbl, count]}
                                    <div class="legend-item">
                                        <span
                                            class="legend-color"
                                            style="background-color: {labelColors[lbl] || labelColors.Default}"
                                        ></span>
                                        <span>{lbl} ({count})</span>
                                    </div>
                                {/each}
                            </div>
                        </div>
                        <div class="legend-section" style="margin-top: 12px;">
                            <strong>Relationships</strong>
                            <div class="legend-items">
                                {#each Object.entries(linkCounts) as [type, count]}
                                    <div class="legend-item">
                                        <span
                                            class="legend-color"
                                            style="background-color: rgba(255,255,255,0.4); border-radius: 2px; height:2px; width:12px; margin-right:4px;"
                                        ></span>
                                        <span>{type} ({count})</span>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {:else}
                    <p class="kg-empty">Tidak ada data di Knowledge Graph.</p>
                {/if}
            </div>
        </div>
    </div>
{:else}
    <div class="analytics-loading">
        <div class="admin-spinner"></div>
        <p>Memuat data statistik...</p>
    </div>
{/if}

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
    .tab-actions {
        display: flex;
        gap: 8px;
    }
    .btn-export {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.1);
        cursor: pointer;
        transition: all 0.2s;
        background: rgba(99, 102, 241, 0.1);
        color: #a5b4fc;
    }
    .btn-export:hover {
        background: rgba(99, 102, 241, 0.25);
    }

    /* Analytics Grid */
    .analytics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        overflow-y: auto;
        flex-grow: 1;
        padding-right: 4px;
    }
    .stat-card {
        background: rgba(15, 13, 36, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        min-height: 120px;
    }
    .stat-primary {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(15, 13, 36, 0.5) 100%);
        border-color: rgba(99, 102, 241, 0.3);
    }
    .stat-num {
        font-size: 32px;
        font-weight: 900;
        color: #fff;
    }
    .stat-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255, 255, 255, 0.4);
        margin-top: 8px;
    }
    .chart-card {
        background: rgba(15, 13, 36, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 24px;
        grid-column: span 2;
    }
    .chart-card h4 {
        margin: 0 0 16px 0;
        font-size: 13px;
        font-weight: 800;
        color: #fff;
    }
    .chart-wide {
        grid-column: span 4;
    }

    /* Distribution bars */
    .dist-bars {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .dist-row {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 12px;
    }
    .dist-label {
        width: 90px;
        color: rgba(255, 255, 255, 0.6);
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
    }
    .dist-bar-bg {
        flex-grow: 1;
        height: 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        overflow: hidden;
    }
    .dist-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1 0%, #a5b4fc 100%);
        border-radius: 10px;
    }
    .dist-bar-fill.bar-blue {
        background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
    }
    .dist-bar-fill.bar-green {
        background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
    }
    .dist-bar-fill.bar-amber {
        background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
    }
    .dist-val {
        width: 24px;
        text-align: right;
        font-weight: 700;
        color: #fff;
    }

    /* KG Stats layout */
    .kg-stats {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
    }
    .kg-item {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 14px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.5);
    }
    .kg-num {
        font-size: 24px;
        font-weight: 900;
        color: #fff;
        margin-bottom: 4px;
    }

    /* KG Visualization & Legend */
    .kg-container {
        height: 500px;
        background: #0c0a1d;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
    }
    .kg-fullscreen .kg-container {
        height: 100%;
        border-radius: 0;
        border: none;
    }
    .kg-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: rgba(255, 255, 255, 0.4);
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
    .kg-stats-inline {
        position: absolute;
        top: 10px;
        left: 10px;
        z-index: 10;
        display: flex;
        gap: 15px;
        background: rgba(15, 13, 36, 0.8);
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 11px;
        color: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .kg-stats-inline strong {
        color: #a5b4fc;
        font-weight: 800;
        font-size: 12px;
    }
    .force-graph-wrapper {
        width: 100%;
        height: 100%;
    }
    .kg-zoom-controls {
        position: absolute;
        bottom: 16px;
        left: 16px;
        display: flex;
        gap: 6px;
        z-index: 10;
        background: rgba(15, 13, 36, 0.8);
        padding: 6px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(4px);
    }
    .kg-fullscreen .kg-zoom-controls {
        bottom: 60px;
    }
    .kg-zoom-controls button {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #a5b4fc;
        width: 28px;
        height: 28px;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    .kg-zoom-controls button:hover {
        background: rgba(99, 102, 241, 0.35);
        color: #fff;
    }
    .kg-legend-overlay {
        position: absolute;
        top: 10px;
        right: 10px;
        width: 180px;
        max-height: calc(100% - 20px);
        overflow-y: auto;
        background: rgba(12, 10, 29, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        font-size: 11px;
        color: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(8px);
        z-index: 10;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    .legend-section strong {
        color: #fff;
        display: block;
        margin-bottom: 6px;
        font-size: 11px;
    }
    .legend-items {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 10px;
    }
    .legend-color {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .kg-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: rgba(255, 255, 255, 0.45);
        font-size: 13px;
    }
    .analytics-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        color: rgba(255, 255, 255, 0.5);
        gap: 12px;
        flex-grow: 1;
    }

    /* Fullscreen specific wrapper style overrides */
    .kg-fullscreen {
        position: fixed !important;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 9999 !important;
        margin: 0 !important;
        border-radius: 0 !important;
        background: #0c0a1d;
    }
</style>
