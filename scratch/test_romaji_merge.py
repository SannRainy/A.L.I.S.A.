import sys
import MeCab
import pykakasi
import re

sys.stdout.reconfigure(encoding='utf-8')

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
    'watakushi': 'watashi', # Standardize formal 'watakushi' to 'watashi' for learners
}

def clean_romaji(romaji_text: str) -> str:
    # Fix standalone は particle (ha → wa)
    romaji_text = re.sub(r'\bha\b', 'wa', romaji_text, flags=re.IGNORECASE)
    # Fix standalone を particle (wo → o)
    romaji_text = re.sub(r'\bwo\b', 'o', romaji_text, flags=re.IGNORECASE)

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

def test_merge_strategy():
    tagger = MeCab.Tagger()
    kks = pykakasi.kakasi()
    
    sentences = [
        "昨日はすき焼きを食べました。",
        "こんにちは！私は学生です。",
        "何をしていますか？",
        "美味しいですね。",
        "一緒に行きましょう！",
        "大人は一人、子供は二人です。",
        "学校に行きたくないです。",
        "本を読んでいます。"
    ]
    
    print("=== Intelligent Merge Strategy ===")
    for text in sentences:
        node = tagger.parseToNode(text)
        tokens = []
        
        # Build node list for analysis
        nodes_list = []
        while node:
            if node.stat not in (2, 3):
                features = node.feature.split(',')
                surface = node.surface
                
                # Extract reading
                reading = surface
                if len(features) > 17 and features[17] and features[17] != '*':
                    reading = features[17]
                elif len(features) > 9 and features[9] and features[9] != '*':
                    reading = features[9]
                
                nodes_list.append({
                    'surface': surface,
                    'pos0': features[0] if len(features) > 0 else '',
                    'pos1': features[1] if len(features) > 1 else '',
                    'reading': reading
                })
            node = node.next
            
        parts = []
        for i, curr in enumerate(nodes_list):
            # Convert reading to Romaji
            res = kks.convert(curr['reading'])
            rom = "".join([item['hepburn'] for item in res])
            
            # Map punctuation
            for fw, hw in _ROMAJI_PUNCT_MAP.items():
                rom = rom.replace(fw, hw)
            
            # Word-level override
            rom_lower = rom.lower()
            if rom_lower in _ROMAJI_WORD_OVERRIDES:
                rom = _ROMAJI_WORD_OVERRIDES[rom_lower]
            
            curr['romaji'] = rom
            
            # Decide spacing before this token
            if i == 0:
                parts.append(rom)
            else:
                prev = nodes_list[i-1]
                
                # Rules to NOT add space (merge with previous):
                # 1. Punctuation
                is_punct = curr['pos0'] in ('補助記号', '記号') or rom in ('.', ',', '!', '?', '"', '(', ')')
                
                # 2. Conjunctive particle 'te' / 'de' after verbs
                is_te_de = curr['pos0'] == '助詞' and curr['pos1'] == '接続助詞' and curr['surface'] in ('て', 'で') and prev['pos0'] == '動詞'
                
                # 3. Auxiliary verbs (助動詞) after Verb (動詞) or another Auxiliary Verb (助動詞)
                is_aux_verb = curr['pos0'] == '助動詞' and prev['pos0'] in ('動詞', '助動詞')
                
                # 4. Suffixes (接尾辞) like tachi, down/up etc.
                is_suffix = curr['pos0'] == '接尾辞'
                
                # 5. Particle 'ha' (wa), 'wo' (o), 'ni', 'de' - wait, we do want spaces before particles! E.g. "watashi wa". So they shouldn't be merged.
                
                if is_punct or is_te_de or is_aux_verb or is_suffix:
                    # Merge (no space)
                    parts[-1] = parts[-1] + rom
                else:
                    # Separate with space
                    parts.append(rom)
        
        raw_romaji = " ".join(parts)
        cleaned = clean_romaji(raw_romaji)
        print(f"JP: {text}")
        print(f"Clean: {cleaned}\n")

if __name__ == "__main__":
    test_merge_strategy()
