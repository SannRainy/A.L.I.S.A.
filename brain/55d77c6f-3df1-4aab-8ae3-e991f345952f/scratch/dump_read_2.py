import urllib.request
import json

try:
    print("Fetching reading passage read_2...")
    url = "http://127.0.0.1:8000/api/v1/reading/passage/read_2"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as response:
        data = json.loads(response.read().decode())
        s = json.dumps(data, indent=2, ensure_ascii=False)
        print(s.encode('ascii', 'backslashreplace').decode('ascii'))
except Exception as e:
    print("Error:", e)
