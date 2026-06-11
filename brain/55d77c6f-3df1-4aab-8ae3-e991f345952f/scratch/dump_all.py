import urllib.request
import json

def to_safe_ascii(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')

try:
    url = "http://127.0.0.1:8000/api/v1/reading/passages"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        passages = data.get("passages", [])
        
        for p in passages:
            pid = p['id']
            detail_url = f"http://127.0.0.1:8000/api/v1/reading/passage/{pid}"
            d_req = urllib.request.Request(detail_url)
            with urllib.request.urlopen(d_req, timeout=5) as d_resp:
                d_data = json.loads(d_resp.read().decode())
                psg = d_data.get("passage", {})
                
                print(f"=== PASSAGE {pid} ===")
                print("Title:", to_safe_ascii(psg.get("title", "")))
                print("Text:", to_safe_ascii(psg.get("text", "")))
                print("Vocab:")
                for v in psg.get("vocab_annotations", []):
                    print(f"  {to_safe_ascii(v.get('word', ''))}: {to_safe_ascii(v.get('reading', ''))}")
                print("Questions:")
                for q in psg.get("questions", []):
                    print(f"  Q: {to_safe_ascii(q.get('question', ''))}")
                    opts = [to_safe_ascii(o) for o in q.get("options", [])]
                    print(f"  Opts: {opts}")
except Exception as e:
    print("Error:", e)
