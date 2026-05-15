import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch

PROCESSED_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'MatchReportDefensivo',
    'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv'
)

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

BINS = (6, 4)


def get_passes_df(df, team_name):
    mask = (df['type'] == 'Pass') & (df['outcomeType'] == 'Successful') & (df['teamName'] == team_name)
    return df.loc[mask, ['x', 'y', 'endX', 'endY']].dropna()


def draw_flow_map(ax, df_pass, col, team_name, away_team_name, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5, line_zorder=2)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    cmap = LinearSegmentedColormap.from_list('flow_cmap', [bg_color, col], N=20)

    bs = pitch.bin_statistic(df_pass.x, df_pass.y, statistic='count', bins=BINS)
    pitch.heatmap(bs, ax=ax, cmap=cmap, edgecolors=bg_color)
    pitch.flow(df_pass.x, df_pass.y, df_pass.endX, df_pass.endY,
               color=col, arrow_type='average', bins=BINS, ax=ax)

    total = len(df_pass)
    if is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Zonas de generación y envío — {team_name} visitante ({total} pases)",
                     color=line_color, fontsize=26, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Zonas de generación y envío — {team_name} local ({total} pases)",
                     color=line_color, fontsize=26, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamName = df['teamName'].dropna().unique()[0]
    ateamName = df['teamName'].dropna().unique()[1]

    hdf = get_passes_df(df, hteamName)
    adf = get_passes_df(df, ateamName)

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_flow_map(axes[0], hdf, hcol, hteamName, ateamName, path_eff)
    draw_flow_map(axes[1], adf, acol, ateamName, ateamName, path_eff)

    plt.tight_layout()

    output_img = os.path.join(os.path.dirname(__file__), 'zonas_de_generacion_y_envio.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
