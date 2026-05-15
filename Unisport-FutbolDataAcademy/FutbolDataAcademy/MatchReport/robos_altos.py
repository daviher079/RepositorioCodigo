import os
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import numpy as np
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def get_high_turnovers(df, hteamID, ateamID):
    mask = (df['type'] == 'BallRecovery') | (df['type'] == 'Interception')

    home_TO = df[(df['teamId'] == hteamID) & mask & (df['x'] >= 70)].copy()
    away_TO = df[(df['teamId'] == ateamID) & mask & (df['x'] >= 70)].copy()

    # fórmula distancia euclídea al centro de la portería (105, 34)
    home_TO['distance'] = np.sqrt((home_TO['x'] - 105) ** 2 + (home_TO['y'] - 34) ** 2)
    away_TO['distance'] = np.sqrt((away_TO['x'] - 105) ** 2 + (away_TO['y'] - 34) ** 2)

    home_TO = home_TO[home_TO['distance'] <= 40]
    away_TO = away_TO[away_TO['distance'] <= 40]

    return home_TO, away_TO


def draw_high_turnovers(ax, home_TO, away_TO, path_eff):
    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.75, corner_arcs=True,
                  pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    ax.set_ylim(-0.5, 68.5)
    ax.set_xlim(-0.5, 105.5)
    ax.set_aspect('equal', adjustable='box')

    hto_count = len(home_TO)
    ato_count = len(away_TO)

    ax.scatter(105 - home_TO['x'], 68 - home_TO['y'],
               s=250, c=hcol, edgecolor=line_color, marker='o', linewidth=2)
    ax.scatter(away_TO['x'], away_TO['y'],
               s=250, c=acol, edgecolor=line_color, marker='o', linewidth=2)

    ax.add_artist(plt.Circle((0, 34),   40, color=hcol, fill=True, alpha=0.25, linestyle='dashed'))
    ax.add_artist(plt.Circle((105, 34), 40, color=acol, fill=True, alpha=0.25, linestyle='dashed'))

    ax.text(0,   70, f"Equipo local\nRobos más altos: {hto_count}",
            color=hcol, size=25, ha='left',  fontweight='bold', path_effects=path_eff)
    ax.text(105, 70, f"Equipo visitante\nRobos más altos: {ato_count}",
            color=acol, size=25, ha='right', fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    home_TO, away_TO = get_high_turnovers(df, hteamID, ateamID)

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    draw_high_turnovers(ax, home_TO, away_TO, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_robos_altos.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
