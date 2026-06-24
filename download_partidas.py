import json
import os
from os.path import join

import requests

DATA_DIR = join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

partidas_url = "https://api.cartolafc.globo.com/copa/partidas/{rodada}"

all_matches = []
for rodada in range(1, 9):
    resp = requests.get(partidas_url.format(rodada=rodada))
    if resp.status_code != 200:
        break
    data = resp.json()
    clubes = data["clubes"]

    for p in data["partidas"]:
        mc = str(p.get("clube_casa_id"))
        mv = str(p.get("clube_visitante_id"))
        match = {
            "rodada": rodada,
            "data": p.get("partida_data"),
            "mandante_id": p.get("clube_casa_id"),
            "mandante": clubes.get(mc, {}).get("nome", mc),
            "visitante_id": p.get("clube_visitante_id"),
            "visitante": clubes.get(mv, {}).get("nome", mv),
            "gols_mandante": p.get("placar_oficial_mandante"),
            "gols_visitante": p.get("placar_oficial_visitante"),
        }
        all_matches.append(match)

    print(f"Rodada {rodada}: {len(data['partidas'])} partidas")

import pandas as pd

df = pd.DataFrame(all_matches)
file = join(DATA_DIR, "partidas.csv")
df.to_csv(file, index=False)
print(f"Saved {len(df)} matches -> {file}")
