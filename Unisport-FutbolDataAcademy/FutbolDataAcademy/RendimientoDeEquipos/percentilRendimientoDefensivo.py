# importamos las librerías que nos van a permitir que aparezca el gráfico de manera adecuada

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import LanusStats as ls
from io import StringIO
from mplsoccer import PyPizza

import warnings
warnings.filterwarnings("ignore")

# Accedemos a FBREF para buscar la competición y los datos que nos interesan:
# entra en https://fbref.com/en/ haz clic en competiciones en el menú, y selecciona la que quieras.
# cambia el enlace siguiente por el de la que hayas elegido

fbref = ls.Fbref()
html = fbref.fbref_request('/en/comps/9/Premier-League-Stats')
df = pd.read_html(StringIO(html))[16]

# el número final entre corchetes, en este caso 16, se sustituye por el número de tabla que nos interesa

# aplanamos el MultiIndex de columnas quedándonos solo con el nivel inferior
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[-1] for col in df.columns]

# Eliminar columnas que puedan estar duplicadas por nombre
df = df.loc[:, ~df.columns.duplicated()]

# vemos de manera ordenada todos los datos que tiene la tabla que vamos a utilizar
print(df.columns.tolist())

# Seleccionamos las métricas que vamos a utilizar. En este caso son defensivas para ver el rendimiento DEF del equipo
# cambia éstas por las que te interesen a ti.
metrics = ['Tkl', 'TklW', 'Blocks', 'Int', 'Clr', 'Err']

# Aquí es cómo se verán las etiquetas en el gráfico
# las traducimos y ponemos al completo para una mejor comprensión del gráfico
metrics_display = ['Entradas totales', 'Entradas ganadas', 'Bloqueos -tiros/pases', 'Interceptaciones', 'Despejes', 'Errores']

# Métricas donde un valor más bajo es mejor (se invierte el percentil)
invertir = ['Err']

# Hacemos una limpieza de datos: quitamos posibles valores nulos y normalizamos por 90 minutos
df = df.copy()
df[metrics] = df[metrics].apply(pd.to_numeric, errors='coerce')
df['90s'] = pd.to_numeric(df['90s'], errors='coerce')
df = df.dropna(subset=metrics + ['90s'])
df[metrics] = df[metrics].div(df['90s'], axis=0)

# Para el ejemplo utilizamos al Everton. Puedes cambiarlo por el que quieras
equipo = 'Everton'
values = df[df['Squad'] == equipo][metrics].values[0]

# Pedimos a Python que nos calcule el percentil de cada métrica para el equipo elegido.
percentiles = []
for col in metrics:
    rank = df[col].rank(pct=True) * 100
    val = df[df['Squad'] == equipo][col].values[0]
    perc = rank[df[col] == val].values[0]
    if col in invertir:
        perc = 100 - perc
    percentiles.append(perc)

# Es importante no tocar nada de lo que aparece a continuación, porque es el código completo para que aparezca el radar
baker = PyPizza(
    params=metrics_display,
    background_color="#FFFFFF",
    straight_line_color="#000000",
    straight_line_lw=1,
    last_circle_lw=1,
    other_circle_lw=0,
)

fig, ax = baker.make_pizza(
    percentiles,
    figsize=(8, 8),
    param_location=110,
    kwargs_slices=dict(
        facecolor="#6CABDD", edgecolor="#000000",
        zorder=2, linewidth=1
    ),
    kwargs_params=dict(
        color="#000000", fontsize=13, va="center"
    ),
    kwargs_values=dict(
        color="#000000", fontsize=11, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="#FFF05D",
            boxstyle="round,pad=0.1", lw=1
        )
    )
)

# Podemos cambiar el título "Percentil Acciones defensivas" por el que quieras según tus datos trabajados
fig.text(
    0.5, 0.99, f"{equipo} – Percentil Acciones defensivas", size=18,
    ha="center", va="top", color="#000000"
)

# Créditos
fig.text(
    0.99, 0.01,
    "Fuente: FBref | Inspirado en @fdata_academy",
    size=9, color="#000000", ha="right"
)

plt.savefig(f'{equipo}_percentil_defensivo.png', dpi=150, bbox_inches='tight')
plt.show()
