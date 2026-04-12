import os
import pandas as pd
import matplotlib.pyplot as plt
from soccerplots.radar_chart import Radar

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)))
ruta_csv = os.path.join(BASE, "radars.csv")
df = pd.read_csv(ruta_csv)
df['Player'] = df['Player'].str.split('\\', expand=True)[0]

df = df[(df['Player']=='Tammy Abraham') | (df['Player']=='Harry Kane')].reset_index()

df = df.drop(['index', 'Rk', 'Nation', 'Pos', 'Squad', 'Age', 'Born', '90s', 'FK', 'PK', 'PKatt', 'Matches'], axis=1)

params = list(df.columns)[1:]

ranges = []
a_values = []
b_values = []

for x in params:
    a = min(df[params][x])
    a = a - (a*.25)

    b = max(df[params][x])
    b = b + (b*.25)

    ranges.append((a,b))

for x in range(len(df['Player'])):
    if df['Player'][x] == 'Tammy Abraham':
        a_values = df.iloc[x].values.tolist()
    if df['Player'][x] == 'Harry Kane':
        b_values = df.iloc[x].values.tolist()

a_values = a_values[1:]
b_values = b_values[1:]

values = [a_values, b_values]

title = dict(
    title_name = 'Tammy Abraham',
    title_color = 'blue',
    subtitle_name = 'Chelsea',
    subtitle_color = 'blue',
    title_name_2 = 'Harry Kane',
    title_color_2 = 'red',
    subtitle_name_2 = 'Bayern',
    subtitle_color_2 = 'red',
    title_fontsize = 18,
    subtitle_fontsize = 15
)

radar = Radar()

fig, ax = radar.plot_radar(ranges=ranges, params=params, values=values,
                           radar_color=['blue', 'red'],
                           alphas=[.75, .6], title=title, compare=True)

plt.show()