<script>
    import { questLevels, checkLocalPrerequisites } from '../lib/data/quest_n5_dataset.js';
    import QuestMap from './QuestMap.svelte';
    import QuestEngine from './QuestEngine.svelte';
    import QuestResult from './QuestResult.svelte';
    import KanjiStudyMode from './KanjiStudyMode.svelte';
    import { user } from "../stores/auth_store";
    import { profile, fetchFullProfile } from "../stores/profile_store";
    import { onMount } from "svelte";

    export let vrmController = null;

    let currentState = "map"; // 'map', 'quiz', 'result', 'kanji_dojo'
    let activeLevelData = null;
    let quizResultsData = null;

    onMount(() => {
        if (typeof window !== "undefined") {
            const savedState = localStorage.getItem("tvjp_quest_state");
            const savedLevel = localStorage.getItem("tvjp_quest_level");
            const savedResults = localStorage.getItem("tvjp_quest_results");
            if (savedState) currentState = savedState;
            if (savedLevel) activeLevelData = JSON.parse(savedLevel);
            if (savedResults) quizResultsData = JSON.parse(savedResults);
        }
    });

    function saveQuestState() {
        if (typeof window !== "undefined") {
            localStorage.setItem("tvjp_quest_state", currentState);
            if (activeLevelData) {
                localStorage.setItem("tvjp_quest_level", JSON.stringify(activeLevelData));
            } else {
                localStorage.removeItem("tvjp_quest_level");
            }
            if (quizResultsData) {
                localStorage.setItem("tvjp_quest_results", JSON.stringify(quizResultsData));
            } else {
                localStorage.removeItem("tvjp_quest_results");
            }
        }
    }

    /**
     * Prerequisite Check — Hybrid Mode:
     * 1. Coba ambil mastered nodes dari backend KG
     * 2. Jika gagal, fallback ke local: cek dari profile store
     */
    async function getMasteredNodes(userId) {
        // Coba ambil dari backend KG
        try {
            const res = await fetch(`http://localhost:8000/api/v1/mastery/${userId}`, {
                signal: AbortSignal.timeout(3000) // timeout 3 detik
            });
            if (res.ok) {
                const data = await res.json();
                // data.mastered_nodes = ["grammar_wa", "grammar_desu", ...]
                return { source: 'backend', nodes: data.mastered_nodes || [] };
            }
        } catch (e) {
            console.warn("KG backend tidak tersedia, fallback ke local profile:", e.message);
        }

        // Fallback: ambil dari completed_quests di profile store
        // Rekonstruksi node yang dikuasai berdasarkan level yang sudah selesai
        const completedIds = $profile?.completed_quests?.map(q => q.level_id) || [];
        const localMasteredNodes = [];
        for (const level of questLevels) {
            if (completedIds.includes(level.id)) {
                level.questions.forEach(q => {
                    if (!localMasteredNodes.includes(q.node_id)) {
                        localMasteredNodes.push(q.node_id);
                    }
                });
            }
        }
        return { source: 'local', nodes: localMasteredNodes };
    }

    async function handleStartLevel(levelId) {
        activeLevelData = questLevels.find(l => l.id === levelId);
        if (!activeLevelData) return;

        // Cek prerequisite sebelum memulai level
        const userId = $user?.id;
        if (userId && activeLevelData.prerequisites?.length > 0) {
            const { nodes: masteredNodes, source } = await getMasteredNodes(userId);
            const { unlocked, missingNodes } = checkLocalPrerequisites(levelId, masteredNodes);

            if (!unlocked) {
                // Tampilkan notifikasi (QuestMap akan handle ini via prop)
                prerequisiteAlert = {
                    show: true,
                    levelTitle: activeLevelData.title,
                    missingNodes,
                    source
                };
                activeLevelData = null;
                saveQuestState();
                return;
            }
        }

        prerequisiteAlert = { show: false };
        currentState = "quiz";
        saveQuestState();
    }

    // Alert state untuk prerequisite tidak terpenuhi
    let prerequisiteAlert = { show: false };

    async function handleQuizFinish(results) {
        quizResultsData = results;
        currentState = "result";
        saveQuestState();

        // Submit score ke backend
        if ($user && activeLevelData) {
            try {
                await fetch("http://localhost:8000/api/v1/quest/submit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_id: $user.id,
                        level_id: activeLevelData.id,
                        score: results.score,
                        session_stats: results.sessionStats || {}
                    })
                });
                // Refresh profile stats
                fetchFullProfile($user.id);
            } catch (e) {
                console.error("Failed to save quest score", e);
            }
        }
    }

    function handleBackToMap() {
        currentState = "map";
        activeLevelData = null;
        prerequisiteAlert = { show: false };
        saveQuestState();
    }

    function handleOpenKanjiDojo() {
        currentState = "kanji_dojo";
        saveQuestState();
    }
</script>

<div class="quest-container w-full h-full relative">
    {#if currentState === "map"}
        <QuestMap
            levels={questLevels}
            onStart={handleStartLevel}
            {prerequisiteAlert}
            on:dismissAlert={() => prerequisiteAlert = { show: false }}
            on:openKanjiDojo={handleOpenKanjiDojo}
        />

    {:else if currentState === "quiz"}
        <QuestEngine
            {vrmController}
            levelData={activeLevelData}
            onFinish={handleQuizFinish}
            onQuit={handleBackToMap}
        />

    {:else if currentState === "result"}
        <QuestResult
            results={quizResultsData}
            levelData={activeLevelData}
            onContinue={handleBackToMap}
        />

    {:else if currentState === "kanji_dojo"}
        <KanjiStudyMode
            onBack={handleBackToMap}
        />
    {/if}
</div>
