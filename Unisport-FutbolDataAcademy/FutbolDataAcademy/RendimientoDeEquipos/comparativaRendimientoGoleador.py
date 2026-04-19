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
html = fbref.fbref_request('/en/comps/11/stats/Serie-A-Stats')
df = pd.read_html(StringIO(html))[0]

# el número final entre corchetes, en este caso 0, se sustituye por el número de tabla que nos interesa en ese enlace

# aplanamos el MultiIndex de columnas quedándonos solo con el nivel inferior
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[-1] for col in df.columns]

# Eliminar columnas que puedan estar duplicadas por nombre
df = df.loc[:, ~df.columns.duplicated()]

# vemos de manera ordenada todos los datos que tiene la tabla que vamos a utilizar
print(df.columns.tolist())

# Asegurarse de que las columnas estén en formato numérico
# Cambia Gls y xG por las estadísticas que necesites (ejemplo: Ast u xA para medir eficacia en asistencias)
df['Gls'] = pd.to_numeric(df['Gls'], errors='coerce')
df['xG'] = pd.to_numeric(df['xG'], errors='coerce')

# Calcular eficiencia goleadora: para saber si están rindiendo por encima o por debajo
# se restan los goles a los xG (si han marcado 20, con un xG de 25, estarán a -5)
df['Eficiencia Gls-xG'] = df['Gls'] - df['xG']

# Ordenar por eficiencia en el gráfico
df_sorted = df.sort_values(by='Eficiencia Gls-xG', ascending=False)

# Añadimos tamaño y colores al gráfico
fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(df_sorted['Squad'], df_sorted['Eficiencia Gls-xG'],
               color=['green' if x >= 0 else 'red' for x in df_sorted['Eficiencia Gls-xG']])

for bar, val in zip(bars, df_sorted['Eficiencia Gls-xG']):
    ax.text(bar.get_width() + 0.1 if val >= 0 else bar.get_width() - 0.3,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}", va='center', ha='left' if val >= 0 else 'right')

# Estética del gráfico: cambia los títulos (set_title y set_xlabel) a la estadística que hagas tú
ax.set_title('Eficiencia Goleadora (Goles - xG)', fontsize=14)
ax.set_xlabel('Goles reales - Goles esperados')
ax.invert_yaxis()
ax.grid(True, axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('eficiencia_goleadora_seriea.png', dpi=150, bbox_inches='tight')
plt.show()
