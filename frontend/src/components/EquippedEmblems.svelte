<script>
    export let profile;

    // Badge unlock conditions — identik dengan Achievement.svelte
    $: hasFireStarter   = (profile?.stats?.kanji_mastered ?? 0) >= 5;
    $: hasLightning     = (profile?.level ?? 1) >= 3;
    $: hasWarrior       = (profile?.xp ?? 0) >= 500;
    $: hasSage          = (profile?.completed_quests?.length ?? 0) >= 9;

    $: equippedBadges = [
        { id: 'fire',     emoji: '🔥', label: 'Fire Starter',    sub: '5+ Kanji',      unlocked: hasFireStarter, grad: 'from-orange-400 to-rose-500',   glow: 'rgba(249,115,22,0.4)',  border: 'border-orange-500/50', text: 'text-orange-600' },
        { id: 'light',    emoji: '⚡', label: 'Lightning Brain', sub: 'Level 3+',       unlocked: hasLightning,   grad: 'from-yellow-300 to-amber-500',  glow: 'rgba(245,158,11,0.4)',  border: 'border-amber-500/50',  text: 'text-amber-600' },
        { id: 'warrior',  emoji: '📅', label: '7-Day Warrior',   sub: '500+ XP',        unlocked: hasWarrior,     grad: 'from-blue-400 to-indigo-500',   glow: 'rgba(96,165,250,0.4)',  border: 'border-blue-500/50',   text: 'text-blue-600' },
        { id: 'sage',     emoji: '🌿', label: 'N5 Sage',         sub: 'All Quests',     unlocked: hasSage,        grad: 'from-teal-300 to-emerald-500',  glow: 'rgba(20,184,166,0.4)',  border: 'border-emerald-500/50', text: 'text-emerald-600' },
    ];

    $: anyUnlocked = equippedBadges.some(b => b.unlocked);
</script>

<div class="rounded-2xl p-4 flex flex-col gap-3">
    {#if anyUnlocked}
        <!-- Grid 2×2 untuk badge yang bisa muncul -->
        <div class="grid grid-cols-2 gap-3">
            {#each equippedBadges as badge (badge.id)}
                {#if badge.unlocked}
                    <!-- Unlocked: tampil penuh dengan glow -->
                    <div class="flex flex-col items-center p-3 rounded-2xl border {badge.border} bg-white/60 shadow-md transition-all duration-300 hover:scale-[1.03]"
                         style="box-shadow: 0 0 16px {badge.glow}">
                        <div class="w-14 h-14 rounded-full bg-gradient-to-br {badge.grad} flex items-center justify-center text-2xl mb-2 border-2 border-white shadow-lg"
                             style="box-shadow: 0 0 12px {badge.glow}">
                            {badge.emoji}
                        </div>
                        <p class="font-black text-xs text-slate-800 text-center leading-tight">{badge.label}</p>
                        <p class="{badge.text} text-[9px] uppercase tracking-wider mt-0.5 font-bold">{badge.sub}</p>
                    </div>
                {:else}
                    <!-- Locked: grayscale + hover tooltip -->
                    <div class="relative flex flex-col items-center p-3 rounded-2xl border border-dashed border-slate-300/60 bg-slate-50/40 opacity-50 grayscale group cursor-not-allowed transition-all duration-300 hover:opacity-75 hover:grayscale-0">
                        <div class="w-14 h-14 rounded-full bg-slate-200 flex items-center justify-center text-2xl mb-2 border-2 border-slate-300">
                            {badge.emoji}
                        </div>
                        <p class="font-black text-xs text-slate-500 text-center leading-tight">{badge.label}</p>
                        <p class="text-slate-400 text-[9px] uppercase tracking-wider mt-0.5 font-semibold">{badge.sub}</p>

                        <!-- Hover tooltip -->
                        <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-slate-800/85 rounded-2xl text-[10px] p-2 text-center text-white font-semibold leading-snug z-10">
                            🔒 {badge.sub} untuk unlock
                        </div>
                    </div>
                {/if}
            {/each}
        </div>
    {:else}
        <!-- Semua locked: tampilkan placeholder motivasi -->
        <div class="flex flex-col items-center justify-center py-6 px-4 text-center">
            <span class="text-3xl mb-3 opacity-50">🏅</span>
            <p class="text-slate-600 font-black text-sm">Belum ada emblem aktif.</p>
            <p class="text-slate-400 text-xs mt-1 leading-relaxed">
                Kuasai 5 Kanji atau capai Level 3 untuk membuka emblem pertamamu!
            </p>
        </div>
    {/if}
</div>
