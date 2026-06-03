<script>
    import { profile } from "../stores/profile_store";
    import { tweened } from "svelte/motion";
    import { backOut } from "svelte/easing";
    import { fly, fade } from "svelte/transition";
    import RadarChart from "./RadarChart.svelte";
    import EquippedEmblems from "./EquippedEmblems.svelte";

    export let user;

    // ── Rank System (lebih granular, sesuai konteks skripsi Jepang) ──────────
    // Menggunakan sistem rank samurai yang lebih kaya untuk motivasi
    const RANKS = [
        { minLevel: 1,  label: "Minarai",    kanji: "見習い",    color: "text-slate-400" },
        { minLevel: 3,  label: "Ronin",       kanji: "浪人",      color: "text-amber-500" },
        { minLevel: 5,  label: "Kenshi",      kanji: "剣士",      color: "text-blue-500" },
        { minLevel: 8,  label: "Samurai",     kanji: "侍",        color: "text-indigo-500" },
        { minLevel: 10, label: "Shogun",      kanji: "将軍",      color: "text-fuchsia-500" },
    ];

    $: currentRank = [...RANKS].reverse().find(r => $profile.level >= r.minLevel) || RANKS[0];
    $: nextRank = RANKS[RANKS.findIndex(r => r === currentRank) + 1] ?? null;

    // ── XP Progress Calculation ────────────────────────────────────────────
    // XP per level: level * 100 (misal level 3 → butuh 300 XP)
    $: xpForCurrentLevel = ($profile.level - 1) * 100;
    $: xpForNextLevel    = $profile.level * 100;
    $: progressXp        = Math.max(0, $profile.xp - xpForCurrentLevel);
    $: xpNeeded          = xpForNextLevel - xpForCurrentLevel; // selalu 100

    const progressPercent = tweened(0, { duration: 1200, easing: backOut });
    $: progressPercent.set(Math.min((progressXp / xpNeeded) * 100, 100));

    // ── Stats Derived ──────────────────────────────────────────────────────
    $: kanjiPct   = Math.round(($profile.stats.kanji_mastered / Math.max($profile.stats.kanji_total, 1)) * 100);
    $: vocabPct   = Math.round(($profile.stats.vocab_learned  / Math.max($profile.stats.vocab_total,  1)) * 100);
    $: grammarPct = Math.round(($profile.stats.grammar_learned / Math.max($profile.stats.grammar_total, 1)) * 100);

    // ── Username Display ───────────────────────────────────────────────────
    $: username = user?.email?.split('@')[0] || 'Player';
    $: avatarChar = username.substring(0, 1).toUpperCase();

    // ── Streak (placeholder — bisa disambung ke backend nanti) ────────────
    $: streakDays = $profile.streak_days ?? 1;

    // ── Quest Progress ─────────────────────────────────────────────────────
    $: completedQuestCount = $profile.completed_quests?.length ?? 0;
    $: totalQuestCount = 9;

    // ── Logout ─────────────────────────────────────────────────────────────
    async function handleLogout() {
        const { logout } = await import('../stores/auth_store');
        await logout();
        window.location.reload();
    }

    // ── Countries List ──
    const countries = [
        "Indonesia", "Jepang", "Malaysia", "Singapura", "Thailand", "Filipina", "Vietnam", 
        "Brunei Darussalam", "Kamboja", "Laos", "Myanmar", "Timor Leste", "Afganistan", 
        "Afrika Selatan", "Albania", "Aljazair", "Amerika Serikat", "Andorra", "Angola", 
        "Antigua dan Barbuda", "Arab Saudi", "Argentina", "Armenia", "Australia", "Austria", 
        "Azerbaijan", "Bahama", "Bahrain", "Bangladesh", "Barbados", "Belanda", "Belarus", 
        "Belgia", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia dan Herzegovina", "Botswana", 
        "Brasil", "Britania Raya", "Bulgaria", "Burkina Faso", "Burundi", "Ceko", "Chad", 
        "Chili", "China", "Denmark", "Djibouti", "Dominika", "Ekuador", "El Salvador", 
        "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finlandia", "Gabon", "Gambia", 
        "Georgia", "Ghana", "Grenada", "Guatemala", "Guinea", "Guinea Khatulistiwa", "Guinea-Bissau", 
        "Guyana", "Haiti", "Honduras", "Hong Kong", "Hongaria", "India", "Irak", "Iran", 
        "Irlandia", "Islandia", "Israel", "Italia", "Jamaika", "Jerman", "Kamerun", "Kanada", 
        "Kazakhstan", "Kenya", "Kepulauan Marshall", "Kepulauan Solomon", "Kirgistan", "Kiribati", 
        "Kolombia", "Komoro", "Kongo", "Kosta Rika", "Kroasia", "Kuba", "Kuwait", "Latvia", 
        "Lebanon", "Lesotho", "Liberia", "Libia", "Liechtenstein", "Lituania", "Luksemburg", 
        "Madagaskar", "Makedonia Utara", "Maladewa", "Malawi", "Mali", "Malta", "Maroko", 
        "Mauritania", "Mauritius", "Meksiko", "Mesir", "Mikronesia", "Moldova", "Monako", 
        "Mongolia", "Montenegro", "Mozambik", "Namibia", "Nauru", "Nepal", "Niger", "Nigeria", 
        "Nikaragua", "Norwegia", "Oman", "Pakistan", "Palau", "Panama", "Papua Nugini", 
        "Paraguay", "Prancis", "Peru", "Polandia", "Portugal", "Qatar", "Rumania", "Rusia", 
        "Rwanda", "Samoa", "San Marino", "Sao Tome dan Principe", "Selandia Baru", "Senegal", 
        "Serbia", "Seychelles", "Siprus", "Slovakia", "Slovenia", "Somalia", "Spanyol", "Sri Lanka", 
        "Sudan", "Sudan Selatan", "Suriname", "Swedia", "Swiss", "Suriah", "Taiwan", "Tajikistan", 
        "Tanjung Verde", "Tanzania", "Togo", "Tonga", "Trinidad dan Tobago", "Tunisia", "Turki", 
        "Turkmenistan", "Tuvalu", "Uganda", "Ukraina", "Uruguay", "Uzbekistan", "Vanuatu", "Vatikan", 
        "Venezuela", "Yaman", "Yordania", "Yunani", "Zambia", "Zimbabwe"
    ];

    // ── Edit Profile State ──
    let isEditing = false;
    let editFullName = "";
    let editAge = "";
    let editGender = "prefer_not_to_say";
    let editCountry = "Indonesia";
    let editPurpose = "";
    let editLevel = "beginner";
    let editError = "";
    let editLoading = false;

    let countrySearchQuery = "";
    let showCountryDropdown = false;

    $: filteredCountries = countries.filter(c => 
        c.toLowerCase().includes(countrySearchQuery.toLowerCase())
    );

    $: {
        if (countries.includes(countrySearchQuery)) {
            editCountry = countrySearchQuery;
        }
    }

    function startEdit() {
        editFullName = $profile.full_name || "";
        editAge = $profile.age !== null && $profile.age !== undefined ? String($profile.age) : "";
        editGender = $profile.gender || "prefer_not_to_say";
        editCountry = $profile.country || "Indonesia";
        countrySearchQuery = editCountry;
        editPurpose = $profile.study_purpose || "";
        editLevel = $profile.japanese_level || "beginner";
        editError = "";
        isEditing = true;
    }

    async function handleSave() {
        if (!editFullName.trim()) {
            editError = "Nama lengkap wajib diisi.";
            return;
        }
        if (!countries.includes(editCountry)) {
            editError = "Harap pilih asal negara yang valid dari daftar.";
            return;
        }
        editLoading = true;
        editError = "";
        try {
            const { updateProfile } = await import('../stores/profile_store');
            await updateProfile(user.id, {
                full_name: editFullName,
                age: editAge ? parseInt(editAge) : null,
                gender: editGender,
                country: editCountry,
                study_purpose: editPurpose,
                japanese_level: editLevel
            });
            isEditing = false;
        } catch (e) {
            editError = e.message || "Gagal memperbarui profil.";
        } finally {
            editLoading = false;
        }
    }
