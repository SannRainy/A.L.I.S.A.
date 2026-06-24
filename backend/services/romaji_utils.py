import re
import logging

logger = logging.getLogger(__name__)

# ── MeCab + pykakasi Hybrid Romaji Configuration ───────────────────────
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
    'watakushi': 'watashi',
}

def generate_romaji_hybrid(jp_text: str) -> str:
    """
    Convert Japanese text to romaji using a hybrid MeCab + pykakasi approach.
    MeCab provides accurate Kanji readings (Kana spelling), while pykakasi
    does direct Kana -> Romaji mapping. Spacing is handled intelligently based on POS.
    """
    if not jp_text or not jp_text.strip():
        return ""

    try:
        import MeCab
        import pykakasi
        
        # Lazy initialize standard tagger
        tagger = MeCab.Tagger()
        kks = pykakasi.kakasi()
        
        node = tagger.parseToNode(jp_text)
        nodes_list = []
        while node:
            if node.stat not in (2, 3):  # Skip BOS/EOS
                features = node.feature.split(',')
                surface = node.surface
                
                # Extract reading (features[17] in UniDic is surface reading, features[9] is pronunciation)
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
            
            # Spacing rules: determine whether to append with space or merge
            if i == 0:
                parts.append(rom)
            else:
                prev = nodes_list[i-1]
                
                # 1. Punctuation
                is_punct = curr['pos0'] in ('補助記号', '記号') or rom in ('.', ',', '!', '?', '"', '(', ')')
                
                # 2. Conjunctive particle 'te' / 'de' after verbs
                is_te_de = curr['pos0'] == '助詞' and curr['pos1'] == '接続助詞' and curr['surface'] in ('て', 'で') and prev['pos0'] == '動詞'
                
                # 3. Auxiliary verbs (助動詞) after Verb (動詞) or another Auxiliary Verb (助動詞)
                is_aux_verb = curr['pos0'] == '助動詞' and prev['pos0'] in ('動詞', '助動詞')
                
                # 4. Suffixes (接尾辞)
                is_suffix = curr['pos0'] == '接尾辞'
                
                if is_punct or is_te_de or is_aux_verb or is_suffix:
                    parts[-1] = parts[-1] + rom
                else:
                    parts.append(rom)
        
        romaji_text = " ".join(parts)
        
        # Post-processing particle overrides:
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

    except Exception as e:
        logger.error(f"Hybrid MeCab + pykakasi conversion error: {e}. Falling back to standard pykakasi.")
        try:
            import pykakasi
            kks = pykakasi.kakasi()
            result = kks.convert(jp_text)
            romaji_text = " ".join([item['hepburn'] for item in result]).strip()
            romaji_text = romaji_text.replace("！", "!").replace("？", "?")
            romaji_text = re.sub(r'\s+([.,!?;:])', r'\1', romaji_text)
            if romaji_text:
                romaji_text = romaji_text[0].upper() + romaji_text[1:]
            return romaji_text
        except Exception as ex:
            logger.error(f"Standard pykakasi fallback also failed: {ex}")
            return jp_text
