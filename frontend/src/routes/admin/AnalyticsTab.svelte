<script>
    import { onMount } from "svelte";

    export let user;
    export let API;

    let loading = true;
    let analyticsData = null;
    let users = [];
    let students = [];
    let selectedUser = null;

    // Search & Filter State
    let searchQuery = "";
    let filterPurpose = "all";
    let filterLevel = "all";
    let sortBy = "xp"; // 'xp' | 'score' | 'name'

    // Overall KPI Stats
    let stats = {
        totalStudents: 0,
        avgXp: 0,
        avgQuestScore: 0,
        totalQuests: 0,
        avgVocab: 0,
        avgGrammar: 0,
        avgKanji: 0
    };

    // Color Palettes
    const donutColors = ["#6366f1", "#ec4899", "#10b981", "#f59e0b", "#8b5cf6", "#6b7280"];
    const genderColors = ["#3b82f6", "#f43f5e", "#6b7280"];

    onMount(async () => {
        await loadData();
    });

    async function loadData() {
        loading = true;
        try {
            // Fetch demographics & overall analytics
            const resAnal = await fetch(`${API}/analytics?admin_id=${user.id}`);
            analyticsData = await resAnal.json();

            // Fetch user-level details
            const resUsers = await fetch(`${API}/users?admin_id=${user.id}`);
            users = await resUsers.json();
            students = users.filter(u => u.role !== "admin");

            if (students.length > 0) {
                selectedUser = students[0];
            }

            calculateSummary();
        } catch (e) {
            console.error("Gagal memuat data analisis:", e);
        } finally {
            loading = false;
        }
    }

    function calculateSummary() {
        if (!students || students.length === 0) return;

        stats.totalStudents = students.length;

        let totalXp = 0;
        let totalQuestScore = 0;
        let questCount = 0;
        let totalVocab = 0;
        let totalGrammar = 0;
        let totalKanji = 0;

        students.forEach(u => {
            totalXp += (u.xp || 0);
            if (u.quest_avg_score > 0) {
                totalQuestScore += u.quest_avg_score;
                questCount++;
            }
            totalVocab += (u.neo4j_stats?.vocab_learned || 0);
            totalGrammar += (u.neo4j_stats?.grammar_learned || 0);
            totalKanji += (u.neo4j_stats?.kanji_mastered || 0);
        });

        stats.avgXp = Math.round(totalXp / Math.max(students.length, 1));
        stats.avgQuestScore = questCount > 0 ? Math.round(totalQuestScore / questCount * 10) / 10 : 0;
        stats.totalQuests = students.reduce((acc, u) => acc + (u.quest_count || 0), 0);
        stats.avgVocab = Math.round(totalVocab / Math.max(students.length, 1) * 10) / 10;
        stats.avgGrammar = Math.round(totalGrammar / Math.max(students.length, 1) * 10) / 10;
        stats.avgKanji = Math.round(totalKanji / Math.max(students.length, 1) * 10) / 10;
    }

    // --- Donut Chart Helper Functions ---
    function makeSlicePath(startPercent, endPercent, radius, innerRadius) {
        const cx = radius;
        const cy = radius;
        
        const startAngle = startPercent * 2 * Math.PI - Math.PI / 2;
        const endAngle = endPercent * 2 * Math.PI - Math.PI / 2;
        
        const x1 = cx + radius * Math.cos(startAngle);
        const y1 = cy + radius * Math.sin(startAngle);
        const x2 = cx + radius * Math.cos(endAngle);
        const y2 = cy + radius * Math.sin(endAngle);
        
        const ix1 = cx + innerRadius * Math.cos(startAngle);
        const iy1 = cy + innerRadius * Math.sin(startAngle);
        const ix2 = cx + innerRadius * Math.cos(endAngle);
        const iy2 = cy + innerRadius * Math.sin(endAngle);
        
        const largeArcFlag = (endPercent - startPercent) > 0.5 ? 1 : 0;
        
        return `
            M ${x1} ${y1}
            A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}
            L ${ix2} ${iy2}
            A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${ix1} ${iy1}
            Z
        `;
    }

    function prepareDonutData(dict, colors) {
        if (!dict) return [];
        const entries = Object.entries(dict).map(([key, val]) => ({
            label: formatCategoryLabel(key),
            value: val
        })).filter(e => e.value > 0);
        
        const total = entries.reduce((acc, e) => acc + e.value, 0);
        if (total === 0) return [];
        
        let currentPercent = 0;
        return entries.map((entry, idx) => {
            const pct = entry.value / total;
            const startPercent = currentPercent;
            const endPercent = Math.min(startPercent + pct, 0.9999);
            currentPercent += pct;
            
            const color = colors[idx % colors.length];
            const path = makeSlicePath(startPercent, endPercent, 100, 62);
            
            return {
                ...entry,
                percentage: Math.round(pct * 100),
                path,
                color
            };
        });
    }

    function formatCategoryLabel(key) {
        const mapping = {
            akademik: "Akademik",
            kerja: "Karir/Kerja",
            hobi: "Minat/Hobi",
            wisata: "Wisata/Travel",
            lainnya: "Lainnya",
            male: "Laki-laki",
            female: "Perempuan",
            prefer_not_to_say: "Tidak Mengisi",
            "N/A": "Tidak Diketahui"
        };
        return mapping[key] || key;
    }

    // --- Bar Chart Helpers ---
    function prepareLevelData(dict) {
        if (!dict) return [];
        const order = ["beginner", "basic", "intermediate"];
        const labels = { beginner: "Pemula (Beginner)", basic: "Dasar (Basic)", intermediate: "Menengah (Intermediate)" };
        const colors = { beginner: "#3b82f6", basic: "#10b981", intermediate: "#8b5cf6" };
        
        const total = Object.values(dict).reduce((acc, v) => acc + v, 0);
        return order.map(key => {
            const count = dict[key] || 0;
            const pct = total > 0 ? (count / total) * 100 : 0;
            return {
                key,
                label: labels[key] || key,
                count,
                percentage: Math.round(pct),
                color: colors[key] || "#6b7280"
            };
        });
    }

    function calculateScoreDistribution(studentList) {
        const brackets = [
            { label: "Sangat Baik (90-100)", count: 0, color: "#10b981" },
            { label: "Baik (75-89)", count: 0, color: "#6366f1" },
            { label: "Cukup (60-74)", count: 0, color: "#f59e0b" },
            { label: "Kurang (<60)", count: 0, color: "#f43f5e" },
            { label: "Belum Ikut", count: 0, color: "#6b7280" }
        ];
        
        studentList.forEach(u => {
            const score = u.quest_avg_score;
            if (u.quest_count === 0 || score === 0 || score === undefined || score === null) {
                brackets[4].count++;
            } else if (score >= 90) {
                brackets[0].count++;
            } else if (score >= 75) {
                brackets[1].count++;
            } else if (score >= 60) {
                brackets[2].count++;
            } else {
                brackets[3].count++;
            }
        });
        
        const maxCount = Math.max(...brackets.map(b => b.count), 1);
        return brackets.map(b => ({
            ...b,
            heightPercent: Math.max((b.count / maxCount) * 80, 5) // Min height 5% for readability
        }));
    }

    // --- Filters and Sorting ---
    let filteredStudents = [];
    $: {
        let list = [...students];
        
        // Search
        if (searchQuery.trim()) {
            const q = searchQuery.toLowerCase();
            list = list.filter(u => 
                (u.full_name || "").toLowerCase().includes(q) ||
                (u.email || "").toLowerCase().includes(q)
            );
        }

        // Filter Purpose
        if (filterPurpose !== "all") {
            list = list.filter(u => u.study_purpose === filterPurpose);
        }

        // Filter Level
        if (filterLevel !== "all") {
            list = list.filter(u => u.japanese_level === filterLevel);
        }

        // Sorting
        if (sortBy === "xp") {
            list.sort((a, b) => (b.xp || 0) - (a.xp || 0));
        } else if (sortBy === "score") {
            list.sort((a, b) => (b.quest_avg_score || 0) - (a.quest_avg_score || 0));
        } else if (sortBy === "name") {
            list.sort((a, b) => (a.full_name || "").localeCompare(b.full_name || ""));
        }

        filteredStudents = list;
    }

    function selectUser(userObj) {
        selectedUser = userObj;
    }

    $: purposeData = prepareDonutData(analyticsData?.demographics?.study_purpose, donutColors);
    $: genderData = prepareDonutData(analyticsData?.demographics?.gender, genderColors);
    $: levelData = prepareLevelData(analyticsData?.demographics?.japanese_level);
    $: scoreDist = calculateScoreDistribution(students);
