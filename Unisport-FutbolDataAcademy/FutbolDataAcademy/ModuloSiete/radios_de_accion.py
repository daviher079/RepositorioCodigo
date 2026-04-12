import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch
from scipy import stats
from scipy.spatial import ConvexHull

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))

ruta_excel = os.path.join(BASE, "convextutorial.csv")

df = pd.read_csv(ruta_excel)
df = df.fillna(0)

# Convertimos los valores 'x' e 'y' que nos aparecía por ejemplo en el mapa de disparos del tema anterior
# estos son los valores del tamaño del terreno de juego, que hemos importado anteriormente en la librería

df['y'] = .8*df['y']
df['x'] = 1.2*df['x']

#filtramos por el equipo que queremos

df = df[df['teamId']==65].reset_index()
df['playerId'] = df['playerId'].astype(int) 

#Con este comando conseguimos que aparezcan los 11 titulares
players = df['playerId'].unique()
starters = players[0:11]
starters.sort()

pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')
fig, ax = pitch.draw(figsize =(16, 11), constrained_layout = True, tight_layout = False)
fig.set_facecolor('#22312b')
plt.gca().invert_yaxis()
# Invierte el eje Y para que las coordenadas del CSV casen con la orientación visual del campo.

#creamos un nuevo df, en el que filtraremos los datos de un jugador y sus pases
df1 = df[df['playerId']==21]
df1 = df1[df1['type/value']==1]

df1 = df1[(np.abs(stats.zscore(df1[['x','y']])) < 3)]
# Elimina los pases que son outliers estadísticos. Calcula el z-score de las coordenadas x e y: 
# si algún punto está a más de 3 desviaciones estándar de la media, se descarta. Sirve para limpiar 
# posiciones fuera del campo o errores del tracking.

#creamos las coordenadas exactas del terreno de juego

points = df1[['x', 'y']].values
hull = ConvexHull(df1[['x', 'y']])
pitch.scatter(df1.x, df1.y, ax=ax, color='white', s=20, zorder=3)


for i in hull.simplices:
    pitch.lines(points[i, 0], points[i, 1], points[i, 0], points[i, 1], ax=ax, color='white', lw=1.5)
    ax.fill(points[hull.vertices, 0], points[hull.vertices, 1], c='white', alpha=0.01)


plt.title('Radio de Acción - Jugador 21', color='white', size=16)
plt.show()
