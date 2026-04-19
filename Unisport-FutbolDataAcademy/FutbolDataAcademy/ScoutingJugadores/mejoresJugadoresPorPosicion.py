import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import LanusStats as ls
from scipy import stats
from mplsoccer import FontManager

# Definimos la lista con las 5 principales ligas europeas de cuyos jugadores queremos analizar.
# también indicamos la temporada de la que queremos obtener los datos

ligas = ["La Liga", "Premier League", "Serie A", "Bundesliga", "Ligue 1"]
temporada = "2024-2025"

# 'ls.Fbref()' es una herramienta de Python que se conecta a la web FBref.com
# haciendo esto podremos pedirle datos específicos de los jugadores

fbref = ls.Fbref()


# este código nos va a permitir descargar todos los datos de los jugadores para luego compararlos
# puede tardar rato en cargar

df_total = []

for liga in ligas:
    print(f"Descargando datos de {liga}...")
    df = fbref.get_all_player_season_stats(liga, temporada)
    df_total.append(df[0])  # solo la tabla principal

df_players = pd.concat(df_total, ignore_index=True)

# Mostramos la lista completa de columnas del DataFrame 
# así vemos qué estadísticas de los jugadores tenemos disponibles para escoger en el análisis comparativo

print(df_players.columns.tolist())

# -------------------------------
# 1. FILTRADO DE DATOS
# -------------------------------

# Jugadores con más de 4 partidos (~360 min)
df_filt = df_players[df_players['stats_90s'].astype(float) > 4].copy()

# Solo centrocampistas
df_filt = df_filt[df_filt["stats_Pos"].str.contains("MF", na=False)]

# -------------------------------
# 2. MÉTRICAS A EVALUAR
# -------------------------------

# Métricas clave para pivote defensivo
raw_stats = [
    "defense_TklW",       # Entradas exitosas
    "defense_Int",        # Intercepciones
    "defense_Blocks",     # Bloqueos de tiros
    "defense_Pass",       # Bloqueos de pase
    "misc_Recov",         # Recuperaciones
    "possession_PrgC"     # Conducciones progresivas
]

# Esta línea se asegura de que cada dato se convierta en un número decimal
for col in raw_stats + ["stats_90s"]:
    df_filt[col] = pd.to_numeric(df_filt[col], errors="coerce")

# Calculamos métricas por 90 minutos, ya que no tendría sentido comparar jugadores si no fuese así
for col in raw_stats:
    df_filt[col + "_per90"] = df_filt[col] / df_filt["stats_90s"]

# Cambiamos el nombre de las columnas a los datos por 90 minutos
stats_cols = [col + "_per90" for col in raw_stats]

# Eliminamos filas con valores faltantes
df_stats = df_filt[["Player"] + stats_cols].dropna().reset_index(drop=True)

# -------------------------------
# 3. NORMALIZACIÓN RELATIVA [0-10]
# -------------------------------

# Lo que hacemos aquí es poner todas las métricas en la misma escala: notas de 0 a 10. 
# 0 será el pivote de las 5 ligas que menos datos tiene de algo; 10 será el que más tenga
# en base a ello, podemos asignar una nota a cada dato del jugador
# esta nota es la que nos dirá cuáles son los que mejor nota media tienen para aparecer entre los mejores pivotes

df_stats_scaled = df_stats.copy()

for col in stats_cols:
    min_val = df_stats_scaled[col].min()
    max_val = df_stats_scaled[col].max()
    df_stats_scaled[col + "_score"] = 10 * (df_stats_scaled[col] - min_val) / (max_val - min_val)

score_cols = [col + "_score" for col in stats_cols]

# -------------------------------
# 4. CÁLCULO DE SCORE FINAL
# -------------------------------

# No todas las estadísticas que hemos escogido tienen la misma importancia para nosotros o un director deportivo
# es por ello que con esta línea damos más peso (importancia), a unas que a otras.
# las puedes personalizar del 0.8 al 1: por ejemplo, 1 sería máxima prioridad; 0.9 menos importantes; 0.8 útiles

pesos = np.array([1.0, 1.0, 0.9, 0.9, 1.0, 0.8])  # mismo orden de "métricas clave"

# Matriz de puntuaciones normalizadas
X_relative = df_stats_scaled[score_cols].values

# Score final ponderado, reescalado sobre 10
df_stats_scaled["pivot_score_10"] = (X_relative * pesos).sum(axis=1) / pesos.sum()

# -------------------------------
# 5. RANKING FINAL
# -------------------------------

ranking_final = df_stats_scaled[["Player", "pivot_score_10"] + score_cols].sort_values("pivot_score_10", ascending=False)
ranking_final.reset_index(drop=True, inplace=True)

# Mostrar top 10 de jugadores con más nota basados en esos 6 datos comparado con los de las 5 competiciones
print(ranking_final.head(10))

# -------------------------------
# GRÁFICO FINAL: HEATMAP
# -------------------------------

# El heatmap permite ver de forma rápida y visual qué jugadores destacan más en cada métrica, 
# usamos colores que van de puntuación más baja (claro) a puntuación más alta (oscuro).

# importamos las librerías que nos permitirán ver el gráfico final
# Seleccionamos el top 10 de jugadores de la celda anterior
top10 = ranking_final.head(10).set_index("Player")

# Dejamos únicamente las puntuaciones, sin datos innecesarios
scores_mtx = top10[score_cols]

# Damos vida al gráfico añadiendo colores y tamaños

plt.figure(figsize=(12, 6))
sns.heatmap(scores_mtx, annot=True, cmap="YlGnBu", cbar=True, linewidths=0.5, fmt=".1f")
plt.title("Puntuaciones individuales (0-10) - Mejores pivotes defensivos", fontsize=14, weight="bold")
plt.ylabel("Jugador")
plt.xlabel("Métrica")
plt.tight_layout()
plt.show()