import numpy as np
import pandas as pd
from statsbombpy import sb
from mplsoccer import VerticalPitch

#eventos ya devuelve un dataFrame
eventos = sb.events(match_id=3923881)

#df es un dataFrame filtrado que muestra solo los tiros
df = eventos[eventos['type'] == 'Shot']
print(df.head())

campo = VerticalPitch(
    half = True, 
    pitch_type = 'statsbomb',
    pitch_color = 'white',
    line_color = 'black')

#Dibuja el campo real (medio campo en vertical) usando Matplotlib.
#fig → la figura de Matplotlib (el lienzo completo)
#ax → los ejes donde está el campo (donde pintarás los eventos)
#figsize=(10, 8)? Define el tamaño del gráfico en pulgadas:
fig, ax = campo.draw(figsize=(10, 8))
sc = campo.scatter(df["start_location_x"], df["start_location_y"], ax=ax)

