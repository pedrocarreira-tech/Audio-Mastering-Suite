from pathlib import Path
from urllib.request import urlopen, Request
from PIL import Image
from io import BytesIO

BASE = 'https://servicos.infraestruturasdeportugal.pt/sites/default/files/inline-images/rodoviaria/seguranca_rodoviaria/normas_sinalizacao'
OUT = Path(__file__).resolve().parents[1] / 'app/src/main/res/drawable-nodpi'
OUT.mkdir(parents=True, exist_ok=True)

mapping = {
    'A1a':'1_perigo','A2a':'1_perigo','A5':'1_perigo','A6':'1_perigo','A9':'1_perigo','A12':'1_perigo','A13':'1_perigo','A14':'1_perigo','A16a':'1_perigo','A20':'1_perigo','A22':'1_perigo','A23':'1_perigo','A24':'1_perigo','A25':'1_perigo','A27':'1_perigo',
    'B1':'2_cedencia_passagem','B2':'2_cedencia_passagem','B3':'2_cedencia_passagem','B4':'2_cedencia_passagem','B5':'2_cedencia_passagem','B6':'2_cedencia_passagem','B7':'2_cedencia_passagem',
    'C1':'3_proibicao','C13':'3_proibicao','C15':'3_proibicao','C16':'3_proibicao',
    'D4':'4_obrigacao','D7a':'4_obrigacao',
    'H1a':'8_informacao','H7':'8_informacao','H24':'8_informacao',
}
for code, folder in mapping.items():
    url=f'{BASE}/{folder}/{code}.gif'
    req=Request(url, headers={'User-Agent':'Mozilla/5.0'})
    data=urlopen(req, timeout=30).read()
    im=Image.open(BytesIO(data)).convert('RGBA')
    dest=OUT / f'sign_{code.lower()}.png'
    im.save(dest, 'PNG', optimize=True)
    print(code, dest.name, len(data))
