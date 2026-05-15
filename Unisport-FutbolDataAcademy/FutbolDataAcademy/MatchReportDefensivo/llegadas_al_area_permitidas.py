import os
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

# Área de penalti en coordenadas UEFA (105x68)
BOX_X    = 88.5
BOX_Y1   = 13.84
BOX_Y2   = 54.16
BOX_W    = 105 - BOX_X   # 16.5
BOX_H    = BOX_Y2 - BOX_Y1


def get_box_entries_df(df, opponent_id):
    box_mask = (
        (df['endX'] >= BOX_X) &
        (df['endY'] >= BOX_Y1) &
        (df['endY'] <= BOX_Y2)
    )
    mask = (
        (df['teamId'] == opponent_id) &
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful') &
        (~df['qualifiers'].str.contains('Corner', na=False)) &
        box_mask
    )
    return df[mask].copy().reset_index(drop=True)


def draw_box_entries(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()
        box_x_draw = 105 - BOX_X - BOX_W
        box_y_draw = BOX_Y1
    else:
        box_x_draw = BOX_X
        box_y_draw = BOX_Y1

    # Sombreado del área de penalti
    rect = patches.Rectangle(
        (box_x_draw, box_y_draw), BOX_W, BOX_H,
        linewidth=0, facecolor=col, alpha=0.08, zorder=1
    )
    ax.add_patch(rect)

    pitch.lines(df.x, df.y, df.endX, df.endY,
                lw=2.5, transparent=True, comet=True, color=col, ax=ax, alpha=0.6)
    pitch.scatter(df.endX, df.endY, s=50, edgecolor=col, linewidth=1,
                  color=bg_color, zorder=3, ax=ax)

    total = len(df)

    if is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Llegadas al área permitidas - Visitante ({total})", color=line_color,
                     fontsize=25, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Llegadas al área permitidas - Local ({total})", color=line_color,
                     fontsize=25, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    # permitidas por local = entradas del visitante; permitidas por visitante = entradas del local
    hdf = get_box_entries_df(df, ateamID)
    adf = get_box_entries_df(df, hteamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_box_entries(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_box_entries(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_llegadas_area_permitidas.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
