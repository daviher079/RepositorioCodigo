import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
import os


BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Files")

ruta_excel = os.path.join(BASE, "messibetis5.csv")

df = pd.read_csv(ruta_excel)

df['x'] = df['x']*1.2
df['y'] = df['y']*.8
df['endX'] = df['endX']*1.2
df['endY'] = df['endY']*.8


fig, ax = plt.subplots(figsize=(13.5,8))
fig.set_facecolor('#22312b')
ax.patch.set_facecolor('#22312b')

pitch = Pitch(pitch_type='statsbomb', pitch_color='#22312b', line_color='#c7d5cc')

pitch.draw(ax=ax)
plt.gca().invert_yaxis()

kde = sns.kdeplot(
    x=df['x'],
    y=df['y'],
    fill=True,           # antes shade=True
    thresh=0,            # parecido a shade_lowest=False
    alpha=0.5,
    levels=10,           # antes n_levels
    cmap='magma',
    ax=ax                # MUY IMPORTANTE
)

for x in range(len(df['x'])):
    if df['outcome'][x] == 'Successful':
        plt.plot((df['x'][x],df['endX'][x]),(df['y'][x],df['endY'][x]), color='green')
        plt.scatter(df['x'][x],df['y'][x], color='green')
    if df['outcome'][x] == 'Unsuccessful':
        plt.plot((df['x'][x],df['endX'][x]),(df['y'][x],df['endY'][x]), color='red')
        plt.scatter(df['x'][x],df['y'][x], color='red')

plt.xlim(0,120)
plt.ylim(0,80)
plt.title('Messi Pass Map vs Real Betis', color='#22312b',size=20)
plt.show()