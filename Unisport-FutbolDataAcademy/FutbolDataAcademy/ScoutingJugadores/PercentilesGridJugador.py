import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import LanusStats as ls
from scipy import stats
from mplsoccer import FontManager

# 'ls.Fbref()' es una herramienta de Python que se conecta a la web FBref.com
# haciendo esto podremos pedirle datos específicos de equipos, jugadores o partidos más adelante.

fbref = ls.Fbref()

# Le pedimos a FBREF que nos diga qué datos de qué temporadas están disponibles para "La Liga"
# puedes cambiar 'La Liga' por otra competición de FBREF, pero con el nombre correcto que aparece en la web
# puedes consultar el nombre correcto de la competición aquí: https://fbref.com/en/comps/

ls.get_available_season_for_leagues('Fbref', 'La Liga')

df = fbref.get_all_player_season_stats("La Liga", "2024-2025")

# FBref nos devuelve varias tablas. Aquí estamos seleccionando la primera (índice 0)
# el 0 es donde están los datos principales de los jugadores.

df_players = df[0]

# Vemos los nombres de todas las columnas (estadísticas) que tiene la tabla de jugadores
# esto nos ayuda a saber qué datos podemos usar.

list(df_players.columns)

# de esta manera es como comprobamos que la lista de jugadores es la adecuada
# jugadores de la liga en la temporada 24/25
# el número 20 lo utilizamos para ver los 20 primeros jugadores que hay en la lista (va en orden alfabético)

df_players.head(20)

# Mostramos la lista completa de columnas del DataFrame
# así vemos qué estadísticas de los jugadores tenemos disponibles para escoger en el análisis

print(df_players.columns.tolist())

# Elegimos una serie de estadísticas que son especialmente relevantes para evaluar a delanteros.
# Estas métricas incluyen aspectos de finalización, participación en ataque y generación de jugadas.
# 'stats_plot' contiene los nombres técnicos (columnas del DataFrame) que vamos a analizar.
# 'stats_labels' contiene cómo se mostrará -qué nombre veremos- cada métrica en los gráficos.
# eres libre de cambiar a las que quieras siempre que uses los nombres de la celda anterior

stats_plot = {
    "Delanteros": [
        "shooting_Sh/90",        # Tiros por 90'
        "shooting_SoT/90",       # Tiros al arco por 90'
        "shooting_G/Sh",         # Goles por tiro
        "shooting_G/SoT",        # Goles por tiro al arco
        "shooting_SoT%",         # % de tiros que van al arco
        "passing_KP",            # Pases clave
        "passing_xA",            # Expected Assists (xA)
        "gca_SCA90",             # Acciones que terminan en tiro
        "gca_GCA90"              # Acciones que terminan en gol
    ]
}

stats_labels = {
    "Delanteros": [
        "Tiros por 90'",
        "Tiros al arco por 90'",
        "Goles por tiro",
        "Goles por tiro al arco",
        "% de tiros al arco",
        "Pases clave (Key Passes)",
        "Expected Assists (xA)",
        "Acciones que terminan en tiro (SCA/90)",
        "Acciones que terminan en gol (GCA/90)"
    ]
}

# Este código convierte la columna "stats_90s" (minutos jugados divididos por 90) a valores numéricos
# es importante para eliminar a aquellos jugadores que han participado poco en el filtro de la próxima celda

df_players['stats_90s'].astype(float).sort_values()

# ▸ Parámetros del jugador (cambia 'Javi Puado' por el que te interese)
jugador = 'Javi Puado'

# aquí estamos creando un filtro: sólo deben tenerse en cuenta jugadores con más de 4 partidos (puedes cambiarlo)

df_filt = df_players[df_players['stats_90s'].astype(float) > 4]
player = df_filt[df_filt['Player'] == jugador]

# mensaje que nos dará el gráfico si ese jugador no está dentro del filtro
if player.empty:
    raise ValueError(f"El jugador {jugador} no fue encontrado en el DataFrame.")

# Obtenemos el equipo y la edad del jugador seleccionado:

equipo = player['stats_Squad'].values[0]
edad = int(player['stats_Age'].str.split('-').values[0][0])

# Preparación del gráfico en cuanto a tamaño

fig, axes = plt.subplots(3, 3, figsize=(25, 10))
plt.subplots_adjust(hspace=0.4, wspace=0.3)
col = 'blue' #aquí puedes cambiar el color por el que quieras

# Convertimos la columna correspondiente a valores numéricos y eliminamos valores vacíos (NaN).

for i, ax in zip(range(len(stats_plot["Delanteros"])), axes.reshape(-1)):
    stat = df_filt[stats_plot["Delanteros"][i]].astype(float).dropna()
    stat.name = None

    try:
        player_value = float(player[stats_plot["Delanteros"][i]].values[0])
        percentile = stats.percentileofscore(stat, player_value)
    except:
        player_value = None
        percentile = None

    sns.kdeplot(stat, ax=ax, color=col, fill=True, legend=False)

    if player_value is not None:
        ax.axvline(player_value, color='black', linewidth=2)
        ax.text(player_value, ax.get_ylim()[1]*0.9, f'{player_value:.2f}',
                color='black', ha='center', va='top', fontsize=10)

        xmin, xmax = ax.get_xlim()
        if player_value < xmin or player_value > xmax:
            ax.set_xlim(min(xmin, player_value - 1), max(xmax, player_value + 1))

    titulo = f"{stats_labels['Delanteros'][i]}"
    if percentile is not None:
        titulo += f"\nPercentil {int(percentile)}"
    ax.set_title(titulo, fontsize=14)

    ax.set(xlabel=None)
    ax.set(ylabel=None)
    ax.set(yticks=[])

# Esto agrega el título al gráfico (jugador + edad + equipo)

fig.text(0.01, 1.03, f'{jugador} ({edad}) - {equipo}',
         fontsize=26, fontweight='bold', ha='left', va='top')

# ▸ SUBTÍTULO A LA DERECHA
fig.text(0.99, 1.03,
         'Distribución de métricas ofensivas comparadas con el resto de jugadores',
         fontsize=16, ha='right', va='top')

# ▸ Layout con margen superior
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(f'{jugador.replace(" ", "_")}_perfil_ofensivo.png', dpi=300, bbox_inches='tight')
plt.show()
