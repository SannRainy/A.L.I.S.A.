<script>
    import { onMount, onDestroy } from "svelte";
    import { user, initAuth } from "../../stores/auth_store";
    import { goto } from "$app/navigation";

    // Import modular components
    import UsersTab from "./UsersTab.svelte";
    import DataPipelineTab from "./DataPipelineTab.svelte";
    import IngestTab from "./IngestTab.svelte";
    import AnalyticsTab from "./AnalyticsTab.svelte";
    import AiModelsTab from "./AiModelsTab.svelte";

    let isAdmin = false;
    let loading = true;
    let adminProfile = null;

    // Tab state
    let activeTab = "users";

    const API = "http://localhost:8000/api/v1/admin";

    onMount(async () => {
        if (typeof document !== "undefined") {
            document.body.style.overflow = "hidden";
            document.body.style.height = "100vh";
        }
        await initAuth();
        if (!$user) {
            goto("/");
            return;
        }

        try {
            const res = await fetch(
                `http://localhost:8000/api/v1/user/profile/${$user.id}`,
            );
            const profile = await res.json();
            if (profile.role !== "admin") {
                goto("/");
                return;
            }
            adminProfile = profile;
            isAdmin = true;
        } catch (e) {
            console.error("Admin check failed:", e);
            goto("/");
        } finally {
            loading = false;
        }
    });

    onDestroy(() => {
        if (typeof document !== "undefined") {
            document.body.style.overflow = "";
            document.body.style.height = "";
        }
    });

    function handleTabClick(tab) {
        activeTab = tab;
    }
</script>

<svelte:head>
    <title>TVJP Admin Dashboard</title>
    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap"
        rel="stylesheet"
    />
</svelte:head>

{#if loading}
    <div class="admin-loading">
        <div class="admin-spinner"></div>
        <p>Memverifikasi akses admin...</p>
    </div>
{:else if isAdmin}
    <div class="admin-shell">
        <!-- Header -->
        <header class="admin-header">
            <div class="admin-brand">
                <span class="brand-icon">🏯</span>
                <div>
                    <h1>TVJP Admin</h1>
                    <p>{adminProfile?.email}</p>
                </div>
            </div>
            <a href="/" class="admin-back-btn">← Kembali ke App</a>
        </header>

        <!-- Tab Nav -->
        <nav class="admin-nav">
            {#each [{ id: "users", icon: "👥", label: "Users" }, { id: "data", icon: "📚", label: "Data Pipeline" }, { id: "ingest", icon: "🔄", label: "Ingest Neo4j" }, { id: "analytics", icon: "📊", label: "Analytics" }, { id: "models", icon: "🤖", label: "AI Models" }] as tab}
                <button
                    class="nav-tab"
                    class:active={activeTab === tab.id}
                    on:click={() => handleTabClick(tab.id)}
                >
                    <span>{tab.icon}</span>
                    {tab.label}
                </button>
            {/each}
        </nav>

        <!-- Content -->
        <main class="admin-content">
            {#if activeTab === "users"}
                <UsersTab user={$user} {API} />
            {:else if activeTab === "data"}
                <DataPipelineTab user={$user} {API} />
            {:else if activeTab === "ingest"}
                <IngestTab user={$user} {API} />
            {:else if activeTab === "analytics"}
                <AnalyticsTab user={$user} {API} />
            {:else if activeTab === "models"}
                <AiModelsTab user={$user} {API} />
            {/if}
        </main>
    </div>
{/if}

<style>
    :global(body) {
        margin: 0;
        background: #0c0a1d;
    }
    * {
        box-sizing: border-box;
    }

    .admin-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        color: rgba(255, 255, 255, 0.5);
        font-family: "Inter", sans-serif;
        gap: 16px;
    }
    .admin-spinner {
        width: 36px;
        height: 36px;
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

    .admin-shell {
        font-family: "Inter", sans-serif;
        color: #e2e8f0;
        height: 100vh;
        background: linear-gradient(
            135deg,
            #0c0a1d 0%,
            #1a1145 50%,
            #0f0d24 100%
        );
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    /* Header */
    .admin-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 32px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        flex-shrink: 0;
    }
    .admin-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-icon {
        font-size: 32px;
    }
    .admin-brand h1 {
        font-size: 20px;
        font-weight: 900;
        margin: 0;
        color: #fff;
    }
    .admin-brand p {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.4);
        margin: 2px 0 0;
    }
    .admin-back-btn {
        padding: 8px 18px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.6);
        text-decoration: none;
        transition: all 0.2s;
    }
    .admin-back-btn:hover {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
    }

    /* Nav */
    .admin-nav {
        display: flex;
        gap: 4px;
        padding: 12px 32px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        flex-shrink: 0;
    }
    .nav-tab {
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 700;
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.45);
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .nav-tab:hover {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.7);
    }
    .nav-tab.active {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
    }

    /* Content */
    .admin-content {
        padding: 24px 32px;
        max-width: 1400px;
        margin: 0 auto;
        width: 100%;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    /* Custom Scrollbar for layout */
    :global(.custom-scroll::-webkit-scrollbar) {
        width: 6px;
        height: 6px;
    }
    :global(.custom-scroll::-webkit-scrollbar-track) {
        background: transparent;
    }
    :global(.custom-scroll::-webkit-scrollbar-thumb) {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    :global(.custom-scroll::-webkit-scrollbar-thumb:hover) {
        background: rgba(255, 255, 255, 0.25);
    }

    /* Responsive */
    @media (max-width: 900px) {
        .admin-header {
            padding: 16px 20px;
        }
        .admin-nav {
            padding: 10px 20px;
            overflow-x: auto;
        }
        .admin-content {
            padding: 20px;
        }
    }
</style>
