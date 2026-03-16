#Inicio con statsbomb

import pandas as pd
from mplsoccer import Sbopen

Sbopen().competition()

df_competitions = Sbopen().competition()

print(df_competitions)

#df_competitions.to_csv('Statsbomb_Competitions.csv', index=False)

df_matches = Sbopen().match(competition_id = 53, season_id = 315)


