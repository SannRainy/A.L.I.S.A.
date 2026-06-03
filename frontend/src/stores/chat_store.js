import { writable } from 'svelte/store';

const initial = {
    messages: [],         // { role: 'user'|'tutor', content: string, vocab: [], grammar: [], suggestions: [] }
    loading: false,
    mode: 'chat',         // 'chat' | 'lesson'
    currentTopic: null,   // { id, name, description }
    suggestions: [],      // string[]
};

const stored = typeof window !== 'undefined' ? localStorage.getItem('tvjp_chat_store') : null;
let parsed = initial;
if (stored) {
    try {
        parsed = JSON.parse(stored);
        if (!parsed.messages) parsed.messages = [];
    } catch (e) {
        console.error("Failed to parse chat store from localStorage:", e);
        parsed = initial;
    }
}

// Pastikan status loading di-reset saat inisialisasi awal
parsed.loading = false;

export const chatStore = writable(parsed);

export const clearChat = () => {
    chatStore.set({
        messages: [
            {
                id: `msg_init_${Date.now()}`,
                role: "tutor",
                content:
                    "こんにちは！ 👋 Aku **A.L.I.S.A**, tutor bahasa Jepang virtualmu untuk level **N5**.\n\nPilih mode interaksi di atas:\n- 💬 **Discovery** — Tanya bebas tentang Kanji, Kosakata, Grammar\n- ⚔️ **Quest** — Kuis berhadiah XP\n- 🎤 **Voice** — Latihan percakapan suara\n\nAyo mulai belajar! **がんばって！** ✨",
                vocab: [],
                grammar: [],
                suggestions: [
                    "Ajari aku kanji N5",
                    "Berikan 3 kosakata",
                    "Apa itu tata bahasa です？",
                ],
            },
        ],
        loading: false,
        mode: 'chat',
        currentTopic: null,
        suggestions: [
            "Ajari aku kanji N5",
            "Berikan 3 kosakata",
            "Apa itu tata bahasa です？",
        ],
    });

    if (typeof window !== "undefined") {
        localStorage.removeItem("tvjp_voice_turns");
        localStorage.removeItem("tvjp_voice_topic");
    }
};

if (typeof window !== 'undefined') {
    chatStore.subscribe(value => {
        localStorage.setItem('tvjp_chat_store', JSON.stringify(value));
    });
}

