import urllib.request

for host in ["localhost", "127.0.0.1", "[::1]"]:
    try:
        url = f"http://{host}:5173/src/components/ReadingMode.svelte"
        print(f"Trying {url}...")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as response:
            content = response.read().decode('utf-8')
            print("Success! File length:", len(content))
            idx = content.find("const FURIGANA_MAP =")
            if idx != -1:
                print("Found FURIGANA_MAP in Vite served file:")
                print(content[idx:idx+200].encode('ascii', 'backslashreplace').decode('ascii'))
            else:
                print("FURIGANA_MAP NOT found in Vite served file!")
            break
    except Exception as e:
        print(f"Failed {host}: {e}")
