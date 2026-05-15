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


def get_progressive_passes_df(df, team_id):
    mask = df['teamId'] == team_id
    dfteam = df[mask].copy()
    dfteam = dfteam.loc[dfteam['type'] == 'Pass']
    dfteam = dfteam[~dfteam['qualifiers'].str.contains('Corner')]
    return dfteam


def draw_progressive_pass_map(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color, linewidth=2,
                  corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    dfpro = df[df['pro'] >= 9.144]
    pro_count = len(dfpro)

    left_pro = len(dfpro[dfpro['y'] >= 45.33])
    mid_pro = len(dfpro[(dfpro['y'] >= 22.67) & (dfpro['y'] < 45.33)])
    right_pro = len(dfpro[(dfpro['y'] >= 0) & (dfpro['y'] < 22.67)])
    left_percentage = int((left_pro / pro_count) * 100)
    mid_percentage = int((mid_pro / pro_count) * 100)
    right_percentage = int((right_pro / pro_count) * 100)

    ax.hlines(22.67, xmin=0, xmax=105, colors=line_color, linestyle='dashed', alpha=0.35)
    ax.hlines(45.33, xmin=0, xmax=105, colors=line_color, linestyle='dashed', alpha=0.35)

    ax.text(27, 11.335, f'{right_pro}\n({right_percentage}%)', color=col, fontsize=24, va='center', ha='center')
    ax.text(27, 34, f'{mid_pro}\n({mid_percentage}%)', color=col, fontsize=24, va='center', ha='center')
    ax.text(27, 56.675, f'{left_pro}\n({left_percentage}%)', color=col, fontsize=24, va='center', ha='center')

    pitch.lines(dfpro.x, dfpro.y, dfpro.endX, dfpro.endY,
                lw=3.5, transparent=True, comet=True, color=col, ax=ax, alpha=0.5)
    pitch.scatter(dfpro.endX, dfpro.endY, s=35, edgecolor=col, linewidth=1,
                  color=bg_color, zorder=2, ax=ax)

    counttext = f"{pro_count} Pases progresivos"

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.set_title(f"Equipo visitante: {counttext}", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.set_title(f"Equipo local: {counttext}", color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID = df['teamId'].dropna().unique()[0]
    ateamID = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    dfhpp = get_progressive_passes_df(df, hteamID)
    dfapp = get_progressive_passes_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_progressive_pass_map(axes[0], dfhpp, hteamName, ateamName, hcol, path_eff)
    draw_progressive_pass_map(axes[1], dfapp, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_pases_progresivos.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
