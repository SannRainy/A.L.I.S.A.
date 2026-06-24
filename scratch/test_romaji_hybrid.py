import sys
import MeCab
import pykakasi
import re

sys.stdout.reconfigure(encoding='utf-8')

# Suffix/particle patterns to split
_ROMAJI_SUFFIX_SPLITS = [
    (r'doudesuka\b', 'dou desu ka'),
    (r'doudesu\b', 'dou desu'),
    (r'nandesuka\b', 'nan desu ka'),
    (r'nandesu\b', 'nan desu'),
    (r'desuka\b', 'desu ka'),
    (r'desune\b', 'desu ne'),
    (r'desuyo\b', 'desu yo'),
    (r'desuga\b', 'desu ga'),
    (r'desukara\b', 'desu kara'),
    (r'masuka\b', 'masu ka'),
    (r'masune\b', 'masu ne'),
    (r'masuyo\b', 'masu yo'),
    (r'masuga\b', 'masu ga'),
    (r'masukara\b', 'masu kara'),
    (r'mashitaka\b', 'mashita ka'),
    (r'mashitane\b', 'mashita ne'),
    (r'mashouka\b', 'mashou ka'),
    (r'masenka\b', 'masen ka'),
    (r'nakattadesu\b', 'nakatta desu'),
    (r'dayo\b', 'da yo'),
    (r'dane\b', 'da ne'),
    (r'koreha\b', 'kore wa'),
    (r'soreha\b', 'sore wa'),
    (r'areha\b', 'are wa'),
    (r'watashiha\b', 'watashi wa'),
    (r'bokuha\b', 'boku wa'),
    (r'kareha\b', 'kare wa'),
    (r'kanojoha\b', 'kanojo wa'),
    (r'watashitachiha\b', 'watashitachi wa'),
    (r'\bwo\b', 'o'),
    (r'isshoni\b', 'issho ni'),
]

_ROMAJI_PUNCT_MAP = {
    '！': '!', '？': '?', '。': '.', '、': ', ',
    '（': '(', '）': ')', '「': '"', '」': '"',
    '〜': '~', '～': '~',
}

_ROMAJI_WORD_OVERRIDES = {
    'konnichiha': 'konnichiwa',
    'ohayougozaimasu': 'ohayou gozaimasu',
    'arigatougozaimasu': 'arigatou gozaimasu',
    'arigatougozaimashita': 'arigatou gozaimashita',
    'oyasuminasai': 'oyasumi nasai',
    'gochisousamadeshita': 'gochisousama deshita',
}

def clean_romaji(romaji_text: str) -> str:
    # Apply suffix/particle corrections
    for pattern, replacement in _ROMAJI_SUFFIX_SPLITS:
        romaji_text = re.sub(pattern, replacement, romaji_text, flags=re.IGNORECASE)
    
    # Fix standalone は particle (ha → wa)
    romaji_text = re.sub(r'\bha\b', 'wa', romaji_text)
    
    # Clean up spacing
    romaji_text = re.sub(r'\s+', ' ', romaji_text).strip()
    romaji_text = re.sub(r'\s+([.,!?;:])', r'\1', romaji_text)
    
    # Capitalize first letter
    if romaji_text:
        romaji_text = romaji_text[0].upper() + romaji_text[1:]
    
    # Capitalize after sentence-ending punctuation
    romaji_text = re.sub(
        r'([.!?])\s+([a-z])',
        lambda m: m.group(1) + ' ' + m.group(2).upper(),
        romaji_text
    )
    return romaji_text

def test_conversion(strategy_name, feature_index_selector):
    tagger = MeCab.Tagger()
    kks = pykakasi.kakasi()
    
    sentences = [
        "昨日はすき焼きを食べました。",
        "こんにちは！私は学生です。",
        "何をしていますか？",
        "美味しいですね。",
        "一緒に行きましょう！",
        "大人は一人、子供は二人です。"
    ]
    
    print(f"=== Strategy: {strategy_name} ===")
    for text in sentences:
        node = tagger.parseToNode(text)
        parts = []
        while node:
            if node.stat not in (2, 3):
                features = node.feature.split(',')
                # Select reading/kana token
                kana_token = feature_index_selector(node.surface, features)
                
                # Convert this specific token to romaji
                res = kks.convert(kana_token)
                rom = "".join([item['hepburn'] for item in res])
                
                # Map punctuation
                for fw, hw in _ROMAJI_PUNCT_MAP.items():
                    rom = rom.replace(fw, hw)
                
                # Apply word-level override
                rom_lower = rom.lower()
                if rom_lower in _ROMAJI_WORD_OVERRIDES:
                    rom = _ROMAJI_WORD_OVERRIDES[rom_lower]
                
                if rom.strip():
                    parts.append(rom)
            node = node.next
        
        raw_romaji = " ".join(parts)
        cleaned = clean_romaji(raw_romaji)
        print(f"JP: {text}")
        print(f"Raw: {raw_romaji}")
        print(f"Clean: {cleaned}\n")

# Strategy 1: Using features[17] (Kana spelling)
def get_kana_spelling(surface, features):
    if len(features) > 17 and features[17] and features[17] != '*':
        return features[17]
    # Fallback to feature[6] if present
    if len(features) > 6 and features[6] and features[6] != '*':
        # Check if lemma form differs significantly for verbs, e.g. 食べ -> タベル instead of タベ
        # Actually features[6] is lemma form, so for conjugated verbs it's the root.
        pass
    return surface

# Strategy 2: Using features[9] (Actual pronunciation)
def get_pronunciation(surface, features):
    if len(features) > 9 and features[9] and features[9] != '*':
        return features[9]
    return surface

# Strategy 3: Best features[17] with correct fallback
def get_best_reading(surface, features):
    # features[17] is surface-form reading in UniDic
    if len(features) > 17 and features[17] and features[17] != '*':
        return features[17]
    # features[6] is lemma reading, but for verbs we want surface form reading.
    # If feature length is enough, features[9] is pronunciation.
    if len(features) > 9 and features[9] and features[9] != '*':
        # Pronunciation form has length/sound updates like キノー, but it's very close to reading.
        # We can normalize pronunciation form or use features[9]
        return features[9]
    return surface

if __name__ == "__main__":
    test_conversion("Kana Spelling (index 17)", get_kana_spelling)
    test_conversion("Pronunciation (index 9)", get_pronunciation)
    test_conversion("Best Reading (index 17 or 9)", get_best_reading)
