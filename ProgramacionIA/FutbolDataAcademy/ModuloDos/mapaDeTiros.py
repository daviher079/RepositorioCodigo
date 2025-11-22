import numpy as np
import pandas as pd
from statsbombpy import sb
from mplsoccer import VerticalPitch
import matplotlib.pyplot as plt 

#eventos ya devuelve un dataFrame
eventos = sb.events(match_id=3923881)

#df es un dataFrame filtrado que muestra solo los tiros
df = eventos[eventos['type'] == 'Shot']

campo = VerticalPitch(
    half = True, 
    pitch_type = 'statsbomb',
    pitch_color = 'white',
    line_color = 'black')

#Dibuja el campo real (medio campo en vertical) usando Matplotlib.
#fig → la figura de Matplotlib (el lienzo completo)
#ax → los ejes donde está el campo (donde pintarás los eventos)
#figsize=(10, 8) Define el tamaño del gráfico en pulgadas:
fig, ax = campo.draw(figsize=(10, 8))
df["x"] = df["location"].str[0]
df["y"] = df["location"].str[1]
#sc = campo.scatter(df["x"], df["y"], 
#                   s = df["shot_statsbomb_xg"]*500+100
#                   ,ax=ax)

nig_color = "#46F415"
df_nigeria = df[df["team"] == "Nigeria"]
df_nigeria["x"] = df_nigeria["location"].str[0]
df_nigeria["y"] = df_nigeria["location"].str[1]
sc = campo.scatter(df_nigeria["x"], df_nigeria["y"] , 
                   s = df_nigeria["shot_statsbomb_xg"]*500+100,
                   c = nig_color,
                   ax = ax,
                   label="Nig")

plt.legend()
plt.show()    
