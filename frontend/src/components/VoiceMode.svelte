<script>
    // ═══════════════════════════════════════════════════════════════════
    // VoiceMode.svelte — Speaking Practice Kasual (Percakapan Bebas JP)
    //
    // Alur:
    //  1. Buka mode → Alisa menyapa dengan kalimat pembuka kasual
    //  2. User bicara → parent STT → finalText masuk via handleVoiceResult()
    //  3. Kirim ke /ws/chat mode=speaking
    //  4. AI balas dalam format:
    //       KOREKSI: ...
    //       USER_JP: ... / USER_ROM: ... / USER_ID: ...
    //       JP: ... / ROM: ... / ID: ...
    //  5. Update bubble user dengan JP/ROM/ID dari AI + tampilkan bubble Alisa
    //  6. Siklus terus sampai user reset percakapan
    // ═══════════════════════════════════════════════════════════════════

    import { onMount, onDestroy, createEventDispatcher } from "svelte";
    import { fly, fade, scale } from "svelte/transition";
    import { backOut } from "svelte/easing";
    import { user } from "../stores/auth_store";
    import { profile } from "../stores/profile_store";

    export let isRecording;
    export let loading;
    export let startRecording;
    export let stopRecording;
    export let liveTranscript = "";
    export let vrmController = null;

    const dispatch = createEventDispatcher();

    // ── State ────────────────────────────────────────────────────────────
    let isAiTurn = false;
    let currentAudio = null;
    let audioQueue = [];
    let isPlaying = false;
    let wsRef = null;
    let aiTypingText = "";
    let activeUserTurnIdx = null;

    // ── Thinking Phase States ───────────────────────────────────────────
    let currentThinkingText = "A.L.I.S.A. sedang berpikir...";
    let thinkingPhase = 0; // 0: inactive, 1: berpikir, 2: merangkai materi, 3: memproses suara
    let animationComplete = false;
    let wsComplete = false;
    let bufferedText = "";
    let bufferedAudio = [];
    let bufferedFinalResponse = null;
    let thinkingTimeouts = []; // to keep track of timers for cleanup
    let phase1StartTime = 0;
    let phase2StartTime = 0;
    let currentDelay1 = 5000;
    let currentDelay2 = 6000;
    let hasHalved = false;

    // Conversation turns: { role, jp, rom, id, correction, grammar_check, raw, ts }
    // role: "alisa" | "user"
    // user turn: { role:"user", raw, jp, rom, id, ts }
    // alisa turn: { role:"alisa", jp, rom, id, correction, grammar_check, ts }
    let turns = [];

    // Popup state for grammar badge (indexed by ts)
    let openGrammarPopups = {};

    let showCancelNotice = false;

    $: if (vrmController) {
        const isVoiceThinking = isAiTurn && !aiTypingText.trim();
        vrmController.setLoading(loading || isVoiceThinking);
    }

    function handleMicClick() {
        if (loading || isAiTurn) return;
        if (isRecording) {
            stopRecording(false);
        } else {
            startRecording();
        }
    }

    // ── Parse AI response ────────────────────────────────────────────────
    function parseAiResponse(raw) {
        const result = {
            jp: "",
            rom: "",
            id: "",
            correction: "",
            user_jp: "",
            user_rom: "",
            user_id: "",
        };
        if (!raw) return result;

        // Koreksi
        const corrMatch = raw.match(/KOREKSI:[ \t]*(.+?)(?:\n|$)/i);
        if (corrMatch) result.correction = corrMatch[1].trim();

        // USER turn fields
        const userJpMatch = raw.match(/USER_JP:[ \t]*(.+?)(?:\n|$)/i);
        const userRomMatch = raw.match(/USER_ROM:[ \t]*(.+?)(?:\n|$)/i);
        const userIdMatch = raw.match(/USER_ID:[ \t]*(.+?)(?:\n|$)/i);
        if (userJpMatch) result.user_jp = userJpMatch[1].trim();
        if (userRomMatch) result.user_rom = userRomMatch[1].trim();
        if (userIdMatch) result.user_id = userIdMatch[1].trim();

        // AI reply fields
        const jpMatch = raw.match(/^JP:[ \t]*(.+?)(?:\n|$)/im);
        const romMatch = raw.match(/^ROM:[ \t]*(.+?)(?:\n|$)/im);
        const idMatch = raw.match(/^ID:[ \t]*(.+?)(?:\n|$)/im);
        if (jpMatch) result.jp = jpMatch[1].trim();
        if (romMatch) result.rom = romMatch[1].trim();
        if (idMatch) result.id = idMatch[1].trim();

        // Fallback jika tidak ada prefix JP:
        if (!result.jp) {
            result.jp = raw
                .replace(/KOREKSI:.+?(\n|$)/gi, "")
                .replace(/USER_JP:.+?(\n|$)/gi, "")
                .replace(/USER_ROM:.+?(\n|$)/gi, "")
                .replace(/USER_ID:.+?(\n|$)/gi, "")
                .replace(/ROM:.+?(\n|$)/gi, "")
                .replace(/ID:.+?(\n|$)/gi, "")
                .trim();
        }

        // Guard: prevent blank bubble
        if (!result.jp && !result.rom && !result.id && !result.correction) {
            result.jp = "うーん...";
            result.id = "(Alisa sedang berpikir...)";
        }

        return result;
    }

    // ── Persistence ──────────────────────────────────────────────────────
    function saveToLocalStorage(updatedTurns = turns) {
        if (typeof window !== "undefined") {
            localStorage.setItem(
                "tvjp_voice_turns_v2",
                JSON.stringify(updatedTurns),
            );
        }
    }

    function addAlisaTurn(parsed, grammar_check = null) {
        turns = [
            ...turns,
            { role: "alisa", ...parsed, grammar_check, ts: Date.now() },
        ];
        saveToLocalStorage(turns);
        scrollToBottom(); // Pesan baru dari Alisa → selalu scroll ke bawah
    }

    function addUserTurn(text) {
        turns = [
            ...turns,
            {
                role: "user",
                raw: text,
                jp: "",
                rom: "",
                id: "",
                ts: Date.now(),
            },
        ];
        saveToLocalStorage(turns);
        scrollToBottom(); // Pesan baru dari user → selalu scroll ke bawah
        return turns.length - 1;
    }

    // Update user turn's JP/ROM/ID after AI echoes it back
    // Tidak scroll — ini hanya update in-place, jangan ganggu posisi scroll
    function updateUserTurnJP(index, user_jp, user_rom, user_id) {
        if (index < 0 || index >= turns.length) return;
        turns[index] = {
            ...turns[index],
            jp: user_jp,
            rom: user_rom,
            id: user_id,
        };
        turns = [...turns];
        saveToLocalStorage(turns);
        // Tidak scroll di sini — update JP/ROM/ID tidak butuh reposition
    }

    // ── PUBLIC METHODS: Dipanggil parent untuk transkripsi suara ─────────
    export function handleVoiceStart(captured) {
        turns = [
            ...turns,
            {
                role: "user",
                raw: captured || "",
                loading: true,
                jp: "",
                rom: "",
                id: "",
                ts: Date.now(),
            },
        ];
        activeUserTurnIdx = turns.length - 1;
        saveToLocalStorage(turns);
        scrollToBottom();
    }

    export function handleVoiceResult(finalText) {
        if (!finalText || !finalText.trim()) {
            // Jika gagal transkripsi, hapus turn loading sementara
            if (activeUserTurnIdx !== null) {
                turns = turns.filter((_, idx) => idx !== activeUserTurnIdx);
                activeUserTurnIdx = null;
                saveToLocalStorage(turns);
            }
            return;
        }

        let userTurnIdx = activeUserTurnIdx;
        if (userTurnIdx !== null && userTurnIdx < turns.length) {
            // Update turn loading sementara dengan teks final dari Whisper
            turns[userTurnIdx] = {
                ...turns[userTurnIdx],
                raw: finalText.trim(),
                loading: false,
            };
            turns = [...turns];
        } else {
            // Fallback jika handleVoiceStart entah bagaimana tidak dipanggil
            userTurnIdx = addUserTurn(finalText.trim());
        }

        activeUserTurnIdx = null;
        saveToLocalStorage(turns);
        scrollToBottom();

        sendToAI(finalText.trim(), userTurnIdx);
    }

    // ── WebSocket ────────────────────────────────────────────────────────
    function ensureWs() {
        return new Promise((resolve, reject) => {
            if (wsRef && wsRef.readyState === WebSocket.OPEN) {
                resolve(wsRef);
                return;
            }
            if (wsRef) {
                try {
                    wsRef.close();
                } catch (_) {}
            }

            const ws = new WebSocket("ws://localhost:8000/api/v1/ws/chat");
            ws.onopen = () => {
                wsRef = ws;
                resolve(ws);
            };
            ws.onclose = () => {
                wsRef = null;
            };
            ws.onerror = (e) => {
                console.error("[WS Speaking] Error:", e);
                wsRef = null;
                reject(e);
            };
        });
    }

    function clearThinkingTimers() {
        for (const t of thinkingTimeouts) {
            clearTimeout(t);
        }
        thinkingTimeouts = [];
    }

    function schedulePhase1Timeout(timeoutDuration) {
        clearThinkingTimers();

        const t1 = setTimeout(() => {
            thinkingPhase = 2;
            currentThinkingText = "A.L.I.S.A. sedang merangkai materi...";
            phase2StartTime = Date.now();

            schedulePhase2Timeout(currentDelay2);
        }, timeoutDuration);

        thinkingTimeouts.push(t1);
    }

    function schedulePhase2Timeout(timeoutDuration) {
        clearThinkingTimers();

        const t2 = setTimeout(() => {
            transitionToPhase3();
        }, timeoutDuration);

        thinkingTimeouts.push(t2);
    }

    function startThinkingAnimation() {
        clearThinkingTimers();

        thinkingPhase = 1;
        currentThinkingText = "A.L.I.S.A. sedang berpikir...";
        animationComplete = false;
        wsComplete = false;
        bufferedText = "";
        bufferedAudio = [];
        bufferedFinalResponse = null;
        hasHalved = false;

        currentDelay1 = 5000;
        currentDelay2 = 6000;
        phase1StartTime = Date.now();

        schedulePhase1Timeout(currentDelay1);
    }

    function halveRemainingTime() {
        if (hasHalved) return;
        hasHalved = true;

        if (thinkingPhase === 1) {
            const elapsed = Date.now() - phase1StartTime;
            const remaining = Math.max(0, currentDelay1 - elapsed);
            const adjustedRemaining = remaining / 2;

            currentDelay2 = currentDelay2 / 2;

            schedulePhase1Timeout(adjustedRemaining);
        } else if (thinkingPhase === 2) {
            const elapsed = Date.now() - phase2StartTime;
            const remaining = Math.max(0, currentDelay2 - elapsed);
            const adjustedRemaining = remaining / 2;

            schedulePhase2Timeout(adjustedRemaining);
        }
    }

    function transitionToPhase3() {
        thinkingPhase = 3;
        currentThinkingText = "A.L.I.S.A. sedang memproses suara...";
        animationComplete = true;

        if (bufferedText.trim() || wsComplete) {
            releaseBuffer();
        }
    }

    function releaseBuffer() {
        if (bufferedText) {
            aiTypingText = bufferedText;
        }

        if (bufferedAudio.length > 0) {
            for (const b64 of bufferedAudio) {
                audioQueue.push(b64);
            }
            bufferedAudio = [];
            processAudioQueue();
        }

        if (wsComplete && bufferedFinalResponse) {
            addAlisaTurn(
                bufferedFinalResponse.parsed,
                bufferedFinalResponse.grammar_check,
            );
            isAiTurn = false;
            aiTypingText = "";
            clearThinkingTimers();
        }
    }

    async function sendToAI(userText, userTurnIdx) {
        if (!userText.trim() || isAiTurn) return;
        isAiTurn = true;
        aiTypingText = "";

        startThinkingAnimation();

        let ws;
        try {
            ws = await ensureWs();
        } catch (e) {
            console.error("WebSocket connection failed:", e);
            addAlisaTurn({
                jp: "ごめんなさい！",
                rom: "Gomen nasai!",
                id: "Maaf, koneksi bermasalah~",
                correction: "",
            });
            isAiTurn = false;
            clearThinkingTimers();
            return;
        }

        // Build history — use JP field if available, otherwise raw
        const history = turns
            .slice(0, -1)
            .slice(-8)
            .map((t) => {
                if (t.role === "alisa") {
                    let aiContent = t.jp || "";
                    if (t.rom) aiContent += `\nROM: ${t.rom}`;
                    if (t.id) aiContent += `\nID: ${t.id}`;
                    return { role: "assistant", content: aiContent };
                } else {
                    return { role: "user", content: t.jp || t.raw || "" };
                }
            });

        ws.send(
            JSON.stringify({
                query: userText,
                student_id: $user?.id ?? "default",
                mode: "speaking",
                history,
            }),
        );

        let rawAccumulator = "";

        const handler = (evt) => {
            let msg;
            try {
                msg = JSON.parse(evt.data);
            } catch {
                return;
            }

            if (msg.type === "sentence") {
                const textChunk = msg.content || "";
                rawAccumulator += textChunk;

                if (animationComplete) {
                    aiTypingText = rawAccumulator;
                    if (msg.audio_b64) playBase64Audio(msg.audio_b64);
                } else {
                    bufferedText = rawAccumulator;
                    if (msg.audio_b64) bufferedAudio.push(msg.audio_b64);
                    halveRemainingTime();
                }
            }

            if (msg.type === "user_translation") {
                updateUserTurnJP(userTurnIdx, msg.jp, msg.rom, msg.id);
            }

            if (msg.type === "done") {
                ws.removeEventListener("message", handler);
                const parsed = parseAiResponse(rawAccumulator);
                const finalData = {
                    parsed,
                    grammar_check: msg.grammar_check || null,
                };

                if (animationComplete) {
                    addAlisaTurn(finalData.parsed, finalData.grammar_check);
                    isAiTurn = false;
                    aiTypingText = "";
                    clearThinkingTimers();
                } else {
                    bufferedFinalResponse = finalData;
                    wsComplete = true;
                }
            }

            if (msg.type === "error") {
                ws.removeEventListener("message", handler);
                const errParsed = {
                    jp: "ごめんなさい！",
                    rom: "Gomen nasai!",
                    id: msg.content || "Maaf, ada masalah~",
                    correction: "",
                };

                if (animationComplete) {
                    addAlisaTurn(errParsed);
                    isAiTurn = false;
                    aiTypingText = "";
                    clearThinkingTimers();
                } else {
                    bufferedFinalResponse = {
                        parsed: errParsed,
                        grammar_check: null,
                    };
                    wsComplete = true;
                }
            }
        };

        ws.addEventListener("message", handler);
    }

    // ── Audio playback ───────────────────────────────────────────────────
    function playBase64Audio(b64) {
        audioQueue.push(b64);
        processAudioQueue();
    }

    function processAudioQueue() {
        if (isPlaying || audioQueue.length === 0) return;
        isPlaying = true;
        try {
            const b64 = audioQueue.shift();
            const bytes = atob(b64);
            const arr = new Uint8Array(bytes.length);
            for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
            const blob = new Blob([arr], { type: "audio/wav" });
            const url = URL.createObjectURL(blob);
            currentAudio = new Audio(url);
            if (vrmController) vrmController.setSpeaking(true);
            currentAudio.play().catch(() => {
                if (vrmController) vrmController.setSpeaking(false);
            });
            currentAudio.onended = () => {
                if (vrmController) vrmController.setSpeaking(false);
                URL.revokeObjectURL(url);
                currentAudio = null;
                isPlaying = false;
                processAudioQueue();
            };
        } catch (e) {
            console.warn("Audio play error:", e);
            if (vrmController) vrmController.setSpeaking(false);
            isPlaying = false;
            processAudioQueue();
        }
    }

    function stopCurrentAudio() {
        if (vrmController) vrmController.setSpeaking(false);
        if (currentAudio) {
            try {
                currentAudio.pause();
                currentAudio.src = "";
            } catch (_) {}
            currentAudio = null;
        }
        audioQueue = [];
        isPlaying = false;
    }

    // ── Reset Percakapan ─────────────────────────────────────────────────
    function resetConversation() {
        stopCurrentAudio();
        clearThinkingTimers();
        turns = [];
        aiTypingText = "";
        isAiTurn = false;
        activeUserTurnIdx = null;
        if (typeof window !== "undefined") {
            localStorage.removeItem("tvjp_voice_turns_v2");
        }
        startSession();
    }

    // ── Mulai sesi dengan kalimat pembuka kasual ──────────────────────────
    function startSession() {
        const openers = [
            {
                jp: "こんにちは！今日はどんな話をしましょうか？",
                rom: "Konnichiwa! Kyou wa donna hanashi wo shimashou ka?",
                id: "Halo! Hari ini mau ngobrol tentang apa?",
            },
            {
                jp: "やあ！元気ですか？何でも話しかけてね。",
                rom: "Yaa! Genki desu ka? Nan demo hanashikakete ne.",
                id: "Hai! Apa kabar? Boleh ngobrol apa saja ya.",
            },
            {
                jp: "こんにちは！なにか話しましょう。",
                rom: "Konnichiwa! Nanika hanashimashou.",
                id: "Halo! Ayo ngobrol sesuatu.",
            },
        ];
        const pick = openers[Math.floor(Math.random() * openers.length)];
        addAlisaTurn({ ...pick, correction: "" });
    }

    // ── Auto scroll ──────────────────────────────────────────────────────
    let chatContainer;

    // Threshold: kalau jarak dari bawah <= 80px, anggap user "di bawah"
    function isNearBottom() {
        if (!chatContainer) return true;
        return (
            chatContainer.scrollHeight -
                chatContainer.scrollTop -
                chatContainer.clientHeight <=
            80
        );
    }

    // Scroll ke bawah HANYA jika user sedang di area bawah
    function scrollToBottomIfNeeded() {
        if (!chatContainer || !isNearBottom()) return;
        // requestAnimationFrame agar DOM sudah terupdate
        requestAnimationFrame(() => {
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        });
    }

    // Selalu scroll ke bawah (dipanggil saat pesan BARU ditambah)
    function scrollToBottom() {
        requestAnimationFrame(() => {
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        });
    }

    // ── Lifecycle ────────────────────────────────────────────────────────
    onMount(() => {
        if (typeof window !== "undefined") {
            try {
                const savedTurns = localStorage.getItem("tvjp_voice_turns_v2");
                if (savedTurns) {
                    turns = JSON.parse(savedTurns).filter((t) => !t.loading);
                    saveToLocalStorage(turns);
                    return;
                }
            } catch (e) {
                console.error("Failed to restore voice chat history:", e);
                localStorage.removeItem("tvjp_voice_turns_v2");
            }
        }
        startSession();
    });

    onDestroy(() => {
        stopCurrentAudio();
        clearThinkingTimers();
        if (wsRef) {
            try {
                wsRef.close();
            } catch (_) {}
        }
    });
