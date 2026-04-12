import os
import pandas as pd
import math
import numpy as np
from scipy import stats
from mplsoccer import PyPizza, add_image, FontManager
import matplotlib.pyplot as plt


BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))

ruta_csv = os.path.join(BASE, "pizza_tutorial.csv")

df = pd.read_csv(ruta_csv)

#corrección nombre jugadores
df['Player'] = df['Player'].str.split('\\', expand=True)[0]
df = df.loc[(df['Pos'] == 'DF') & (df['90s'] > 15)]

#creacion de la lista de parametros necesarios para el analisis
df = df.drop(['Rk', 'Nation', 'Pos', 'Squad', 'Age', 'Born'], axis=1).reset_index()

params = list(df.columns)[3:]
player = df.loc[df['Player'] == 'Trent Alexander-Arnold'].reset_index()
player = list(player.loc[0])[3:]

values = []
for x in range (len(params)):
    values.append(math.floor(stats.percentileofscore(df[params[x]], player[x])))

for n, i in enumerate(values):
    if i == 100:
        values[n] = 99

baker = PyPizza(
    params= params,
    straight_line_color= '#000000',
    straight_line_lw = 1,
    last_circle_lw = 1,
    other_circle_lw = 1,
    other_circle_ls = "-." 
)

fig, ax = baker.make_pizza(    
    values,              
    figsize=(8, 8),          
    param_location=110,      
    kwargs_slices=dict(        
        facecolor="#6CABDD", edgecolor="#000000",       
        zorder=2, linewidth=1    
    ),
    kwargs_params=dict(
        color="#000000", fontsize=12,
        va="center", alpha=.5    
    ),                       
    kwargs_values=dict(
        color="#000000", 
        fontsize=12,
        zorder=3,
        bbox=dict(
            edgecolor="#000000",
            facecolor="#6CABDD",
            boxstyle="round,pad=0.2", 
            lw=1
        )
    )
)

fig.text(    
    0.515, 
    0.97, 
    "Trent Alexander-Arnold - Liverpool", 
    size=18,
    ha="center", 
    color="#000000" 
) 

fig.text(    
    0.515, 
    0.942,    
    "Percentil en comparación al resto de defensores | 2020-21",    
    size=15,
    ha="center", 
    color="#000000") 
# añade créditos 

NOTES = 'jugadores con más de 15 partido con 90 minutos' 
CREDIT_1 = "datos: fbref"

fig.text(
    0.99, 
    0.005, 
    f"{NOTES}\n{CREDIT_1}", 
    size=9,
    color="#000000",
    ha="right"
) 

plt.show()