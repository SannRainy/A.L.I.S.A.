<script>
    export let profile;

    // Derived from profile.completed_quests or stats
    $: hasKanjiMastery = (profile?.stats?.kanji_mastered || 0) >= 5;
    $: hasSpeedEmblem = (profile?.level || 0) >= 3;
    $: is7DayWarrior = (profile?.xp || 0) >= 500; 
    $: isSage = (profile?.completed_quests?.length || 0) >= 9;
</script>

<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
    <!-- Mastery -->
    <div class="glass-card p-5 flex gap-5 items-center transition-all duration-300 {hasKanjiMastery ? 'border-orange-500/30 bg-orange-500/5' : 'opacity-50 grayscale hover:opacity-80 hover:grayscale-0'}">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl shadow-lg border {hasKanjiMastery ? 'bg-orange-100 border-orange-200' : 'bg-white/10 border-white/20'}">
            🔥
        </div>
        <div>
            <h4 class="font-bold {hasKanjiMastery ? 'text-orange-300' : 'text-white/60'}">Fire Starter</h4>
            <p class="text-xs {hasKanjiMastery ? 'text-orange-400/80' : 'text-white/40'} mt-1">
                {hasKanjiMastery ? 'Telah menguasai minimal 5 Kanji' : 'Kuasai minimal 5 Kanji untuk membuka'}
            </p>
        </div>
    </div>

    <!-- Streak -->
    <div class="glass-card p-5 flex gap-5 items-center transition-all duration-300 {is7DayWarrior ? 'border-blue-500/30 bg-blue-500/5' : 'opacity-50 grayscale hover:opacity-80 hover:grayscale-0'}">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl shadow-lg border {is7DayWarrior ? 'bg-blue-100 border-blue-200' : 'bg-white/10 border-white/20'}">
            📅
        </div>
        <div>
            <h4 class="font-bold {is7DayWarrior ? 'text-blue-300' : 'text-white/60'}">7-Day Warrior</h4>
            <p class="text-xs {is7DayWarrior ? 'text-blue-400/80' : 'text-white/40'} mt-1">
                {is7DayWarrior ? 'Login dan belajar 7 hari berturut-turut' : 'Capai 500 XP untuk membuka'}
            </p>
        </div>
    </div>

    <!-- Speed -->
    <div class="glass-card p-5 flex gap-5 items-center transition-all duration-300 {hasSpeedEmblem ? 'border-yellow-500/30 bg-yellow-500/5' : 'opacity-50 grayscale hover:opacity-80 hover:grayscale-0'}">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl shadow-lg border {hasSpeedEmblem ? 'bg-yellow-100 border-yellow-200' : 'bg-white/10 border-white/20'}">
            ⚡
        </div>
        <div>
            <h4 class="font-bold {hasSpeedEmblem ? 'text-yellow-300' : 'text-white/60'}">Lightning Brain</h4>
            <p class="text-xs {hasSpeedEmblem ? 'text-yellow-400/80' : 'text-white/40'} mt-1">
                {hasSpeedEmblem ? 'Mencapai Level 3' : 'Capai Level 3 untuk membuka'}
            </p>
        </div>
    </div>

    <!-- Social -->
    <div class="glass-card p-5 flex gap-5 items-center transition-all duration-300 {isSage ? 'border-emerald-500/30 bg-emerald-500/5' : 'opacity-50 grayscale hover:opacity-80 hover:grayscale-0'}">
        <div class="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl shadow-lg border {isSage ? 'bg-emerald-100 border-emerald-200' : 'bg-white/10 border-white/20'}">
            💬
        </div>
        <div>
            <h4 class="font-bold {isSage ? 'text-emerald-300' : 'text-white/60'}">N5 Sage</h4>
            <p class="text-xs {isSage ? 'text-emerald-400/80' : 'text-white/40'} mt-1">
                {isSage ? 'Selesaikan semua (9) Quest N5' : 'Selesaikan 9 Quest untuk membuka'}
            </p>
        </div>
    </div>
</div>
