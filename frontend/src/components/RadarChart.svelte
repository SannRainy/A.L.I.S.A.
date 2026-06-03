<script>
    export let profile;

    // ── Derived Skill Values (0–100) ────────────────────────────────────
    // Reading: dari kanji + vocab (N5 target: ~100 kanji, ~800 vocab)
    $: reading = Math.min(100, Math.round(
        ((profile?.stats?.kanji_mastered ?? 0) * 0.5) +
        ((profile?.stats?.vocab_learned ?? 0) * 0.05)
    ));

    // Grammar/Writing: dari grammar nodes yang dikuasai (N5: 80–100 poin)
    $: grammar = Math.min(100, Math.round(
        (profile?.stats?.grammar_learned ?? 0)
    ));

    // Speaking: dari level + XP progression (gamifikasi)
    $: speaking = Math.min(100, Math.round(
        (profile?.level ?? 1) * 9 +
        Math.floor(((profile?.xp ?? 0) % 100) / 10)
    ));

    // Listening: dari level (representasi exposure konten audio)
    $: listening = Math.min(100, Math.round(
        (profile?.level ?? 1) * 10
    ));

    // Quest: dari completed quests / 9 total
    $: quest = Math.min(100, Math.round(
        ((profile?.completed_quests?.length ?? 0) / 9) * 100
    ));

    // ── Radar Chart SVG (Pentagon — 5 axes) ─────────────────────────────
    // viewBox 100×100, center = (50,50), radius = 38
    const cx = 50, cy = 50, R = 38;

    // 5 titik sudut: sudut dimulai dari atas (−90°), searah jarum jam
    // Degrees: -90, -90+72, -90+144, -90+216, -90+288
    const angles = [-90, -18, 54, 126, 198].map(d => d * Math.PI / 180);

    // Grid rings (20%, 40%, 60%, 80%, 100%)
    const rings = [0.2, 0.4, 0.6, 0.8, 1.0];

    function toXY(angle, radius) {
        return {
            x: cx + radius * Math.cos(angle),
            y: cy + radius * Math.sin(angle)
        };
    }

    function polygonPoints(values, maxR = R) {
        return values.map((v, i) => {
            const r = (v / 100) * maxR;
            const p = toXY(angles[i], r);
            return `${p.x.toFixed(2)},${p.y.toFixed(2)}`;
        }).join(' ');
    }

    function ringPoints(ratio) {
        return angles.map(a => {
            const p = toXY(a, R * ratio);
            return `${p.x.toFixed(2)},${p.y.toFixed(2)}`;
        }).join(' ');
    }

    $: skillValues = [reading, grammar, speaking, listening, quest];
    $: dataPoints = polygonPoints(skillValues);

    const labels = [
        { key: 'Reading',   icon: '📖' },
        { key: 'Grammar',   icon: '📚' },
        { key: 'Speaking',  icon: '🗣' },
        { key: 'Listening', icon: '👂' },
        { key: 'Quest',     icon: '⚔️' },
    ];

    // Label positions (sedikit di luar radius)
    const labelR = R + 14;
    $: labelPositions = angles.map((a, i) => ({
        ...toXY(a, labelR),
        ...labels[i],
        value: skillValues[i]
    }));

    // Axis lines
    $: axisLines = angles.map(a => ({
        x2: toXY(a, R).x.toFixed(2),
        y2: toXY(a, R).y.toFixed(2)
    }));
</script>

<div class="relative w-full max-w-[280px] mx-auto">
    <svg viewBox="0 0 100 100" class="w-full h-auto overflow-visible">

        <!-- ── Grid Rings ── -->
        {#each rings as ratio}
            <polygon
                points={ringPoints(ratio)}
                fill="none"
                stroke="rgba(148,163,184,0.3)"
                stroke-width="0.5"
            />
        {/each}

        <!-- ── Axis Lines ── -->
        {#each axisLines as axis}
            <line x1={cx} y1={cy} x2={axis.x2} y2={axis.y2}
                  stroke="rgba(148,163,184,0.25)" stroke-width="0.5" />
        {/each}

        <!-- ── Data Polygon ── -->
        <polygon
            points={dataPoints}
            fill="rgba(217,70,239,0.18)"
            stroke="#d946ef"
            stroke-width="1.5"
            stroke-linejoin="round"
        />

        <!-- ── Data Points ── -->
        {#each skillValues as val, i}
            {@const p = toXY(angles[i], (val / 100) * R)}
            <circle cx={p.x.toFixed(2)} cy={p.y.toFixed(2)} r="2.5"
                    fill="#d946ef" stroke="white" stroke-width="1" />
        {/each}

        <!-- ── Labels ── -->
        {#each labelPositions as lp}
            <text
                x={lp.x.toFixed(2)}
                y={lp.y.toFixed(2)}
                text-anchor="middle"
                dominant-baseline="middle"
                font-size="5"
                font-weight="700"
                fill="#94a3b8"
                class="select-none"
            >{lp.key}</text>
            <text
                x={lp.x.toFixed(2)}
                y={(lp.y + 6).toFixed(2)}
                text-anchor="middle"
                dominant-baseline="middle"
                font-size="4.5"
                font-weight="900"
                fill="#d946ef"
                class="select-none"
            >{lp.value}</text>
        {/each}

    </svg>
</div>
