import json
import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba
from mplsoccer import Pitch


MATCH_FOLDER = os.path.join(os.path.dirname(__file__), 'Match')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def extract_data_from_dict(data):
    events_dict = data["matchCentreData"]["events"]
    teams_dict = {data["matchCentreData"]['home']['teamId']: data["matchCentreData"]['home']['name'],
                  data["matchCentreData"]['away']['teamId']: data["matchCentreData"]['away']['name']}
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])
    return events_dict, players_df, teams_dict


def get_passes_df(events_dict):
    df = pd.DataFrame(events_dict)
    df['eventType'] = df.apply(lambda row: row['type']['displayName'], axis=1)
    df['outcomeType'] = df.apply(lambda row: row['outcomeType']['displayName'], axis=1)
    df["receiver"] = df["playerId"].shift(-1)
    passes_ids = df.index[df['eventType'] == 'Pass']
    df_passes = df.loc[passes_ids, ["id", "x", "y", "endX", "endY", "teamId", "playerId", "receiver", "eventType", "outcomeType"]]
    return df_passes


def get_passes_between_df(team_id, passes_df, players_df, events_dict):
    passes_df = passes_df[passes_df["teamId"] == team_id].copy()
    df = pd.DataFrame(events_dict)
    dfteam = df[df['teamId'] == team_id]

    passes_df = passes_df.merge(players_df[["playerId", "isFirstEleven"]], on='playerId', how='left')

    average_locs_and_count_df = dfteam.groupby('playerId').agg({'x': ['median'], 'y': ['median', 'count']})
    average_locs_and_count_df.columns = ['pass_avg_x', 'pass_avg_y', 'count']
    average_locs_and_count_df = average_locs_and_count_df.merge(
        players_df[['playerId', 'name', 'shirtNo', 'position', 'isFirstEleven']],
        on='playerId', how='left'
    )
    average_locs_and_count_df = average_locs_and_count_df.set_index('playerId')

    passes_player_ids_df = passes_df.loc[:, ['id', 'playerId', 'receiver', 'teamId']]
    passes_player_ids_df['pos_max'] = passes_player_ids_df[['playerId', 'receiver']].max(axis='columns')
    passes_player_ids_df['pos_min'] = passes_player_ids_df[['playerId', 'receiver']].min(axis='columns')

    passes_between_df = passes_player_ids_df.groupby(['pos_min', 'pos_max']).id.count().reset_index()
    passes_between_df.rename({'id': 'pass_count'}, axis='columns', inplace=True)

    passes_between_df = passes_between_df.merge(average_locs_and_count_df, left_on='pos_min', right_index=True)
    passes_between_df = passes_between_df.merge(average_locs_and_count_df, left_on='pos_max', right_index=True, suffixes=['', '_end'])

    return passes_between_df, average_locs_and_count_df


def pass_network_visualization(ax, passes_between_df, average_locs_and_count_df, col, team_id, home_team_id, away_team_id, path_eff):
    MAX_LINE_WIDTH = 15
    passes_between_df['width'] = passes_between_df.pass_count / passes_between_df.pass_count.max() * MAX_LINE_WIDTH

    MIN_TRANSPARENCY = 0.05
    MAX_TRANSPARENCY = 0.85
    color = np.array(to_rgba(col))
    color = np.tile(color, (len(passes_between_df), 1))
    c_transparency = passes_between_df.pass_count / passes_between_df.pass_count.max()
    c_transparency = (c_transparency * (MAX_TRANSPARENCY - MIN_TRANSPARENCY)) + MIN_TRANSPARENCY
    color[:, 3] = c_transparency

    pitch = Pitch(pitch_type='opta', goal_type='box', goal_alpha=.5, corner_arcs=True,
                  pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)

    pitch.lines(passes_between_df.pass_avg_x, passes_between_df.pass_avg_y,
                passes_between_df.pass_avg_x_end, passes_between_df.pass_avg_y_end,
                lw=passes_between_df.width, color=color, zorder=1, ax=ax)

    for index, row in average_locs_and_count_df.iterrows():
        if row['isFirstEleven'] == True:
            pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='o',
                         color=bg_color, edgecolor=line_color, linewidth=2, alpha=1, ax=ax)
        else:
            pitch.scatter(row['pass_avg_x'], row['pass_avg_y'], s=1000, marker='s',
                         color=bg_color, edgecolor=line_color, linewidth=2, alpha=0.75, ax=ax)

    for index, row in average_locs_and_count_df.iterrows():
        pitch.annotate(row["shirtNo"], xy=(row.pass_avg_x, row.pass_avg_y),
                      c=col, ha='center', va='center', size=18, ax=ax)

    avgph = average_locs_and_count_df['pass_avg_x'].median()
    avgph_show = round(avgph * 1.05, 2)
    ax.axvline(x=avgph, color='gray', linestyle='--', alpha=0.75, linewidth=2)

    if team_id == away_team_id:
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.text(avgph + 1, 105, f"{avgph_show}m", fontsize=15, color=line_color, ha='right')
    else:
        ax.text(avgph + 1, -5, f"{avgph_show}m", fontsize=15, color=line_color, ha='left')

    if team_id == home_team_id:
        ax.text(2, 98, "círculos = titulares\ncuadrado = suplente", color=hcol, size=12, ha='left', va='top')
        ax.text(-2, -5, "Dirección ataque --->", color=hcol, size=15, ha='left', va='center')
        ax.set_title("Red de pases - Equipo local", color=line_color, size=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(2, 2, "círculos = titulares\ncuadrado = suplente", color=acol, size=12, ha='right', va='top')
        ax.text(-2, 105, "<--- Dirección ataque", color=acol, size=15, ha='right', va='center')
        ax.set_title("Red de pases - Equipo visitante", color=line_color, size=30, fontweight='bold', path_effects=path_eff)

    return pitch


if __name__ == "__main__":
    # CAMBIA ESTE NOMBRE POR EL ARCHIVO GENERADO CON scraping_data.py
    match_json_path = os.path.join(MATCH_FOLDER, 'Real_Madrid_vs_Bayern_2026-04-07.json')

    with open(match_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events_dict, players_df, teams_dict = extract_data_from_dict(data)
    passes_df = get_passes_df(events_dict)

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    home_team_id = list(teams_dict.keys())[0]
    away_team_id = list(teams_dict.keys())[1]

    home_passes_between_df, home_average_locs_df = get_passes_between_df(home_team_id, passes_df, players_df, events_dict)
    away_passes_between_df, away_average_locs_df = get_passes_between_df(away_team_id, passes_df, players_df, events_dict)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    pass_network_visualization(axes[0], home_passes_between_df, home_average_locs_df,
                               hcol, home_team_id, home_team_id, away_team_id, path_eff)
    pass_network_visualization(axes[1], away_passes_between_df, away_average_locs_df,
                               acol, away_team_id, home_team_id, away_team_id, path_eff)

    plt.tight_layout()

    output_img = match_json_path.replace('.json', '_pass_network.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
