import os
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def get_dangerous_passes_df(df, team_id):
    mask = df['teamId'] == team_id
    dfteam = df[mask].copy()
    dfteam = dfteam.loc[dfteam['type'] == 'Pass']
    dfteam = dfteam.loc[dfteam['outcomeType'] == 'Successful']
    dfteam = dfteam[~dfteam['qualifiers'].str.contains('Corner')]
    return dfteam


def draw_dangerous_pass_map(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color, linewidth=2,
                  corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)
    ax.set_facecolor(bg_color)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    z14 = 0
    hs = 0

    for index, row in df.iterrows():
        if row['endX'] >= 70 and row['endX'] <= 88.54 and row['endY'] >= 22.66 and row['endY'] <= 45.32:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']),
                                            arrowstyle='->', alpha=0.75, mutation_scale=20,
                                            color='orange', linewidth=1.5)
            ax.add_patch(arrow)
            z14 += 1
        if row['endX'] >= 70 and row['endY'] >= 11.33 and row['endY'] <= 22.66:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']),
                                            arrowstyle='->', alpha=0.75, mutation_scale=20,
                                            color=col, linewidth=1.5)
            ax.add_patch(arrow)
            hs += 1
        if row['endX'] >= 70 and row['endY'] >= 45.32 and row['endY'] <= 56.95:
            arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']),
                                            arrowstyle='->', alpha=0.75, mutation_scale=20,
                                            color=col, linewidth=1.5)
            ax.add_patch(arrow)
            hs += 1

    y_z14 = [22.66, 22.66, 45.32, 45.32]
    x_z14 = [70, 88.54, 88.54, 70]
    ax.fill(x_z14, y_z14, 'yellow', alpha=0.2, label='Zone14')

    y_rhs = [11.33, 11.33, 22.66, 22.66]
    x_rhs = [70, 105, 105, 70]
    ax.fill(x_rhs, y_rhs, col, alpha=0.2, label='HalfSpaces')

    y_lhs = [45.32, 45.32, 56.95, 56.95]
    x_lhs = [70, 105, 105, 70]
    ax.fill(x_lhs, y_lhs, col, alpha=0.2, label='HalfSpaces')

    ax.scatter(16.46, 13.85, color=col, s=15000, edgecolor=line_color, linewidth=2, alpha=1, marker='h')
    ax.scatter(16.46, 54.15, color='yellow', s=15000, edgecolor=line_color, linewidth=2, alpha=1, marker='h')
    ax.text(16.46, 13.85 - 4, "Intervalos", fontsize=20, color=line_color, ha='center', va='center', path_effects=path_eff)
    ax.text(16.46, 54.15 - 4, "Zona 14", fontsize=20, color=line_color, ha='center', va='center', path_effects=path_eff)
    ax.text(16.46, 13.85 + 2, f"{hs}", fontsize=40, color=line_color, ha='center', va='center', path_effects=path_eff)
    ax.text(16.46, 54.15 + 2, f"{z14}", fontsize=40, color=line_color, ha='center', va='center', path_effects=path_eff)

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title("Zona 14 e Intervalos - Equipo visitante", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title("Zona 14 e Intervalos - Equipo local", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID = df['teamId'].dropna().unique()[0]
    ateamID = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    dfhp = get_dangerous_passes_df(df, hteamID)
    dfap = get_dangerous_passes_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_dangerous_pass_map(axes[0], dfhp, hteamName, ateamName, hcol, path_eff)
    draw_dangerous_pass_map(axes[1], dfap, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_zonas_peligrosas_pases.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
