import os
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'
green = '#00ff85'
violet = '#a855f7'


def get_key_passes_df(df, team_id):
    mask = (df['teamId'] == team_id) & (df['qualifiers'].str.contains('KeyPass', na=False))
    return df[mask].copy()


def draw_chance_creating_zone(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', line_color=line_color, goal_type='box', goal_alpha=.5,
                  corner_arcs=True, line_zorder=2, pitch_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    cmap = LinearSegmentedColormap.from_list("pearl_earring", [bg_color, col], N=20)

    bin_statistic = pitch.bin_statistic_positional(df.x, df.y, statistic='count', positional='full', normalize=False)
    pitch.heatmap_positional(bin_statistic, ax=ax, cmap=cmap, edgecolors='gray')
    pitch.scatter(df.x, df.y, c='gray', s=5, ax=ax)

    cc = 0
    for index, row in df.iterrows():
        if 'IntentionalGoalAssist' in row['qualifiers']:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']),
                                            arrowstyle='->', mutation_scale=20,
                                            color=green, linewidth=1.25, alpha=1)
            ax.add_patch(arrow)
        else:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']),
                                            arrowstyle='->', mutation_scale=20,
                                            color=violet, linewidth=1.25, alpha=1)
            ax.add_patch(arrow)
        cc += 1

    pitch.label_heatmap(bin_statistic, color=line_color, fontsize=30, ax=ax, ha='center', va='center',
                        str_format='{:.0f}', path_effects=path_eff)

    if team_name == away_team_name:
        ax.text(105, 71.5, "flecha lila = pases clave\nflecha verde = asistencia", color=col, size=15, ha='left', va='center')
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.text(52.5, -2, f"Oportunidades claras creadas = {cc}", color=col, fontsize=15, ha='center', va='center')
        ax.set_title("Zonas de creación de más peligro - Equipo visitante", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(105, -3.5, "flecha lila = pases clave\nflecha verde = asistencia", color=col, size=15, ha='right', va='center')
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.text(52.5, 70, f"Oportunidades claras creadas = {cc}", color=col, fontsize=15, ha='center', va='center')
        ax.set_title("Zonas de creación de más peligro - Equipo local", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID = df['teamId'].dropna().unique()[0]
    ateamID = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    dfchch = get_key_passes_df(df, hteamID)
    dfchca = get_key_passes_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_chance_creating_zone(axes[0], dfchch, hteamName, ateamName, hcol, path_eff)
    draw_chance_creating_zone(axes[1], dfchca, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_zona_creacion_oportunidades.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
