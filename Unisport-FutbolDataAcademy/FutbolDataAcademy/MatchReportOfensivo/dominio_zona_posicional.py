import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

HCOL_DOM = '#4FC3F7'  # azul claro — más legible que blanco en colormap divergente
BINS     = (9, 6)     # 9 columnas × 6 filas = 54 celdas


def get_touches_df(df, team_id):
    return df[(df['teamId'] == team_id) & (df['isTouch'] == 1)].copy()


def draw_dominance_map(ax, hdf, adf, hteamName, ateamName, path_eff):
    pitch = Pitch(pitch_type='uefa', line_color=line_color, goal_type='box', goal_alpha=.5,
                  corner_arcs=True, line_zorder=3, pitch_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)

    h_stat = pitch.bin_statistic(hdf.x, hdf.y, statistic='count', bins=BINS)
    a_stat = pitch.bin_statistic(adf.x, adf.y, statistic='count', bins=BINS)

    total      = h_stat['statistic'] + a_stat['statistic']
    dominance  = np.where(total > 0,
                          (h_stat['statistic'] - a_stat['statistic']) / total,
                          0)

    dom_stat               = h_stat.copy()
    dom_stat['statistic']  = dominance

    cmap = LinearSegmentedColormap.from_list('dom_cmap', [acol, bg_color, HCOL_DOM], N=256)
    norm = TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)

    pitch.heatmap(dom_stat, ax=ax, cmap=cmap, norm=norm,
                  edgecolors=bg_color, linewidth=0.5, zorder=2)

    # leyenda
    ax.text(3, 64, f'■ {hteamName}', color=HCOL_DOM, fontsize=16,
            fontweight='bold', va='center', path_effects=path_eff)
    ax.text(3, 58, f'■ {ateamName}', color=acol, fontsize=16,
            fontweight='bold', va='center', path_effects=path_eff)

    h_total = int(total[dominance > 0].sum())
    a_total = int(total[dominance < 0].sum())

    ax.text(52.5, -5, f'{hteamName}: {h_total} toques en zonas dominadas  ·  {ateamName}: {a_total} toques en zonas dominadas',
            color=line_color, fontsize=12, ha='center', va='center')

    ax.set_title(f'Dominio por zona posicional — {hteamName} vs {ateamName}',
                 color=line_color, fontsize=26, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_touches_df(df, hteamID)
    adf = get_touches_df(df, ateamID)

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.patch.set_facecolor(bg_color)

    draw_dominance_map(ax, hdf, adf, hteamName, ateamName, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_dominio_zona_posicional.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