</script>

<div class="analytics-tab custom-scroll">
    <div class="tab-header">
        <div>
            <h2>📊 Analisis & Evaluasi Pengguna</h2>
            <p class="subtitle">Evaluasi demografi, tingkat kelulusan quest, dan status penguasaan materi siswa secara real-time.</p>
        </div>
    </div>

    {#if loading}
        <div class="analytics-loading">
            <div class="admin-spinner"></div>
            <p>Menganalisis data pengguna...</p>
        </div>
    {:else}
        <!-- KPI Cards Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon icon-users">👥</div>
                <div class="kpi-content">
                    <span class="kpi-label">Total Target User</span>
                    <span class="kpi-value">{stats.totalStudents} <span class="unit">Siswa</span></span>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon icon-xp">⚡</div>
                <div class="kpi-content">
                    <span class="kpi-label">Rata-rata XP</span>
                    <span class="kpi-value">{stats.avgXp.toLocaleString()} <span class="unit">XP</span></span>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon icon-score">🏆</div>
                <div class="kpi-content">
                    <span class="kpi-label">Rata-rata Nilai Quest</span>
                    <span class="kpi-value">{stats.avgQuestScore} <span class="unit">/ 100</span></span>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon icon-book">📚</div>
                <div class="kpi-content">
                    <span class="kpi-label">Total Penyelesaian Quest</span>
                    <span class="kpi-value">{stats.totalQuests} <span class="unit">Quest</span></span>
                </div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="charts-grid">
            <!-- Donut Chart: Study Purpose -->
            <div class="chart-box">
                <h3>🎯 Distribusi Tujuan Belajar</h3>
                <div class="donut-wrapper">
                    {#if purposeData.length > 0}
                        <svg class="donut-svg" viewBox="0 0 200 200">
                            {#each purposeData as slice}
                                <path
                                    d={slice.path}
                                    fill={slice.color}
                                    class="donut-segment"
                                    title="{slice.label}: {slice.value} ({slice.percentage}%)"
                                />
                            {/each}
                        </svg>
                        <div class="donut-legend custom-scroll">
                            {#each purposeData as slice}
                                <div class="legend-item">
                                    <span class="color-dot" style="background: {slice.color}"></span>
                                    <span class="legend-label">{slice.label}</span>
                                    <span class="legend-value">{slice.value} ({slice.percentage}%)</span>
                                </div>
                            {/each}
                        </div>
                    {:else}
                        <p class="no-data">Data tidak tersedia</p>
                    {/if}
                </div>
            </div>

            <!-- Horizontal Bars: Japanese Level -->
            <div class="chart-box">
                <h3>📈 Tingkat Kemampuan Awal</h3>
                <div class="bar-list-wrapper">
                    {#each levelData as lvl}
                        <div class="bar-row">
                            <div class="bar-info">
                                <span class="lvl-label">{lvl.label}</span>
                                <span class="lvl-count">{lvl.count} siswa ({lvl.percentage}%)</span>
                            </div>
                            <div class="progress-track">
                                <div 
                                    class="progress-bar-fill" 
                                    style="width: {lvl.percentage}%; background: {lvl.color}"
                                ></div>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>

            <!-- Vertical Bar Chart: Score Distribution -->
            <div class="chart-box">
                <h3>🏆 Distribusi Rerata Nilai</h3>
                <div class="vertical-chart-container">
                    <div class="vertical-bars">
                        {#each scoreDist as bar}
                            <div class="v-bar-wrapper">
                                <div class="v-bar-tooltip">{bar.count} siswa</div>
                                <div 
                                    class="v-bar-fill" 
                                    style="height: {bar.heightPercent}%; background: {bar.color}"
                                ></div>
                                <span class="v-bar-label">{bar.label.split(' ')[0]}</span>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Donut Chart: Gender Distribution -->
            <div class="chart-box">
                <h3>👥 Demografi Gender</h3>
                <div class="donut-wrapper">
                    {#if genderData.length > 0}
                        <svg class="donut-svg" viewBox="0 0 200 200">
                            {#each genderData as slice}
                                <path
                                    d={slice.path}
                                    fill={slice.color}
                                    class="donut-segment"
                                    title="{slice.label}: {slice.value} ({slice.percentage}%)"
                                />
                            {/each}
                        </svg>
                        <div class="donut-legend custom-scroll">
                            {#each genderData as slice}
                                <div class="legend-item">
                                    <span class="color-dot" style="background: {slice.color}"></span>
                                    <span class="legend-label">{slice.label}</span>
                                    <span class="legend-value">{slice.value} ({slice.percentage}%)</span>
                                </div>
                            {/each}
                        </div>
                    {:else}
                        <p class="no-data">Data tidak tersedia</p>
                    {/if}
                </div>
            </div>
        </div>

        <!-- Single Column Full Width Table: Student Evaluation List -->
        <div class="evaluation-container">
            <div class="box-header-row">
                <h3>👥 Daftar Evaluasi & Progres Siswa</h3>
                <div class="sorting-controls">
                    <span class="sort-lbl">Urutkan:</span>
                    <select bind:value={sortBy} class="admin-select select-mini">
                        <option value="xp">XP Tertinggi</option>
                        <option value="score">Nilai Quest</option>
                        <option value="name">Nama (A-Z)</option>
                    </select>
                </div>
            </div>

            <!-- Filters -->
            <div class="filters-row">
                <input 
                    type="text" 
                    placeholder="Cari nama atau email siswa..." 
                    bind:value={searchQuery}
                    class="admin-input search-input"
                />
                <select bind:value={filterPurpose} class="admin-select">
                    <option value="all">Semua Tujuan Belajar</option>
                    <option value="akademik">Akademik</option>
                    <option value="kerja">Kerja</option>
                    <option value="hobi">Hobi</option>
                    <option value="wisata">Wisata</option>
                </select>
                <select bind:value={filterLevel} class="admin-select">
                    <option value="all">Semua Tingkat Kemampuan</option>
                    <option value="beginner">Pemula</option>
                    <option value="basic">Dasar</option>
                    <option value="intermediate">Menengah</option>
                </select>
            </div>

            <div class="scrollable-table-wrapper custom-scroll">
                <table class="evaluation-table">
                    <thead>
                        <tr>
                            <th>Siswa</th>
                            <th>Tujuan Belajar</th>
                            <th>Tingkat JP</th>
                            <th>XP & Level</th>
                            <th>Mastery Vocab</th>
                            <th>Mastery Grammar</th>
                            <th>Mastery Kanji</th>
                            <th>Rerata Quest</th>
                            <th>Status Evaluasi</th>
                        </tr>
                    </thead>
                    <tbody>
                        {#each filteredStudents as u}
                            <tr>
                                <td>
                                    <div class="user-info-col">
                                        <span class="u-name">{u.full_name || "Tanpa Nama"}</span>
                                        <span class="u-email">{u.email || "—"}</span>
                                    </div>
                                </td>
                                <td><span class="val-txt">{formatCategoryLabel(u.study_purpose)}</span></td>
                                <td><span class="val-txt">{formatCategoryLabel(u.japanese_level)}</span></td>
                                <td>
                                    <div class="xp-level-col">
                                        <span class="val-xp">⚡ {u.xp || 0} XP</span>
                                        <span class="val-level">Lv {u.level || 1}</span>
                                    </div>
                                </td>
                                <td>
                                    <div class="mastery-cell-col">
                                        <span class="mastery-text">{u.neo4j_stats?.vocab_learned || 0} <span class="divider">/</span> {analyticsData?.knowledge_graph?.total_vocab || 149}</span>
                                        <div class="mini-bar-track">
                                            <div class="mini-bar-fill fill-vocab" style="width: {Math.min(((u.neo4j_stats?.vocab_learned || 0) / (analyticsData?.knowledge_graph?.total_vocab || 149)) * 100, 100)}%"></div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="mastery-cell-col">
                                        <span class="mastery-text">{u.neo4j_stats?.grammar_learned || 0} <span class="divider">/</span> {analyticsData?.knowledge_graph?.total_grammar || 104}</span>
                                        <div class="mini-bar-track">
                                            <div class="mini-bar-fill fill-grammar" style="width: {Math.min(((u.neo4j_stats?.grammar_learned || 0) / (analyticsData?.knowledge_graph?.total_grammar || 104)) * 100, 100)}%"></div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <div class="mastery-cell-col">
                                        <span class="mastery-text">{u.neo4j_stats?.kanji_mastered || 0} <span class="divider">/</span> {analyticsData?.knowledge_graph?.total_kanji || 103}</span>
                                        <div class="mini-bar-track">
                                            <div class="mini-bar-fill fill-kanji" style="width: {Math.min(((u.neo4j_stats?.kanji_mastered || 0) / (analyticsData?.knowledge_graph?.total_kanji || 103)) * 100, 100)}%"></div>
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <span class="val-score" class:low-score={u.quest_avg_score > 0 && u.quest_avg_score < 70}>
                                        {u.quest_avg_score > 0 ? `${u.quest_avg_score} / 100` : "—"}
                                    </span>
                                </td>
                                <td>
                                    {#if u.quest_count === 0}
                                        <span class="status-badge badge-gray">⚠️ Belum Mengerjakan</span>
                                    {:else if u.quest_avg_score < 70}
                                        <span class="status-badge badge-red">🚨 Butuh Pendampingan</span>
                                    {:else}
                                        <span class="status-badge badge-green">✅ Sangat Baik</span>
                                    {/if}
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="9" class="no-results-table">Tidak ada siswa yang cocok dengan filter pencarian</td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        </div>
    {/if}
</div>

<style>
    .analytics-tab {
        display: flex;
        flex-direction: column;
        gap: 24px;
        flex-grow: 1;
        overflow-y: auto;
        padding-right: 4px;
    }

    .tab-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 14px;
        flex-shrink: 0;
    }
    .tab-header h2 {
        font-size: 20px;
        font-weight: 900;
        margin: 0;
        color: #fff;
    }
    .subtitle {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.4);
        margin: 4px 0 0;
    }

    .analytics-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px;
        color: rgba(255, 255, 255, 0.5);
        gap: 12px;
        flex-grow: 1;
    }
    .admin-spinner {
        width: 32px;
        height: 32px;
        border: 3px solid rgba(99, 102, 241, 0.2);
        border-top-color: #6366f1;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        flex-shrink: 0;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 18px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        border-color: rgba(99, 102, 241, 0.2);
    }
    .kpi-icon {
        font-size: 28px;
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
    }
    .icon-users { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .icon-xp { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .icon-score { background: rgba(16, 185, 129, 0.15); color: #34d399; }
    .icon-book { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
    
    .kpi-content {
        display: flex;
        flex-direction: column;
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: rgba(255, 255, 255, 0.4);
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 800;
        color: #fff;
        margin-top: 4px;
    }
    .kpi-value .unit {
        font-size: 11px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.35);
        margin-left: 2px;
    }

    /* Charts Layout */
    .charts-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        flex-shrink: 0;
    }
    @media (max-width: 900px) {
        .charts-grid {
            grid-template-columns: 1fr;
        }
    }
    .chart-box {
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        min-height: 360px;
    }
    .chart-box h3 {
        font-size: 14px;
        font-weight: 800;
        color: #fff;
        margin: 0 0 16px;
        border-left: 3px solid #6366f1;
        padding-left: 10px;
    }

    /* Donut styles */
    .donut-wrapper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 24px;
        flex-grow: 1;
    }
    .donut-svg {
        width: 160px;
        height: 160px;
        flex-shrink: 0;
        transform: rotate(-90deg);
    }
    .donut-segment {
        transition: stroke-width 0.2s, filter 0.2s, transform 0.2s;
        transform-origin: center;
        cursor: pointer;
    }
    .donut-segment:hover {
        filter: brightness(1.15) drop-shadow(0 0 4px rgba(255, 255, 255, 0.1));
        transform: scale(1.03);
    }
    .donut-legend {
        display: flex;
        flex-direction: column;
        gap: 8px;
        overflow-y: auto;
        max-height: 220px;
        flex-grow: 1;
        padding-right: 4px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        font-size: 11px;
    }
    .color-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
        flex-shrink: 0;
    }
    .legend-label {
        color: rgba(255, 255, 255, 0.5);
        margin-right: auto;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .legend-value {
        color: #fff;
        font-weight: 600;
        margin-left: 8px;
    }

    /* Horizontal Progress bars */
    .bar-list-wrapper {
        display: flex;
        flex-direction: column;
        gap: 16px;
        justify-content: center;
        flex-grow: 1;
    }
    .bar-row {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .bar-info {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
    }
    .lvl-label {
        color: rgba(255, 255, 255, 0.65);
        font-weight: 600;
    }
    .lvl-count {
        color: rgba(255, 255, 255, 0.4);
    }
    .progress-track {
        height: 8px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s ease-out;
    }

    /* Vertical Score Dist chart */
    .vertical-chart-container {
        display: flex;
        align-items: flex-end;
        justify-content: center;
        flex-grow: 1;
        height: 250px;
    }
    .vertical-bars {
        display: flex;
        justify-content: space-around;
        width: 100%;
        height: 100%;
        align-items: flex-end;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
    }
    .v-bar-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 16%;
        position: relative;
        height: 100%;
        justify-content: flex-end;
    }
    .v-bar-fill {
        width: 100%;
        border-radius: 6px 6px 0 0;
        transition: height 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
    }
    .v-bar-fill:hover {
        filter: brightness(1.2);
    }
    .v-bar-fill:hover + .v-bar-tooltip,
    .v-bar-wrapper:hover .v-bar-tooltip {
        opacity: 1;
        visibility: visible;
        transform: translateY(-8px);
    }
    .v-bar-tooltip {
        position: absolute;
        bottom: 100%;
        background: #1e1b4b;
        border: 1px solid #4f46e5;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 10px;
        color: #fff;
        opacity: 0;
        visibility: hidden;
        transition: all 0.2s;
        pointer-events: none;
        white-space: nowrap;
        z-index: 100;
    }
    .v-bar-label {
        font-size: 9px;
        color: rgba(255, 255, 255, 0.4);
        margin-top: 8px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        width: 100%;
    }

    /* Evaluation Table Container */
    .evaluation-container {
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 16px;
        padding: 24px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        max-height: 480px;
        margin-bottom: 12px;
        flex-shrink: 0;
    }

    .box-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        flex-shrink: 0;
    }
    .box-header-row h3 {
        font-size: 15px;
        font-weight: 800;
        color: #fff;
        margin: 0;
    }

    /* Filters inside evaluation box */
    .filters-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: 8px;
        margin-bottom: 14px;
        flex-shrink: 0;
    }
    .admin-input, .admin-select {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        color: #e2e8f0;
        font-size: 11px;
        padding: 8px 12px;
        outline: none;
        width: 100%;
        transition: all 0.2s;
    }
    .admin-input:focus, .admin-select:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
    }
    .select-mini {
        width: auto;
        padding: 4px 8px;
    }
    .sorting-controls {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .sort-lbl {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.4);
        font-weight: 600;
    }

    /* Scrollable table wrapper */
    .scrollable-table-wrapper {
        overflow-x: auto;
        overflow-y: auto;
        flex-grow: 1;
        margin-top: 8px;
    }

    /* Evaluation Table */
    .evaluation-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 11px;
        min-width: 1000px;
    }
    .evaluation-table th {
        position: sticky;
        top: 0;
        background: #120f2e;
        padding: 12px 14px;
        font-weight: 800;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: rgba(255, 255, 255, 0.45);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        text-align: left;
        z-index: 10;
        white-space: nowrap;
    }
    .evaluation-table td {
        padding: 10px 14px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        color: rgba(255, 255, 255, 0.7);
        vertical-align: middle;
        white-space: nowrap;
    }
    .evaluation-table tr:hover td {
        background: rgba(99, 102, 241, 0.04);
    }

    .user-info-col {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .u-name {
        font-weight: 700;
        color: #fff;
        font-size: 12px;
    }
    .u-email {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.4);
    }

    .xp-level-col {
        display: flex;
        flex-direction: column;
        gap: 2px;
        font-weight: 700;
    }
    .val-xp {
        color: #f59e0b;
    }
    .val-level {
        color: #a5b4fc;
        font-size: 10px;
    }
    .val-txt {
        color: rgba(255, 255, 255, 0.75);
    }

    .mastery-cell-col {
        display: flex;
        flex-direction: column;
        gap: 4px;
        width: 100px;
    }
    .mastery-text {
        font-size: 10px;
        font-weight: 700;
        color: #fff;
    }
    .mastery-text .divider {
        color: rgba(255, 255, 255, 0.2);
        font-weight: 400;
    }
    .mini-bar-track {
        height: 4px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 2px;
        overflow: hidden;
    }
    .mini-bar-fill {
        height: 100%;
        border-radius: 2px;
    }
    .fill-vocab { background: #3b82f6; }
    .fill-grammar { background: #ec4899; }
    .fill-kanji { background: #10b981; }

    .val-score {
        font-weight: 800;
        color: #10b981;
    }
    .val-score.low-score {
        color: #f43f5e;
    }

    .status-badge {
        font-size: 9px;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        display: inline-block;
        white-space: nowrap;
    }
    .badge-gray {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .badge-red {
        background: rgba(244, 63, 94, 0.1);
        color: #f43f5e;
        border: 1px solid rgba(244, 63, 94, 0.18);
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.18);
    }

    .no-results-table {
        text-align: center;
        color: rgba(255, 255, 255, 0.3);
        padding: 30px;
        font-size: 11px;
    }

    .no-data {
        color: rgba(255, 255, 255, 0.3);
        font-size: 11px;
    }

    /* Responsive */
    @media (max-width: 1100px) {
        .filters-row {
            grid-template-columns: 1fr;
        }
    }
</style>
