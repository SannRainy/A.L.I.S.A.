<script>
    import { browser } from "$app/environment";
    import { onMount, onDestroy, afterUpdate, tick } from "svelte";
    import { fly, fade } from "svelte/transition";
    import { chatStore } from "../stores/chat_store";
    import {
        user,
        initAuth,
        login,
        logout,
        register,
    } from "../stores/auth_store";
    import { profile, fetchFullProfile } from "../stores/profile_store";
    import { goto } from "$app/navigation";
    import * as THREE from "three";
    import { marked } from "marked";
    import DOMPurify from "dompurify";
    import { sfx } from "../lib/sfx_manager";

    // Components
    import Profile from "../components/Profile.svelte";
    import Achievement from "../components/Achievement.svelte";
    import DiscoveryMode from "../components/DiscoveryMode.svelte";
    import QuestMode from "../components/QuestMode.svelte";
    import VoiceMode from "../components/VoiceMode.svelte";

    let mainTab = "study"; // 'study' | 'profile' | 'achievement'
    if (browser) {
        mainTab = localStorage.getItem("tvjp_main_tab") || "study";
    }

    let canvas;
    let query = "";
    let loading = false;
    let vrmController = null;
    let mouse = { x: 0, y: 0 };
    let animationFrameId;
    let renderer = null;
    let ro = null;
    let mode = "discovery"; // 'discovery' | 'quest' | 'voice'
    if (browser) {
        mode = localStorage.getItem("tvjp_mode") || "discovery";
    }

    let isStreaming = false;
    let activeStreamText = "";

    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let audioPlayer;
    let sentencePlaybackQueue = [];
    let isPlayingAudio = false;
    let isStreamDone = false;
    let finalRawText = "";
    let finalMetadata = null;
    let finalAccuracy = null;
    let typeInterval = null;
    // Track current typing chunk state (module-level so playNextAudio can flush it)
    let _typing = { text: "", index: 0 };

    // Live Voice Feedback
    let liveTranscript = "";
    let finalTranscriptBuffer = ""; // Akumulasi semua kalimat final dalam 1 sesi Hold
    let speechRecognizer = null;
    let voiceModeRef = null; // Reference ke VoiceMode component untuk handleVoiceResult()

    function finalizeStream() {
        // Guard: prevent duplicate bubble creation
        if (!isStreamDone || !finalMetadata) return;
        isStreamDone = false; // Reset immediately to prevent re-entry
        isStreaming = false;
        chatStore.update((s) => ({
            ...s,
            messages: [
                ...s.messages,
                {
                    id: nextMsgId(),
                    role: "tutor",
                    content: finalRawText.trim(),
                    vocab: finalMetadata.vocab,
                    grammar: finalMetadata.grammar,
                    suggestions: finalMetadata.suggestions,
                    accuracy: finalAccuracy || null,
                },
            ],
            suggestions: finalMetadata.suggestions,
        }));
        activeStreamText = "";
        finalMetadata = null; // Clear to prevent re-entry
        finalAccuracy = null;
    }

    function playNextAudio() {
        if (sentencePlaybackQueue.length === 0) {
            isPlayingAudio = false;
            if (vrmController) vrmController.setSpeaking(false);
            if (isStreamDone && !typeInterval) finalizeStream();
            return;
        }
        isPlayingAudio = true;
        const item = sentencePlaybackQueue.shift();

        // Sebelum membunuh typewriter lama, selesaikan sisa teks seketika
        // agar kata tidak terpotong di tengah (mis. "teli" → harus "telinga")
        if (typeInterval) {
            clearInterval(typeInterval);
            typeInterval = null;
            if (_typing.index < _typing.text.length) {
                activeStreamText += _typing.text.slice(_typing.index);
            }
        }

        const textToType = item.text;
        const durationAvgMs = item.audioUrl ? 60 : 30;

        // Reset state typewriter untuk chunk ini
        _typing = { text: textToType, index: 0 };

        typeInterval = setInterval(() => {
            if (_typing.index < _typing.text.length) {
                activeStreamText += _typing.text[_typing.index];
                _typing.index++;
            } else {
                clearInterval(typeInterval);
                typeInterval = null;
                if (
                    sentencePlaybackQueue.length === 0 &&
                    isStreamDone &&
                    !isPlayingAudio
                ) {
                    finalizeStream();
                }
            }
        }, durationAvgMs);

        if (item.audioUrl) {
            if (vrmController) vrmController.setSpeaking(true);
            audioPlayer.src = item.audioUrl;
            audioPlayer.play().catch(() => {
                if (vrmController) vrmController.setSpeaking(false);
                if (item.blobUrl) URL.revokeObjectURL(item.audioUrl);
                playNextAudio();
            });
            audioPlayer.onended = () => {
                // Revoke Blob URL to free memory (only for WS path)
                if (item.blobUrl) URL.revokeObjectURL(item.audioUrl);
                playNextAudio();
            };
        } else {
            setTimeout(playNextAudio, durationAvgMs * textToType.length + 500);
        }
    }

    let chatContainer;
    let email = "";
    let password = "";
    let authError = "";
    let authLoading = false;
    let isDemoMode = false;
    if (browser) {
        isDemoMode = localStorage.getItem("tvjp_is_demo_mode") === "true";
    }
    $: if (browser) {
        localStorage.setItem("tvjp_is_demo_mode", isDemoMode.toString());
    }
    let isRegistering = false;
    let messageIdCounter = 0;
    let openAccuracyPopups = {};

    let toast = { show: false, message: "", type: "info" };
    function showToast(msg, type = "info") {
        toast = { show: true, message: msg, type };
        setTimeout(() => {
            toast.show = false;
        }, 5000);
    }

    function nextMsgId() {
        return `msg_${++messageIdCounter}_${Date.now()}`;
    }

    function renderMarkdown(content) {
        if (!content) return "";
        return DOMPurify.sanitize(marked.parse(content));
    }

    afterUpdate(() => {
        // Auto-scroll hanya aktif jika AI sedang berpikir (loading) atau sedang mengetik (isStreaming)
        if (chatContainer && (isStreaming || loading)) {
            requestAnimationFrame(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            });
        }
    });

    const handleMouseMove = (event) => {
        const canvasWidth = window.innerWidth / 2;
        mouse.x = (event.clientX / canvasWidth) * 1.2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2.2 + 1;
        if (vrmController) vrmController.updateMouse(mouse.x, mouse.y);
    };

    onMount(async () => {
        if (browser && typeof document !== "undefined") {
            document.body.style.overflow = "hidden";
            document.body.style.height = "100vh";
        }
        await initAuth();
        if (!canvas) return;
        window.addEventListener("mousemove", handleMouseMove);

        const { VRMController } = await import("../lib/vrm_controller");
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(
            35.0,
            canvas.clientWidth / canvas.clientHeight,
            0.1,
            20.0,
        );
        camera.position.set(0, 2.4, 3.5);

        renderer = new THREE.WebGLRenderer({
            canvas,
            antialias: true,
            alpha: true,
        });
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.1;

        scene.add(new THREE.AmbientLight(0xffffff, 1.0));
        const hemi = new THREE.HemisphereLight(0xe8f4ff, 0xfff4e0, 0.6);
        scene.add(hemi);
        const key = new THREE.DirectionalLight(0xfff8f0, 1.5);
        key.position.set(2, 4, 4);
        key.castShadow = true;
        scene.add(key);
        const rim = new THREE.DirectionalLight(0xb0d8ff, 0.5);
        rim.position.set(-2, 2, -3);
        scene.add(rim);

        vrmController = new VRMController(scene, camera);
        try {
            await vrmController.loadModel("/Alisa Sensei.vrm");
        } catch (e) {
            console.error(e);
        }

        // Fetch User Profile if logged in
        if ($user) fetchFullProfile($user.id);

        let lastTime = performance.now();
        ro = new ResizeObserver(() => {
            if (!canvas?.clientWidth) return;
            camera.aspect = canvas.clientWidth / canvas.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        });
        ro.observe(canvas);

        const loop = (t) => {
            animationFrameId = requestAnimationFrame(loop);
            const d = (t - lastTime) / 1000;
            lastTime = t;
            if (vrmController && d > 0) vrmController.update(d, t / 1000);
            renderer.render(scene, camera);
        };
        animationFrameId = requestAnimationFrame(loop);

        chatStore.update((s) => {
            if (s.messages && s.messages.length > 0) {
                return s; // Keep existing chat history
            }
            return {
                ...s,
                messages: [
                    {
                        id: nextMsgId(),
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
                suggestions: [
                    "Ajari aku kanji N5",
                    "Berikan 3 kosakata",
                    "Apa itu tata bahasa です？",
                ],
            };
        });
    });

    onDestroy(() => {
        if (browser && typeof window !== "undefined") {
            window.removeEventListener("mousemove", handleMouseMove);
        }
        if (ro) ro.disconnect();
        if (renderer) renderer.dispose();
        if (animationFrameId) cancelAnimationFrame(animationFrameId);
        if (browser && typeof document !== "undefined") {
            document.body.style.overflow = "";
            document.body.style.height = "";
        }
    });

    async function handleLogin() {
        if (!email || !password) {
            authError = "Email dan password wajib diisi.";
            return;
        }
        if (!email.includes("@")) {
            authError = "Format email tidak valid.";
            return;
        }

        authLoading = true;
        authError = "";
        try {
            const loggedInUser = await login(email, password);
            isDemoMode = false;
            if (loggedInUser) {
                // Fetch profile to verify role immediately
                const res = await fetch(
                    `http://localhost:8000/api/v1/user/profile/${loggedInUser.id}`,
                );
                if (res.ok) {
                    const profileData = await res.json();
                    if (profileData.role === "admin") {
                        showToast(
                            "Selamat datang, Admin! Mengalihkan...",
                            "success",
                        );
                        await fetchFullProfile(loggedInUser.id);
                        goto("/admin");
                        return;
                    }
                }
                await fetchFullProfile(loggedInUser.id);
            }
            showToast("Berhasil masuk! Selamat datang kembali.", "success");
        } catch (e) {
            console.error("Login error:", e);
            authError = e.message || "Login gagal. Periksa email dan password.";
        } finally {
            authLoading = false;
        }
    }

    // ── Countries List (ISO-compliant complete list in Indonesian, without 'Lainnya') ──
    const countries = [
        "Indonesia",
        "Jepang",
        "Malaysia",
        "Singapura",
        "Thailand",
        "Filipina",
        "Vietnam",
        "Brunei Darussalam",
        "Kamboja",
        "Laos",
        "Myanmar",
        "Timor Leste",
        "Afganistan",
        "Afrika Selatan",
        "Albania",
        "Aljazair",
        "Amerika Serikat",
        "Andorra",
        "Angola",
        "Antigua dan Barbuda",
        "Arab Saudi",
        "Argentina",
        "Armenia",
        "Australia",
        "Austria",
        "Azerbaijan",
        "Bahama",
        "Bahrain",
        "Bangladesh",
        "Barbados",
        "Belanda",
        "Belarus",
        "Belgia",
        "Belize",
        "Benin",
        "Bhutan",
        "Bolivia",
        "Bosnia dan Herzegovina",
        "Botswana",
        "Brasil",
        "Britania Raya",
        "Bulgaria",
        "Burkina Faso",
        "Burundi",
        "Ceko",
        "Chad",
        "Chili",
        "China",
        "Denmark",
        "Djibouti",
        "Dominika",
        "Ekuador",
        "El Salvador",
        "Eritrea",
        "Estonia",
        "Eswatini",
        "Ethiopia",
        "Fiji",
        "Finlandia",
        "Gabon",
        "Gambia",
        "Georgia",
        "Ghana",
        "Grenada",
        "Guatemala",
        "Guinea",
        "Guinea Khatulistiwa",
        "Guinea-Bissau",
        "Guyana",
        "Haiti",
        "Honduras",
        "Hong Kong",
        "Hongaria",
        "India",
        "Irak",
        "Iran",
        "Irlandia",
        "Islandia",
        "Israel",
        "Italia",
        "Jamaika",
        "Jerman",
        "Kamerun",
        "Kanada",
        "Kazakhstan",
        "Kenya",
        "Kepulauan Marshall",
        "Kepulauan Solomon",
        "Kirgistan",
        "Kiribati",
        "Kolombia",
        "Komoro",
        "Kongo",
        "Korea Selatan",
        "Korea Utara",
        "Kosta Rika",
        "Kroasia",
        "Kuba",
        "Kuwait",
        "Latvia",
        "Lebanon",
        "Lesotho",
        "Liberia",
        "Libia",
        "Liechtenstein",
        "Lituania",
        "Luksemburg",
        "Madagaskar",
        "Makedonia Utara",
        "Maladewa",
        "Malawi",
        "Mali",
        "Malta",
        "Maroko",
        "Mauritania",
        "Mauritius",
        "Meksiko",
        "Mesir",
        "Mikronesia",
        "Moldova",
        "Monako",
        "Mongolia",
        "Montenegro",
        "Mozambik",
        "Namibia",
        "Nauru",
        "Nepal",
        "Niger",
        "Nigeria",
        "Nikaragua",
        "Norwegia",
        "Oman",
        "Pakistan",
        "Palau",
        "Panama",
        "Papua Nugini",
        "Paraguay",
        "Prancis",
        "Peru",
        "Polandia",
        "Portugal",
        "Qatar",
        "Republik Afrika Tengah",
        "Republik Demokratik Kongo",
        "Republik Dominika",
        "Rumania",
        "Rusia",
        "Rwanda",
        "Saint Kitts dan Nevis",
        "Saint Lucia",
        "Saint Vincent dan Grenadines",
        "Samoa",
        "San Marino",
        "Sao Tome dan Principe",
        "Selandia Baru",
        "Senegal",
        "Serbia",
        "Seychelles",
        "Siprus",
        "Slovakia",
        "Slovenia",
        "Somalia",
        "Spanyol",
        "Sri Lanka",
        "Sudan",
        "Sudan Selatan",
        "Suriname",
        "Swedia",
        "Swiss",
        "Suriah",
        "Taiwan",
        "Tajikistan",
        "Tanjung Verde",
        "Tanzania",
        "Togo",
        "Tonga",
        "Trinidad dan Tobago",
        "Tunisia",
        "Turki",
        "Turkmenistan",
        "Tuvalu",
        "Uganda",
        "Ukraina",
        "Uruguay",
        "Uzbekistan",
        "Vanuatu",
        "Vatikan",
        "Venezuela",
        "Yaman",
        "Yordania",
        "Yunani",
        "Zambia",
        "Zimbabwe",
    ];

    // ── Searchable Country Dropdown State ──
    let countrySearchQuery = "Indonesia";
    let showCountryDropdown = false;
    $: filteredCountries = countries.filter((c) =>
        c.toLowerCase().includes(countrySearchQuery.toLowerCase()),
    );
    $: {
        if (countries.includes(countrySearchQuery)) {
            regCountry = countrySearchQuery;
        }
    }

    // ── Registration Demographics State ──
    let regFullName = "";
    let regAge = "";
    let regGender = "prefer_not_to_say";
    let regCountry = "Indonesia";
    let regPurpose = "";
    let regLevel = "beginner";

    async function handleRegister() {
        if (!email || !password) {
            authError = "Email dan password wajib diisi.";
            return;
        }
        if (password.length < 6) {
            authError = "Password minimal 6 karakter.";
            return;
        }
        if (!countries.includes(regCountry)) {
            authError = "Harap pilih asal negara yang valid dari daftar.";
            return;
        }

        authLoading = true;
        authError = "";
        try {
            await register(email, password, {
                full_name: regFullName || email.split("@")[0],
                age: regAge ? parseInt(regAge) : null,
                gender: regGender,
                country: regCountry,
                study_purpose: regPurpose,
                japanese_level: regLevel,
            });
            showToast(
                "Registrasi berhasil! Silakan cek email atau langsung login.",
                "success",
            );
            isRegistering = false;
            // Clear inputs
            password = "";
            regFullName = "";
            regAge = "";
            regGender = "prefer_not_to_say";
            regCountry = "Indonesia";
            countrySearchQuery = "Indonesia";
            regPurpose = "";
            regLevel = "beginner";
        } catch (e) {
            console.error("Register error:", e);
            authError = e.message || "Registrasi gagal.";
        } finally {
            authLoading = false;
        }
    }

    let showLoginModal = false;

    function handleTabClick(tab) {
        if (tab !== "study" && !$user) {
            showLoginModal = true;
            return;
        }
        mainTab = tab;
        if (browser) {
            localStorage.setItem("tvjp_main_tab", tab);
        }
    }

    function handleModeClick(k) {
        if (k === "quest" && isDemoMode) {
            showLoginModal = true;
            return;
        }
        mode = k;
        if (browser) {
            localStorage.setItem("tvjp_mode", k);
        }
    }

    // ── WebSocket state ─────────────────────────────────────────────────────────
    let _ws = null;
    let _currentWsHandler = null; // Track active handler to prevent listener leaks
    const WS_URL = "ws://localhost:8000/api/v1/ws/chat";

    /** Lazily open (or reuse) a persistent WebSocket connection. */
    function getWS() {
        if (
            _ws &&
            (_ws.readyState === WebSocket.OPEN ||
                _ws.readyState === WebSocket.CONNECTING)
        ) {
            return _ws;
        }
        _ws = new WebSocket(WS_URL);
        _ws.onclose = () => {
            _ws = null;
        };
        _ws.onerror = (e) => {
            console.warn("[WS] error", e);
        };
        return _ws;
    }

    /** Convert base64 WAV string → Blob URL (no extra HTTP fetch). */
    function b64ToUrl(b64) {
        const binary = atob(b64);
        const buf = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) buf[i] = binary.charCodeAt(i);
        return URL.createObjectURL(new Blob([buf], { type: "audio/wav" }));
    }

    // ── Primary: WebSocket-based sendChat ──────────────────────────────
    async function sendChat(text = null) {
        const userText = (text || query).trim();
        if (!userText || loading) return;
        query = "";

        chatStore.update((s) => ({
            ...s,
            messages: [
                ...s.messages,
                {
                    id: nextMsgId(),
                    role: "user",
                    content: userText,
                    vocab: [],
                    grammar: [],
                    suggestions: [],
                },
            ],
            suggestions: [],
        }));

        loading = true;
        isStreaming = false; // Don't show typing bubble until we actually have text
        activeStreamText = "";
        finalRawText = "";
        isStreamDone = false;
        finalMetadata = null;
        finalAccuracy = null;
        sentencePlaybackQueue = [];
        isPlayingAudio = false;
        let currentMetadata = { vocab: [], grammar: [], suggestions: [] };

        let historyData = [];
        const unsub = chatStore.subscribe((s) => {
            historyData = s.messages
                .slice(0, -1)
                .slice(-10)
                .map((m) => ({
                    role: m.role === "tutor" ? "assistant" : "user",
                    content: m.content,
                }));
        });
        unsub();

        const ws = getWS();

        /** Handler scoped to this conversation turn. */
        function handleMessage(evt) {
            let ev;
            try {
                ev = JSON.parse(evt.data);
            } catch {
                return;
            }

            if (ev.type === "metadata") {
                currentMetadata = ev;
            } else if (ev.type === "sentence") {
                if (loading) {
                    loading = false;
                    isStreaming = true; // Switch from thinking bubble to typing bubble
                }

                let cleanContent = (ev.content || "").replace(
                    /Wiki\s*Link:\s*\[.*?\]/gi,
                    "",
                );

                if (cleanContent) {
                    finalRawText += cleanContent;

                    // Decode base64 audio → Blob URL (zero extra HTTP requests!)
                    let audioUrl = null,
                        blobUrl = false;
                    if (ev.audio_b64) {
                        audioUrl = b64ToUrl(ev.audio_b64);
                        blobUrl = true;
                    }
                    sentencePlaybackQueue.push({
                        text: cleanContent,
                        audioUrl,
                        blobUrl,
                    });
                    if (!isPlayingAudio) playNextAudio();
                }
            } else if (ev.type === "profile_update") {
                const oldXp = $profile?.xp || 0;
                const oldLevel = $profile?.level || 1;
                if ($user) {
                    fetchFullProfile($user.id).then(() => {
                        const newXp = $profile?.xp || 0;
                        const newLevel = $profile?.level || 1;
                        if (newXp > oldXp) sfx.playXpGain();
                        else sfx.playWikiSync();
                        if (newLevel > oldLevel) {
                            sfx.playLevelUp();
                            shootConfetti();
                        }
                    });
                }
            } else if (ev.type === "error") {
                loading = false;
                activeStreamText += ev.content || "";
            } else if (ev.type === "done") {
                ws.removeEventListener("message", handleMessage);
                _currentWsHandler = null;
                isStreamDone = true;
                finalMetadata = currentMetadata;
                finalAccuracy = ev.accuracy || null;

                // ── Debug: log detail verifikasi tiap fakta di console ──
                if (ev.accuracy?.facts_detail?.length > 0) {
                    const acc = ev.accuracy;
                    console.groupCollapsed(
                        `%c[KG Verify] ${acc.pct}% — ${acc.verified}/${acc.total} fakta terverifikasi`,
                        `color: ${acc.pct >= 90 ? "#4ade80" : acc.pct >= 70 ? "#facc15" : "#f97316"}; font-weight:bold`,
                    );
                    console.table(
                        acc.facts_detail.map((f) => ({
                            status: f.match ? "✅" : "❌",
                            tipe: f.type,
                            subjek: f.subject,
                            props: f.props.join(" | ") || "(none)",
                            cocok: f.matched_prop ?? "—",
                        })),
                    );
                    console.groupEnd();
                }

                if (
                    !isPlayingAudio &&
                    sentencePlaybackQueue.length === 0 &&
                    !typeInterval
                ) {
                    finalizeStream();
                }
            }
        }

        function dispatch() {
            // Clean up any stale handler from previous queries
            if (_currentWsHandler) {
                ws.removeEventListener("message", _currentWsHandler);
            }
            _currentWsHandler = handleMessage;
            ws.send(
                JSON.stringify({
                    query: userText,
                    student_id: $user?.id || "default_user",
                    mode,
                    history: historyData,
                }),
            );
            ws.addEventListener("message", handleMessage);
        }

        if (ws.readyState === WebSocket.OPEN) {
            dispatch();
        } else {
            ws.addEventListener("open", () => dispatch(), { once: true });
        }
    }

    // ── Fallback: SSE-based chat (legacy path) ──────────────────────────
    async function sendChatSSE(userText) {
        let currentMetadata = { vocab: [], grammar: [], suggestions: [] };
        let historyData = [];
        const unsub = chatStore.subscribe((s) => {
            historyData = s.messages
                .slice(0, -1)
                .slice(-10)
                .map((m) => ({
                    role: m.role === "tutor" ? "assistant" : "user",
                    content: m.content,
                }));
        });
        unsub();
        try {
            const res = await fetch("http://localhost:8000/api/v1/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: userText,
                    history: historyData,
                    mode,
                    student_id: $user?.id || "default_user",
                }),
            });
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "",
                done = false;
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
                            if (ev.type === "metadata") {
                                currentMetadata = ev;
                            } else if (ev.type === "sentence") {
                                if (loading && (ev.content || "").trim())
                                    loading = false;
                                let cleanContent = (ev.content || "").replace(
                                    /Wiki\s*Link:\s*\[.*?\]/gi,
                                    "",
                                );
                                if (cleanContent) {
                                    finalRawText += cleanContent;
                                    const audioUrl = ev.audio
                                        ? `http://localhost:8000/api/v1/get-audio/${ev.audio}`
                                        : null;
                                    sentencePlaybackQueue.push({
                                        text: cleanContent,
                                        audioUrl,
                                        blobUrl: false,
                                    });
                                    if (!isPlayingAudio) playNextAudio();
                                }
                            } else if (ev.type === "done") {
                                isStreamDone = true;
                                finalMetadata = currentMetadata;
                                finalAccuracy = ev.accuracy || null;
                                if (
                                    !isPlayingAudio &&
                                    sentencePlaybackQueue.length === 0
                                )
                                    finalizeStream();
                            }
                        } catch {
                            /* ignore */
                        }
                    }
                }
            }
        } catch (e) {
            console.error("[SSE]", e);
            isStreaming = false;
            chatStore.update((s) => ({
                ...s,
                messages: [
                    ...s.messages,
                    {
                        id: nextMsgId(),
                        role: "tutor",
                        content:
                            "⚠️ Maaf, koneksi ke server terputus. Pastikan backend aktif.",
                        vocab: [],
                        grammar: [],
                        suggestions: [],
                    },
                ],
            }));
        } finally {
            loading = false;
        }
    }

    let voiceRecordingCancelled = false;

    async function startRecording() {
        if (!navigator.mediaDevices?.getUserMedia)
            return showToast("Browser tidak mendukung mikrofon.", "error");
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true,
            });
            const mimeType = MediaRecorder.isTypeSupported(
                "audio/webm;codecs=opus",
            )
                ? "audio/webm;codecs=opus"
                : "audio/webm";
            mediaRecorder = new MediaRecorder(stream, { mimeType });
            audioChunks = [];
            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) audioChunks.push(e.data);
            };
            mediaRecorder.onstop = sendVoiceData;
            mediaRecorder.start();
            isRecording = true;
            liveTranscript = "";
            finalTranscriptBuffer = ""; // Reset buffer di awal sesi baru
            voiceRecordingCancelled = false; // Reset status batal

            // Init Real-time Speech Recognition for visual feedback (nonaktifkan di Voice Mode)
            if (
                browser &&
                mode !== "voice" &&
                (window.SpeechRecognition || window.webkitSpeechRecognition)
            ) {
                const SpeechRecognition =
                    window.SpeechRecognition || window.webkitSpeechRecognition;
                speechRecognizer = new SpeechRecognition();
                speechRecognizer.continuous = true;
                speechRecognizer.interimResults = true;
                // Gunakan id-ID agar teks mengambang menggunakan alfabet (seperti Romaji)
                speechRecognizer.lang = "id-ID";

                speechRecognizer.onresult = (event) => {
                    // Iterasi hanya dari resultIndex (kalimat baru sejak event terakhir)
                    for (
                        let i = event.resultIndex;
                        i < event.results.length;
                        ++i
                    ) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            // Kalimat sudah final → masuk ke buffer permanen
                            finalTranscriptBuffer +=
                                (finalTranscriptBuffer ? " " : "") +
                                transcript.trim();
                        }
                    }
                    // Kumpulkan interim (belum final) dari hasil terkini
                    let interim = "";
                    for (let i = 0; i < event.results.length; ++i) {
                        if (!event.results[i].isFinal) {
                            interim += event.results[i][0].transcript;
                        }
                    }
                    // liveTranscript = semua kalimat final + interim yang sedang diucapkan
                    liveTranscript =
                        finalTranscriptBuffer +
                        (interim ? " " + interim.trim() : "");
                };

                speechRecognizer.start();
            }
        } catch (err) {
            console.error("Mic error:", err);
            showToast("Akses mikrofon ditolak.", "error");
        }
    }

    function stopRecording(isCancelled = false) {
        if (mediaRecorder && isRecording) {
            voiceRecordingCancelled = isCancelled;
            // Stop speech recognizer FIRST to avoid race condition with MediaRecorder onstop
            if (speechRecognizer) {
                try {
                    speechRecognizer.stop();
                } catch (_) {}
                speechRecognizer = null;
            }

            mediaRecorder.stop();
            isRecording = false;
            mediaRecorder.stream.getTracks().forEach((t) => t.stop());
        }
    }

    async function sendVoiceData() {
        if (!audioChunks.length) return;
        if (voiceRecordingCancelled) {
            voiceRecordingCancelled = false; // Reset
            audioChunks = [];
            loading = false;
            return;
        }
        loading = true;
        // Snapshot seluruh teks: finalBuffer (semua kalimat final) atau liveTranscript
        const captured =
            finalTranscriptBuffer.trim() || liveTranscript.trim() || "";
        liveTranscript = "";
        finalTranscriptBuffer = "";
        const blob = new Blob(audioChunks, { type: "audio/webm" });
        const fd = new FormData();
        fd.append("audio", blob, "input.webm");
        fd.append("mode", mode);
        try {
            const res = await fetch("http://localhost:8000/api/v1/transcribe", {
                method: "POST",
                body: fd,
            });
            const d = await res.json();
            // Prioritas: Jika voice mode, abaikan liveTranscript (Web Speech) karena tidak aktif, andalkan Whisper sepenuhnya.
            const finalText =
                mode === "voice"
                    ? d.text || d.transcript || null
                    : captured || d.text || d.transcript || null;

            loading = false;

            if (finalText) {
                // Mode voice: kirim ke VoiceMode speaking practice (bukan sendChat biasa)
                if (mode === "voice" && voiceModeRef) {
                    voiceModeRef.handleVoiceResult(finalText);
                } else {
                    await sendChat(finalText);
                }
            } else {
                throw new Error("STT kosong");
            }
        } catch (e) {
            console.error(e);
            chatStore.update((s) => ({
                ...s,
                messages: [
                    ...s.messages,
                    {
                        id: nextMsgId(),
                        role: "tutor",
                        content: "⚠️ Suara tidak terdeteksi. Coba lagi.",
                        vocab: [],
                        grammar: [],
                        suggestions: [],
                    },
                ],
            }));
        } finally {
            loading = false;
        }
    }

    // Mode label helpers
    const modeConfig = {
        discovery: {
            label: "Discovery",
            icon: "💬",
            color: "from-sky-500 to-indigo-600",
            ring: "ring-sky-400/40",
            badge: "bg-sky-500/20 text-sky-300 border-sky-400/30",
            placeholder: "Tanya apa saja tentang N5...",
        },
        quest: {
            label: "Quest",
            icon: "⚔️",
            color: "from-emerald-500 to-teal-600",
            ring: "ring-emerald-400/40",
            badge: "bg-emerald-500/20 text-emerald-300 border-emerald-400/30",
            placeholder: "Ketik jawaban atau minta soal baru...",
        },
        voice: {
            label: "Voice",
            icon: "🎤",
            color: "from-violet-500 to-purple-600",
            ring: "ring-violet-400/40",
            badge: "bg-violet-500/20 text-violet-300 border-violet-400/30",
            placeholder: "",
        },
    };
    $: cfg = modeConfig[mode];

    // SIMPLE CONFETTI SCRIPT
    function shootConfetti() {
        const duration = 3 * 1000;
        const end = Date.now() + duration;

        (function frame() {
            // Kita bisa menggunakan emoji partikel sederhana via DOM jika library tidak tersedia
            const el = document.createElement("div");
            el.innerHTML = "✨";
            el.className = "fixed pointer-events-none text-2xl z-[9999]";
            el.style.left = Math.random() * 100 + "vw";
            el.style.top = "-50px";
            document.body.appendChild(el);

            const animation = el.animate(
                [
                    {
                        transform: "translate3d(0,0,0) rotate(0deg)",
                        opacity: 1,
                    },
                    {
                        transform: `translate3d(${Math.random() * 200 - 100}px, 100vh, 0) rotate(${Math.random() * 360}deg)`,
                        opacity: 0,
                    },
                ],
                {
                    duration: Math.random() * 1000 + 1000,
                    easing: "cubic-bezier(.37,0,.63,1)",
                },
            );

            animation.onfinish = () => el.remove();

            if (Date.now() < end) {
                requestAnimationFrame(frame);
            }
        })();
    }
