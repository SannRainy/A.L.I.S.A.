import urllib.request
import json

def to_safe_ascii(s):
    return s.encode('ascii', 'backslashreplace').decode('ascii')

try:
    print("Fetching reading passages list...")
    url = "http://127.0.0.1:8000/api/v1/reading/passages"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        print("Success! Number of passages:", len(data.get("passages", [])))
        for p in data.get("passages", []):
            safe_title = to_safe_ascii(p['title'])
            print(f"ID: {p['id']}, Title: {safe_title}")
            
            detail_url = f"http://127.0.0.1:8000/api/v1/reading/passage/{p['id']}"
            detail_req = urllib.request.Request(detail_url)
            with urllib.request.urlopen(detail_req, timeout=5) as detail_resp:
                detail_data = json.loads(detail_resp.read().decode())
                passage = detail_data.get("passage", {})
                passage_text = passage.get("text", "")
                vocab_annotations = passage.get("vocab_annotations", [])
                print(f"  Text: {to_safe_ascii(passage_text)}")
                print(f"  Vocab Annotations:")
                for v in vocab_annotations:
                    print(f"    Word: {to_safe_ascii(v.get('word', ''))}, Reading: {to_safe_ascii(v.get('reading', ''))}")
except Exception as e:
    print("Error fetching passages:", e)
