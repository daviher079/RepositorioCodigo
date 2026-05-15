import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch

from jugador_estadisticas import get_short_name


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'
violet     = '#a855f7'
green      = '#22c55e'


def get_forward(df, team_id):
    team_df = df[(df['teamId'] == team_id) & (df['position'] == 'FW')]
    return team_df['name'].dropna().iloc[0]


def get_received_passes(df, player_name):
    received = df[
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful') &
        (df['name'].shift(-1) == player_name)
    ]
    keypasses = received[received['qualifiers'].str.contains('KeyPass',               na=False)]
    assists   = received[received['qualifiers'].str.contains('IntentionalGoalAssist', na=False)]
    return received, keypasses, assists


def draw_received_passes(ax, df, team_id, col, invert, path_eff):
    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.75, corner_arcs=True,
                  pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)

    if invert:
        ax.invert_xaxis()
        ax.invert_yaxis()
        info_y     = -2
        arrow_x, arrow_y, arrow_ha = 0, 73, 'right'
        arrow_txt  = "<----- Dirección ataque"
    else:
        info_y     = 70
        arrow_x, arrow_y, arrow_ha = 0, -5, 'left'
        arrow_txt  = "Dirección ataque ----->"

    player_name  = get_forward(df, team_id)
    player_short = get_short_name(player_name)

    received, keypasses, assists = get_received_passes(df, player_name)
    pr  = len(received)
    kpr = len(keypasses)

    pitch.lines(received.x,   received.y,   received.endX,   received.endY,
                lw=3, transparent=True, comet=True, color=col,    alpha=0.5,  ax=ax)
    pitch.lines(keypasses.x,  keypasses.y,  keypasses.endX,  keypasses.endY,
                lw=4, transparent=True, comet=True, color=violet, alpha=0.75, ax=ax)
    pitch.lines(assists.x,    assists.y,    assists.endX,    assists.endY,
                lw=4, transparent=True, comet=True, color=green,  alpha=0.75, ax=ax)

    pitch.scatter(received.endX,  received.endY,  s=30, edgecolor=col,    linewidth=1,   color=bg_color, zorder=2, ax=ax)
    pitch.scatter(keypasses.endX, keypasses.endY, s=40, edgecolor=violet, linewidth=1.5, color=bg_color, zorder=2, ax=ax)
    pitch.scatter(assists.endX,   assists.endY,   s=50, edgecolors=green, linewidths=1,
                  marker='football', c=bg_color, zorder=2, ax=ax)

    avg_endX = received['endX'].median()
    avg_endY = received['endY'].median()
    ax.axvline(x=avg_endX, color='gray', linestyle='--', alpha=0.6, linewidth=2)
    ax.axhline(y=avg_endY, color='gray', linestyle='--', alpha=0.6, linewidth=2)

    ax.text(52.5, info_y,     f"Pases recibidos: {pr}",
            color=line_color, fontsize=15, ha='center', va='center')
    ax.text(52.5, info_y - 4, f"Pases clave recibidos: {kpr}",
            color=violet, fontsize=15, ha='center', va='center')

    ax.text(arrow_x, arrow_y, arrow_txt, color=col, fontsize=15, va='center', ha=arrow_ha)
    ax.set_title(f"{player_short} — Pases recibidos", color=col, fontsize=25,
                 fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID = df['teamId'].dropna().unique()[0]
    ateamID = df['teamId'].dropna().unique()[1]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    fig.patch.set_facecolor(bg_color)

    draw_received_passes(axes[0], df, hteamID, hcol, invert=False, path_eff=path_eff)
    draw_received_passes(axes[1], df, ateamID, acol, invert=True,  path_eff=path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_receptores_de_pases.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
