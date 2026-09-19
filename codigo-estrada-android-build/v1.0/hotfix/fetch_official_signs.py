from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse, unquote
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import json
import re
import time

BASE = 'https://servicos.infraestruturasdeportugal.pt'
CATALOG = BASE + '/pt-pt/parceiros/normas-de-sinalizacao/sinais-de-alerta?field_categoriasinas_target_id=All&page={page}'
LEGACY_BASE = BASE + '/sites/default/files/inline-images/rodoviaria/seguranca_rodoviaria/normas_sinalizacao'
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'app/src/main/res/drawable-nodpi'
RAW = ROOT / 'app/src/main/res/raw'
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

# RST vertical-sign code families. K/M are not used by the current consolidated enumeration.
CODE_RE = re.compile(r'\b([A-JLNO]\d+[a-z]?)\s*[-–]\s*([^\n\r|]{2,120})', re.I)
FILE_CODE_RE = re.compile(r'^([A-JLNO]\d+[a-z]?)$', re.I)

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; CodigoEstradaPT/1.0; educational offline catalogue)'}

def get(url: str) -> bytes:
    req = Request(url, headers=HEADERS)
    return urlopen(req, timeout=45).read()

def resource_name(code: str) -> str:
    return 'sign_' + re.sub(r'[^a-z0-9_]', '_', code.lower())

def clean_title(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip(' -–\t\r\n')
    return text[:120]

def discover_catalog():
    records = {}
    for page in range(0, 81):
        html = get(CATALOG.format(page=page)).decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        page_text = soup.get_text('\n', strip=True)
        titles = {m.group(1).upper(): clean_title(m.group(2)) for m in CODE_RE.finditer(page_text)}

        images = {}
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or ''
            if not src:
                continue
            stem = Path(unquote(urlparse(src).path)).stem
            m = FILE_CODE_RE.match(stem)
            if m:
                images[m.group(1).upper()] = urljoin(BASE, src)

        for code, title in titles.items():
            image_url = images.get(code)
            if image_url:
                records[code] = {'code': code, 'title': title, 'imageUrl': image_url}

        # The IP catalogue interleaves category pages with pages that may not
        # expose code/image pairs in the same way. Do not stop after empty pages:
        # later page numbers contain other RST families (e.g. B and I).
        time.sleep(0.05)

    return records

# Core fallbacks guarantee that the existing question bank always retains its legally exact assets.
CORE_FOLDERS = {
    'A1a':'1_perigo','A2a':'1_perigo','A5':'1_perigo','A6':'1_perigo','A9':'1_perigo','A12':'1_perigo','A13':'1_perigo','A14':'1_perigo','A16a':'1_perigo','A20':'1_perigo','A22':'1_perigo','A23':'1_perigo','A24':'1_perigo','A25':'1_perigo','A27':'1_perigo',
    'B1':'2_cedencia_passagem','B2':'2_cedencia_passagem','B3':'2_cedencia_passagem','B4':'2_cedencia_passagem','B5':'2_cedencia_passagem','B6':'2_cedencia_passagem','B7':'2_cedencia_passagem',
    'C1':'3_proibicao','C13':'3_proibicao','C15':'3_proibicao','C16':'3_proibicao',
    'D4':'4_obrigacao','D7a':'4_obrigacao',
    'H1a':'8_informacao','H7':'8_informacao','H24':'8_informacao',
}

records = discover_catalog()
for code, folder in CORE_FOLDERS.items():
    key = code.upper()
    if key not in records:
        records[key] = {
            'code': code,
            'title': f'Sinal {code}',
            'imageUrl': f'{LEGACY_BASE}/{folder}/{code}.gif'
        }

written = []
failures = []
for code in sorted(records, key=lambda x: (x[0], len(x), x)):
    rec = records[code]
    try:
        data = get(rec['imageUrl'])
        im = Image.open(BytesIO(data)).convert('RGBA')
        name = resource_name(code)
        dest = OUT / f'{name}.png'
        im.save(dest, 'PNG', optimize=True)
        written.append({
            'code': code,
            'title': rec['title'],
            'imageName': name,
            'source': rec['imageUrl'],
        })
        print(code, rec['title'], dest.name)
    except Exception as exc:
        failures.append((code, str(exc)))
        print('FAILED', code, exc)

# A full catalogue should be comfortably above 100 vertical sign variants.
if len(written) < 100:
    raise SystemExit(f'Official vertical-sign crawl incomplete: only {len(written)} assets downloaded; failures={len(failures)}')

(RAW / 'official_sign_catalog.json').write_text(
    json.dumps(written, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(f'OFFICIAL_SIGN_COUNT={len(written)}')
if failures:
    print(f'NON_FATAL_DOWNLOAD_FAILURES={len(failures)}')
