from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")

s = s.replace(
    "from urllib.request import urlopen, Request\n",
    "from urllib.request import urlopen, Request\nfrom urllib.error import URLError, HTTPError\nfrom concurrent.futures import ThreadPoolExecutor, as_completed\nimport socket\n",
)

old_get = """def get(url: str) -> bytes:
    req = Request(url, headers=HEADERS)
    return urlopen(req, timeout=45).read()
"""
new_get = """def get(url: str, attempts: int = 2, timeout: int = 10) -> bytes:
    last = None
    for attempt in range(1, attempts + 1):
        try:
            req = Request(url, headers=HEADERS)
            return urlopen(req, timeout=timeout).read()
        except (TimeoutError, socket.timeout, URLError, HTTPError, OSError) as exc:
            last = exc
            print(f'RETRY {attempt}/{attempts} {url}: {exc}')
            if attempt < attempts:
                time.sleep(min(0.8 * attempt, 2.0))
    raise last
"""
if old_get not in s:
    raise SystemExit("get() patch anchor not found")
s = s.replace(old_get, new_get)

start = s.index("def discover_catalogs():")
end = s.index("\nCORE_FOLDERS = {", start)
old_discover = s[start:end]
new_discover = """def _catalog_page(page: int):
    try:
        html = get(CATALOG.format(page=page)).decode('utf-8', errors='ignore')
        return page, html, None
    except Exception as exc:
        return page, None, str(exc)

def discover_catalogs():
    signs = {}
    symbols = {}
    failed_pages = []
    pages = {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_catalog_page, page) for page in range(0, 81)]
        for future in as_completed(futures):
            page, html, error = future.result()
            if error:
                failed_pages.append((page, error))
                print('FAILED CATALOG PAGE', page, error)
            else:
                pages[page] = html

    for page in sorted(pages):
        soup = BeautifulSoup(pages[page], 'html.parser')
        page_text = soup.get_text('\\n', strip=True)

        sign_titles = {m.group(1).upper(): clean_title(m.group(2)) for m in CODE_RE.finditer(page_text)}
        sign_images = {}
        symbol_titles = {m.group(1): clean_title(m.group(2)) for m in SYMBOL_RE.finditer(page_text)}
        symbol_images = {}

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or ''
            if not src:
                continue
            stem = Path(unquote(urlparse(src).path)).stem
            m = FILE_CODE_RE.match(stem)
            if m:
                sign_images[m.group(1).upper()] = urljoin(BASE, src)
                continue
            numeric = normalize_numeric_stem(stem)
            if SYMBOL_FILE_RE.match(stem) and re.fullmatch(r'\\d+(?:\\.\\d+)*', numeric):
                symbol_images[numeric] = urljoin(BASE, src)

        for code, title in sign_titles.items():
            if code in sign_images:
                signs[code] = {'code': code, 'title': title, 'imageUrl': sign_images[code]}

        heading = ''
        for h in soup.find_all(['h2','h3','h4','h5']):
            txt = clean_title(h.get_text(' ', strip=True))
            if 'símbol' in txt.lower() or 'simbol' in txt.lower():
                heading = txt
                break
        if not heading:
            for line in page_text.splitlines():
                if 'símbol' in line.lower() or 'simbol' in line.lower():
                    heading = clean_title(line)
                    break

        if heading:
            family = heading
            for code, title in symbol_titles.items():
                image_url = symbol_images.get(code)
                if image_url:
                    sid = f'p{page:02d}_{slug(family)}_{code.replace(".", "_")}'
                    symbols[sid] = {'id': sid, 'code': code, 'family': family, 'title': title, 'imageUrl': image_url}

    if failed_pages:
        print(f'NON_FATAL_CATALOG_PAGE_FAILURES={len(failed_pages)}')
    print(f'DISCOVERED_SIGNS={len(signs)} DISCOVERED_SYMBOLS={len(symbols)}')
    return signs, symbols
"""
s = s[:start] + new_discover + s[end:]

download_start = s.index("written_signs = []")
download_end = s.index("\nif len(written_signs) < 200:", download_start)
new_download = """def _download_asset(kind, key, rec):
    try:
        im = Image.open(BytesIO(get(rec['imageUrl']))).convert('RGBA')
        if kind == 'sign':
            name = 'sign_' + re.sub(r'[^a-z0-9_]', '_', key.lower())
            im.save(OUT / f'{name}.png', 'PNG', optimize=True)
            return kind, key, {
                'code': key, 'title': rec['title'], 'imageName': name, 'source': rec['imageUrl']
            }, None
        name = 'symbol_' + re.sub(r'[^a-z0-9_]', '_', key.lower())
        im.save(OUT / f'{name}.png', 'PNG', optimize=True)
        return kind, key, {
            'id': key, 'code': rec['code'], 'family': rec['family'], 'title': rec['title'],
            'imageName': name, 'source': rec['imageUrl']
        }, None
    except Exception as exc:
        return kind, key, None, str(exc)

written_signs = []
written_symbols = []
failures = []
tasks = [('sign', code, sign_records[code]) for code in sorted(sign_records, key=lambda x: (x[0], len(x), x))]
tasks += [('symbol', sid, symbol_records[sid]) for sid in sorted(symbol_records)]

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(_download_asset, kind, key, rec) for kind, key, rec in tasks]
    for future in as_completed(futures):
        kind, key, record, error = future.result()
        if error:
            failures.append((kind, key, error))
            print('FAILED', kind.upper(), key, error)
        elif kind == 'sign':
            written_signs.append(record)
            print('SIGN', key, record['title'])
        else:
            written_symbols.append(record)
            print('SYMBOL', record['family'], record['code'], record['title'])

written_signs.sort(key=lambda r: (r['code'][0], len(r['code']), r['code']))
written_symbols.sort(key=lambda r: r['id'])
"""
s = s[:download_start] + new_download + s[download_end:]

p.write_text(s, encoding="utf-8")
print("Parallel resilient crawler hotfix applied:", p)
