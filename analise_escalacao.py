"""
Análise da escalação do Cartola Copa — Rodada 3.
"""

import os
from os.path import join

import pandas as pd

DATA_DIR = join(os.path.dirname(__file__), "data")

ranking_fifa = pd.read_csv(join(DATA_DIR, "fifa_ranking.csv"))
partidas = pd.read_csv(join(DATA_DIR, "partidas.csv"))

pontuados_files = sorted(
    [f for f in os.listdir(DATA_DIR) if f.startswith("pontuados-rodada-")]
)
dfs = [pd.read_csv(join(DATA_DIR, f)) for f in pontuados_files]
pontuados = pd.concat(dfs, ignore_index=True)
em_campo = pontuados[pontuados["entrou_em_campo"] == True]

TITULARES = [
    {"apelido": "Courtois", "posicao": "Goleiro", "selecao": "Bélgica", "preco": 13.66},
    {"apelido": "Nuno Mendes", "posicao": "Lateral", "selecao": "Portugal", "preco": 15.42},
    {"apelido": "Laporte", "posicao": "Zagueiro", "selecao": "Espanha", "preco": 10.39},
    {"apelido": "Van Dijk", "posicao": "Zagueiro", "selecao": "Holanda", "preco": 10.66},
    {"apelido": "Hakimi", "posicao": "Lateral", "selecao": "Marrocos", "preco": 16.34},
    {"apelido": "Saibari", "posicao": "Meia", "selecao": "Marrocos", "preco": 11.24},
    {"apelido": "Olise", "posicao": "Meia", "selecao": "França", "preco": 21.86},
    {"apelido": "Nmecha", "posicao": "Meia", "selecao": "Alemanha", "preco": 14.73},
    {"apelido": "Vini Jr.", "posicao": "Atacante", "selecao": "Brasil", "preco": 21.83},
    {"apelido": "Haaland", "posicao": "Atacante", "selecao": "Noruega", "preco": 27.32},
    {"apelido": "Messi", "posicao": "Atacante", "selecao": "Argentina", "preco": 25.88, "capitao": True},
]

BANCO = [
    {"apelido": "Room", "posicao": "Goleiro", "selecao": "Curaçao", "preco": 7.92},
    {"apelido": "Doué", "posicao": "Meia", "selecao": "França", "preco": 3.91},
    {"apelido": "Riad", "posicao": "Zagueiro", "selecao": "Espanha", "preco": 3.46},
    {"apelido": "H. In-Beom", "posicao": "Meia", "selecao": "Coreia do Sul", "preco": 9.23},
    {"apelido": "Lamine Yamal", "posicao": "Atacante", "selecao": "Espanha", "preco": 21.60},
]

TECNICO = {"apelido": "M. Ouahbi", "selecao": "Marrocos", "preco": 5.33}


def get_adversario(selecao, partidas_df, rodada=3):
    r = partidas_df[partidas_df["rodada"] == rodada]
    m = r[(r["mandante"] == selecao) | (r["visitante"] == selecao)]
    if m.empty:
        return "?"
    row = m.iloc[0]
    return row["visitante"] if row["mandante"] == selecao else row["mandante"]


def get_fifa_rank(selecao):
    r = ranking_fifa[ranking_fifa["clube_nome"] == selecao]
    return r["fifa_ranking"].values[0] if len(r) > 0 else "?"


def get_historico(apelido):
    jogador = em_campo[em_campo["apelido"].str.contains(apelido, case=False, na=False)]
    if jogador.empty:
        return {"pts_total": 0, "media": 0, "gols": 0, "assists": 0, "rodadas": 0}
    return {
        "pts_total": round(jogador["pontuacao"].sum(), 2),
        "media": round(jogador["pontuacao"].mean(), 2),
        "gols": int(jogador["G"].sum()) if "G" in jogador.columns else 0,
        "assists": int(jogador["A"].sum()) if "A" in jogador.columns else 0,
        "rodadas": len(jogador),
    }


def analyze_player(player):
    hist = get_historico(player["apelido"])
    adv = get_adversario(player["selecao"], partidas)
    adv_rank = get_fifa_rank(adv) if adv != "?" else "?"
    team_rank = get_fifa_rank(player["selecao"])

    diff = ""
    if isinstance(adv_rank, int) and isinstance(team_rank, int):
        d = adv_rank - team_rank
        diff = f"(+{d} favorável)" if d > 0 else f"({d} desfavorável)" if d < 0 else "(igual)"

    return {
        "jogador": player["apelido"],
        "posicao": player.get("posicao", ""),
        "selecao": player["selecao"],
        "fifa_rank": team_rank,
        "adversario": adv,
        "adv_rank": adv_rank,
        "diff_rank": diff,
        "pts_total": hist["pts_total"],
        "media": hist["media"],
        "gols": hist["gols"],
        "assists": hist["assists"],
        "preco": player["preco"],
        "capitao": player.get("capitao", False),
    }


