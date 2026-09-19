from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

s = s.replace(
    "from urllib.request import urlopen, Request\n",
    "from urllib.request import urlopen, Request\nfrom urllib.error import URLError, HTTPError\nimport socket\n",
)

old_get = """def get(url: str) -> bytes:
    req = Request(url, headers=HEADERS)
    return urlopen(req, timeout=45).read()
"""
new_get = """def get(url: str, attempts: int = 3, timeout: int = 15) -> bytes:
    last = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers=HEADERS)
            return urlopen(req, timeout=timeout).read()
        except (TimeoutError, socket.timeout, URLError, HTTPError, OSError) as exc:
            last = exc
            print(f'RETRY {attempt}/{attempts} {url}: {exc}')
            if attempt < attempts:
                time.sleep(min(1.5 * attempt, 4.0))
    raise last
"""
if old_get not in s:
    raise SystemExit("get() patch anchor not found")
s = s.replace(old_get, new_get)

old_loop = """    for page in range(0, 81):
        html = get(CATALOG.format(page=page)).decode('utf-8', errors='ignore')
"""
new_loop = """    failed_pages = []
    for page in range(0, 81):
        try:
            html = get(CATALOG.format(page=page)).decode('utf-8', errors='ignore')
        except Exception as exc:
            failed_pages.append((page, str(exc)))
            print('FAILED CATALOG PAGE', page, exc)
            continue
"""
if old_loop not in s:
    raise SystemExit("catalog loop patch anchor not found")
s = s.replace(old_loop, new_loop)

old_return = "    return signs, symbols\n"
new_return = """    if failed_pages:
        print(f'NON_FATAL_CATALOG_PAGE_FAILURES={len(failed_pages)}')
    return signs, symbols
"""
if old_return not in s:
    raise SystemExit("return patch anchor not found")
s = s.replace(old_return, new_return, 1)

p.write_text(s, encoding="utf-8")
print("Crawler retry hotfix applied:", p)
