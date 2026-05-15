import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch

from jugador_estadisticas import get_defensive_player_stats, get_short_name


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

# (etiqueta, marker, relleno)
MARKER_DEFS = [
    ('Entrada',      '+', True),
    ('Anticipación', 's', False),
    ('Recuperación', 'o', False),
    ('Despeje',      'd', False),
    ('Falta',        'x', True),
    ('Duelo aéreo',  '^', False),
]


def get_player_def_actions(df, player_name):
    pdf = df[df['name'] == player_name]
    return [
        pdf[pdf['type'] == 'Tackle'],
        pdf[(pdf['type'] == 'Interception') | (pdf['type'] == 'BlockedPass')],
        pdf[pdf['type'] == 'BallRecovery'],
        pdf[pdf['type'] == 'Clearance'],
        pdf[pdf['type'] == 'Foul'],
        pdf[(pdf['type'] == 'Aerial') & pdf['qualifiers'].str.contains('Defensive', na=False)],
    ]


def draw_player_def_acts(ax, df, defender_df, col, invert, path_eff):
    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.75, corner_arcs=True,
                  pitch_color=bg_color, line_color=line_color, line_zorder=2, linewidth=2)
    pitch.draw(ax=ax)

    if invert:
        ax.set_ylim(-0.5, 81)
        ax.invert_xaxis()
        ax.invert_yaxis()
        legend_y  = [71, 75, 79]
        legend_ha = 'right'
        arrow_txt = "<----- Dirección ataque"
        arrow_x, arrow_y, arrow_ha = 0, 73, 'right'
    else:
        ax.set_ylim(-13, 68.5)
        legend_y  = [-3, -7, -11]
        legend_ha = 'left'
        arrow_txt = "Dirección ataque ----->"
        arrow_x, arrow_y, arrow_ha = 0, -5, 'left'

    player_name  = defender_df['name'].iloc[0]
    player_short = get_short_name(player_name)
    action_dfs   = get_player_def_actions(df, player_name)

    for action_df, (_, marker, filled) in zip(action_dfs, MARKER_DEFS):
        c = col if filled else 'None'
        pitch.scatter(action_df.x, action_df.y,
                      s=250, c=c, lw=2.5, edgecolor=col, marker=marker, ax=ax)

    # leyenda: dos columnas de 3
    legend_xs = [51, 78]
    labels_col1 = [m[0] for m in MARKER_DEFS[:3]]
    labels_col2 = [m[0] for m in MARKER_DEFS[3:]]
    markers_col1 = MARKER_DEFS[:3]
    markers_col2 = MARKER_DEFS[3:]

    for ly, (_, marker, filled), label in zip(legend_y, markers_col1, labels_col1):
        c = col if filled else 'None'
        pitch.scatter(legend_xs[0], ly, s=150, c=c, lw=2.5, edgecolor=col, marker=marker, ax=ax)
        ax.text(legend_xs[0] + 2, ly, label, color=col, ha=legend_ha, va='center', fontsize=13)

    for ly, (_, marker, filled), label in zip(legend_y, markers_col2, labels_col2):
        c = col if filled else 'None'
        pitch.scatter(legend_xs[1], ly, s=150, c=c, lw=2.5, edgecolor=col, marker=marker, ax=ax)
        ax.text(legend_xs[1] + 2, ly, label, color=col, ha=legend_ha, va='center', fontsize=13)

    ax.text(arrow_x, arrow_y, arrow_txt, color=col, fontsize=15, va='center', ha=arrow_ha)
    ax.set_title(f"{player_short} — Acciones defensivas", color=col, fontsize=25,
                 fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    home_defender_df = get_defensive_player_stats(df, hteamID)
    away_defender_df = get_defensive_player_stats(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    fig.patch.set_facecolor(bg_color)

    draw_player_def_acts(axes[0], df, home_defender_df, hcol, invert=False, path_eff=path_eff)
    draw_player_def_acts(axes[1], df, away_defender_df, acol, invert=True,  path_eff=path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_acciones_defensivas_jugador.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
