import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
ruta_csv = os.path.join(BASE, "beeswarmTutorial.csv")
df = pd.read_csv(ruta_csv)

text_color = 'white'
background = '#313332'
df['per90'] = df['Prog']/df['90s']
df = df[(df['90s'] >= 6.5) & (df['Pos'] != 'GK')].reset_index()
print(df.describe())
df = df.sort_values(by='per90', ascending=False)


fig, ax = plt.subplots(figsize=(10,5))
fig.set_facecolor(background)
ax.patch.set_facecolor(background)

# configuracion de los jugadores y colores que van a aparecer

ax.tick_params(colors='white')

ax.grid(ls= 'dotted', lw= 5, color= 'lightgrey', axis= 'y', zorder= 1)
spines = ['top', 'bottom', 'left', 'right']

for x in spines:
        ax.spines[x].set_visible(False)

sns.swarmplot(x='per90', data=df, color='white', zorder=1)
#plot de Thiago Alcantara

plt.scatter(x=9.87, y=0, c='red', edgecolors='white', s=200, zorder=2)
plt.text(s='Thiago', x=9.87, y=-.04, c= text_color)

plt.title('Pases progresivos de Thiago en la Premier League', c=text_color, fontsize=14)
plt.xlabel('Pases progresivos por 90', c=text_color)

plt.show()
