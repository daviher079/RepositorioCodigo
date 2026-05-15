import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch

PROCESSED_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'MatchReportDefensivo',
    'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv'
)

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'


def draw_avg_positions(ax, locs, col, team_name, away_team_name, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5, line_zorder=2)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    teammate_flag = pd.Series([True] * len(locs))
    team1, _ = pitch.voronoi(locs.x, locs.y, teammate_flag)
    pitch.polygon(team1, ax=ax, fc=col, ec=line_color, lw=2, alpha=0.3)

    pitch.scatter(locs.x, locs.y, c=col, s=120, ec=bg_color, zorder=4, ax=ax)

    for _, row in locs.iterrows():
        ax.text(row.x, row.y + 2, row['shortName'], color=col, fontsize=8,
                ha='center', va='bottom', zorder=5, path_effects=path_eff)

    if is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Posición media — {team_name} (visitante)", color=line_color,
                     fontsize=28, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Posición media — {team_name} (local)", color=line_color,
                     fontsize=28, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamName = df['teamName'].dropna().unique()[0]
    ateamName = df['teamName'].dropna().unique()[1]

    touches = df[
        (df['isTouch'] == True) &
        (df['isFirstEleven'] == True) &
        df['name'].notna() &
        df['x'].notna()
    ]
    avg_pos = touches.groupby(['name', 'shortName', 'teamName'])[['x', 'y']].mean().reset_index()

    hlocs = avg_pos[avg_pos['teamName'] == hteamName].reset_index(drop=True)
    alocs = avg_pos[avg_pos['teamName'] == ateamName].reset_index(drop=True)

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_avg_positions(axes[0], hlocs, hcol, hteamName, ateamName, path_eff)
    draw_avg_positions(axes[1], alocs, acol, ateamName, ateamName, path_eff)

    plt.tight_layout()

    output_img = os.path.join(os.path.dirname(__file__), 'posicion_media_del_equipo.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
