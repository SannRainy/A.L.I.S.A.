import { writable } from 'svelte/store';
import { kanjiSets } from '../lib/data/kanji_n5_dataset.js';

export const profile = writable({
    xp: 0,
    level: 1,
    email: '',
    streak_days: 1,
    completed_quests: [],
    stats: {
        kanji_mastered:   0, kanji_total:   103,
        vocab_learned:    0, vocab_total:   800,
        grammar_learned:  0, grammar_total: 100,
        assimilation_rate: 0
    },
    mastery_path: []
});

// ── Satu kali per session: sinkronkan localStorage → Neo4j ──────────────────
let _kanjiBulkSynced = false;

async function syncKanjiMasteryToNeo4j(userId) {
    if (_kanjiBulkSynced || !userId || userId === 'default') return;
    try {
        const masteredSetIds = JSON.parse(localStorage.getItem('tvjp_kanji_mastered') || '[]');
        if (masteredSetIds.length === 0) return;

        // Kumpulkan semua kanji_id dari set yang sudah mastered di localStorage
        const kanjiIds = kanjiSets
            .filter(s => masteredSetIds.includes(s.id))
            .flatMap(s => s.kanji.map(k => k.id));

        if (kanjiIds.length === 0) return;

        const res = await fetch('http://localhost:8000/api/v1/kanji/mastery/bulk-sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: userId, kanji_ids: kanjiIds })
        });

        if (res.ok) {
            const data = await res.json();
            console.info(`[ProfileStore] Bulk-sync OK: ${data.synced} kanji → Neo4j ✅`);
            _kanjiBulkSynced = true;
        } else {
            console.warn(`[ProfileStore] Bulk-sync gagal (HTTP ${res.status})`);
        }
    } catch (e) {
        console.warn('[ProfileStore] Bulk-sync error:', e.message);
    }
}

export const fetchFullProfile = async (userId) => {
    if (!userId || userId === 'default') return;

    // Sinkronkan localStorage ke Neo4j (sekali per session, non-blocking)
    syncKanjiMasteryToNeo4j(userId);

    try {
        // Fetch base profile
        const profRes = await fetch(`http://localhost:8000/api/v1/user/profile/${userId}`);
        if (!profRes.ok) throw new Error(`Profile fetch failed: ${profRes.status}`);
        const profData = await profRes.json();

        // Fetch achievements (completed quests, badges, dll)
        const achRes = await fetch(`http://localhost:8000/api/v1/user/achievements/${userId}`);
        if (!achRes.ok) throw new Error(`Achievements fetch failed: ${achRes.status}`);
        const achData = await achRes.json();

        profile.set({
            ...profData,
            streak_days: profData.streak_days ?? 1,
            stats: profData.stats ?? {
                kanji_mastered:   0, kanji_total:   103,
                vocab_learned:    0, vocab_total:   800,
                grammar_learned:  0, grammar_total: 100,
                assimilation_rate: 0
            },
            mastery_path:      profData.mastery_path      ?? [],
            completed_quests:  achData.completed_quests   ?? [],
        });
    } catch (e) {
        console.warn("Profile fetch gagal, menggunakan data default:", e.message);
        // Tidak throw — biarkan app tetap jalan dengan state default
    }
};

export const updateProfile = async (userId, payload) => {
    if (!userId || userId === 'default') return;
    const res = await fetch(`http://localhost:8000/api/v1/user/profile/${userId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Gagal memperbarui profil.");
    
    // Reload profile data to update UI
    await fetchFullProfile(userId);
};
