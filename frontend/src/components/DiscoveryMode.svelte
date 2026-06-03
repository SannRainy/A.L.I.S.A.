<script>
    export let query;
    export let loading;
    export let isStreaming;
    export let modeConfig;
    export let sendChat;

    const cfg = modeConfig.discovery;
</script>

<div class="input-row">
    <div class="input-wrap">
        <input
            id="chat-input-discovery"
            bind:value={query}
            on:keypress={(e) => e.key === "Enter" && !e.shiftKey && sendChat()}
            placeholder={cfg.placeholder}
            disabled={loading || isStreaming}
            class="input-field"
        />
    </div>

    <button
        id="btn-send-discovery"
        on:click={() => sendChat()}
        disabled={!query.trim() || loading || isStreaming}
        class="send-btn"
    >
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="22"
            height="22"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
        >
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
    </button>
</div>

<style>
    .input-row {
        display: flex;
        gap: 10px;
        align-items: center;
        width: 100%;
    }

    .input-wrap {
        flex: 1;
        position: relative;
        min-width: 0;
    }

    .input-field {
        width: 100%;
        padding: 13px 18px;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        font-size: 14px;
        color: #fff;
        outline: none;
        transition: all 0.2s;
        font-family: inherit;
        box-sizing: border-box;
    }

    .input-field::placeholder {
        color: rgba(255, 255, 255, 0.3);
    }

    .input-field:focus {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.06);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
    }

    .input-field:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .send-btn {
        flex-shrink: 0;
        width: 48px;
        height: 48px;
        border-radius: 14px;
        border: none;
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        cursor: pointer;
        outline: none;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
        transition: all 0.2s;
    }

    .send-btn:hover:not(:disabled) {
        transform: translateY(-2px) scale(1.04);
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45);
    }

    .send-btn:disabled {
        opacity: 0.35;
        cursor: not-allowed;
        transform: none;
    }
</style>
