import os
import numpy as np
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'

goal_color = '#00ff85'    # gol
saved_color = '#FFDD00'   # parada del portero (a puerta)
blocked_color = '#ff8c00' # bloqueado por defensa
missed_color = '#ff4444'  # fuera
post_color = '#4fa3e0'    # al palo

GOAL_CENTER = (105, 34)   # centro de la portería en coordenadas uefa


def get_shots_df(df, team_id):
    mask = (df['teamId'] == team_id) & (
        (df['type'] == 'Goal') |
        (df['type'] == 'MissedShots') |
        (df['type'] == 'SavedShot') |
        (df['type'] == 'ShotOnPost')
    )
    return df[mask].copy().reset_index(drop=True)


def draw_shot_map(ax, shots_df, team_name, away_team_name, col, path_eff, xg=None):
    pitch = VerticalPitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                          half=True, linewidth=2, goal_type='box', goal_alpha=0.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    goals    = shots_df[shots_df['type'] == 'Goal']
    saved    = shots_df[(shots_df['type'] == 'SavedShot') & (~shots_df['qualifiers'].str.contains(': 82,', na=False))]
    blocked  = shots_df[(shots_df['type'] == 'SavedShot') & (shots_df['qualifiers'].str.contains(': 82,', na=False))]
    missed   = shots_df[shots_df['type'] == 'MissedShots']
    post     = shots_df[shots_df['type'] == 'ShotOnPost']
    own_goals = shots_df[shots_df['qualifiers'].str.contains('OwnGoal', na=False)]

    pitch.scatter(missed.x,  missed.y,  s=150, marker='x', color=missed_color,  linewidth=2, zorder=3, ax=ax)
    pitch.scatter(post.x,    post.y,    s=150, marker='D', color=post_color,     linewidth=2, zorder=3, ax=ax)
    pitch.scatter(blocked.x, blocked.y, s=150, marker='o', color=blocked_color,  linewidth=2, zorder=3, ax=ax)
    pitch.scatter(saved.x,   saved.y,   s=150, marker='o', color=saved_color,    linewidth=2, zorder=3, ax=ax)
    pitch.scatter(goals.x,   goals.y,   s=300, marker='*', color=goal_color,     linewidth=2, zorder=4, ax=ax)

    total_shots     = len(shots_df)
    shots_on_target = len(saved) + len(goals) - len(own_goals)
    distances       = np.sqrt((shots_df['x'] - GOAL_CENTER[0])**2 + (shots_df['y'] - GOAL_CENTER[1])**2)
    avg_distance    = round(distances.mean(), 2)
    xg_per_shot     = round(xg / total_shots, 2) if xg is not None and total_shots > 0 else None

    stats_lines = [f"Tiros: {total_shots}   A puerta: {shots_on_target}   Dist. media: {avg_distance}m"]
    if xg is not None:
        stats_lines.append(f"xG: {xg}   xG/tiro: {xg_per_shot}")
    stats_text = "\n".join(stats_lines)

    ax.text(34, 45, stats_text, color=col, fontsize=11, ha='center', va='center', path_effects=path_eff)

    if team_name == away_team_name:
        ax.set_title("Mapa de tiros - Equipo visitante", color=line_color, fontsize=25,
                     fontweight='bold', path_effects=path_eff)
    else:
        ax.set_title("Mapa de tiros - Equipo local", color=line_color, fontsize=25,
                     fontweight='bold', path_effects=path_eff)

    ax.scatter([], [], s=150, marker='*', color=goal_color,    label='Gol')
    ax.scatter([], [], s=150, marker='o', color=saved_color,   label='A puerta')
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

    # xG manual desde FotMob — dejar None si no se dispone
    hxg = None
    axg = None

    hShotsdf = get_shots_df(df, hteamID)
    aShotsdf = get_shots_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    fig.patch.set_facecolor(bg_color)

    draw_shot_map(axes[0], hShotsdf, hteamName, ateamName, hcol, path_eff, xg=hxg)
    draw_shot_map(axes[1], aShotsdf, ateamName, ateamName, acol, path_eff, xg=axg)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_mapa_tiros.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
