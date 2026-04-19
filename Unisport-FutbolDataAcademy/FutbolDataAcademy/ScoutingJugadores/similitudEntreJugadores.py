import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import LanusStats as ls
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler

# 'ls.Fbref()' se conecta a FBref.com para pedir datos específicos de jugadores
fbref = ls.Fbref()

ligas = ["La Liga", "Premier League", "Serie A", "Bundesliga", "Ligue 1"]
temporada = "2024-2025"

df_total = []

for liga in ligas:
    print(f"Descargando datos de {liga}...")
    df = fbref.get_all_player_season_stats(liga, temporada)
    df_total.append(df[0])

df_players = pd.concat(df_total, ignore_index=True)

print(df_players.columns.tolist())

# -------------------------------
# 1. FILTRAR JUGADORES RELEVANTES
# -------------------------------
df_filt = df_players[df_players['stats_90s'].astype(float) > 8].copy()
print(df_filt)

# -------------------------------
# 2. SELECCIÓN DE ESTADÍSTICAS
# -------------------------------
stats_cols = [
    "stats_Gls",
    "stats_xG",
    "shooting_Sh",
    "shooting_SoT",
    "shooting_G/SoT",
    "stats_Ast",
    "stats_G+A",
    "stats_PrgC",
    "gca_SCA"
]

# -------------------------------
# 3. PREPARAR MATRIZ DE CARACTERÍSTICAS
# -------------------------------
df_stats = df_filt[["Player"] + stats_cols].dropna().reset_index(drop=True)
print(df_stats)

X = df_stats[stats_cols].astype(float)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# -------------------------------
# 4. JUGADOR DE REFERENCIA
# -------------------------------
jugador_ref = "Julián Álvarez"

if jugador_ref not in df_stats["Player"].values:
    raise ValueError(f"'{jugador_ref}' no está en el DataFrame filtrado.")

idx_ref = df_stats[df_stats["Player"] == jugador_ref].index[0]
ref_vector = X_scaled[idx_ref].reshape(1, -1)

# -------------------------------
# 5. CÁLCULO DE DISTANCIA EUCLIDIANA
# -------------------------------
distancias = cdist(ref_vector, X_scaled, metric='euclidean').flatten()

# -------------------------------
# 6. RESULTADOS
# -------------------------------
df_stats["distancia"] = distancias
df_resultado = df_stats.sort_values("distancia").reset_index(drop=True)

print(df_resultado[["Player"] + stats_cols + ["distancia"]].head(6))

# -------------------------------
# 7. VISUALIZACIÓN
# -------------------------------
df_resultado_filtrado = df_resultado[df_resultado["Player"] != jugador_ref].copy()
df_resultado_filtrado["similitud"] = 1 / (1 + df_resultado_filtrado["distancia"])

top_similares = df_resultado_filtrado[["Player", "similitud"]].head(5)
top_similares = top_similares.iloc[::-1]

plt.figure(figsize=(10, 6))
bars = plt.barh(top_similares["Player"], top_similares["similitud"], color='royalblue')
plt.xlabel("Similitud (0 a 1)")
plt.title(f"Jugadores más similares a {jugador_ref} 2024/25", fontsize=14, weight='bold')
plt.xlim(0, 1.05)

for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.01, bar.get_y() + bar.get_height() / 2, f'{width:.3f}', va='center')

plt.tight_layout()
plt.show()
