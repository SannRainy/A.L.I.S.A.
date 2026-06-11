const FURIGANA_MAP = {
    "六月": "<ruby>六月<rt>ろくがつ</rt></ruby>",
    "月": "<ruby>月<rt>つき</rt></ruby>"
};

function applyFurigana(text) {
    if (!text) return "";
    const keys = Object.keys(FURIGANA_MAP).sort((a, b) => b.length - a.length);
    const escapedKeys = keys.map(k => k.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
    const regex = new RegExp(`(${escapedKeys.join('|')})`, 'g');
    return text.replace(regex, match => {
        return FURIGANA_MAP[match] || match;
    });
}

console.log("Result (六月):", applyFurigana("六月"));
