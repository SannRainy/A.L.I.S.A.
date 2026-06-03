<script>
    import { onMount } from "svelte";

    export let user;
    export let API;

    let availableModels = [];
    let activeModel = "";
    let modelLoading = false;
    let switchingStatus = "";

    let playgroundMessages = [];
    let playgroundInput = "";
    let playgroundStreaming = false;
    let playgroundError = "";

    onMount(async () => {
        await loadModels();
    });

    async function loadModels() {
        try {
            const res = await fetch(`${API}/models?admin_id=${user.id}`);
            const data = await res.json();
            availableModels = data.available_models || [];
            activeModel = data.active_model || "";
        } catch (e) {
            console.error("Gagal memuat model:", e);
        }
    }

    async function selectModel(name) {
        if (name === activeModel || modelLoading) return;
        modelLoading = true;
        switchingStatus = `Mengalihkan model ke ${name}... Silakan tunggu beberapa detik untuk preloading ke VRAM/RAM.`;
        try {
            const res = await fetch(`${API}/models/select`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    admin_id: user.id,
                    model_name: name
                })
            });
            const data = await res.json();
            if (res.ok) {
                activeModel = name;
                alert(`✅ Model berhasil dialihkan ke ${name}`);
            } else {
                alert(`❌ Gagal: ${data.detail || "Terjadi kesalahan"}`);
            }
        } catch (e) {
            alert(`❌ Gagal: ${e.message}`);
        } finally {
            modelLoading = false;
            switchingStatus = "";
        }
    }

    let testingHf = false;

    async function testHfConnection() {
        if (testingHf) return;
        testingHf = true;
        try {
            const res = await fetch(`${API}/models/test-hf`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    admin_id: user.id
                })
            });
            const data = await res.json();
            if (res.ok && data.ok) {
                alert(`✅ Koneksi Sukses!\nModel: ${data.model}\nLatency: ${data.latency_ms}ms\nSample: "${data.reply_sample}"`);
            } else {
                alert(`❌ Koneksi Gagal: ${data.error || "Gagal menghubungi HuggingFace Hub"}`);
            }
        } catch (e) {
            alert(`❌ Gagal: ${e.message}`);
        } finally {
            testingHf = false;
        }
    }

    async function sendPlaygroundChat() {
        const text = playgroundInput.trim();
        if (!text || playgroundStreaming) return;
        playgroundInput = "";
        playgroundError = "";

        // Append user message
        playgroundMessages = [
            ...playgroundMessages,
            { role: "user", content: text }
        ];

        // Append empty assistant message for streaming
        playgroundMessages = [
            ...playgroundMessages,
            { role: "assistant", content: "" }
        ];

        playgroundStreaming = true;
        const targetMsgIndex = playgroundMessages.length - 1;

        const history = playgroundMessages.slice(0, -2).map(m => ({
            role: m.role,
            content: m.content
        }));

        try {
            const res = await fetch(`${API}/models/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    admin_id: user.id,
                    query: text,
                    history: history
                })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || `Server error: ${res.status}`);
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            let done = false;

            while (!done) {
                const { value, done: d } = await reader.read();
                done = d;
                if (value) {
                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split("\n\n");
                    buffer = parts.pop() || "";
                    for (const part of parts) {
                        const line = part.trim();
                        if (!line.startsWith("data: ")) continue;
                        try {
                            const ev = JSON.parse(line.slice(6));
                            if (ev.content) {
                                playgroundMessages[targetMsgIndex].content += ev.content;
                                playgroundMessages = [...playgroundMessages];
                            }
                        } catch (e) {
                            // ignore json parse errors
                        }
                    }
                }
            }
        } catch (e) {
            console.error("[Playground Chat Error]", e);
            playgroundError = e.message || "Koneksi terputus. Pastikan backend aktif.";
            playgroundMessages[targetMsgIndex].content = `⚠️ Gagal menghasilkan respon: ${playgroundError}`;
            playgroundMessages = [...playgroundMessages];
        } finally {
            playgroundStreaming = false;
        }
    }

    function clearPlayground() {
        playgroundMessages = [];
        playgroundError = "";
    }
</script>

<div class="tab-header">
    <h2>🤖 AI Model Management</h2>
</div>
<div class="models-panel custom-scroll">
    <!-- Switcher Section -->
    <div class="model-switcher-card">
        <h3>Pilih Model AI Aktif</h3>
        <p class="model-desc">
            Ganti model bahasa lokal yang melayani asisten belajar Alisa. Model 8B memiliki penalaran yang lebih kuat namun memerlukan kapasitas VRAM/RAM yang lebih tinggi daripada model 4B.
        </p>

        {#if modelLoading}
            <div class="model-loading-overlay">
                <div class="admin-spinner"></div>
                <p>{switchingStatus}</p>
            </div>
        {/if}

        <div class="model-list">
            {#each availableModels as modelName}
                <div class="model-item" class:active={activeModel === modelName}>
                    <div class="model-meta">
                        <span class="model-icon">{modelName.startsWith("hf_cloud:") ? "☁️" : "🧠"}</span>
                        <div class="model-details">
                            {#if modelName.startsWith("hf_cloud:")}
                                <span class="model-filename">HF Cloud: {modelName.replace("hf_cloud:", "")}</span>
                                <span class="model-size">Hugging Face Inference API • Run on Cloud</span>
                            {:else}
                                <span class="model-filename">{modelName}</span>
                                <span class="model-size">
                                    {modelName.includes("8B") ? "8 Billion Parameters • Rekomendasi VRAM >= 6GB" : "4 Billion Parameters • Cepat & Ringan"}
                                </span>
                            {/if}
                        </div>
                    </div>
                    <div class="model-actions">
                        {#if modelName.startsWith("hf_cloud:")}
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <button 
                                    class="btn-test-hf" 
                                    on:click={testHfConnection}
                                    disabled={testingHf}
                                >
                                    {testingHf ? "Mencoba..." : "⚡ Test Koneksi"}
                                </button>
                                {#if activeModel === modelName}
                                    <span class="badge-active">● Aktif Saat Ini</span>
                                {:else}
                                    <button 
                                        class="btn-activate" 
                                        on:click={() => selectModel(modelName)}
                                        disabled={modelLoading}
                                    >
                                        Aktifkan
                                    </button>
                                {/if}
                            </div>
                        {:else}
                            {#if activeModel === modelName}
                                <span class="badge-active">● Aktif Saat Ini</span>
                            {:else}
                                <button 
                                    class="btn-activate" 
                                    on:click={() => selectModel(modelName)}
                                    disabled={modelLoading}
                                >
                                    Aktifkan
                                </button>
                            {/if}
                        {/if}
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <!-- Playground Section -->
    <div class="playground-card">
        <div class="playground-header">
            <div>
                <h3>💬 Pure Playground (CCP Mode)</h3>
                <p class="playground-desc">
                    Uji model AI terpilih secara langsung. Mode ini murni mengirim instruksi Anda tanpa menyambungkan data Neo4j (Knowledge Graph), histori Supabase, atau suara (TTS).
                </p>
            </div>
            <button class="btn-clear" on:click={clearPlayground} title="Bersihkan Percakapan">🧹 Bersihkan</button>
        </div>

        <div class="playground-chat-area custom-scroll">
            {#if playgroundMessages.length === 0}
                <div class="playground-empty">
                    <p>Belum ada percakapan. Mulai dengan mengirimkan pesan di bawah.</p>
                </div>
            {/if}
            {#each playgroundMessages as msg}
                <div class="playground-msg" class:user={msg.role === "user"}>
                    <div class="msg-avatar">{msg.role === "user" ? "👤" : "🤖"}</div>
                    <div class="msg-content">
                        <div class="msg-sender">{msg.role === "user" ? "Anda" : "Alisa (" + activeModel + ")"}</div>
                        <div class="msg-text">
                            {#if msg.content === "" && playgroundStreaming && msg === playgroundMessages[playgroundMessages.length - 1]}
                                <span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span>
                            {:else}
                                {msg.content}
                            {/if}
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        {#if playgroundError}
            <div class="playground-error">⚠️ {playgroundError}</div>
        {/if}

        <form class="playground-input-wrap" on:submit|preventDefault={sendPlaygroundChat}>
            <textarea 
                class="playground-input" 
                placeholder="Ketik pesan untuk mengetes model (tekan Enter untuk kirim, Shift+Enter untuk baris baru)..."
                bind:value={playgroundInput}
                on:keydown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        sendPlaygroundChat();
                    }
                }}
            ></textarea>
            <button 
                type="submit" 
                class="btn-send"
                disabled={!playgroundInput.trim() || playgroundStreaming}
            >
                {playgroundStreaming ? "..." : "Kirim"}
            </button>
        </form>
    </div>
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

    /* AI Models Panel Styles */
    .models-panel {
        display: grid;
        grid-template-columns: 1fr;
        gap: 24px;
        overflow-y: auto;
        flex-grow: 1;
        padding-right: 4px;
    }
    
    @media (min-width: 1024px) {
        .models-panel {
            grid-template-columns: 1fr 1fr;
            align-items: start;
        }
    }

    .model-switcher-card,
    .playground-card {
        background: rgba(15, 13, 36, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }

    .model-switcher-card h3,
    .playground-card h3 {
        font-size: 16px;
        font-weight: 800;
        margin: 0 0 8px 0;
        color: #fff;
    }

    .model-desc,
    .playground-desc {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.5);
        line-height: 1.5;
        margin: 0 0 20px 0;
    }

    /* Model Loading Overlay */
    .model-loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(12, 10, 29, 0.9);
        z-index: 20;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 24px;
        gap: 14px;
    }

    .model-loading-overlay p {
        font-size: 12px;
        color: rgba(255, 255, 255, 0.7);
        text-align: center;
        max-width: 80%;
        line-height: 1.5;
        margin: 0;
    }

    /* Model List */
    .model-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .model-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        transition: all 0.2s;
    }

    .model-item.active {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.3);
    }

    .model-meta {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .model-icon {
        font-size: 24px;
    }

    .model-details {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .model-filename {
        font-size: 13px;
        font-weight: 700;
        color: #fff;
    }

    .model-size {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.4);
    }

    .badge-active {
        font-size: 11px;
        font-weight: 800;
        color: #10b981;
        background: rgba(16, 185, 129, 0.1);
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    .btn-activate {
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(255, 255, 255, 0.06);
        color: rgba(255, 255, 255, 0.8);
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-activate:hover:not(:disabled) {
        background: rgba(99, 102, 241, 0.8);
        color: #fff;
        border-color: transparent;
    }

    /* Playground Styles */
    .playground-header {
        display: flex;
        align-items: start;
        justify-content: space-between;
        gap: 16px;
    }

    .btn-clear {
        padding: 6px 12px;
        font-size: 11px;
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.2);
        background: rgba(239, 68, 68, 0.06);
        color: #fca5a5;
        cursor: pointer;
        font-weight: 700;
        transition: all 0.2s;
    }

    .btn-clear:hover {
        background: rgba(239, 68, 68, 0.2);
        color: #fff;
    }

    .playground-chat-area {
        height: 320px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(0, 0, 0, 0.2);
        padding: 16px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 14px;
        margin-bottom: 16px;
    }

    .playground-empty {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: rgba(255, 255, 255, 0.3);
        font-size: 12px;
        text-align: center;
    }

    .playground-msg {
        display: flex;
        gap: 12px;
        align-items: start;
        max-width: 85%;
    }

    .playground-msg.user {
        align-self: flex-end;
        flex-direction: row-reverse;
    }

    .msg-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        flex-shrink: 0;
    }

    .playground-msg.user .msg-avatar {
        background: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.3);
    }

    .msg-content {
        display: flex;
        flex-direction: column;
        gap: 4px;
        max-width: 100%;
    }

    .msg-sender {
        font-size: 10px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.4);
    }

    .playground-msg.user .msg-sender {
        text-align: right;
    }

    .msg-text {
        padding: 10px 14px;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 12.5px;
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.5;
        white-space: pre-wrap;
    }

    .playground-msg.user .msg-text {
        background: rgba(99, 102, 241, 0.8);
        border-color: transparent;
        color: #fff;
    }

    .playground-error {
        margin-bottom: 12px;
        padding: 8px 12px;
        border-radius: 8px;
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        font-size: 11px;
    }

    .playground-input-wrap {
        display: flex;
        gap: 10px;
        align-items: stretch;
    }

    .playground-input {
        flex-grow: 1;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #fff;
        padding: 11px 14px;
        font-size: 13px;
        font-family: inherit;
        resize: none;
        height: 42px;
        line-height: 1.4;
        outline: none;
        transition: all 0.2s;
        overflow-y: auto;
        scrollbar-width: none;
    }

    .playground-input::-webkit-scrollbar {
        display: none;
    }

    .playground-input:focus {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15);
    }

    .btn-send {
        padding: 0 20px;
        border-radius: 10px;
        border: none;
        background: #6366f1;
        color: #fff;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .btn-send:hover:not(:disabled) {
        background: #4f46e5;
    }

    .btn-send:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Thinking dots */
    .thinking-dots span {
        animation: blink 1.4s infinite both;
        font-weight: 900;
        display: inline-block;
        font-size: 16px;
        line-height: 1;
    }
    .thinking-dots span:nth-child(2) {
        animation-delay: .2s;
    }
    .thinking-dots span:nth-child(3) {
        animation-delay: .4s;
    }
    @keyframes blink {
        0% { opacity: .2; }
        20% { opacity: 1; }
        100% { opacity: .2; }
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

    .btn-test-hf {
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid rgba(139, 92, 246, 0.3);
        background: rgba(139, 92, 246, 0.1);
        color: #c084fc;
        cursor: pointer;
        transition: all 0.2s;
    }

    .btn-test-hf:hover:not(:disabled) {
        background: rgba(139, 92, 246, 0.25);
        color: #fff;
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    .btn-test-hf:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
