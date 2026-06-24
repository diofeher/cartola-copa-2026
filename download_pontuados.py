import os
import sys
from os.path import exists, join

import pandas as pd
import requests

COPA_PONTUADOS_URL = "https://api.cartolafc.globo.com/copa/atletas/pontuados/{rodada}"
COPA_MERCADO_URL = "https://api.cartolafc.globo.com/copa/atletas/mercado"
DATA_DIR = join(os.path.dirname(__file__), "data")

rodada = int(sys.argv[1]) if len(sys.argv) > 1 else 1

mercado = requests.get(COPA_MERCADO_URL).json()
df_clubes = pd.DataFrame(mercado["clubes"].values())
df_clubes = df_clubes.rename(columns=dict(id="clube_id", nome="clube_nome"))
df_clubes = df_clubes[["clube_id", "clube_nome"]]

resp = requests.get(COPA_PONTUADOS_URL.format(rodada=rodada))
data = resp.json()

rows = []
for atleta_id, info in data["atletas"].items():
    row = {
        "atleta_id": int(atleta_id),
        "apelido": info["apelido"],
        "posicao_id": info["posicao_id"],
        "clube_id": info["clube_id"],
        "pontuacao": info["pontuacao"],
        "entrou_em_campo": info["entrou_em_campo"],
    }
    for k, v in (info.get("scout") or {}).items():
        row[k] = v
    rows.append(row)

df = pd.DataFrame(rows)
df = df.merge(df_clubes, on="clube_id", how="left")
df.sort_values("atleta_id", inplace=True, ignore_index=True)

file = join(DATA_DIR, f"pontuados-rodada-{rodada}.csv")
os.makedirs(DATA_DIR, exist_ok=True)
df.to_csv(file, index=False)
print(f"Saved {len(df)} atletas -> {file}")
