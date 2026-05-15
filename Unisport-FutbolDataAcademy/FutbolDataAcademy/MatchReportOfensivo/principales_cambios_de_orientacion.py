import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'

SWITCH_THRESHOLD = 25.0  # metros mínimos de cambio lateral para considerarlo cambio de orientación


def get_switches_df(df, team_id):
    mask = (
        (df['teamId'] == team_id) &
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful') &
        (~df['qualifiers'].str.contains('Corner|ThrowIn', na=False))
    )
    dfteam = df[mask].copy()
    dfteam['lateral_dist'] = (dfteam['endY'] - dfteam['y']).abs()
    return dfteam[dfteam['lateral_dist'] >= SWITCH_THRESHOLD]


def draw_switches_map(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color, linewidth=2,
                  corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    # línea central del ancho del campo (Y=34 en uefa)
    ax.vlines(52.5, ymin=0, ymax=68, colors=line_color, linestyle='dashed', alpha=0.35)

    total = len(df)

    # derecha → izquierda (y < 34 → endY > 34) y viceversa
    right_to_left = len(df[(df['y'] < 34) & (df['endY'] > 34)])
    left_to_right = len(df[(df['y'] > 34) & (df['endY'] < 34)])

    pitch.lines(df.x, df.y, df.endX, df.endY,
                lw=3, transparent=True, comet=True, color=col, ax=ax, alpha=0.6)
    pitch.scatter(df.endX, df.endY, s=35, edgecolor=col, linewidth=1,
                  color=bg_color, zorder=2, ax=ax)

    ax.text(26, 34, f'{right_to_left}\nBanda der → izq',
            color=col, fontsize=18, va='center', ha='center', path_effects=path_eff)
    ax.text(79, 34, f'{left_to_right}\nBanda izq → der',
            color=col, fontsize=18, va='center', ha='center', path_effects=path_eff)

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Equipo visitante: {total} cambios de orientación",
                     color=line_color, fontsize=28, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Equipo local: {total} cambios de orientación",
                     color=line_color, fontsize=28, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID = df['teamId'].dropna().unique()[0]
    ateamID = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_switches_df(df, hteamID)
    adf = get_switches_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_switches_map(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_switches_map(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_cambios_orientacion.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
