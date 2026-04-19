# importamos las librerías que nos van a permitir que aparezca el gráfico de manera adecuada

import pandas as pd
import matplotlib.pyplot as plt
import LanusStats as ls
from io import StringIO

import warnings
warnings.filterwarnings("ignore")

# Accedemos a FBREF para buscar la competición y los datos que nos interesan:
# entra en https://fbref.com/en/ haz clic en competiciones en el menú, y selecciona la que quieras.
# cambia el enlace siguiente por el de la que hayas elegido

fbref = ls.Fbref()
html = fbref.fbref_request('/en/comps/9/Premier-League-Stats')
df = pd.read_html(StringIO(html))[15]

# el número final entre corchetes, en este caso 8, se sustituye por el número de tabla que nos interesa
# en ese enlace, ve contando cada tabla que aparece. La primera es la 1, la segunda la 2, etc.

# aplanamos el MultiIndex de columnas quedándonos solo con el nivel inferior
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[-1] for col in df.columns]

# vemos de manera ordenada todos los datos que tiene la tabla

print(df.columns.tolist())

# añadimos en la línea horizontal del gráfico -x-, el valor de tiros por 90 minutos. 
# en la línea vertical -y-, añadimos el dato de tiros a puerta por 90 minutos.
# si quisieras otros datos, sólo tendrías que cambiar lo que aparece aquí como Sh/90 y SoT/90

x, promx = df['Sh/90'], df['Sh/90'].mean()
y, promy = df['SoT/90'], df['SoT/90'].mean()

# estética general: facecolor para color de fondo, y color_plot para que el texto y el gráfico sean negros

facecolor = 'white'
color_plot = 'black'

# con este código generamos el gráfico de dispersión

fig, ax = plt.subplots(figsize=(20, 12))
ax.scatter(x, y)

# Personalizamos los bordes para que todo salga correctamente

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(color_plot)
ax.spines['left'].set_color(color_plot)
for axis in ['top', 'bottom', 'left', 'right']:
    ax.spines[axis].set_linewidth(1.5)
ax.yaxis.set_tick_params(pad=12, colors=color_plot, labelsize=12)
ax.xaxis.set_tick_params(pad=12, colors=color_plot, labelsize=12)

fig.patch.set_facecolor(facecolor)
ax.set_facecolor(facecolor)
ax.grid(True, color=color_plot, linestyle='-', linewidth=0, alpha=0.5)
ax.grid(which='minor', color=color_plot, linestyle='-', linewidth=1.5, alpha=1)

# con este código añadimos las líneas de promedio:
# -la cruz del gráfico para saber dónde está la media de tiros vs tiros a puerta-

ax.axvline(promx, color=color_plot)
ax.axhline(promy, color=color_plot)

# Añadimos los títulos de cada línea del gráfico. Si haces otros datos, sólo tendrías que cambiar lo rojo
dato1 = 'Tiros por 90 minutos'
dato2 = 'Tiros a puerta por 90 minutos'

# este código sirve para agregar el nombre del equipo al lado de cada punto
for i in range(len(df)):
    ax.text(x.iloc[i], y.iloc[i], df['Squad'].iloc[i],
            fontsize=10, color=color_plot, ha='left', va='center')

# por último, añadimos esto para que aparezca el título
ax.set_xlabel(dato1, fontsize=18, color=color_plot)
ax.set_ylabel(dato2, fontsize=18, color=color_plot)
ax.set_title(f'{dato1} vs {dato2} - Premier League 2025',
             loc='left', color=color_plot, fontsize=25, fontweight="bold", pad=20)

plt.tight_layout()
plt.savefig('tiros_vs_tiros_a_puerta_premier.png', dpi=150, bbox_inches='tight')
plt.show()