</script>

<div class="flex flex-col h-full overflow-hidden">
    <!-- ═══════════════════════════════════════════════════
         HEADER: Percakapan Kasual
    ═══════════════════════════════════════════════════ -->
    <div class="shrink-0 px-5 pt-5 pb-3">
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div
                    class="w-8 h-8 rounded-xl bg-gradient-to-br from-fuchsia-400 to-indigo-500 flex items-center justify-center text-sm shadow-md"
                >
                    🗣
                </div>
                <div>
                    <p
                        class="text-[10px] font-black text-white/40 uppercase tracking-widest"
                    >
                        Mode Latihan
                    </p>
                    <p class="text-sm font-black text-white leading-none">
                        Percakapan Kasual 🇯🇵
                    </p>
                </div>
            </div>
            <button
                on:click={resetConversation}
                disabled={isAiTurn}
                class="text-[10px] font-black uppercase tracking-widest text-white/40 hover:text-fuchsia-400 bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-xl transition disabled:opacity-30"
            >
                Reset ↺
            </button>
        </div>

        <!-- Hint label -->
        <div class="mt-2 flex items-center gap-2">
            <span
                class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-fuchsia-500/10 border border-fuchsia-400/20 text-[10px] font-bold text-fuchsia-300"
            >
                ✨ Bicara bebas bahasa Jepang
            </span>
            <span class="text-[9px] text-white/25"
                >JP → ROM → ID ditampilkan otomatis</span
            >
        </div>

        <div class="mt-3 border-b border-white/10"></div>
    </div>

    <!-- ═══════════════════════════════════════════════════
         CONVERSATION TURNS
    ═══════════════════════════════════════════════════ -->
    <div
        bind:this={chatContainer}
        class="flex-grow overflow-y-auto px-5 py-4 space-y-5 custom-scroll"
    >
        {#if turns.length === 0 && !isAiTurn}
            <div
                class="flex flex-col items-center justify-center h-full text-center"
                in:fade
            >
                <div class="text-4xl mb-3 opacity-50">🌸</div>
                <p class="text-white/40 text-sm font-medium">
                    Memulai percakapan...
                </p>
            </div>
        {/if}

        {#each turns as turn, i (turn.ts)}
            <!-- ── ALISA TURN ── -->
            {#if turn.role === "alisa"}
                <div
                    class="flex gap-3 items-start"
                    in:fly={{ x: -20, duration: 400, easing: backOut }}
                >
                    <!-- Avatar -->
                    <div
                        class="w-9 h-9 rounded-xl bg-gradient-to-br from-fuchsia-400 to-indigo-500 flex items-center justify-center text-sm font-black text-white shrink-0 shadow-md border border-white/10"
                    >
                        A
                    </div>

                    <div class="flex-grow space-y-2 min-w-0">
                        <!-- JP/ROM/ID bubble -->
                        <div class="voice-bubble-alisa">
                            {#if turn.jp}
                                <p
                                    class="text-white text-lg font-bold leading-snug mb-2"
                                    style="font-family: 'Noto Serif JP', serif;"
                                >
                                    {turn.jp}
                                </p>
                            {/if}
                            {#if turn.rom}
                                <p
                                    class="text-fuchsia-300 text-xs font-semibold italic mb-1"
                                >
                                    {turn.rom}
                                </p>
                            {/if}
                            {#if turn.id}
                                <p class="text-white/50 text-xs font-medium">
                                    {turn.id}
                                </p>
                            {/if}
                        </div>

                        <!-- Grammar Check Badge (identik visual dengan Discovery accuracy badge) -->
                        {#if turn.grammar_check}
                            <div class="grammar-badge-container">
                                <!-- Badge button -->
                                <button
                                    type="button"
                                    class="grammar-badge grammar-{turn
                                        .grammar_check.category}
                                        {turn.grammar_check.category !==
                                    'correct'
                                        ? 'grammar-badge-clickable'
                                        : ''}"
                                    on:click={() => {
                                        if (
                                            turn.grammar_check.category !==
                                            "correct"
                                        ) {
                                            openGrammarPopups[turn.ts] =
                                                !openGrammarPopups[turn.ts];
                                        }
                                    }}
                                >
                                    {#if turn.grammar_check.category === "correct"}
                                        <span class="grammar-icon">✅</span>
                                        <span class="grammar-text"
                                            >Tata Bahasa Tepat</span
                                        >
                                    {:else if turn.grammar_check.category === "corrected"}
                                        <span class="grammar-icon">✏️</span>
                                        <span class="grammar-text"
                                            >Ada Koreksi Grammar</span
                                        >
                                        <span class="grammar-chevron"
                                            >{openGrammarPopups[turn.ts]
                                                ? "▲"
                                                : "▼"}</span
                                        >
                                    {:else if turn.grammar_check.category === "kg_verified"}
                                        <span class="grammar-icon">🛡️</span>
                                        <span class="grammar-text"
                                            >Koreksi Terverifikasi KG</span
                                        >
                                        <span class="grammar-chevron"
                                            >{openGrammarPopups[turn.ts]
                                                ? "▲"
                                                : "▼"}</span
                                        >
                                    {/if}
                                </button>

                                <!-- Popup detail -->
                                {#if openGrammarPopups[turn.ts] && turn.grammar_check.category !== "correct"}
                                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                                    <div
                                        class="grammar-popup"
                                        transition:fade={{ duration: 150 }}
                                        on:click|stopPropagation
                                    >
                                        <div class="grammar-popup-header">
                                            <span class="grammar-popup-title"
                                                >Detail Koreksi Grammar</span
                                            >
                                            <button
                                                class="grammar-popup-close"
                                                on:click={() =>
                                                    (openGrammarPopups[
                                                        turn.ts
                                                    ] = false)}>&times;</button
                                            >
                                        </div>
                                        <div class="grammar-popup-body">
                                            <!-- Correction text -->
                                            <div
                                                class="grammar-fact-row {turn
                                                    .grammar_check.category ===
                                                'kg_verified'
                                                    ? 'fact-success'
                                                    : 'fact-amber'}"
                                            >
                                                <span class="grammar-fact-icon"
                                                    >{turn.grammar_check
                                                        .category ===
                                                    "kg_verified"
                                                        ? "✅"
                                                        : "✏️"}</span
                                                >
                                                <div class="grammar-fact-info">
                                                    <div
                                                        class="grammar-fact-subject-row"
                                                    >
                                                        <span
                                                            class="grammar-fact-type-badge"
                                                            >KOREKSI</span
                                                        >
                                                    </div>
                                                    <p
                                                        class="grammar-fact-detail"
                                                    >
                                                        {turn.grammar_check
                                                            .correction}
                                                    </p>
                                                    {#if turn.grammar_check.kg_match}
                                                        <p
                                                            class="grammar-fact-ref"
                                                        >
                                                            Ref KG: <strong
                                                                >{turn
                                                                    .grammar_check
                                                                    .kg_match}</strong
                                                            >
                                                        </p>
                                                    {/if}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                {/if}
                            </div>
                        {/if}
                    </div>
                </div>

                <!-- ── USER TURN ── -->
            {:else}
                <div
                    class="flex gap-3 items-start justify-end"
                    in:fly={{ x: 20, duration: 400, easing: backOut }}
                >
                    <div
                        class="flex flex-col items-end gap-1 max-w-xs md:max-w-sm"
                    >
                        <!-- User bubble: selalu tampilkan apa yang diucapkan user (raw atau JP/ROM/ID jika sudah diterjemahkan) -->
                        <div class="voice-bubble-user">
                            {#if turn.loading}
                                <div
                                    class="flex items-center gap-2 text-white/70 text-xs font-medium"
                                >
                                    <span class="animate-pulse">🎙️</span>
                                    {#if turn.raw}
                                        <span class="italic font-medium"
                                            >"{turn.raw}"</span
                                        >
                                    {:else}
                                        <span
                                            class="font-semibold uppercase tracking-wider text-[10px] text-indigo-200"
                                            >Memproses suara...</span
                                        >
                                    {/if}
                                    <div class="user-thinking-dots">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            {:else if turn.jp}
                                <p
                                    class="text-white text-lg font-bold leading-snug mb-2"
                                    style="font-family: 'Noto Serif JP', serif;"
                                >
                                    {turn.jp}
                                </p>
                                {#if turn.rom}
                                    <p
                                        class="text-fuchsia-300 text-xs font-semibold italic mb-1"
                                    >
                                        {turn.rom}
                                    </p>
                                {/if}
                                {#if turn.id}
                                    <p
                                        class="text-white/50 text-xs font-medium"
                                    >
                                        {turn.id}
                                    </p>
                                {/if}
                            {:else}
                                <p
                                    class="text-white text-sm font-medium leading-relaxed"
                                >
                                    {turn.raw}
                                </p>
                                {#if isAiTurn && i === turns.length - 1}
                                    <div
                                        class="mt-1.5 flex items-center gap-1.5 text-[9px] text-fuchsia-300/80"
                                    >
                                        <span class="animate-spin text-[8px]"
                                            >⏳</span
                                        >
                                        <span class="font-medium italic"
                                            >Menerjemahkan ucapan...</span
                                        >
                                    </div>
                                {/if}
                            {/if}
                        </div>
                    </div>

                    <!-- Avatar user -->
                    <div
                        class="w-9 h-9 rounded-xl bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center text-sm font-black text-white shrink-0 shadow-md border border-white/10"
                    >
                        {($user?.email?.[0] ?? "U").toUpperCase()}
                    </div>
                </div>
            {/if}
        {/each}

        <!-- AI sedang mengetik -->
        {#if isAiTurn}
            <div
                class="flex gap-3 items-start"
                in:fly={{ x: -20, duration: 300 }}
            >
                <div
                    class="w-9 h-9 rounded-xl bg-gradient-to-br from-fuchsia-400 to-indigo-500 flex items-center justify-center text-sm font-black text-white shrink-0 shadow-md border border-white/10"
                >
                    A
                </div>
                {#if aiTypingText.trim()}
                    <div class="voice-bubble-alisa max-w-xs">
                        <p
                            class="text-white/70 text-sm leading-relaxed whitespace-pre-line"
                        >
                            {aiTypingText}
                        </p>
                    </div>
                {:else}
                    <div
                        class="thinking-bubble rounded-2xl rounded-tl-none p-4"
                    >
                        <div class="thinking-content">
                            <div class="thinking-dots-premium">
                                <span></span><span></span><span></span>
                            </div>
                            <p class="thinking-label">{currentThinkingText}</p>
                        </div>
                        <div class="thinking-shimmer"></div>
                    </div>
                {/if}
            </div>
        {/if}
    </div>

    <!-- ═══════════════════════════════════════════════════
         BOTTOM: Mic Control
    ═══════════════════════════════════════════════════ -->
    <div class="shrink-0 px-5 pb-6 pt-3 border-t border-white/10">
        <div class="flex flex-col items-center gap-4">
            <!-- Cancel Notice Banner -->
            {#if showCancelNotice}
                <div
                    class="px-4 py-1.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[10px] font-black uppercase tracking-wider rounded-full animate-bounce"
                    transition:fade
                >
                    🚫 Perekaman Dibatalkan
                </div>
            {/if}

            <p
                class="text-[10px] font-black uppercase tracking-[0.25em] text-center transition-all duration-300
                {isRecording
                    ? 'text-rose-400'
                    : isAiTurn
                      ? 'text-fuchsia-400 animate-pulse'
                      : loading
                        ? 'text-amber-400 animate-pulse'
                        : 'text-white/30'}"
            >
                {#if isRecording}
                    🔴 Merekam — Klik tombol mic untuk mengirim
                {:else if loading}
                    ⏳ Memproses suara...
                {:else if isAiTurn}
                    ✨ A.L.I.S.A. sedang menjawab...
                {:else}
                    Klik untuk berbicara
                {/if}
            </p>

            <!-- Live transcript (saat recording) -->
            {#if isRecording && liveTranscript}
                <div
                    class="w-full max-w-sm px-4 py-2 bg-indigo-500/10 backdrop-blur-md border border-indigo-400/20 rounded-2xl text-center shadow-[0_4px_20px_rgba(99,102,241,0.15)] animate-pulse"
                    in:fade
                >
                    <p class="text-indigo-200 text-xs font-semibold italic">
                        {liveTranscript}
                    </p>
                </div>
            {/if}

            <div class="flex items-center gap-6 justify-center">
                <!-- Mic Button with rings -->
                <div
                    class="voice-rings {isRecording ? 'active' : ''} {isAiTurn
                        ? 'ai-turn'
                        : ''}"
                >
                    <div class="voice-ring ring-1"></div>
                    <div class="voice-ring ring-2"></div>
                    <div class="voice-ring ring-3"></div>
                    <button
                        id="btn-mic"
                        on:click={handleMicClick}
                        disabled={loading || isAiTurn}
                        class="voice-btn {isRecording
                            ? 'voice-btn-recording'
                            : ''} {isAiTurn ? 'voice-btn-ai' : ''}"
                    >
                        {#if isAiTurn}
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="30"
                                height="30"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                stroke-width="2.2"
                                class="pointer-events-none"
                            >
                                <path
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    d="M9 19V6l12-3v13"
                                />
                                <circle cx="6" cy="18" r="3" /><circle
                                    cx="18"
                                    cy="15"
                                    r="3"
                                />
                            </svg>
                        {:else}
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="30"
                                height="30"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                stroke-width="2.2"
                                class="pointer-events-none"
                            >
                                <path
                                    d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"
                                />
                                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                                <line x1="12" y1="19" x2="12" y2="23" />
                                <line x1="8" y1="23" x2="16" y2="23" />
                            </svg>
                        {/if}
                    </button>
                </div>

                <!-- Batal Button (Only appears when recording) -->
                {#if isRecording}
                    <button
                        type="button"
                        on:click={() => {
                            stopRecording(true);
                            showCancelNotice = true;
                            setTimeout(() => {
                                showCancelNotice = false;
                            }, 1500);
                        }}
                        class="px-4 py-2 rounded-2xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-[10px] font-black uppercase tracking-widest transition hover:scale-105 active:scale-95 shadow-md shadow-rose-950/20"
                        in:fade={{ duration: 150 }}
                    >
                        ✕ BATAL
                    </button>
                {/if}
            </div>

            <p
                class="text-[9px] text-white/20 text-center font-medium max-w-[260px] leading-relaxed"
            >
                Bicara bebas dalam bahasa Jepang atau Indonesia. Setiap ucapan
                ditampilkan dalam JP・ROM・ID.
            </p>
        </div>
    </div>
</div>

<style>
    /* ── Bubble Alisa (kiri) ── */
    .voice-bubble-alisa {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        border-top-left-radius: 4px;
        padding: 14px 16px;
        max-width: 320px;
    }

    /* ── Bubble User (kanan) ── */
    .voice-bubble-user {
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.25),
            rgba(139, 92, 246, 0.2)
        );
        backdrop-filter: blur(8px);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 20px;
        border-top-right-radius: 4px;
        padding: 14px 16px;
        max-width: 320px;
    }

    /* ── User thinking animation inside bubble ── */
    .user-thinking-dots {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        margin-left: 6px;
    }
    .user-thinking-dots span {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.85);
        animation: user-think-bounce 1.4s infinite ease-in-out;
    }
    .user-thinking-dots span:nth-child(2) {
        animation-delay: 0.16s;
    }
    .user-thinking-dots span:nth-child(3) {
        animation-delay: 0.32s;
    }
    @keyframes user-think-bounce {
        0%,
        80%,
        100% {
            transform: translateY(0);
            opacity: 0.4;
        }
        40% {
            transform: translateY(-3px);
            opacity: 1;
        }
    }

    /* ── Voice rings & button ── */
    .voice-rings {
        position: relative;
        width: 110px;
        height: 110px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .voice-ring {
        position: absolute;
        border-radius: 50%;
        border: 1px solid rgba(255, 255, 255, 0.07);
        animation: ring-idle 5s cubic-bezier(0.23, 1, 0.32, 1) infinite;
    }
    .ring-1 {
        width: 100px;
        height: 100px;
        animation-delay: 0s;
    }
    .ring-2 {
        width: 140px;
        height: 140px;
        animation-delay: 1.5s;
    }
    .ring-3 {
        width: 180px;
        height: 180px;
        animation-delay: 3s;
    }

    .voice-rings.active .voice-ring {
        border-color: rgba(239, 68, 68, 0.3);
        animation: ring-active 1.2s ease-out infinite;
    }
    .voice-rings.ai-turn .voice-ring {
        border-color: rgba(217, 70, 239, 0.3);
        animation: ring-ai 2s ease-out infinite;
    }

    @keyframes ring-idle {
        0% {
            opacity: 0.6;
            transform: scale(0.85);
        }
        100% {
            opacity: 0;
            transform: scale(1.5);
        }
    }
    @keyframes ring-active {
        0% {
            opacity: 1;
            transform: scale(0.85);
        }
        100% {
            opacity: 0;
            transform: scale(1.7);
        }
    }
    @keyframes ring-ai {
        0% {
            opacity: 0.8;
            transform: scale(0.9);
        }
        100% {
            opacity: 0;
            transform: scale(1.6);
        }
    }

    .voice-btn {
        position: relative;
        z-index: 2;
        width: 76px;
        height: 76px;
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff;
        cursor: pointer;
        outline: none;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.4);
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .voice-btn:hover:not(:disabled) {
        transform: scale(1.08) translateY(-2px);
        box-shadow: 0 18px 40px rgba(99, 102, 241, 0.5);
    }
    .voice-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }
    .voice-btn-recording {
        background: linear-gradient(135deg, #ef4444, #b91c1c) !important;
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.55) !important;
        animation: rec-pulse 1s ease-in-out infinite !important;
    }
    .voice-btn-ai {
        background: linear-gradient(135deg, #d946ef, #8b5cf6) !important;
        box-shadow: 0 0 35px rgba(217, 70, 239, 0.45) !important;
        animation: ai-pulse 1.8s ease-in-out infinite !important;
        cursor: not-allowed !important;
    }

    @keyframes rec-pulse {
        0%,
        100% {
            transform: scale(1.05);
        }
        50% {
            transform: scale(1.18);
        }
    }
    @keyframes ai-pulse {
        0%,
        100% {
            transform: scale(1);
            box-shadow: 0 0 20px rgba(217, 70, 239, 0.3);
        }
        50% {
            transform: scale(1.08);
            box-shadow: 0 0 40px rgba(217, 70, 239, 0.55);
        }
    }

    /* ── Scrollbar ── */
    .custom-scroll::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scroll::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 9999px;
    }

    /* ── Premium Thinking Bubble ── */
    .thinking-bubble {
        position: relative;
        overflow: hidden;
        min-width: 200px;
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.08),
            rgba(139, 92, 246, 0.12)
        ) !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
        backdrop-filter: blur(8px);
        animation: think-pulse 2s ease-in-out infinite;
    }
    @keyframes think-pulse {
        0%,
        100% {
            border-color: rgba(139, 92, 246, 0.2);
            box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
        }
        50% {
            border-color: rgba(139, 92, 246, 0.4);
            box-shadow: 0 0 20px 0 rgba(139, 92, 246, 0.08);
        }
    }
    .thinking-content {
        display: flex;
        align-items: center;
        gap: 12px;
        position: relative;
        z-index: 1;
    }
    .thinking-dots-premium {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .thinking-dots-premium span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg, #a78bfa, #818cf8);
        animation: think-bounce 1.4s infinite ease-in-out;
        box-shadow: 0 0 8px rgba(139, 92, 246, 0.4);
    }
    .thinking-dots-premium span:nth-child(2) {
        animation-delay: 0.16s;
    }
    .thinking-dots-premium span:nth-child(3) {
        animation-delay: 0.32s;
    }
    @keyframes think-bounce {
        0%,
        80%,
        100% {
            transform: translateY(0) scale(1);
            opacity: 0.5;
        }
        40% {
            transform: translateY(-8px) scale(1.2);
            opacity: 1;
        }
    }
    .thinking-label {
        font-size: 12px;
        font-weight: 600;
        color: rgba(167, 139, 250, 0.8);
        letter-spacing: 0.02em;
        margin: 0;
        animation: label-fade 2s ease-in-out infinite;
    }
    @keyframes label-fade {
        0%,
        100% {
            opacity: 0.6;
        }
        50% {
            opacity: 1;
        }
    }
    .thinking-shimmer {
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(139, 92, 246, 0.06) 40%,
            rgba(139, 92, 246, 0.12) 50%,
            rgba(139, 92, 246, 0.06) 60%,
            transparent 100%
        );
        animation: shimmer 2.5s ease-in-out infinite;
    }
    @keyframes shimmer {
        0% {
            left: -100%;
        }
        100% {
            left: 200%;
        }
    }

    /* ═══════════════════════════════════════════════════
       GRAMMAR BADGE — identik visual dengan Discovery accuracy badge
    ═══════════════════════════════════════════════════ */
    .grammar-badge-container {
        position: relative;
        display: inline-block;
    }

    /* Base badge */
    .grammar-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-top: 6px;
        backdrop-filter: blur(6px);
        animation: grammar-badge-in 0.4s ease-out;
        cursor: default;
        user-select: none;
        border: 1px solid transparent;
        background: none;
        outline: none;
    }
    @keyframes grammar-badge-in {
        from {
            opacity: 0;
            transform: translateY(4px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ✅ Tata Bahasa Tepat */
    .grammar-correct {
        background: rgba(34, 197, 94, 0.1);
        border-color: rgba(34, 197, 94, 0.25);
        color: rgba(134, 239, 172, 0.9);
    }

    /* ✏️ Ada Koreksi Grammar */
    .grammar-corrected {
        background: rgba(251, 191, 36, 0.1);
        border-color: rgba(251, 191, 36, 0.3);
        color: rgba(253, 224, 71, 0.95);
    }

    /* 🛡️ Koreksi Terverifikasi KG */
    .grammar-kg_verified {
        background: rgba(99, 102, 241, 0.12);
        border-color: rgba(99, 102, 241, 0.35);
        color: rgba(165, 180, 252, 1);
    }

    /* Clickable badges */
    .grammar-badge-clickable {
        cursor: pointer !important;
        transition: all 0.2s ease-in-out;
    }
    .grammar-badge-clickable:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        filter: brightness(1.15);
    }

    .grammar-icon {
        font-size: 11px;
        line-height: 1;
    }
    .grammar-text {
        font-weight: 700;
    }
    .grammar-chevron {
        font-size: 8px;
        margin-left: 4px;
        opacity: 0.7;
        transition: transform 0.2s;
    }

    /* ── Popup ── */
    .grammar-popup {
        position: absolute;
        bottom: calc(100% + 8px);
        left: 0;
        z-index: 100;
        width: 300px;
        max-width: 90vw;
        background: rgba(15, 23, 42, 0.96);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        box-shadow:
            0 10px 25px -5px rgba(0, 0, 0, 0.5),
            0 8px 10px -6px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        overflow: hidden;
        animation: grammar-popup-in 0.15s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes grammar-popup-in {
        from {
            opacity: 0;
            transform: scale(0.95) translateY(4px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    .grammar-popup-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .grammar-popup-title {
        font-size: 11px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.9);
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .grammar-popup-close {
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.5);
        font-size: 18px;
        cursor: pointer;
        line-height: 1;
        padding: 0 4px;
        transition: color 0.15s;
    }
    .grammar-popup-close:hover {
        color: #fff;
    }

    .grammar-popup-body {
        padding: 8px;
        max-height: 200px;
        overflow-y: auto;
    }

    /* Fact rows inside popup */
    .grammar-fact-row {
        display: flex;
        gap: 10px;
        padding: 8px 10px;
        border-radius: 8px;
        font-size: 12px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid transparent;
    }
    .fact-success {
        border-color: rgba(34, 197, 94, 0.15);
        background: rgba(34, 197, 94, 0.04);
    }
    .fact-amber {
        border-color: rgba(251, 191, 36, 0.2);
        background: rgba(251, 191, 36, 0.04);
    }
    .grammar-fact-icon {
        font-size: 14px;
        line-height: 1.3;
        flex-shrink: 0;
    }
    .grammar-fact-info {
        flex: 1;
        min-width: 0;
    }
    .grammar-fact-subject-row {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 4px;
    }
    .grammar-fact-type-badge {
        font-size: 8px;
        text-transform: uppercase;
        font-weight: 800;
        padding: 1px 6px;
        border-radius: 4px;
        letter-spacing: 0.04em;
        background: rgba(236, 72, 153, 0.2);
        color: #fbcfe8;
    }
    .grammar-fact-detail {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.45;
        margin: 0;
    }
    .grammar-fact-ref {
        font-size: 10px;
        color: rgba(165, 180, 252, 0.7);
        margin: 4px 0 0;
    }
    .grammar-fact-ref strong {
        color: rgba(165, 180, 252, 1);
    }

    /* ═══════════════════════════════════════════════════
       VOICE DRAG-TO-CANCEL STYLING
    ═══════════════════════════════════════════════════ */
    .voice-cancel-zone {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 12px;
        color: rgba(255, 255, 255, 0.35);
        transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        pointer-events: none;
    }

    .cancel-icon-wrap {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.25s ease;
    }

    .voice-cancel-zone.target-reached {
        color: #f43f5e; /* Rose-500 red */
    }

    .voice-cancel-zone.target-reached .cancel-icon-wrap {
        background: rgba(244, 63, 94, 0.18);
        border-color: rgba(244, 63, 94, 0.45);
        transform: scale(1.18);
        box-shadow: 0 0 20px rgba(244, 63, 94, 0.4);
        animation: cancel-shake 0.5s infinite;
    }

    @keyframes cancel-shake {
        0%,
        100% {
            transform: translateX(0) scale(1.18);
        }
        25% {
            transform: translateX(-2.5px) scale(1.18);
        }
        75% {
            transform: translateX(2.5px) scale(1.18);
        }
    }

    .voice-btn.cancel-active {
        background: linear-gradient(135deg, #f43f5e, #be123c) !important;
        box-shadow: 0 0 25px rgba(244, 63, 94, 0.6) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
</style>
