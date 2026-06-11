const fs = require('fs');

const content = fs.readFileSync('c:/Users/satya/OneDrive/Desktop/TVJP/frontend/src/components/ReadingMode.svelte', 'utf8');
const startIdx = content.indexOf('const FURIGANA_MAP = {');
const endIdx = content.indexOf('};', startIdx);
const mapStr = content.substring(startIdx + 'const FURIGANA_MAP ='.length, endIdx + 1);

// Eval the map safely
const FURIGANA_MAP = eval('(' + mapStr + ')');

const keys = Object.keys(FURIGANA_MAP).sort((a, b) => b.length - a.length);
const escapedKeys = keys.map(k => k.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
const regex = new RegExp(`(${escapedKeys.join('|')})`, 'g');

console.log("Sorted Keys (first 30):", keys.slice(0, 30));
console.log("Regex Pattern length:", regex.source.length);
console.log("Index of '三月':", keys.indexOf('三月'));
console.log("Index of '三':", keys.indexOf('三'));
console.log("Index of '月':", keys.indexOf('月'));
console.log("Position of '三月' in regex:", regex.source.indexOf('三月'));
console.log("Position of '三' in regex:", regex.source.indexOf('三'));
console.log("Position of '月' in regex:", regex.source.indexOf('月'));

function applyFurigana(text) {
    return text.replace(regex, match => FURIGANA_MAP[match] || match);
}

console.log("Test三月:", applyFurigana("三月"));
console.log("Test十一月:", applyFurigana("十一月"));