</script>

<svelte:head>
    <title>A.L.I.S.A — Japanese Virtual Tutor N5</title>
    <meta
        name="description"
        content="Belajar bahasa Jepang N5 bersama A.L.I.S.A, tutor virtual berbasis AI & Knowledge Graph."
    />
</svelte:head>

<!-- ══════════════════════════════════════════
     LOGIN OVERLAY
══════════════════════════════════════════ -->
{#if !$user && !isDemoMode}
    <div class="login-overlay">
        <div class="login-card animate-slide-up">
            <!-- Card glow accent -->
            <div class="login-glow"></div>

            <!-- Logo / Avatar -->
            <div class="login-avatar">
                <span class="login-avatar-letter">A</span>
                <span class="login-avatar-badge"></span>
            </div>

            <h1 class="login-title">A.L.I.S.A</h1>
            <p class="login-sub">Tutor Virtual Bahasa Jepang N5</p>

            <!-- Japanese decorative text -->
            <p class="login-jp">
                {isRegistering ? "Pengguna Baru" : "Selamat Datang"}
            </p>

            <div class="login-form">
                <div class="input-group">
                    <label for="login-email" class="input-label">Email</label>
                    <input
                        id="login-email"
                        type="email"
                        bind:value={email}
                        on:keypress={(e) =>
                            e.key === "Enter" &&
                            (isRegistering ? handleRegister() : handleLogin())}
                        class="login-input"
                        placeholder="nama@email.com"
                    />
                </div>
                <div class="input-group">
                    <label for="login-password" class="input-label"
                        >Password</label
                    >
                    <input
                        id="login-password"
                        type="password"
                        bind:value={password}
                        on:keypress={(e) =>
                            e.key === "Enter" &&
                            (isRegistering ? handleRegister() : handleLogin())}
                        class="login-input"
                        placeholder="••••••••"
                    />
                </div>

                {#if isRegistering}
                    <div class="register-demographics">
                        <div class="input-group">
                            <label for="reg-fullname" class="input-label"
                                >Nama Lengkap</label
                            >
                            <input
                                id="reg-fullname"
                                type="text"
                                bind:value={regFullName}
                                class="login-input"
                                placeholder="Nama lengkap"
                            />
                        </div>
                        <div class="demo-row">
                            <div class="input-group" style="flex:1">
                                <label for="reg-age" class="input-label"
                                    >Umur</label
                                >
                                <input
                                    id="reg-age"
                                    type="number"
                                    bind:value={regAge}
                                    class="login-input"
                                    placeholder="22"
                                    min="10"
                                    max="99"
                                />
                            </div>
                            <div class="input-group" style="flex:1">
                                <label for="reg-gender" class="input-label"
                                    >Gender</label
                                >
                                <select
                                    id="reg-gender"
                                    bind:value={regGender}
                                    class="login-input"
                                >
                                    <option value="male">Laki-laki</option>
                                    <option value="female">Perempuan</option>
                                    <option value="prefer_not_to_say"
                                        >Lainnya</option
                                    >
                                </select>
                            </div>
                        </div>
                        <div class="input-group" style="position: relative;">
                            <label for="reg-country" class="input-label"
                                >Asal Negara</label
                            >
                            <input
                                id="reg-country"
                                type="text"
                                bind:value={countrySearchQuery}
                                on:focus={() => (showCountryDropdown = true)}
                                on:blur={() =>
                                    setTimeout(
                                        () => (showCountryDropdown = false),
                                        200,
                                    )}
                                class="login-input"
                                placeholder="Cari asal negara..."
                            />
                            {#if showCountryDropdown}
                                <div
                                    class="absolute z-[100] left-0 right-0 mt-1 max-h-48 overflow-y-auto bg-[#1e1b4b] border border-white/10 rounded-xl shadow-2xl custom-scroll"
                                >
                                    {#each filteredCountries as c}
                                        <button
                                            type="button"
                                            on:click={() => {
                                                countrySearchQuery = c;
                                                showCountryDropdown = false;
                                            }}
                                            class="w-full text-left px-4 py-2.5 text-sm text-slate-200 hover:bg-indigo-600 hover:text-white transition bg-transparent border-none cursor-pointer"
                                        >
                                            {c}
                                        </button>
                                    {/each}
                                    {#if filteredCountries.length === 0}
                                        <div
                                            class="px-4 py-2.5 text-sm text-slate-400"
                                        >
                                            Negara tidak ditemukan
                                        </div>
                                    {/if}
                                </div>
                            {/if}
                        </div>
                        <div class="input-group">
                            <label for="reg-purpose" class="input-label"
                                >Tujuan Belajar</label
                            >
                            <select
                                id="reg-purpose"
                                bind:value={regPurpose}
                                class="login-input"
                            >
                                <option value="">-- Pilih --</option>
                                <option value="akademik"
                                    >Akademik / Sekolah</option
                                >
                                <option value="kerja">Bekerja di Jepang</option>
                                <option value="hobi"
                                    >Hobi / Anime / Manga</option
                                >
                                <option value="wisata">Wisata ke Jepang</option>
                            </select>
                        </div>
                        <div class="input-group">
                            <label for="reg-level" class="input-label"
                                >Level Bahasa Jepang</label
                            >
                            <select
                                id="reg-level"
                                bind:value={regLevel}
                                class="login-input"
                            >
                                <option value="beginner"
                                    >Pemula (belum bisa)</option
                                >
                                <option value="basic"
                                    >Dasar (tahu sedikit)</option
                                >
                                <option value="intermediate"
                                    >Menengah (bisa percakapan dasar)</option
                                >
                            </select>
                        </div>
                    </div>
                {/if}

                {#if authError}
                    <div class="login-error">⚠️ {authError}</div>
                {/if}

                <button
                    id="btn-login"
                    on:click={isRegistering ? handleRegister : handleLogin}
                    disabled={authLoading}
                    class="btn-login"
                >
                    {#if authLoading}
                        <span class="btn-spinner"></span>
                        {isRegistering ? "Mendaftar..." : "Masuk..."}
                    {:else}
                        {isRegistering ? "Daftar Sekarang" : "Masuk Sekarang →"}
                    {/if}
                </button>

                <button
                    on:click={() => (isRegistering = !isRegistering)}
                    class="text-indigo-400 text-xs mt-3 block mx-auto hover:underline bg-transparent border-none cursor-pointer"
                >
                    {isRegistering
                        ? "Sudah punya akun? Login"
                        : "Belum punya akun? Daftar"}
                </button>

                <div class="login-divider"><span>atau</span></div>

                <button on:click={() => (isDemoMode = true)} class="btn-demo">
                    Coba Tanpa Akun (Demo)
                </button>
            </div>

            <p class="login-footer">
                Sistem AI • Knowledge Graph • N5 Curriculum
            </p>
        </div>
    </div>
{/if}

<!-- ══════════════════════════════════════════
     CUSTOM TOAST NOTIFICATION
══════════════════════════════════════════ -->
{#if toast.show}
    <div
        class="fixed top-10 left-1/2 -translate-x-1/2 z-[200] max-w-sm w-full px-4"
        in:fly={{ y: -50, duration: 500 }}
        out:fade
    >
        <div
            class="bg-slate-900/90 backdrop-blur-xl border border-white/10 p-5 rounded-[24px] shadow-[0_20px_50px_rgba(0,0,0,0.5)] flex items-center gap-4 relative overflow-hidden group"
        >
            <!-- Accent glow inside toast -->
            <div
                class="absolute inset-0 bg-gradient-to-r {toast.type ===
                'success'
                    ? 'from-emerald-500/10'
                    : 'from-indigo-500/10'} to-transparent opacity-50"
            ></div>

            <div
                class="w-12 h-12 {toast.type === 'success'
                    ? 'bg-emerald-500'
                    : 'bg-indigo-500'} rounded-2xl flex items-center justify-center text-2xl shadow-lg relative z-10"
            >
                {toast.type === "success" ? "✅" : "ℹ️"}
            </div>

            <div class="flex-1 relative z-10">
                <h4
                    class="text-white font-black text-sm uppercase tracking-wider mb-0.5"
                >
                    Berhasil!
                </h4>
                <p class="text-slate-400 text-xs leading-relaxed font-medium">
                    {toast.message}
                </p>
            </div>

            <button
                on:click={() => (toast.show = false)}
                class="text-slate-500 hover:text-white transition relative z-10 px-2"
                >✕</button
            >
        </div>
    </div>
{/if}

<!-- ══════════════════════════════════════════
     MAIN APP
══════════════════════════════════════════ -->
<main class="app-root">
    <!-- Background: kelas cerah, tidak gelap -->
    <div class="bg-scene"></div>
    <div class="bg-overlay"></div>

    <!-- LEFT: VRM Canvas -->
    <section class="vrm-panel">
        <canvas bind:this={canvas} class="vrm-canvas"></canvas>

        <!-- Mode badge floating on VRM panel -->
        <div class="vrm-mode-badge {cfg.badge}">
            {cfg.icon}
            {cfg.label} Mode
        </div>

        <!-- Status card bottom-left -->
        <div class="vrm-status-card">
            <div class="vrm-status-dot"></div>
            <div>
                <p class="vrm-status-name">A.L.I.S.A</p>
                <p class="vrm-status-sub">Online • N5 Specialist</p>
            </div>
        </div>
    </section>

    <!-- Custom Login Modal Popup -->
    {#if showLoginModal}
        <div
            class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm pointer-events-auto"
        >
            <div
                class="bg-slate-800 rounded-3xl p-8 max-w-sm w-full mx-4 shadow-2xl border border-slate-600 outline outline-4 outline-indigo-500/20 transform transition-all"
            >
                <div class="text-4xl mb-4 text-center">🔒</div>
                <h3 class="text-xl font-bold text-white text-center mb-2">
                    Fitur Terkunci
                </h3>
                <p
                    class="text-slate-400 text-center text-sm mb-6 leading-relaxed"
                >
                    Harap <b>Login</b> terlebih dahulu untuk mengakses fitur Quest,
                    Memory, Profile, dan Pencapaian Gamifikasi kamu.
                </p>
                <div class="flex gap-3">
                    <button
                        on:click={() => {
                            showLoginModal = false;
                            isDemoMode = false;
                        }}
                        class="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl transition cursor-pointer shadow-lg shadow-indigo-500/30"
                    >
                        Login Sekarang
                    </button>
                    <button
                        on:click={() => (showLoginModal = false)}
                        class="flex-1 bg-slate-700 hover:bg-slate-600 text-slate-300 font-bold py-3 rounded-xl transition cursor-pointer border border-slate-600"
                    >
                        Nanti
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- RIGHT: Chat Interface -->
    <aside class="chat-panel">
        <div class="chat-shell">
            <!-- ── HEADER ── -->
            <header class="chat-header">
                <div class="chat-header-left">
                    <div class="chat-avatar">
                        <span class="chat-avatar-letter">A</span>
                        <span class="chat-avatar-online"></span>
                    </div>
                    <div>
                        <h2 class="chat-title">A.L.I.S.A</h2>
                        <p class="chat-subtitle">Tutor Bahasa Jepang N5</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    {#if $profile && $profile.role === "admin"}
                        <a
                            href="/admin"
                            class="px-3 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider bg-indigo-600 hover:bg-indigo-500 text-white shadow-md transition duration-200"
                        >
                            🏰 Admin Portal
                        </a>
                    {/if}
                    <button
                        on:click={() => handleTabClick("study")}
                        class="px-3 py-1.5 rounded-lg text-sm font-bold transition {mainTab ===
                        'study'
                            ? 'bg-indigo-500 text-white shadow-md'
                            : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600 hover:text-white border border-slate-600'}"
                        >Study</button
                    >
                    <button
                        on:click={() => handleTabClick("achievement")}
                        class="px-3 py-1.5 rounded-lg text-sm font-bold transition {mainTab ===
                        'achievement'
                            ? 'bg-orange-500 text-white shadow-md'
                            : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600 hover:text-white border border-slate-600'}"
                        >🏆</button
                    >
                    <button
                        on:click={() => handleTabClick("profile")}
                        class="px-3 py-1.5 rounded-lg text-sm font-bold transition {mainTab ===
                        'profile'
                            ? 'bg-blue-500 text-white shadow-md'
                            : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600 hover:text-white border border-slate-600'}"
                        >👤</button
                    >

                    {#if isDemoMode}
                        <button
                            on:click={() => (isDemoMode = false)}
                            class="ml-2 px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500 hover:text-white transition"
                            >Daftar Akun</button
                        >
                    {/if}

                    {#if $user}
                        <div class="w-px h-6 bg-slate-200 mx-1"></div>
                        <button
                            on:click={logout}
                            class="btn-logout"
                            title="Logout"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="16"
                                height="16"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                stroke-width="2"
                                ><path
                                    d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"
                                /><polyline points="16 17 21 12 16 7" /><line
                                    x1="21"
                                    y1="12"
                                    x2="9"
                                    y2="12"
                                /></svg
                            >
                        </button>
                    {/if}
                </div>
            </header>

            {#if mainTab === "profile"}
                <!-- PROFILE TAB -->
                <Profile user={$user} />
            {:else if mainTab === "achievement"}
                <!-- ACHIEVEMENT TAB -->
                <Achievement />
            {:else}
                <!-- ── STUDY / CHAT TAB ── -->

                <!-- ── MODE TABS ── -->
                <div class="mode-tabs">
                    {#each Object.entries(modeConfig) as [k, v]}
                        <button
                            id="tab-{k}"
                            on:click={() => handleModeClick(k)}
                            class="mode-tab {mode === k
                                ? 'mode-tab-active bg-gradient-to-r ' + v.color
                                : ''} {isDemoMode && k === 'quest'
                                ? 'opacity-60 grayscale-[0.5]'
                                : ''}"
                        >
                            <span
                                >{isDemoMode && k === "quest"
                                    ? "🔒"
                                    : v.icon}</span
                            >
                            <span>{v.label}</span>
                        </button>
                    {/each}
                </div>

                <audio bind:this={audioPlayer} class="hidden"></audio>

                <!-- ── MAIN CONTENT ── -->
                <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
                    {#if mode === "quest"}
                        <QuestMode {vrmController} />
                    {:else if mode === "voice"}
                        <!-- ── VOICE: full-panel speaking practice ── -->
                        <VoiceMode
                            bind:this={voiceModeRef}
                            bind:isRecording
                            {loading}
                            {startRecording}
                            {stopRecording}
                            {liveTranscript}
                            {vrmController}
                        />
                    {:else}
                        <!-- ── MESSAGES ── -->
                        <div
                            bind:this={chatContainer}
                            class="messages-area custom-scroll"
                        >
                            {#each $chatStore.messages as msg (msg.id)}
                                <div
                                    class="msg-row {msg.role === 'user'
                                        ? 'msg-row-user'
                                        : 'msg-row-tutor'} animate-msg"
                                >
                                    {#if msg.role === "tutor"}
                                        <div class="msg-avatar-sm">A</div>
                                    {/if}
                                    <div
                                        class="msg-bubble-wrap {msg.role ===
                                        'user'
                                            ? 'items-end'
                                            : 'items-start'}"
                                    >
                                        <div
                                            class="msg-bubble {msg.role ===
                                            'user'
                                                ? 'bubble-user'
                                                : 'bubble-tutor'}"
                                        >
                                            <div class="markdown-content">
                                                {@html renderMarkdown(
                                                    msg.content,
                                                )}
                                            </div>
                                        </div>
                                        {#if msg.role === "tutor" && msg.suggestions?.length > 0}
                                            <div class="suggestions-row">
                                                {#each msg.suggestions as s}
                                                    <button
                                                        on:click={() =>
                                                            sendChat(s)}
                                                        class="suggestion-chip"
                                                        >{s}</button
                                                    >
                                                {/each}
                                            </div>
                                        {/if}

                                        {#if msg.role === "tutor" && msg.accuracy}
                                            <div class="accuracy-container">
                                                <button
                                                    type="button"
                                                    class="accuracy-badge accuracy-{msg
                                                        .accuracy.category} {msg
                                                        .accuracy.category ===
                                                    'grounded'
                                                        ? 'accuracy-badge-clickable'
                                                        : ''} {msg.accuracy
                                                        .category === 'grounded'
                                                        ? msg.accuracy.pct >= 90
                                                            ? 'accuracy-pct-high'
                                                            : msg.accuracy
                                                                    .pct >= 70
                                                              ? 'accuracy-pct-med'
                                                              : msg.accuracy
                                                                      .pct >= 50
                                                                ? 'accuracy-pct-low'
                                                                : 'accuracy-pct-critical'
                                                        : ''}"
                                                    on:click={() => {
                                                        if (
                                                            msg.accuracy
                                                                .category ===
                                                            "grounded"
                                                        ) {
                                                            openAccuracyPopups[
                                                                msg.id
                                                            ] =
                                                                !openAccuracyPopups[
                                                                    msg.id
                                                                ];
                                                        }
                                                    }}
                                                >
                                                    {#if msg.accuracy.category === "no_data"}
                                                        <span
                                                            class="accuracy-icon"
                                                            >📭</span
                                                        >
                                                        <span
                                                            class="accuracy-text"
                                                            >{msg.accuracy
                                                                .label ||
                                                                "Data Tidak Tersedia"}</span
                                                        >
                                                    {:else if msg.accuracy.category === "casual"}
                                                        <span
                                                            class="accuracy-icon"
                                                            >💬</span
                                                        >
                                                        <span
                                                            class="accuracy-text"
                                                            >{msg.accuracy
                                                                .label ||
                                                                "Casual Chat"}</span
                                                        >
                                                    {:else}
                                                        <span
                                                            class="accuracy-icon"
                                                            >🛡️</span
                                                        >
                                                        <span
                                                            class="accuracy-text"
                                                        >
                                                            {msg.accuracy.pct}%
                                                            KG Verified ({msg
                                                                .accuracy
                                                                .verified}/{msg
                                                                .accuracy
                                                                .total})
                                                        </span>
                                                        <span
                                                            class="accuracy-chevron"
                                                            >{openAccuracyPopups[
                                                                msg.id
                                                            ]
                                                                ? "▲"
                                                                : "▼"}</span
                                                        >
                                                    {/if}
                                                </button>

                                                {#if openAccuracyPopups[msg.id] && msg.accuracy.facts_detail && msg.accuracy.facts_detail.length > 0}
                                                    <!-- svelte-ignore a11y-click-events-have-key-events -->
                                                    <!-- svelte-ignore a11y-no-static-element-interactions -->
                                                    <div
                                                        class="accuracy-popup"
                                                        transition:fade={{
                                                            duration: 150,
                                                        }}
                                                        on:click|stopPropagation
                                                    >
                                                        <div
                                                            class="popup-header"
                                                        >
                                                            <span
                                                                class="popup-title"
                                                                >Detail
                                                                Verifikasi</span
                                                            >
                                                            <button
                                                                class="popup-close"
                                                                on:click={() =>
                                                                    (openAccuracyPopups[
                                                                        msg.id
                                                                    ] = false)}
                                                                >&times;</button
                                                            >
                                                        </div>
                                                        <div
                                                            class="popup-body custom-scroll"
                                                        >
                                                            {#each msg.accuracy.facts_detail as fact}
                                                                <div
                                                                    class="fact-row {fact.match
                                                                        ? 'fact-success'
                                                                        : 'fact-fail'}"
                                                                >
                                                                    <span
                                                                        class="fact-status-icon"
                                                                        >{fact.match
                                                                            ? "✅"
                                                                            : "❌"}</span
                                                                    >
                                                                    <div
                                                                        class="fact-info"
                                                                    >
                                                                        <div
                                                                            class="fact-subject-row"
                                                                        >
                                                                            <span
                                                                                class="fact-type-badge type-{fact.type}"
                                                                                >{fact.type}</span
                                                                            >
                                                                            <strong
                                                                                class="fact-subject"
                                                                                >{fact.subject}</strong
                                                                            >
                                                                        </div>
                                                                        <div
                                                                            class="fact-details-text"
                                                                        >
                                                                            {#if fact.match}
                                                                                <span
                                                                                    class="text-success"
                                                                                    >Cocok:
                                                                                    "{fact.matched_prop}"</span
                                                                                >
                                                                            {:else}
                                                                                <span
                                                                                    class="text-fail"
                                                                                    >Tidak
                                                                                    cocok</span
                                                                                >
                                                                            {/if}
                                                                            {#if fact.props && fact.props.length > 0}
                                                                                <div
                                                                                    class="fact-props-list"
                                                                                    title={fact.props.join(
                                                                                        ", ",
                                                                                    )}
                                                                                >
                                                                                    Ref:
                                                                                    {fact.props.join(
                                                                                        ", ",
                                                                                    )}
                                                                                </div>
                                                                            {/if}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            {/each}
                                                        </div>
                                                    </div>
                                                {/if}
                                            </div>
                                        {/if}
                                    </div>
                                </div>
                            {/each}

                            {#if isStreaming}
                                <div class="msg-row msg-row-tutor animate-msg">
                                    <div class="msg-avatar-sm">A</div>
                                    <div class="msg-bubble-wrap items-start">
                                        <div
                                            class="msg-bubble bubble-tutor streaming-bubble"
                                        >
                                            <div class="markdown-content">
                                                {@html renderMarkdown(
                                                    activeStreamText,
                                                )}<span class="cursor-blink"
                                                ></span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            {/if}

                            {#if loading && !isStreaming}
                                <div class="msg-row msg-row-tutor animate-msg">
                                    <div class="msg-avatar-sm">A</div>
                                    <div class="msg-bubble-wrap items-start">
                                        <div
                                            class="msg-bubble bubble-tutor thinking-bubble"
                                        >
                                            <div class="thinking-content">
                                                <div
                                                    class="thinking-dots-premium"
                                                >
                                                    <span></span><span
                                                    ></span><span></span>
                                                </div>
                                                <p class="thinking-label">
                                                    A.L.I.S.A. sedang
                                                    berpikir...
                                                </p>
                                            </div>
                                            <div class="thinking-shimmer"></div>
                                        </div>
                                    </div>
                                </div>
                            {/if}
                        </div>

                        <!-- ── INPUT AREA ── -->
                        <div class="input-area">
                            <DiscoveryMode
                                bind:query
                                {loading}
                                {isStreaming}
                                {modeConfig}
                                {sendChat}
                            />
                        </div>
                    {/if}
                </div>
            {/if}
        </div>
    </aside>
</main>

<style>
    /* ═══════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════ */
    :global(*, *::before, *::after) {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    :global(body) {
        font-family: "Inter", "Noto Sans JP", sans-serif;
        background: #0a0e1a;
    }

    /* ═══════════════════════════════════════════
   LOGIN OVERLAY
═══════════════════════════════════════════ */
    .login-overlay {
        position: fixed;
        inset: 0;
        z-index: 200;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(
            135deg,
            rgba(10, 14, 26, 0.85) 0%,
            rgba(20, 30, 60, 0.9) 100%
        );
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }
    .login-card {
        position: relative;
        width: 100%;
        max-width: 420px;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 28px;
        padding: 48px 40px 40px;
        box-shadow:
            0 32px 64px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.05) inset;
        text-align: center;
        overflow: hidden;
    }
    .login-glow {
        position: absolute;
        top: -80px;
        left: 50%;
        transform: translateX(-50%);
        width: 300px;
        height: 300px;
        background: radial-gradient(
            ellipse,
            rgba(99, 102, 241, 0.25) 0%,
            transparent 70%
        );
        pointer-events: none;
    }
    .login-avatar {
        position: relative;
        width: 80px;
        height: 80px;
        margin: 0 auto 20px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow:
            0 8px 24px rgba(99, 102, 241, 0.4),
            0 0 0 4px rgba(99, 102, 241, 0.15);
        font-size: 32px;
        font-weight: 700;
        color: white;
    }
    .login-avatar-letter {
        line-height: 1;
    }
    .login-avatar-badge {
        position: absolute;
        bottom: 2px;
        right: 2px;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background: #22c55e;
        border: 3px solid rgba(255, 255, 255, 0.1);
        animation: pulse-badge 2s infinite;
    }
    @keyframes pulse-badge {
        0%,
        100% {
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5);
        }
        50% {
            box-shadow: 0 0 0 6px rgba(34, 197, 94, 0);
        }
    }
    .login-title {
        font-size: 26px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 6px;
    }
    .login-sub {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 8px;
    }
    .login-jp {
        font-size: 16px;
        color: rgba(147, 197, 253, 0.7);
        letter-spacing: 4px;
        margin-bottom: 32px;
    }
    .login-form {
        text-align: left;
    }
    .input-group {
        margin-bottom: 16px;
    }
    .input-label {
        display: block;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(255, 255, 255, 0.45);
        margin-bottom: 8px;
    }
    .login-input {
        width: 100%;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 14px 18px;
        font-size: 14px;
        color: #fff;
        outline: none;
        transition: all 0.2s;
    }
    .login-input::placeholder {
        color: rgba(255, 255, 255, 0.25);
    }
    .login-input:focus {
        border-color: rgba(99, 102, 241, 0.6);
        background: rgba(99, 102, 241, 0.08);
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }
    .register-demographics {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 14px 0 4px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        margin-top: 4px;
        animation: demo-slide 0.35s ease-out;
    }
    @keyframes demo-slide {
        from {
            opacity: 0;
            max-height: 0;
            transform: translateY(-8px);
        }
        to {
            opacity: 1;
            max-height: 600px;
            transform: translateY(0);
        }
    }
    .demo-row {
        display: flex;
        gap: 10px;
    }
    .register-demographics .input-group {
        margin-bottom: 0;
    }
    .register-demographics select.login-input {
        appearance: none;
        -webkit-appearance: none;
        cursor: pointer;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='rgba(255,255,255,0.4)' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 14px center;
        padding-right: 36px;
    }
    .register-demographics select.login-input option {
        background: #1e1b4b;
        color: #fff;
    }
    .login-error {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 14px;
        font-size: 13px;
        color: #fca5a5;
    }
    .btn-login {
        width: 100%;
        padding: 15px;
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        border: none;
        border-radius: 14px;
        font-size: 15px;
        font-weight: 600;
        color: #fff;
        cursor: pointer;
        outline: none;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
        margin-bottom: 16px;
    }
    .btn-login:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.45);
    }
    .btn-login:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    .btn-spinner {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        animation: spin 0.7s linear infinite;
    }
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
    .login-divider {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 4px 0 12px;
        color: rgba(255, 255, 255, 0.2);
        font-size: 12px;
    }
    .login-divider::before,
    .login-divider::after {
        content: "";
        flex: 1;
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
    }
    .btn-demo {
        width: 100%;
        padding: 13px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 14px;
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        outline: none;
        transition: all 0.2s;
    }
    .btn-demo:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
    }
    .login-footer {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.2);
        margin-top: 28px;
        letter-spacing: 0.05em;
    }
    .animate-slide-up {
        animation: slide-up 0.45s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }
    @keyframes slide-up {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ═══════════════════════════════════════════
   APP LAYOUT
═══════════════════════════════════════════ */
    .app-root {
        position: relative;
        width: 100%;
        height: 100vh;
        display: flex;
        overflow: hidden;
    }
    .chat-panel {
        position: relative;
        z-index: 20;
        flex: 0 0 45%;
        height: 100%;
        padding: 20px 20px 20px 0;
        display: flex;
        flex-direction: column;
        min-width: 0;
    }
    /* Background – kelas tetap cerah & terang */
    .bg-scene {
        position: absolute;
        inset: 0;
        z-index: 0;
        background-image: url("/img/Class.jpg");
        background-size: cover;
        background-position: center;
        filter: brightness(0.95) saturate(1.15) contrast(1.05);
        transform: scale(1.03);
    }
    .bg-overlay {
        position: absolute;
        inset: 0;
        z-index: 1;
        /* Ringan saja agar background kelas tetap terang */
        background: linear-gradient(
            to right,
            rgba(240, 248, 255, 0.08) 0%,
            rgba(30, 35, 65, 0.45) 55%,
            rgba(15, 18, 45, 0.72) 100%
        );
    }

    /* ─── VRM Panel ─── */
    .vrm-panel {
        position: relative;
        z-index: 10;
        flex: 0 0 55%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .vrm-canvas {
        width: 100%;
        height: 100%;
        display: block;
    }
    .vrm-mode-badge {
        position: absolute;
        top: 24px;
        left: 24px;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid currentColor;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        backdrop-filter: blur(12px);
        background: rgba(255, 255, 255, 0.08);
        color: inherit;
        transition: all 0.3s;
    }
    .vrm-status-card {
        position: absolute;
        bottom: 32px;
        left: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 12px 18px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
    }
    .vrm-status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
        animation: pulse-badge 2s infinite;
        flex-shrink: 0;
    }
    .vrm-status-name {
        font-size: 13px;
        font-weight: 700;
        color: #fff;
    }
    .vrm-status-sub {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.55);
    }

    .chat-shell {
        flex: 1;
        display: flex;
        flex-direction: column;
        background: rgba(10, 12, 28, 0.72);
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        overflow: hidden;
        min-width: 0;
        min-height: 0;
        box-shadow:
            0 24px 64px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    /* ─── Header ─── */
    .chat-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 18px 22px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        background: rgba(255, 255, 255, 0.03);
        flex-shrink: 0;
    }
    .chat-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .chat-avatar {
        position: relative;
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 700;
        color: white;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
        flex-shrink: 0;
    }
    .chat-avatar-letter {
        line-height: 1;
    }
    .chat-avatar-online {
        position: absolute;
        bottom: -2px;
        right: -2px;
        width: 13px;
        height: 13px;
        border-radius: 50%;
        background: #22c55e;
        border: 2px solid rgba(10, 12, 28, 0.9);
    }
    .chat-title {
        font-size: 15px;
        font-weight: 700;
        color: #fff;
    }
    .chat-subtitle {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.4);
        font-weight: 500;
        letter-spacing: 0.03em;
    }
    .btn-logout {
        width: 34px;
        height: 34px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.5);
        cursor: pointer;
        outline: none;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }
    .btn-logout:hover {
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border-color: rgba(239, 68, 68, 0.3);
    }

    /* ─── Mode Tabs ─── */
    .mode-tabs {
        display: flex;
        gap: 6px;
        padding: 12px 16px;
        background: rgba(0, 0, 0, 0.25);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        flex-shrink: 0;
    }
    .mode-tab {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 9px 8px;
        border-radius: 12px;
        border: 1px solid transparent;
        font-size: 12px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.4);
        cursor: pointer;
        outline: none;
        background: transparent;
        transition: all 0.25s;
    }
    .mode-tab:hover:not(.mode-tab-active) {
        color: rgba(255, 255, 255, 0.7);
        background: rgba(255, 255, 255, 0.06);
    }
    .mode-tab-active {
        color: #fff;
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    }

    /* ─── Quest Banner ─── */
    .quest-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin: 12px 16px 0;
        padding: 14px 18px;
        background: linear-gradient(
            135deg,
            rgba(16, 185, 129, 0.12),
            rgba(20, 184, 166, 0.08)
        );
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 16px;
        flex-shrink: 0;
    }
    .quest-banner-title {
        font-size: 13px;
        font-weight: 700;
        color: #6ee7b7;
        margin-bottom: 2px;
    }
    .quest-banner-sub {
        font-size: 11px;
        color: rgba(110, 231, 183, 0.6);
    }
    .btn-quest-start {
        padding: 9px 18px;
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #10b981, #0d9488);
        color: #fff;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        outline: none;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        transition: all 0.2s;
    }
    .btn-quest-start:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
    }

    /* ─── Messages ─── */
    .messages-area {
        flex: 1;
        overflow-y: auto;
        padding: 20px 16px;
        display: flex;
        flex-direction: column;
        gap: 14px;
    }
    .custom-scroll::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scroll::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    .custom-scroll::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    .hidden {
        display: none;
    }

    .msg-row {
        display: flex;
        gap: 10px;
        align-items: flex-end;
    }
    .msg-row-user {
        flex-direction: row-reverse;
    }
    .msg-row-tutor {
        flex-direction: row;
    }

    .msg-avatar-sm {
        width: 32px;
        height: 32px;
        border-radius: 10px;
        flex-shrink: 0;
        background: linear-gradient(135deg, #6366f1, #3b82f6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        color: white;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        align-self: flex-end;
    }
    .msg-bubble-wrap {
        display: flex;
        flex-direction: column;
        max-width: 82%;
    }
    .msg-bubble-wrap.items-end {
        align-items: flex-end;
    }
    .msg-bubble-wrap.items-start {
        align-items: flex-start;
    }

    .msg-bubble {
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.65;
        max-width: 100%;
    }
    .bubble-user {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        color: #fff;
        border-bottom-right-radius: 5px;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.25);
    }
    .bubble-tutor {
        background: rgba(255, 255, 255, 0.09);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.92);
        border-bottom-left-radius: 5px;
        backdrop-filter: blur(8px);
    }
    .streaming-bubble {
        background: rgba(99, 102, 241, 0.08);
        border-color: rgba(99, 102, 241, 0.2);
    }

    .suggestions-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    .suggestion-chip {
        padding: 5px 12px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.13);
        color: rgba(200, 218, 255, 0.85);
        font-size: 11.5px;
        font-weight: 500;
        cursor: pointer;
        outline: none;
        transition: all 0.18s;
    }
    .suggestion-chip:hover {
        background: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.4);
        color: #c7d2fe;
    }

    .thinking-dots {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 12px 16px;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        border-bottom-left-radius: 5px;
    }
    .thinking-dots span {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: rgba(147, 197, 253, 0.7);
        animation: bounce 1.2s infinite ease-in-out;
    }
    .thinking-dots span:nth-child(2) {
        animation-delay: 0.15s;
    }
    .thinking-dots span:nth-child(3) {
        animation-delay: 0.3s;
    }
    @keyframes bounce {
        0%,
        80%,
        100% {
            transform: translateY(0) scale(1);
            opacity: 0.7;
        }
        40% {
            transform: translateY(-6px) scale(1.1);
            opacity: 1;
        }
    }

    .cursor-blink {
        display: inline-block;
        width: 2px;
        height: 15px;
        background: rgba(147, 197, 253, 0.9);
        vertical-align: text-bottom;
        margin-left: 3px;
        border-radius: 2px;
        animation: blink 1s step-end infinite;
    }
    @keyframes blink {
        0%,
        100% {
            opacity: 1;
        }
        50% {
            opacity: 0;
        }
    }

    /* ─── Premium Thinking Bubble (Discovery Mode) ─── */
    .thinking-bubble {
        position: relative;
        overflow: hidden;
        min-width: 200px;
        background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.08),
            rgba(139, 92, 246, 0.12)
        ) !important;
        border-color: rgba(139, 92, 246, 0.25) !important;
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

    /* ─── KG Accuracy Badge ─── */
    .accuracy-badge {
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
        animation: badge-fade-in 0.4s ease-out;
        cursor: default;
        user-select: none;
    }
    @keyframes badge-fade-in {
        from {
            opacity: 0;
            transform: translateY(4px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    .accuracy-grounded {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.25);
        color: rgba(134, 239, 172, 0.9);
    }
    .accuracy-casual {
        background: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.15);
        color: rgba(148, 163, 184, 0.7);
    }
    .accuracy-no_data {
        background: rgba(251, 191, 36, 0.08);
        border: 1px solid rgba(251, 191, 36, 0.15);
        color: rgba(251, 191, 36, 0.7);
    }
    .accuracy-icon {
        font-size: 11px;
        line-height: 1;
    }
    .accuracy-text {
        font-weight: 700;
    }
    .accuracy-detail {
        opacity: 0.6;
        font-weight: 500;
    }

    /* ─── Accuracy Badge Clickable & Popup Styles ─── */
    .accuracy-badge-clickable {
        cursor: pointer !important;
        transition: all 0.2s ease-in-out;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .accuracy-badge-clickable:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        filter: brightness(1.15);
    }
    .accuracy-chevron {
        font-size: 8px;
        margin-left: 4px;
        opacity: 0.7;
        transition: transform 0.2s;
    }

    .accuracy-pct-high {
        background: rgba(34, 197, 94, 0.12) !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
        color: rgba(134, 239, 172, 1) !important;
    }
    .accuracy-pct-med {
        background: rgba(234, 179, 8, 0.12) !important;
        border: 1px solid rgba(234, 179, 8, 0.3) !important;
        color: rgba(253, 224, 71, 1) !important;
    }
    .accuracy-pct-low {
        background: rgba(249, 115, 22, 0.12) !important;
        border: 1px solid rgba(249, 115, 22, 0.3) !important;
        color: rgba(253, 186, 116, 1) !important;
    }
    .accuracy-pct-critical {
        background: rgba(239, 68, 68, 0.12) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: rgba(252, 165, 165, 1) !important;
    }

    .accuracy-container {
        position: relative;
        display: inline-block;
    }
    .accuracy-popup {
        position: absolute;
        bottom: calc(100% + 8px);
        left: 0;
        z-index: 100;
        width: 320px;
        max-width: 90vw;
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        box-shadow:
            0 10px 25px -5px rgba(0, 0, 0, 0.5),
            0 8px 10px -6px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(12px);
        overflow: hidden;
        animation: popup-scale-in 0.15s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes popup-scale-in {
        from {
            opacity: 0;
            transform: scale(0.95) translateY(4px);
        }
        to {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    .popup-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .popup-title {
        font-size: 11px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.9);
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    .popup-close {
        background: none;
        border: none;
        color: rgba(255, 255, 255, 0.5);
        font-size: 18px;
        cursor: pointer;
        line-height: 1;
        padding: 0 4px;
        transition: color 0.15s;
    }
    .popup-close:hover {
        color: #fff;
    }
    .popup-body {
        padding: 8px;
        max-height: 240px;
        overflow-y: auto;
    }
    .fact-row {
        display: flex;
        gap: 10px;
        padding: 8px 10px;
        border-radius: 8px;
        margin-bottom: 6px;
        font-size: 12px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid transparent;
        transition: background 0.15s;
    }
    .fact-row:last-child {
        margin-bottom: 0;
    }
    .fact-success {
        border-color: rgba(34, 197, 94, 0.15);
        background: rgba(34, 197, 94, 0.03);
    }
    .fact-fail {
        border-color: rgba(239, 68, 68, 0.15);
        background: rgba(239, 68, 68, 0.03);
    }
    .fact-status-icon {
        font-size: 14px;
        line-height: 1.2;
    }
    .fact-info {
        flex: 1;
        min-width: 0;
    }
    .fact-subject-row {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 3px;
        flex-wrap: wrap;
    }
    .fact-type-badge {
        font-size: 8px;
        text-transform: uppercase;
        font-weight: 800;
        padding: 1px 5px;
        border-radius: 4px;
        letter-spacing: 0.03em;
        line-height: 1.3;
    }
    .fact-type-badge.type-vocab {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
    }
    .fact-type-badge.type-grammar {
        background: rgba(236, 72, 153, 0.2);
        color: #fbcfe8;
    }
    .fact-type-badge.type-kanji {
        background: rgba(20, 184, 166, 0.2);
        color: #99f6e4;
    }
    .fact-subject {
        color: #f8fafc;
        font-size: 12px;
    }
    .fact-details-text {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.6);
        line-height: 1.4;
    }
    .text-success {
        color: #4ade80;
        font-weight: 600;
    }
    .text-fail {
        color: #f87171;
        font-weight: 600;
    }
    .fact-props-list {
        font-size: 10px;
        color: rgba(255, 255, 255, 0.4);
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* ─── Input Area ─── */
    .input-area {
        padding: 14px 16px 18px;
        border-top: 1px solid rgba(255, 255, 255, 0.07);
        background: rgba(0, 0, 0, 0.2);
        flex-shrink: 0;
    }
    /* ─── Input Row (wrapper area) ─── */
    /* Styling input & send button dikelola di DiscoveryMode.svelte */

    /* ─── Message Animation ─── */
    .animate-msg {
        animation: msg-in 0.3s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    @keyframes msg-in {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ─── Markdown ─── */
    :global(.markdown-content p) {
        margin-bottom: 0.65rem;
    }
    :global(.markdown-content p:last-child) {
        margin-bottom: 0;
    }
    :global(.markdown-content strong) {
        font-weight: 700;
        color: #c7d2fe;
    }
    :global(.markdown-content em) {
        font-style: italic;
        color: rgba(255, 255, 255, 0.75);
    }
    :global(.markdown-content ul) {
        list-style: disc;
        margin: 0.5rem 0 0.5rem 1.4rem;
    }
    :global(.markdown-content ol) {
        list-style: decimal;
        margin: 0.5rem 0 0.5rem 1.4rem;
    }
    :global(.markdown-content li) {
        margin-bottom: 0.25rem;
    }
    :global(.markdown-content h1, .markdown-content h2, .markdown-content h3) {
        font-weight: 700;
        margin: 0.75rem 0 0.4rem;
        color: #e2e8f0;
    }
    :global(.markdown-content code:not(pre code)) {
        background: rgba(255, 255, 255, 0.1);
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.85em;
        color: #a5b4fc;
        font-family: "Courier New", monospace;
    }
    :global(.markdown-content pre) {
        background: rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 14px;
        border-radius: 12px;
        overflow-x: auto;
        margin: 0.75rem 0;
    }
    :global(.markdown-content blockquote) {
        border-left: 3px solid #6366f1;
        padding-left: 1rem;
        margin: 0.5rem 0;
        color: rgba(255, 255, 255, 0.6);
        font-style: italic;
    }
    :global(.markdown-content table) {
        width: 100%;
        border-collapse: collapse;
        margin: 0.75rem 0;
        font-size: 13px;
    }
    :global(.markdown-content th, .markdown-content td) {
        padding: 8px 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    :global(.markdown-content th) {
        background: rgba(99, 102, 241, 0.15);
        font-weight: 600;
        color: #c7d2fe;
    }
</style>
