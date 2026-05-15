import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

# tercios en coordenadas uefa (0-105 en X)
THIRD_LIMITS  = [0, 35, 70, 105]
THIRD_LABELS  = ['Tercio\ndefensivo', 'Tercio\nmedio', 'Tercio\natacante']
THIRD_COLORS  = ['#F50900', '#FFD700', '#00FF87']
THIRD_CENTERS = [17.5, 52.5, 87.5]


def get_passes_df(df, team_id):
    mask = (
        (df['teamId'] == team_id) &
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful')
    )
    return df[mask].copy()


def assign_third(x):
    if x < 35:
        return 0
    elif x < 70:
        return 1
    else:
        return 2


def draw_distribution(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    ax.vlines([35, 70], ymin=0, ymax=68, colors=line_color, linestyle='dashed', alpha=0.4)

    df = df.copy()
    df['third'] = df['x'].apply(assign_third)
    total = len(df)

    for i in range(3):
        tdf   = df[df['third'] == i]
        count = len(tdf)
        pct   = int((count / total) * 100) if total > 0 else 0
        tc    = THIRD_COLORS[i]
        xc    = THIRD_CENTERS[i]

        pitch.lines(tdf.x, tdf.y, tdf.endX, tdf.endY,
                    lw=1.5, transparent=True, comet=True, color=tc, alpha=0.55, ax=ax)

        ax.text(xc, 60, THIRD_LABELS[i],
                color=tc, fontsize=13, ha='center', va='center', path_effects=path_eff)
        ax.text(xc, 50, f'{count}\n({pct}%)',
                color=tc, fontsize=22, fontweight='bold', ha='center', va='center', path_effects=path_eff)

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=13, ha='right', va='center')
        ax.set_title(f"Equipo visitante — Distribución de pase por tercio\n{total} pases exitosos",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=13, ha='left', va='center')
        ax.set_title(f"Equipo local — Distribución de pase por tercio\n{total} pases exitosos",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_passes_df(df, hteamID)
    adf = get_passes_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_distribution(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_distribution(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_distribucion_tercio.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
