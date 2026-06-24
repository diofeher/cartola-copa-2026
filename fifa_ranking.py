import os
from os.path import join

import pandas as pd

DATA_DIR = join(os.path.dirname(__file__), "data")

# FIFA Men's World Ranking - June 11, 2026
# Source: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_seeding
# Teams with (*) are playoff winners — ranking from March 2026
RANKING = [
    (1, "Argentina", 1877.27),
    (2, "Espanha", 1874.71),
    (3, "França", 1870.70),
    (4, "Inglaterra", 1828.02),
    (5, "Portugal", 1767.85),
    (6, "Brasil", 1765.86),
    (7, "Marrocos", 1755.10),
    (8, "Holanda", 1753.57),
    (9, "Bélgica", 1742.24),
    (10, "Alemanha", 1735.77),
    (11, "Croácia", 1714.87),
    (13, "Colômbia", 1698.35),
    (14, "México", 1687.48),
    (15, "Senegal", 1684.07),
    (16, "Uruguai", 1673.07),
    (17, "Estados Unidos", 1671.23),
    (18, "Japão", 1661.58),
    (19, "Suíça", 1650.06),
    (20, "Irã", 1619.58),
    (22, "Coreia do Sul", 1600.0),
    (23, "Equador", 1595.0),
    (24, "Áustria", 1590.0),
    (26, "Austrália", 1575.0),
    (27, "Canadá", 1570.0),
    (29, "Noruega", 1555.0),
    (30, "Panamá", 1550.0),
    (34, "Egito", 1530.0),
    (35, "Argélia", 1525.0),
    (36, "Escócia", 1520.0),
    (39, "Paraguai", 1500.0),
    (40, "Tunísia", 1495.0),
    (42, "Costa do Marfim", 1480.0),
    (45, "Turquia", 1460.0),
    (48, "Iraque", 1440.0),
    (50, "Uzbequistão", 1430.0),
    (51, "Catar", 1425.0),
    (55, "Suécia", 1400.0),
    (60, "Arábia Saudita", 1370.0),
    (61, "África do Sul", 1365.0),
    (65, "República Tcheca", 1340.0),
    (66, "Jordânia", 1335.0),
    (68, "Cabo Verde", 1320.0),
    (70, "RD Congo", 1310.0),
    (72, "Gana", 1300.0),
    (75, "Bósnia", 1280.0),
    (82, "Curaçao", 1240.0),
    (84, "Haiti", 1225.0),
    (86, "Nova Zelândia", 1210.0),
]

df = pd.DataFrame(RANKING, columns=["fifa_ranking", "clube_nome", "fifa_points"])
file = join(DATA_DIR, "fifa_ranking.csv")
os.makedirs(DATA_DIR, exist_ok=True)
df.to_csv(file, index=False)
print(f"Saved {len(df)} teams -> {file}")
