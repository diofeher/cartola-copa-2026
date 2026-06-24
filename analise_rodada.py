"""
Análise da melhor escalação para rodada atual da Copa 2026.
Considera: FIFA ranking, desempenho nas rodadas anteriores e adversário.
"""

import os
from os.path import join

import pandas as pd

DATA_DIR = join(os.path.dirname(__file__), "data")


def load_data():
    ranking = pd.read_csv(join(DATA_DIR, "fifa_ranking.csv"))
    partidas = pd.read_csv(join(DATA_DIR, "partidas.csv"))

    pontuados_files = sorted(
        [f for f in os.listdir(DATA_DIR) if f.startswith("pontuados-rodada-")]
    )
    dfs = [pd.read_csv(join(DATA_DIR, f)) for f in pontuados_files]
    pontuados = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    return ranking, partidas, pontuados


def team_performance(pontuados):
    em_campo = pontuados[pontuados["entrou_em_campo"] == True]
    return (
        em_campo.groupby("clube_nome")
        .agg(
            pontuacao_total=("pontuacao", "sum"),
            media_pontuacao=("pontuacao", "mean"),
            jogadores_usados=("atleta_id", "nunique"),
            gols=("G", "sum"),
        )
        .round(2)
    )


def match_results(partidas):
    played = partidas.dropna(subset=["gols_mandante", "gols_visitante"]).copy()
    played["gols_mandante"] = played["gols_mandante"].astype(int)
    played["gols_visitante"] = played["gols_visitante"].astype(int)

    rows = []
    for _, m in played.iterrows():
        gm, gv = m["gols_mandante"], m["gols_visitante"]

        if gm > gv:
            rm, rv = "V", "D"
        elif gm < gv:
            rm, rv = "D", "V"
        else:
            rm, rv = "E", "E"

        rows.append({"clube_nome": m["mandante"], "gols_pro": gm, "gols_contra": gv, "resultado": rm})
        rows.append({"clube_nome": m["visitante"], "gols_pro": gv, "gols_contra": gm, "resultado": rv})

    df = pd.DataFrame(rows)
    stats = (
        df.groupby("clube_nome")
        .agg(
            jogos=("resultado", "count"),
            vitorias=("resultado", lambda x: (x == "V").sum()),
            empates=("resultado", lambda x: (x == "E").sum()),
            derrotas=("resultado", lambda x: (x == "D").sum()),
            gols_pro=("gols_pro", "sum"),
            gols_contra=("gols_contra", "sum"),
        )
    )
    stats["saldo"] = stats["gols_pro"] - stats["gols_contra"]
    stats["pontos_copa"] = stats["vitorias"] * 3 + stats["empates"]
    return stats


def next_round_matches(partidas):
    future = partidas[partidas["gols_mandante"].isna()].copy()
    if future.empty:
        return future
    next_rodada = future["rodada"].min()
    return future[future["rodada"] == next_rodada]


def score_teams(ranking, perf, results, next_matches):
    all_teams = set()
    for _, m in next_matches.iterrows():
        all_teams.add(m["mandante"])
        all_teams.add(m["visitante"])

    scores = []
    for team in sorted(all_teams):
        fifa_rank = ranking.loc[ranking["clube_nome"] == team, "fifa_ranking"]
        fifa_pts = ranking.loc[ranking["clube_nome"] == team, "fifa_points"]
        rank_val = fifa_rank.values[0] if len(fifa_rank) > 0 else 99
        pts_val = fifa_pts.values[0] if len(fifa_pts) > 0 else 1000

        # FIFA ranking score (higher points = better)
        rank_score = pts_val / 20

        # Cartola performance score
        cartola_media = 0
        if team in perf.index:
            cartola_media = perf.loc[team, "media_pontuacao"]

        # Match results score
        result_score = 0
        if team in results.index:
            r = results.loc[team]
            result_score = r["pontos_copa"] * 2 + r["saldo"]

        # Find opponent
        match = next_matches[
            (next_matches["mandante"] == team) | (next_matches["visitante"] == team)
        ].iloc[0]
        opponent = match["visitante"] if match["mandante"] == team else match["mandante"]

        opp_rank = ranking.loc[ranking["clube_nome"] == opponent, "fifa_ranking"]
        opp_rank_val = opp_rank.values[0] if len(opp_rank) > 0 else 99

        # Opponent weakness bonus (weaker opponent = higher bonus)
        opp_bonus = max(0, (opp_rank_val - rank_val)) * 0.3

        total = rank_score + cartola_media * 3 + result_score + opp_bonus
        scores.append({
            "clube_nome": team,
            "fifa_ranking": rank_val,
            "fifa_score": round(rank_score, 2),
            "cartola_media": cartola_media,
            "cartola_score": round(cartola_media * 3, 2),
            "resultado_score": round(result_score, 2),
            "adversario": opponent,
            "adversario_ranking": opp_rank_val,
            "bonus_adversario": round(opp_bonus, 2),
            "score_total": round(total, 2),
        })

    return pd.DataFrame(scores).sort_values("score_total", ascending=False)


def main():
    ranking, partidas, pontuados = load_data()
    perf = team_performance(pontuados)
    results = match_results(partidas)
    next_matches = next_round_matches(partidas)

    if next_matches.empty:
        print("Nenhuma partida futura encontrada.")
        return

    rodada = next_matches["rodada"].iloc[0]
    print(f"\n{'=' * 70}")
    print(f"ANÁLISE RODADA {rodada} - COPA DO MUNDO 2026")
    print(f"{'=' * 70}")

    print(f"\n{'=' * 70}")
    print("PARTIDAS DA RODADA")
    print(f"{'=' * 70}")
    for _, m in next_matches.iterrows():
        r1 = ranking.loc[ranking["clube_nome"] == m["mandante"], "fifa_ranking"]
        r2 = ranking.loc[ranking["clube_nome"] == m["visitante"], "fifa_ranking"]
        rk1 = f"#{r1.values[0]}" if len(r1) > 0 else "?"
        rk2 = f"#{r2.values[0]}" if len(r2) > 0 else "?"
        print(f"  {m['mandante']} ({rk1}) vs {m['visitante']} ({rk2}) | {m['data']}")

    scored = score_teams(ranking, perf, results, next_matches)

    print(f"\n{'=' * 70}")
    print("RANKING DE SELEÇÕES PARA ESCALAR (score composto)")
    print("Fatores: FIFA ranking + média Cartola + resultados Copa + adversário")
    print(f"{'=' * 70}\n")
    print(
        scored[
            [
                "clube_nome",
                "fifa_ranking",
                "cartola_media",
                "adversario",
                "adversario_ranking",
                "score_total",
            ]
        ].to_string(index=False)
    )

    print(f"\n{'=' * 70}")
    print("TOP 5 - MELHORES SELEÇÕES PARA ESCALAR")
    print(f"{'=' * 70}")
    for i, (_, row) in enumerate(scored.head(5).iterrows(), 1):
        print(f"\n  {i}. {row['clube_nome']} (FIFA #{row['fifa_ranking']})")
        print(f"     Adversário: {row['adversario']} (FIFA #{row['adversario_ranking']})")
        print(f"     Média Cartola: {row['cartola_media']}")
        print(f"     Score total: {row['score_total']}")


if __name__ == "__main__":
    main()
