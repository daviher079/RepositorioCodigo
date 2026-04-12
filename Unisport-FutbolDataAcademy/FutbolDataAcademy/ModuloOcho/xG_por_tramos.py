import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))

ruta_csv = os.path.join(BASE, "xgtutorial-2.csv")

df = pd.read_csv(ruta_csv)

#Se comienza en cero para que los graficos comiencen en 0
a_xG = [0]
h_xG = [0]
a_min = [0]
h_min = [0]

#Identificar a los dos equipos
hteam = df['team'].iloc[0]
ateam =df['team'].iloc[-1]

for x in range (len(df['xG'])):
    if df['team'][x] == ateam:
        a_xG.append(df['xG'][x])
        a_min.append(df['minute'][x])
    if df['team'][x] == hteam:
        h_xG.append(df['xG'][x])
        h_min.append(df['minute'][x])

def nums_cumulative_sum(nums_list):
    return [sum(nums_list[:i+1]) for i in range(len(nums_list))]

a_cumulative = nums_cumulative_sum(a_xG)
h_cumulative = nums_cumulative_sum(h_xG)

alast = round(a_cumulative[-1],2)
hlast = round(h_cumulative[-1],2)


#Configurar el grafico con colores y tipos

fig, ax = plt.subplots(figsize = (10,5))
fig.set_facecolor('#3d4849')
ax.patch.set_facecolor('#3d4849')

#configuracion de la base
ax.tick_params(colors='white')

ax.grid(ls='dotted', lw=5, color='lightgrey', axis='y', zorder=1)
spines = ['top', 'bottom', 'left', 'right']

for x in spines:
        ax.spines[x].set_visible(False)

plt.xticks([0,15,30,45,60,75,90])
plt.xlabel('Minute', fontname = 'Andale Mono', color = 'white', fontsize = 16)
plt.ylabel('xG', fontname = 'Andale Mono', color = 'white', fontsize = 16)
ax.step(x = a_min, y = a_cumulative, color='#d3d3d3', label=ateam, linewidth=5, where='post')
ax.step(x = h_min, y = h_cumulative, color='#fd3607', label=hteam, linewidth=5, where='post')

plt.legend(facecolor='#3d4849', edgecolor='white', labelcolor='white', fontsize=12)
plt.show()
