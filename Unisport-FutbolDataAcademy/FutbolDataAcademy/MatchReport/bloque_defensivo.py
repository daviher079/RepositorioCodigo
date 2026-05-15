import json
import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba, LinearSegmentedColormap
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


def get_defensive_action_df(events_dict):
    df = pd.DataFrame(events_dict)
    df['eventType'] = df.apply(lambda row: row['type']['displayName'], axis=1)
    df['outcomeType'] = df.apply(lambda row: row['outcomeType']['displayName'], axis=1)

    defensive_actions_ids = df.index[(df['eventType'] == 'Aerial') & (df['x'] <= 80) |
                                     (df['eventType'] == 'BallRecovery') |
                                     (df['eventType'] == 'BlockedPass') |
                                     (df['eventType'] == 'Challenge') |
                                     (df['eventType'] == 'Clearance') |
                                     (df['eventType'] == 'Error') |
                                     (df['eventType'] == 'Foul') |
                                     (df['eventType'] == 'Interception') |
                                     (df['eventType'] == 'Tackle')]
    df_defensive_actions = df.loc[defensive_actions_ids, ["id", "x", "y", "teamId", "playerId", "eventType", "outcomeType"]]

    return df_defensive_actions


def get_da_count_df(team_id, defensive_actions_df, players_df):
    defensive_actions_df = defensive_actions_df[defensive_actions_df["teamId"] == team_id].copy()
    defensive_actions_df = defensive_actions_df.merge(players_df[["playerId", "isFirstEleven"]], on='playerId', how='left')
    average_locs_and_count_df = (defensive_actions_df.groupby('playerId').agg({'x': ['median'], 'y': ['median', 'count']}))
    average_locs_and_count_df.columns = ['x', 'y', 'count']
    average_locs_and_count_df = average_locs_and_count_df.merge(players_df[['playerId', 'name', 'shirtNo', 'position', 'isFirstEleven']], on='playerId', how='left')
    average_locs_and_count_df = average_locs_and_count_df.set_index('playerId')

    return average_locs_and_count_df


def defensive_block(ax, average_locs_and_count_df, defensive_actions_df, team_id, home_team_id, away_team_id, col, path_eff):
    defensive_actions_team_df = defensive_actions_df[defensive_actions_df["teamId"] == team_id]

    pitch = Pitch(pitch_type='opta', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, line_zorder=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)
    ax.set_facecolor(bg_color)

    MAX_MARKER_SIZE = 3500
    average_locs_and_count_df['marker_size'] = (average_locs_and_count_df['count'] / average_locs_and_count_df['count'].max() * MAX_MARKER_SIZE)

    flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors", [bg_color, col], N=500)
    pitch.kdeplot(defensive_actions_team_df.x, defensive_actions_team_df.y, ax=ax,
                  fill=True, levels=5000, thresh=0.02, cut=4, cmap=flamingo_cmap)

    for index, row in average_locs_and_count_df.iterrows():
        if row['isFirstEleven'] == True:
            pitch.scatter(row['x'], row['y'], s=row['marker_size'] + 100, marker='o',
                         color=bg_color, edgecolor=line_color, linewidth=1, alpha=1, zorder=3, ax=ax)
        else:
            pitch.scatter(row['x'], row['y'], s=row['marker_size'] + 100, marker='s',
                         color=bg_color, edgecolor=line_color, linewidth=1, alpha=1, zorder=3, ax=ax)

    pitch.scatter(defensive_actions_team_df.x, defensive_actions_team_df.y,
                  s=10, marker='x', color='yellow', alpha=0.2, ax=ax)

    for index, row in average_locs_and_count_df.iterrows():
        pitch.annotate(row["shirtNo"], xy=(row.x, row.y),
                      c=line_color, ha='center', va='center', size=14, ax=ax)

    dah = average_locs_and_count_df['x'].mean().round(2)
    dah_show = (dah * 1.05).round(2)
    ax.axvline(x=dah, color='gray', linestyle='--', alpha=0.75, linewidth=2)

    if team_id == away_team_id:
        ax.invert_xaxis()
        ax.invert_yaxis()
        ax.text(dah + 1, 105, f"{dah_show}m", fontsize=15, color=line_color, ha='right', va='center')
    else:
        ax.text(dah + 1, -5, f"{dah_show}m", fontsize=15, color=line_color, ha='left', va='center')

    if team_id == home_team_id:
        ax.text(2, 98, "círculos = titulares\ncuadrados = suplentes", color='gray', size=12, ha='left', va='top')
        ax.text(-2, -5, "Dirección ataque --->", color=hcol, size=15, ha='left', va='center')
        ax.set_title("Posición defensiva media - Equipo local", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(2, 2, "círculos = titulares\ncuadrados = suplentes", color='gray', size=12, ha='right', va='top')
        ax.text(-2, 105, "<--- Dirección ataque", color=acol, size=15, ha='right', va='center')
        ax.set_title("Posición defensiva media - Equipo visitante", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)

    return pitch


if __name__ == "__main__":
    # CAMBIA ESTE NOMBRE POR EL ARCHIVO GENERADO CON scraping_data.py
    match_json_path = os.path.join(MATCH_FOLDER, 'Real_Madrid_vs_Bayern_2026-04-07.json')

    with open(match_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    events_dict, players_df, teams_dict = extract_data_from_dict(data)
    defensive_actions_df = get_defensive_action_df(events_dict)

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    home_team_id = list(teams_dict.keys())[0]
    away_team_id = list(teams_dict.keys())[1]

    home_average_locs_df = get_da_count_df(home_team_id, defensive_actions_df, players_df)
    away_average_locs_df = get_da_count_df(away_team_id, defensive_actions_df, players_df)

    home_average_locs_df = home_average_locs_df[home_average_locs_df['position'] != 'GK']
    away_average_locs_df = away_average_locs_df[away_average_locs_df['position'] != 'GK']

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    defensive_block(axes[0], home_average_locs_df, defensive_actions_df,
                    home_team_id, home_team_id, away_team_id, hcol, path_eff)
    defensive_block(axes[1], away_average_locs_df, defensive_actions_df,
                    away_team_id, home_team_id, away_team_id, acol, path_eff)

    plt.tight_layout()

    output_img = match_json_path.replace('.json', '_defensive_block.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