</script>

<div class="h-full overflow-y-auto custom-scroll glass-panel rounded-[2.5rem] relative transition-all duration-500">
    <!-- Ambient Background Glows -->
    <div class="absolute top-0 right-0 w-96 h-96 bg-indigo-300/20 rounded-full blur-[100px] pointer-events-none"></div>
    <div class="absolute bottom-0 left-0 w-[450px] h-[450px] bg-fuchsia-200/10 rounded-full blur-[120px] pointer-events-none"></div>

    <div class="p-6 md:p-8 relative z-10">

        <!-- ═══════════════════════════════════════════════
             PLAYER CARD
        ═══════════════════════════════════════════════ -->
        <div class="relative rounded-[2rem] p-[1.5px] mb-8 overflow-hidden group shadow-xl"
             style="background: linear-gradient(135deg, rgba(99,102,241,0.4), rgba(217,70,239,0.3), rgba(99,102,241,0.1));">
            <div class="bg-slate-800/80 backdrop-blur-2xl rounded-[1.9rem] p-6 flex flex-col sm:flex-row items-center sm:items-start gap-6 relative">
                <!-- Hover shimmer -->
                <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-[1.9rem]"></div>

                <!-- ── Avatar ── -->
                <div class="relative shrink-0">
                    <div class="w-20 h-20 md:w-24 md:h-24 bg-gradient-to-br from-indigo-400 to-fuchsia-500 rounded-2xl rotate-3 flex items-center justify-center shadow-xl transition-transform group-hover:rotate-6 duration-500 border border-white/30">
                        <span class="text-3xl md:text-4xl font-black text-white -rotate-3 select-none drop-shadow">
                            {avatarChar}
                        </span>
                    </div>
                    <!-- Level Badge -->
                    <div class="absolute -bottom-3 -right-3 bg-white text-indigo-700 font-black px-2.5 py-1 rounded-xl text-xs shadow-lg border border-indigo-100 z-10">
                        Lv.{$profile.level}
                    </div>
                </div>

                <!-- ── Info ── -->
                <div class="flex-grow w-full min-w-0">
                    <div class="flex flex-col sm:flex-row justify-between items-center sm:items-start gap-3">
                        <div class="text-center sm:text-left">
                            <h2 class="text-xl md:text-2xl font-black text-white tracking-tight capitalize leading-none truncate max-w-[180px]">
                                {username}
                            </h2>
                            <!-- Rank Badge -->
                            <div class="inline-flex items-center gap-1.5 mt-2 px-3 py-1 rounded-xl bg-indigo-900/50 border border-indigo-400/30">
                                <span class="text-sm font-black text-white">{currentRank.kanji}</span>
                                <span class="text-[10px] font-black uppercase tracking-widest {currentRank.color}">
                                    {currentRank.label}
                                </span>
                                {#if nextRank}
                                    <span class="text-[9px] text-slate-400">→ {nextRank.label}</span>
                                {:else}
                                    <span class="text-[9px] text-fuchsia-400">★ MAX</span>
                                {/if}
                            </div>
                        </div>

                        <!-- Right: Streak + Logout -->
                        <div class="flex flex-row sm:flex-col items-center sm:items-end gap-3">
                            {#if $profile.role === 'admin'}
                                <a
                                    href="/admin"
                                    class="text-[10px] uppercase font-black tracking-wider text-white bg-indigo-600 hover:bg-indigo-500 border border-indigo-500 px-3 py-1.5 rounded-lg transition-all shadow-md text-center no-underline"
                                >
                                    Admin Panel
                                </a>
                            {/if}
                            <button
                                on:click={handleLogout}
                                class="text-[10px] uppercase font-bold text-slate-400 hover:text-rose-500 bg-white/40 border border-white/60 px-3 py-1.5 rounded-lg transition-all backdrop-blur-sm"
                            >
                                Keluar
                            </button>
                            <div class="flex flex-col items-center sm:items-end">
                                <div class="text-[9px] font-black uppercase tracking-widest text-slate-400 mb-0.5">Streak</div>
                                <div class="text-lg font-black text-orange-500 leading-none">
                                    🔥 {streakDays} {streakDays === 1 ? 'Day' : 'Days'}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- XP Bar -->
                    <div class="mt-5">
                        <div class="flex justify-between text-[10px] font-black text-slate-200 mb-1.5 tracking-widest uppercase">
                            <span>Total XP: <span class="text-indigo-300">{$profile.xp}</span></span>
                            <span class="text-slate-300">{progressXp} / {xpNeeded} XP level ini</span>
                            <span>Level berikutnya: <span class="text-indigo-300">{xpForNextLevel} XP</span></span>
                        </div>
                        <div class="w-full bg-slate-200/60 rounded-full h-3.5 p-[2px] border border-white/50 shadow-inner">
                            <div
                                class="bg-gradient-to-r from-indigo-500 via-purple-500 to-fuchsia-400 h-full rounded-full relative overflow-hidden"
                                style="width: {$progressPercent}%"
                            >
                                <div class="absolute inset-0 bg-white/25 animate-shimmer"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ═══════════════════════════════════════════════
             MAIN CONTENT GRID
        ═══════════════════════════════════════════════ -->
        <div class="grid grid-cols-12 gap-6 md:gap-8">

            <!-- ── LEFT: Stats ── -->
            <div class="col-span-12 lg:col-span-7 space-y-6">

                <!-- Section Header -->
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-indigo-400 rounded-full"></span>
                    Statistik Pembelajaran
                </h3>

                <!-- Stat Cards (3 kolom) -->
                <div class="grid grid-cols-3 gap-3 md:gap-4">

                    <!-- Kanji -->
                    <div class="glass-card p-4 md:p-5 group relative overflow-hidden cursor-default">
                        <div class="absolute -right-2 -top-2 text-5xl md:text-6xl opacity-[0.04] group-hover:opacity-[0.09] transition-opacity duration-500 font-serif select-none">漢字</div>
                        <p class="text-slate-300 text-[9px] md:text-[10px] font-black uppercase tracking-widest mb-2 md:mb-3">Kanji</p>
                        <div class="flex items-baseline gap-1">
                            <span class="text-2xl md:text-3xl font-black text-white leading-none tabular-nums">{$profile.stats.kanji_mastered}</span>
                            <span class="text-xs font-bold text-slate-300">/{$profile.stats.kanji_total}</span>
                        </div>
                        <div class="text-[10px] font-bold text-emerald-500 mb-2">{kanjiPct}%</div>
                        <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-gradient-to-r from-emerald-400 to-teal-400 h-full rounded-full transition-all duration-1000 shadow-[0_0_8px_rgba(52,211,153,0.4)]"
                                 style="width: {kanjiPct}%"></div>
                        </div>
                    </div>

                    <!-- Vocab -->
                    <div class="glass-card p-4 md:p-5 group relative overflow-hidden cursor-default">
                        <div class="absolute -right-2 -top-2 text-5xl md:text-6xl opacity-[0.04] group-hover:opacity-[0.09] transition-opacity duration-500 font-serif select-none">語彙</div>
                        <p class="text-slate-300 text-[9px] md:text-[10px] font-black uppercase tracking-widest mb-2 md:mb-3">Kosakata</p>
                        <div class="flex items-baseline gap-1">
                            <span class="text-2xl md:text-3xl font-black text-white leading-none tabular-nums">{$profile.stats.vocab_learned}</span>
                            <span class="text-xs font-bold text-slate-300">/{$profile.stats.vocab_total}</span>
                        </div>
                        <div class="text-[10px] font-bold text-blue-400 mb-2">{vocabPct}%</div>
                        <div class="w-full bg-slate-700 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-gradient-to-r from-blue-400 to-cyan-400 h-full rounded-full transition-all duration-1000 shadow-[0_0_8px_rgba(96,165,250,0.4)]"
                                 style="width: {vocabPct}%"></div>
                        </div>
                    </div>

                    <!-- Grammar -->
                    <div class="glass-card p-4 md:p-5 group relative overflow-hidden cursor-default">
                        <div class="absolute -right-2 -top-2 text-5xl md:text-6xl opacity-[0.04] group-hover:opacity-[0.09] transition-opacity duration-500 font-serif select-none">文法</div>
                        <p class="text-slate-300 text-[9px] md:text-[10px] font-black uppercase tracking-widest mb-2 md:mb-3">Grammar</p>
                        <div class="flex items-baseline gap-1">
                            <span class="text-2xl md:text-3xl font-black text-white leading-none tabular-nums">{$profile.stats.grammar_learned}</span>
                            <span class="text-xs font-bold text-slate-300">/{$profile.stats.grammar_total}</span>
                        </div>
                        <div class="text-[10px] font-bold text-rose-300 mb-2">{grammarPct}%</div>
                        <div class="w-full bg-slate-700 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-gradient-to-r from-rose-400 to-pink-400 h-full rounded-full transition-all duration-1000 shadow-[0_0_8px_rgba(251,113,133,0.4)]"
                                 style="width: {grammarPct}%"></div>
                        </div>
                    </div>
                </div>

                <!-- Assimilation Rate (full width) -->
                <div class="glass-card p-5 md:p-6">
                    <div class="flex justify-between items-center mb-3">
                        <div>
                            <p class="text-slate-300 text-[10px] font-black uppercase tracking-widest mb-1">Tingkat Asimilasi</p>
                            <p class="text-2xl font-black text-white tabular-nums">{$profile.stats.assimilation_rate}<span class="text-base text-slate-300">%</span></p>
                        </div>
                        <div class="text-right">
                            <div class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-900/40 border border-emerald-400/30">
                                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                                <span class="text-[10px] font-black text-emerald-300 uppercase tracking-wide">Aktif Belajar</span>
                            </div>
                        </div>
                    </div>
                    <div class="relative h-4 w-full bg-slate-700 rounded-full border border-white/20 overflow-hidden shadow-inner">
                        <div class="h-full bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full transition-all duration-1000 relative"
                             style="width: {$profile.stats.assimilation_rate}%">
                            <!-- Stripe animation -->
                            <div class="absolute inset-0 overflow-hidden">
                                <div class="absolute inset-0 bg-[linear-gradient(45deg,rgba(255,255,255,0.25)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.25)_50%,rgba(255,255,255,0.25)_75%,transparent_75%,transparent)] bg-[length:18px_18px] animate-stripe"></div>
                            </div>
                        </div>
                    </div>
                    <p class="text-[10px] text-slate-300 mt-2">Kombinasi dari progres kanji, vocab, dan grammar yang dikuasai.</p>
                </div>

                <!-- Radar Penguasaan -->
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-fuchsia-400 rounded-full"></span>
                    Radar Penguasaan
                </h3>
                <div class="glass-card p-6 flex justify-center">
                    <RadarChart profile={$profile} />
                </div>

                <!-- Status Knowledge Graph -->
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-teal-400 rounded-full"></span>
                    Status Knowledge Graph
                </h3>
                <div class="glass-card p-5 border-indigo-400/30 bg-indigo-900/30">
                    <div class="space-y-2">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-300 font-medium">Node Grammar Dikuasai</span>
                            <span class="text-xs font-black text-indigo-400">{$profile.stats.grammar_learned} node</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-300 font-medium">Node Dipelajari</span>
                            <span class="text-xs font-black text-blue-400">{$profile.mastery_path?.filter(n => n.status !== 'LOCKED').length ?? 0} node</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-300 font-medium">Peta Materi</span>
                            <span class="text-xs font-black text-emerald-400">{$profile.mastery_path?.length ?? 0} total node</span>
                        </div>
                    </div>
                    <p class="text-[9px] text-slate-300 mt-3 leading-relaxed">Data diambil dari Knowledge Graph N5. Node yang MASTERED digunakan untuk membuka level Quest berikutnya.</p>
                </div>
            </div>

            <!-- ── RIGHT: Profile + Quests + Emblems ── -->
            <div class="col-span-12 lg:col-span-5 space-y-6">

                <!-- Biodata Profil -->
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-indigo-500 rounded-full"></span>
                    Biodata Profil
                </h3>
                <div class="glass-card p-5 relative overflow-hidden group border-indigo-400/30">
                    <button 
                        on:click={startEdit}
                        class="absolute top-4 right-4 text-[10px] uppercase font-black tracking-wider text-indigo-300 hover:text-white hover:bg-indigo-600 bg-indigo-900/40 border border-indigo-400/30 px-3 py-1.5 rounded-xl transition-all shadow-sm cursor-pointer animate-pulse-subtle"
                    >
                        ✏️ Edit
                    </button>

                    <div class="space-y-3 mt-1">
                        <div>
                            <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest block mb-0.5">Nama Lengkap</span>
                            <span class="text-sm font-bold text-white">{$profile.full_name || '-'}</span>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest block mb-0.5">Umur</span>
                                <span class="text-sm font-bold text-white">{$profile.age ? `${$profile.age} Tahun` : '-'}</span>
                            </div>
                            <div>
                                <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest block mb-0.5">Gender</span>
                                <span class="text-sm font-bold text-white">{
                                    $profile.gender === 'male' ? 'Laki-laki' : 
                                    $profile.gender === 'female' ? 'Perempuan' : 
                                    $profile.gender === 'prefer_not_to_say' ? 'Tidak menyebutkan' : '-'
                                }</span>
                            </div>
                        </div>
                        <div>
                            <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest block mb-0.5">Asal Negara</span>
                            <span class="text-sm font-bold text-white">{$profile.country || '-'}</span>
                        </div>
                        <div>
                            <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest block mb-0.5">Tujuan Belajar</span>
                            <span class="text-sm font-bold text-white">{
                                $profile.study_purpose === 'akademik' ? 'Akademik / Sekolah' : 
                                $profile.study_purpose === 'kerja' ? 'Bekerja di Jepang' : 
                                $profile.study_purpose === 'hobi' ? 'Hobi / Anime / Manga' : 
                                $profile.study_purpose === 'wisata' ? 'Wisata ke Jepang' : '-'
                            }</span>
                        </div>
                        <div>
                            <span class="text-[9px] font-black text-slate-300 uppercase tracking-widest block mb-0.5">Level Bahasa Jepang</span>
                            <span class="text-sm font-bold text-white">{
                                $profile.japanese_level === 'beginner' ? 'Pemula (belum bisa)' : 
                                $profile.japanese_level === 'basic' ? 'Dasar (tahu sedikit)' : 
                                $profile.japanese_level === 'intermediate' ? 'Menengah (bisa percakapan dasar)' : '-'
                            }</span>
                        </div>
                    </div>
                </div>

                <!-- Misi & Quest N5 -->
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-amber-500 rounded-full"></span>
                    Misi & Quest N5
                </h3>
                <div class="glass-card p-5">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <p class="text-slate-300 text-[10px] font-black uppercase tracking-widest mb-1">Quest N5</p>
                            <p class="text-xl font-black text-white">
                                {completedQuestCount} <span class="text-slate-400 font-bold text-base">/ {totalQuestCount} Level</span>
                            </p>
                        </div>
                        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-2xl shadow-lg shadow-amber-500/30">
                            ⚔️
                        </div>
                    </div>
                    <div class="flex gap-1.5">
                        {#each Array(totalQuestCount) as _, i}
                            <div class="flex-1 h-2 rounded-full transition-all duration-700
                                {i < completedQuestCount
                                    ? 'bg-gradient-to-r from-amber-400 to-orange-400'
                                    : 'bg-slate-600/70'}">
                            </div>
                        {/each}
                    </div>
                    <p class="text-[10px] text-slate-300 mt-2">{completedQuestCount === 0 ? 'Mulai Quest untuk mengumpulkan XP!' : `${totalQuestCount - completedQuestCount} level lagi untuk jadi N5 Sage! 🌿`}</p>
                </div>

                <!-- Emblem Aktif -->
                <h3 class="flex items-center gap-3 text-xs font-black text-slate-300 uppercase tracking-[0.25em]">
                    <span class="w-1.5 h-5 bg-orange-400 rounded-full"></span>
                    Emblem Aktif
                </h3>
                <div class="glass-card p-2">
                    <EquippedEmblems profile={$profile} />
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Edit Profile Modal -->
{#if isEditing}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-md" transition:fade={{ duration: 200 }}>
        <!-- Modal Backdrop click to close -->
        <button 
            type="button"
            class="absolute inset-0 w-full h-full cursor-default bg-transparent border-none" 
            on:click={() => isEditing = false}
            aria-label="Tutup modal"
        ></button>
        
        <div class="bg-white/95 backdrop-blur-2xl border border-white/50 rounded-[2.5rem] w-full max-w-lg p-6 md:p-8 shadow-2xl relative z-10 flex flex-col max-h-[90vh] overflow-hidden" transition:fly={{ y: 20, duration: 300 }}>
            <!-- Modal Header -->
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                    👤 Edit Biodata Profil
                </h3>
                <button 
                    type="button"
                    on:click={() => isEditing = false} 
                    class="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-700 flex items-center justify-center transition-all border-none font-bold cursor-pointer"
                    aria-label="Tutup"
                >
                    ✕
                </button>
            </div>

            <!-- Modal Content - Scrollable -->
            <div class="flex-1 overflow-y-auto pr-2 custom-scroll space-y-4">
                {#if editError}
                    <div class="p-3.5 bg-rose-50 border border-rose-100 rounded-2xl text-xs font-bold text-rose-600 flex items-center gap-2">
                        ⚠️ {editError}
                    </div>
                {/if}

                <!-- Nama Lengkap -->
                <div class="flex flex-col gap-1.5">
                    <label for="edit-fullname" class="text-xs font-black text-slate-400 uppercase tracking-wider">Nama Lengkap</label>
                    <input 
                        id="edit-fullname" 
                        type="text" 
                        bind:value={editFullName} 
                        class="w-full px-4 py-3 bg-slate-100/80 border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all shadow-inner" 
                        placeholder="Nama lengkap" 
                    />
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <!-- Umur -->
                    <div class="flex flex-col gap-1.5">
                        <label for="edit-age" class="text-xs font-black text-slate-400 uppercase tracking-wider">Umur</label>
                        <input 
                            id="edit-age" 
                            type="number" 
                            bind:value={editAge} 
                            class="w-full px-4 py-3 bg-slate-100/80 border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all shadow-inner" 
                            placeholder="22" 
                            min="10" 
                            max="99" 
                        />
                    </div>

                    <!-- Gender -->
                    <div class="flex flex-col gap-1.5">
                        <label for="edit-gender" class="text-xs font-black text-slate-400 uppercase tracking-wider">Gender</label>
                        <select 
                            id="edit-gender" 
                            bind:value={editGender} 
                            class="w-full px-4 py-3 bg-slate-100/80 border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all shadow-inner appearance-none cursor-pointer"
                        >
                            <option value="male">Laki-laki</option>
                            <option value="female">Perempuan</option>
                            <option value="prefer_not_to_say">Tidak menyebutkan</option>
                        </select>
                    </div>
                </div>

                <!-- Asal Negara -->
                <div class="flex flex-col gap-1.5 relative">
                    <label for="edit-country" class="text-xs font-black text-slate-400 uppercase tracking-wider">Asal Negara</label>
                    <input 
                        id="edit-country" 
                        type="text" 
                        bind:value={countrySearchQuery} 
                        on:focus={() => showCountryDropdown = true}
                        on:blur={() => setTimeout(() => showCountryDropdown = false, 250)}
                        class="w-full px-4 py-3 bg-slate-100/80 border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all shadow-inner" 
                        placeholder="Cari asal negara..." 
                    />
                    
                    {#if showCountryDropdown}
                        <div class="absolute z-[60] left-0 right-0 top-full mt-1 max-h-48 overflow-y-auto bg-white border border-slate-200 rounded-2xl shadow-xl custom-scroll">
                            {#each filteredCountries as c}
                                <button 
                                    type="button"
                                    on:click={() => {
                                        countrySearchQuery = c;
                                        editCountry = c;
                                        showCountryDropdown = false;
                                    }}
                                    class="w-full text-left px-4 py-2.5 text-sm text-slate-700 hover:bg-indigo-600 hover:text-white transition bg-transparent border-none cursor-pointer"
                                >
                                    {c}
                                </button>
                            {/each}
                            {#if filteredCountries.length === 0}
                                <div class="px-4 py-2.5 text-sm text-slate-400">Negara tidak ditemukan</div>
                            {/if}
                        </div>
                    {/if}
                </div>

                <!-- Tujuan Belajar -->
                <div class="flex flex-col gap-1.5">
                    <label for="edit-purpose" class="text-xs font-black text-slate-400 uppercase tracking-wider">Tujuan Belajar</label>
                    <select 
                        id="edit-purpose" 
                        bind:value={editPurpose} 
                        class="w-full px-4 py-3 bg-slate-100/80 border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all shadow-inner appearance-none cursor-pointer"
                    >
                        <option value="">-- Pilih --</option>
                        <option value="akademik">Akademik / Sekolah</option>
                        <option value="kerja">Bekerja di Jepang</option>
                        <option value="hobi">Hobi / Anime / Manga</option>
                        <option value="wisata">Wisata ke Jepang</option>
                    </select>
                </div>

                <!-- Level Bahasa Jepang -->
                <div class="flex flex-col gap-1.5">
                    <label for="edit-level" class="text-xs font-black text-slate-400 uppercase tracking-wider">Level Bahasa Jepang</label>
                    <select 
                        id="edit-level" 
                        bind:value={editLevel} 
                        class="w-full px-4 py-3 bg-slate-100/80 border border-slate-200 rounded-2xl text-sm font-medium text-slate-800 focus:outline-none focus:border-indigo-500 focus:bg-white transition-all shadow-inner appearance-none cursor-pointer"
                    >
                        <option value="beginner">Pemula (belum bisa)</option>
                        <option value="basic">Dasar (tahu sedikit)</option>
                        <option value="intermediate">Menengah (bisa percakapan dasar)</option>
                    </select>
                </div>
            </div>

            <!-- Modal Footer -->
            <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-slate-100">
                <button 
                    type="button" 
                    on:click={() => isEditing = false} 
                    class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold rounded-xl transition-all border-none text-sm cursor-pointer"
                >
                    Batal
                </button>
                <button 
                    type="button" 
                    on:click={handleSave} 
                    disabled={editLoading}
                    class="px-5 py-2.5 bg-gradient-to-r from-indigo-500 to-fuchsia-500 text-white font-bold rounded-xl shadow-lg hover:shadow-indigo-500/25 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50 border-none text-sm cursor-pointer"
                >
                    {editLoading ? 'Menyimpan...' : 'Simpan Perubahan'}
                </button>
            </div>
        </div>
    </div>
{/if}

<style>
    @keyframes shimmer {
        0%   { transform: translateX(-100%); }
        100% { transform: translateX(200%); }
    }
    .animate-shimmer {
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: shimmer 2s infinite;
        position: absolute;
        inset: 0;
    }

    @keyframes stripe {
        0%   { background-position: 0 0; }
        100% { background-position: 36px 0; }
    }
    .animate-stripe {
        animation: stripe 0.8s linear infinite;
    }

    @keyframes pulse-subtle {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.85; transform: scale(0.98); }
    }
    .animate-pulse-subtle {
        animation: pulse-subtle 3s ease-in-out infinite;
    }
</style>