print("=" * 70)
print("ANÁLISE DA ESCALAÇÃO — CARTOLA COPA RODADA 3")
print("=" * 70)

print("\n📋 TITULARES (4-3-3)")
print("-" * 70)
rows = []
for p in TITULARES:
    r = analyze_player(p)
    cap = " ⭐ CAPITÃO" if r["capitao"] else ""
    print(
        f"  {r['posicao']:10s} | {r['jogador']:15s} | {r['selecao']:15s} (#{r['fifa_rank']}) "
        f"vs {r['adversario']:15s} (#{r['adv_rank']}) {r['diff_rank']}"
    )
    print(
        f"             {'':15s} | Média: {r['media']:5.1f} | Gols: {r['gols']} | "
        f"Assists: {r['assists']} | Total: {r['pts_total']:5.1f}{cap}"
    )
    rows.append(r)

print(f"\n📋 TÉCNICO")
print("-" * 70)
t = analyze_player(TECNICO)
print(f"  {'Técnico':10s} | {t['jogador']:15s} | {t['selecao']:15s} (#{t['fifa_rank']}) vs {t['adversario']:15s} (#{t['adv_rank']}) {t['diff_rank']}")

print(f"\n📋 BANCO")
print("-" * 70)
for p in BANCO:
    r = analyze_player(p)
    print(
        f"  {r['posicao']:10s} | {r['jogador']:15s} | {r['selecao']:15s} (#{r['fifa_rank']}) "
        f"vs {r['adversario']:15s} (#{r['adv_rank']}) {r['diff_rank']}"
    )
    print(
        f"             {'':15s} | Média: {r['media']:5.1f} | Gols: {r['gols']} | "
        f"Assists: {r['assists']} | Total: {r['pts_total']:5.1f}"
    )
    rows.append(r)

# Resumo
df_esc = pd.DataFrame(rows)
selecoes_usadas = set(df_esc["selecao"])
print(f"\n{'=' * 70}")
print("RESUMO")
print(f"{'=' * 70}")
print(f"  Seleções: {', '.join(sorted(selecoes_usadas))} ({len(selecoes_usadas)} diferentes)")
print(f"  Custo total titulares: C$ {sum(p['preco'] for p in TITULARES):.2f}")
print(f"  Custo total banco: C$ {sum(p['preco'] for p in BANCO):.2f}")
print(f"  Custo técnico: C$ {TECNICO['preco']:.2f}")
print(f"  Custo total: C$ {sum(p['preco'] for p in TITULARES) + sum(p['preco'] for p in BANCO) + TECNICO['preco']:.2f}")
print(f"  Capitão: {[p['apelido'] for p in TITULARES if p.get('capitao')][0]} (pontua em dobro)")

# Análise de risco
print(f"\n{'=' * 70}")
print("ANÁLISE DE RISCO POR CONFRONTO")
print(f"{'=' * 70}")
confrontos = {}
for p in TITULARES:
    adv = get_adversario(p["selecao"], partidas)
    key = f"{p['selecao']} vs {adv}"
    if key not in confrontos:
        tr = get_fifa_rank(p["selecao"])
        ar = get_fifa_rank(adv)
        confrontos[key] = {"jogadores": [], "team_rank": tr, "adv_rank": ar}
    confrontos[key]["jogadores"].append(p["apelido"])

for conf, info in sorted(confrontos.items(), key=lambda x: len(x[1]["jogadores"]), reverse=True):
    n = len(info["jogadores"])
    tr, ar = info["team_rank"], info["adv_rank"]
    try:
        diff = int(ar) - int(tr)
        risk = "BAIXO ✅" if diff > 20 else "MÉDIO ⚠️" if diff > 0 else "ALTO 🔴"
    except (ValueError, TypeError):
        risk = "?"
    print(f"\n  {conf} (#{tr} vs #{ar}) — Risco: {risk}")
    print(f"    Jogadores: {', '.join(info['jogadores'])} ({n})")
    if n >= 3:
        print(f"    ⚠️  {n} jogadores no mesmo jogo — alta concentração")
