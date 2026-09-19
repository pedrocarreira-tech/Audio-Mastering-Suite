from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from PIL import Image
import json, re, socket, time

ROOT = Path("/tmp/codigo-build")
OUT = ROOT / "app/src/main/res/drawable-nodpi"
RAW = ROOT / "app/src/main/res/raw"
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

BASE = "https://servicos.infraestruturasdeportugal.pt/sites/default/files/inline-images/rodoviaria/seguranca_rodoviaria/normas_sinalizacao"
HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; CodigoEstradaPT/1.1; educational offline catalogue)"}

EMERGENCY = {
 "1.1":"Hospital",
 "1.2":"Hospital com urgência médica",
 "1.3":"Posto de socorros",
 "1.4":"Farmácia",
 "1.5":"Bombeiros",
 "1.6":"GNR",
 "1.7":"PSP",
 "1.8":"Oficina",
 "1.9":"Posto de combustível com GPL (gás de petróleo liquefeito)",
 "1.10":"Posto de combustível",
 "1.11":"Telefone",
}
OTHER = {
 "2.1":"Parque de estacionamento",
 "2.2":"Igreja / santuário",
 "2.3":"Cemitério",
 "2.4":"Mercado",
 "2.5":"Escola",
 "2.6":"Correios",
 "2.7":"Centro",
 "2.8":"Zona pedonal",
 "2.9":"Bairro",
 "2.10":"Metro",
 "2.11":"Estação ferroviária",
 "2.12":"Estação rodoviária",
 "2.13":"Táxis",
 "2.14":"Aluguer de viaturas",
 "2.15":"Ferry-boat",
 "2.16":"Cais de embarque",
 "2.17":"Porto",
 "2.18":"Aeroporto / aeródromo",
 "2.19":"Heliporto",
 "2.20":"Município",
 "2.21":"Autoestrada",
 "2.22":"Deficiente",
 "2.23":"Passagem desnivelada para peões com rampa",
 "2.24":"Passagem desnivelada para peões com escada",
 "2.25":"Sanitários",
 "2.26":"Centro de inspeções",
 "2.27":"Via reservada a automóveis e motociclos",
 "2.28":"Fontanário",
}

def get(url, attempts=3, timeout=15):
    last = None
    for n in range(attempts):
        try:
            return urlopen(Request(url, headers=HEADERS), timeout=timeout).read()
        except (TimeoutError, socket.timeout, URLError, HTTPError, OSError) as exc:
            last = exc
            if n + 1 < attempts:
                time.sleep(1 + n)
    raise last

def safe(value):
    return re.sub(r"[^a-z0-9_]", "_", value.lower().replace(".", "_"))

def job(family, folder, code, title, filename):
    url = f"{BASE}/{folder}/{filename}"
    try:
        image = Image.open(BytesIO(get(url))).convert("RGBA")
        sid = ("emergencia_" if code.startswith("1.") else "outras_") + code.replace(".", "_")
        image_name = "symbol_" + safe(sid)
        image.save(OUT / f"{image_name}.png", "PNG", optimize=True)
        return {
            "id": sid,
            "code": code,
            "family": family,
            "title": title,
            "imageName": image_name,
            "source": url,
        }, None
    except Exception as exc:
        return None, f"{code} {url}: {exc}"

tasks = []
for i in range(1, 12):
    code = f"1.{i}"
    tasks.append(("Símbolos - Apoio ao Utente Emergência", "16_apoio_utente_emergencia", code, EMERGENCY[code], f"1-{i:02d}.gif"))
for i in range(1, 29):
    code = f"2.{i}"
    tasks.append(("Símbolos - Apoio ao Utente Outras Indicações", "17_apoio_utente_outras_indicacoes", code, OTHER[code], f"2-{i:02d}.gif"))

records, failures = [], []
with ThreadPoolExecutor(max_workers=6) as pool:
    futures = [pool.submit(job, *t) for t in tasks]
    for future in as_completed(futures):
        rec, error = future.result()
        if rec:
            records.append(rec)
            print("SYMBOL", rec["code"], rec["title"])
        else:
            failures.append(error)
            print("FAILED_SYMBOL", error)

records.sort(key=lambda x: (x["family"], tuple(int(p) for p in x["code"].split("."))))
(RAW / "official_symbol_catalog.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"OFFICIAL_SYMBOL_COUNT={len(records)}")
print(f"SYMBOL_FAILURES={len(failures)}")
if len(records) < 20:
    raise SystemExit(f"Insufficient official symbols: {len(records)}")
