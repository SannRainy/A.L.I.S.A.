import pykakasi

def test():
    kks = pykakasi.kakasi()
    res1 = kks.convert("こんにちは")
    res2 = kks.convert("今日はどうですか？")
    
    with open("test_out.txt", "w", encoding="utf-8") as f:
        f.write("RES1: " + " ".join([i['hepburn'] for i in res1]) + "\n")
        f.write("RES2: " + " ".join([i['hepburn'] for i in res2]) + "\n")

if __name__ == "__main__":
    test()
