import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

PRO_THRESHOLD = 9.144  # 10 yardas en metros — umbral de pase progresivo


def get_progressive_passes_df(df, team_id):
    mask = (
        (df['teamId'] == team_id) &
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful') &
        (df['pro'] >= PRO_THRESHOLD)
    )
    return df[mask].copy()


def draw_reception_zones(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', line_color=line_color, goal_type='box', goal_alpha=.5,
                  corner_arcs=True, line_zorder=2, pitch_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    cmap = LinearSegmentedColormap.from_list('prog_recv_cmap', [bg_color, col], N=20)

    bin_statistic = pitch.bin_statistic_positional(
        df.endX, df.endY, statistic='count', positional='full', normalize=True
    )
    pitch.heatmap_positional(bin_statistic, ax=ax, cmap=cmap, edgecolors=bg_color)
    pitch.scatter(df.endX, df.endY, c='gray', s=15, ax=ax, zorder=3, alpha=0.6)
    pitch.label_heatmap(
        bin_statistic, color=line_color, fontsize=26, ax=ax,
        ha='center', va='center', str_format='{:.0%}', path_effects=path_eff
    )

    total = len(df)

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=13, ha='right', va='center')
        ax.set_title(f"Equipo visitante — Recepción de pases progresivos ({total})",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=13, ha='left', va='center')
        ax.set_title(f"Equipo local — Recepción de pases progresivos ({total})",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_progressive_passes_df(df, hteamID)
    adf = get_progressive_passes_df(df, ateamID)

    print(f"{hteamName}: {len(hdf)} pases progresivos")
    print(f"{ateamName}: {len(adf)} pases progresivos")

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_reception_zones(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_reception_zones(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_recepcion_pases_progresivos.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
