<script>
    import { onMount } from "svelte";

    export let user;
    export let API;

    let users = [];
    let loading = true;

    onMount(async () => {
        await loadUsers();
    });

    async function loadUsers() {
        loading = true;
        try {
            const res = await fetch(`${API}/users?admin_id=${user.id}`);
            users = await res.json();
        } catch (e) {
            console.error("Gagal memuat pengguna:", e);
        } finally {
            loading = false;
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

<div class="tab-header">
    <h2>📋 Semua Pengguna ({users.length})</h2>
    <div class="tab-actions">
        <button class="btn-export" on:click={() => exportUsers("csv")}>
            📥 Export CSV
        </button>
        <button class="btn-export" on:click={() => exportUsers("json")}>
            📥 Export JSON
        </button>
    </div>
</div>

{#if loading}
    <div class="users-loading">
        <div class="admin-spinner"></div>
        <p>Memuat daftar pengguna...</p>
    </div>
{:else}
    <div class="table-wrap custom-scroll">
        <table class="admin-table">
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Nama</th>
                    <th>Umur</th>
                    <th>Gender</th>
                    <th>Negara</th>
                    <th>Tujuan</th>
                    <th>Level JP</th>
                    <th>XP</th>
                    <th>Lv</th>
                    <th>Vocab</th>
                    <th>Grammar</th>
                    <th>Kanji</th>
                    <th>Quest Avg</th>
                </tr>
            </thead>
            <tbody>
                {#each users as u}
                    <tr class:admin-row={u.role === "admin"}>
                        <td class="td-email">{u.email || "—"}</td>
                        <td>{u.full_name || "—"}</td>
                        <td class="td-center">{u.age || "—"}</td>
                        <td class="td-center">{genderLabel(u.gender)}</td>
                        <td>{u.country || "—"}</td>
                        <td>{purposeLabel(u.study_purpose)}</td>
                        <td>{levelLabel(u.japanese_level)}</td>
                        <td class="td-center td-xp">{u.xp || 0}</td>
                        <td class="td-center">{u.level || 1}</td>
                        <td class="td-center">{u.neo4j_stats?.vocab_learned || 0}</td>
                        <td class="td-center">{u.neo4j_stats?.grammar_learned || 0}</td>
                        <td class="td-center">{u.neo4j_stats?.kanji_mastered || 0}</td>
                        <td class="td-center">{u.quest_avg_score || 0}</td>
                    </tr>
                {/each}
            </tbody>
        </table>
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
    .users-loading {
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
    .admin-table tr:hover td {
        background: rgba(99, 102, 241, 0.04);
    }
    .admin-row td {
        color: rgba(251, 191, 36, 0.8);
    }
    .td-center {
        text-align: center;
    }
    .td-email {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.5);
    }
    .td-xp {
        color: #a5b4fc;
        font-weight: 700;
    }
</style>
