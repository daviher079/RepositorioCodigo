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


def get_recoveries_df(df, team_id):
    mask_recovery    = df['type'] == 'BallRecovery'
    mask_interception = df['type'] == 'Interception'
    mask_tackle      = (df['type'] == 'Tackle') & (df['outcomeType'] == 'Successful')
    mask = (df['teamId'] == team_id) & (mask_recovery | mask_interception | mask_tackle)
    return df[mask].copy()


def draw_recovery_zones(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', line_color=line_color, goal_type='box', goal_alpha=.5,
                  corner_arcs=True, line_zorder=2, pitch_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    cmap = LinearSegmentedColormap.from_list('recovery_cmap', [bg_color, col], N=20)

    bin_statistic = pitch.bin_statistic_positional(
        df.x, df.y, statistic='count', positional='full', normalize=True
    )
    pitch.heatmap_positional(bin_statistic, ax=ax, cmap=cmap, edgecolors=bg_color)
    pitch.scatter(df.x, df.y, c='gray', s=5, ax=ax, zorder=3)
    pitch.label_heatmap(
        bin_statistic, color=line_color, fontsize=30, ax=ax,
        ha='center', va='center', str_format='{:.0%}', path_effects=path_eff
    )

    total = len(df)
    if is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Zonas de recuperación - Equipo visitante ({total})", color=line_color,
                     fontsize=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Zonas de recuperación - Equipo local ({total})", color=line_color,
                     fontsize=30, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_recoveries_df(df, hteamID)
    adf = get_recoveries_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_recovery_zones(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_recovery_zones(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_zonas_de_recuperacion.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
    