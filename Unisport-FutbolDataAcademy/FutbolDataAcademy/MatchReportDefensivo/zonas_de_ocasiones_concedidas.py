import os
import numpy as np
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

goal_color    = '#00ff85'
saved_color   = '#FFDD00'
blocked_color = '#ff8c00'
missed_color  = '#ff4444'
post_color    = '#4fa3e0'

GOAL_CENTER = (105, 34)

SHOT_TYPES = ['Goal', 'MissedShots', 'SavedShot', 'ShotOnPost']


def get_conceded_shots_df(df, opponent_id):
    mask = (df['teamId'] == opponent_id) & (df['type'].isin(SHOT_TYPES))
    return df[mask].copy().reset_index(drop=True)


def draw_conceded_occasions(ax, shots_df, team_name, away_team_name, col, path_eff):
    pitch = VerticalPitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                          half=True, linewidth=2, goal_type='box', goal_alpha=0.5)
    pitch.draw(ax=ax)

    # Las ocasiones concedidas por el local son tiros del visitante (x bajas),
    # por eso la inversión es la contraria a mapa_de_tiros.py
    if team_name != away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    goals   = shots_df[shots_df['type'] == 'Goal']
    saved   = shots_df[(shots_df['type'] == 'SavedShot') & (~shots_df['qualifiers'].str.contains(': 82,', na=False))]
    blocked = shots_df[(shots_df['type'] == 'SavedShot') & (shots_df['qualifiers'].str.contains(': 82,', na=False))]
    missed  = shots_df[shots_df['type'] == 'MissedShots']
    post    = shots_df[shots_df['type'] == 'ShotOnPost']

    pitch.scatter(missed.x,  missed.y,  s=150, marker='x', color=missed_color,  linewidth=2, zorder=3, ax=ax)
    pitch.scatter(post.x,    post.y,    s=150, marker='D', color=post_color,     linewidth=2, zorder=3, ax=ax)
    pitch.scatter(blocked.x, blocked.y, s=150, marker='o', color=blocked_color,  linewidth=2, zorder=3, ax=ax)
    pitch.scatter(saved.x,   saved.y,   s=150, marker='o', color=saved_color,    linewidth=2, zorder=3, ax=ax)
    pitch.scatter(goals.x,   goals.y,   s=300, marker='*', color=goal_color,     linewidth=2, zorder=4, ax=ax)

    total         = len(shots_df)
    on_target     = len(saved) + len(goals)
    distances     = np.sqrt((shots_df['x'] - GOAL_CENTER[0])**2 + (shots_df['y'] - GOAL_CENTER[1])**2)
    avg_distance  = round(distances.mean(), 2) if total > 0 else 0

    ax.text(34, 45, f"Ocasiones concedidas: {total}   A puerta: {on_target}   Dist. media: {avg_distance}m",
            color=col, fontsize=11, ha='center', va='center', path_effects=path_eff)

    if team_name != away_team_name:
        ax.set_title("Ocasiones concedidas - Equipo local", color=line_color,
                     fontsize=25, fontweight='bold', path_effects=path_eff)
    else:
        ax.set_title("Ocasiones concedidas - Equipo visitante", color=line_color,
                     fontsize=25, fontweight='bold', path_effects=path_eff)

    ax.scatter([], [], s=150, marker='*', color=goal_color,    label='Gol encajado')
    ax.scatter([], [], s=150, marker='o', color=saved_color,   label='Parada')
    ax.scatter([], [], s=150, marker='o', color=blocked_color, label='Bloqueado')
    ax.scatter([], [], s=150, marker='D', color=post_color,    label='Al palo')
    ax.scatter([], [], s=150, marker='x', color=missed_color,  label='Fuera')
    ax.legend(loc='lower center', ncol=5, facecolor=bg_color, labelcolor=line_color,
              fontsize=9, edgecolor=line_color)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    # concedidas por local = tiros del visitante; concedidas por visitante = tiros del local
    hdf = get_conceded_shots_df(df, ateamID)
    adf = get_conceded_shots_df(df, hteamID)

    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    fig.patch.set_facecolor(bg_color)

    draw_conceded_occasions(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_conceded_occasions(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_zonas_ocasiones_concedidas.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
