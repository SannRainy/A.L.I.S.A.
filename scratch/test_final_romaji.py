import sys
import os

# Ensure backend directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
sys.stdout.reconfigure(encoding='utf-8')

try:
    from services.romaji_utils import generate_romaji_hybrid
    
    test_cases = [
        "昨日はすき焼きを食べました。",
        "こんにちは！私は学生です。",
        "何をしていますか？",
        "美味しいですね。",
        "一緒に行きましょう！",
        "大人は一人、子供は二人です。",
        "学校に行きたくないです。",
        "本を読んでいます。"
    ]
    
    print("=== FINAL HYBRID ROMAJI ENGINE TEST ===")
    for text in test_cases:
        romaji = generate_romaji_hybrid(text)
        print(f"JP: {text}")
        print(f"Romaji: {romaji}\n")
        
except Exception as e:
    print("Error during test execution:", e)
    import traceback
    traceback.print_exc()
