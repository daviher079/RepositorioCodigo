import matplotlib.pyplot as plt
from mplsoccer import Pitch, Sbopen
import pandas as pd
import seaborn as sns


parser = Sbopen()
df_match = parser.match(competition_id=55, season_id=43)

team = "Spain"

#lista de partidos de la selección durante el torneo
match_ids = df_match.loc[(df_match["home_team_name"] == team) | (df_match["away_team_name"] == team)]["match_id"].to_list()
no_games = len(match_ids)

danger_passes = pd.DataFrame()
for idx in match_ids:
    #abrimos los datos del evento de pases
    df = parser.event(idx)[0]
    for period in [1, 2]:
        # dentro del bucle por partido y period
        mask_pass = (
            (df.team_name == team) &
            (df.type_name == "Pass") &
            (df.outcome_name.isnull()) &
            (df.period == period) &
            (df.sub_type_name.isnull())
        )
        passes = df.loc[mask_pass, ["x", "y", "end_y", "end_x", "minute", "second", "player_name"]]

        # seleccionar tiros del equipo en ese periodo (type_name == "Shot")
        mask_shot = (df.team_name == team) & (df.type_name == "Shot") & (df.period == period)
        shots = df.loc[mask_shot, ["minute", "second"]]

        # si no hubo tiros en ese periodo, saltamos (evita errores con Series vacías)
        if shots.empty:
            continue

        # convertir minutos+segundos a segundos (Series)
        shot_times = shots["minute"] * 60 + shots["second"]
        shot_window = 15
        shot_start = shot_times - shot_window

        # evitar valores negativos: si start < 0, poner inicio en el comienzo del periodo
        # (period-1)*45*60 si quieres en segundos; si usas minutos en minuto-base, aquí usaremos segundos:
        period_start_seconds = (period - 1) * 45 * 60
        shot_start = shot_start.apply(lambda s: s if s > period_start_seconds else period_start_seconds)

        # convertir a segundos los tiempos de los pases
        pass_times = passes["minute"] * 60 + passes["second"]

        # Para cada pase, comprobamos si existe algún tiro tal que shot_start_i < pass_time < shot_time_i
        # Resultado: Series booleana de la misma longitud que pass_times
        pass_to_shot = pass_times.apply(lambda x: ((shot_start < x) & (x < shot_times)).any())

        # quedarnos solo con los pases "peligrosos" de este periodo
        danger_passes_period = passes.loc[pass_to_shot]

        # concatenar con el DataFrame global
        danger_passes = pd.concat([danger_passes, danger_passes_period], ignore_index=True)

pitch = Pitch(
    pitch_type='statsbomb',
    pitch_color='#3f3f3f',
    line_color='white',
    linewidth=1.5
)

fig, ax = pitch.grid(
    figheight=10,
    axis=False
)
scale = 0.85

# 1. Escalar el centro del campo
cx, cy = 60, 40  # centro StatsBomb


danger_passes = danger_passes[danger_passes["x"] > 60]

pitch.kdeplot(
    danger_passes.x,
    danger_passes.y,
    ax=ax['pitch'],
    fill=True,
    cmap='turbo',
    bw_adjust=1.1,
    thresh=0.1,
    alpha=0.9,
    levels=150,
    linewidths=0
)
pitch.draw(ax=ax['pitch'])

plt.show()