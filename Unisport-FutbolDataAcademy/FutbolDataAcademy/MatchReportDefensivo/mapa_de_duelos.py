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


def get_duels_df(df, team_id):
    mask = (df['teamId'] == team_id) & df['type'].isin(['Tackle', 'Aerial', 'Challenge'])
    return df[mask].copy()


def draw_duel_map(ax, df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    aerial_won  = df[(df['type'] == 'Aerial')  & (df['outcomeType'] == 'Successful')]
    aerial_lost = df[(df['type'] == 'Aerial')  & (df['outcomeType'] == 'Unsuccessful')]
    tackle_won  = df[(df['type'] == 'Tackle')  & (df['outcomeType'] == 'Successful')]
    tackle_lost = df[(df['type'] == 'Tackle')  & (df['outcomeType'] == 'Unsuccessful')]
    challenge   = df[ df['type'] == 'Challenge']  # siempre Unsuccessful

    # Duelos aéreos
    pitch.scatter(aerial_won.x,  aerial_won.y,  s=200, marker='^', color=col,      edgecolor=col,      linewidth=1.5, zorder=3, ax=ax)
    pitch.scatter(aerial_lost.x, aerial_lost.y, s=200, marker='^', color=bg_color, edgecolor=col,      linewidth=1.5, zorder=3, ax=ax)
    # Duelos en el suelo
    pitch.scatter(tackle_won.x,  tackle_won.y,  s=150, marker='o', color=col,      edgecolor=col,      linewidth=1.5, zorder=3, ax=ax)
    pitch.scatter(tackle_lost.x, tackle_lost.y, s=150, marker='o', color=bg_color, edgecolor=col,      linewidth=1.5, zorder=3, ax=ax)
    pitch.scatter(challenge.x,   challenge.y,   s=150, marker='x', color=col,      linewidth=2,        zorder=3, ax=ax)

    # Estadísticas
    total_aerial  = len(aerial_won) + len(aerial_lost)
    total_ground  = len(tackle_won) + len(tackle_lost) + len(challenge)
    pct_aerial    = round(len(aerial_won) / total_aerial * 100) if total_aerial > 0 else 0
    pct_ground    = round(len(tackle_won) / total_ground * 100) if total_ground > 0 else 0

    stats = (f"Aéreos: {len(aerial_won)}G/{total_aerial}T ({pct_aerial}%)   "
             f"Suelo: {len(tackle_won)}G/{total_ground}T ({pct_ground}%)")

    # Leyenda
    ax.scatter([], [], s=100, marker='^', color=col,      label='Aéreo ganado')
    ax.scatter([], [], s=100, marker='^', color=bg_color, edgecolor=col, linewidth=1.5, label='Aéreo perdido')
    ax.scatter([], [], s=100, marker='o', color=col,      label='Tackle ganado')
    ax.scatter([], [], s=100, marker='o', color=bg_color, edgecolor=col, linewidth=1.5, label='Tackle perdido')
    ax.scatter([], [], s=100, marker='x', color=col,      linewidth=2, label='Disputa perdida')
    ax.legend(loc='lower center', ncol=5, facecolor=bg_color, labelcolor=line_color,
              fontsize=9, edgecolor=line_color)

    if is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.text(52.5, -3, stats, color=col, fontsize=12, ha='center', path_effects=path_eff)
        ax.set_title("Mapa de duelos - Equipo visitante", color=line_color,
                     fontsize=28, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.text(52.5, 71, stats, color=col, fontsize=12, ha='center', path_effects=path_eff)
        ax.set_title("Mapa de duelos - Equipo local", color=line_color,
                     fontsize=28, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_duels_df(df, hteamID)
    adf = get_duels_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_duel_map(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_duel_map(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_mapa_de_duelos.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
