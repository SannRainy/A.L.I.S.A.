import sys
import MeCab

# Reconfigure stdout to support printing Japanese
sys.stdout.reconfigure(encoding='utf-8')

def test_mecab():
    # 1. Test standard tagger
    print("--- Default Tagger ---")
    try:
        tagger = MeCab.Tagger()
        text = "昨日はすき焼きを食べました。こんにちは！"
        res = tagger.parse(text)
        print("Raw parse success")
        # Print first 5 lines of raw parse
        for line in res.splitlines()[:10]:
            print(line)
    except Exception as e:
        print("Error Default:", e)

    # 2. Test Node parsing to inspect features
    print("\n--- Node Features ---")
    try:
        tagger = MeCab.Tagger()
        node = tagger.parseToNode(text)
        while node:
            if node.stat not in (2, 3):
                features = node.feature.split(',')
                # Print surface form and features length
                print(f"Surface: {node.surface} | Features count: {len(features)}")
                for i, f in enumerate(features):
                    print(f"  [{i}]: {f}")
            node = node.next
    except Exception as e:
        print("Error Nodes:", e)

if __name__ == "__main__":
    test_mecab()
