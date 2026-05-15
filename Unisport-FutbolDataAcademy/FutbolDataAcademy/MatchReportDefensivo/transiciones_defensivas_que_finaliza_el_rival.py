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

goal_color    = '#00ff85'
saved_color   = '#FFDD00'
blocked_color = '#ff8c00'
missed_color  = '#ff4444'
post_color    = '#4fa3e0'

TRANS_WINDOW_S = 12

LOSS_TYPES = ['Dispossessed', 'Error']
SHOT_TYPES = ['Goal', 'MissedShots', 'SavedShot', 'ShotOnPost']


def build_transition_df(df, team_id):
    df = df.copy()
    df['time_s'] = df['expandedMinute'] * 60 + df['second'].fillna(0)

    loss_mask = (
        df['type'].isin(LOSS_TYPES) |
        ((df['type'] == 'TakeOn') & (df['outcomeType'] == 'Unsuccessful')) |
        ((df['type'] == 'Pass')   & (df['outcomeType'] == 'Unsuccessful'))
    )

    opp_id  = df[df['teamId'] != team_id]['teamId'].dropna().unique()[0]
    losses  = df[(df['teamId'] == team_id) & loss_mask]
    shots   = df[(df['teamId'] == opp_id)  & df['type'].isin(SHOT_TYPES)]

    rows = []
    for _, loss in losses.iterrows():
        t = loss['time_s']
        window = shots[
            (shots['time_s'] > t) &
            (shots['time_s'] <= t + TRANS_WINDOW_S)
        ]
        if len(window) > 0:
            shot = window.iloc[0]
            rows.append({
                'loss_x':   loss['x'],  'loss_y':   loss['y'],
                'shot_x':   shot['x'],  'shot_y':   shot['y'],
                'shot_type': shot['type'],
                'seconds':  shot['time_s'] - t,
            })

    return pd.DataFrame(rows)


def draw_transitions(ax, trans_df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    # Misma lógica que zonas_de_ocasiones_concedidas: los tiros del rival
    # tienen x bajas cuando defiendes como local → invertir panel local
    is_away = team_name == away_team_name
    if not is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    if len(trans_df) > 0:
        # Punto de pérdida
        pitch.scatter(trans_df.loss_x, trans_df.loss_y,
                      s=100, edgecolor='gray', linewidth=1.5,
                      color=bg_color, zorder=3, ax=ax)
        # Flecha de la transición
        pitch.lines(trans_df.loss_x, trans_df.loss_y,
                    trans_df.shot_x, trans_df.shot_y,
                    lw=2, transparent=True, comet=True,
                    color='gray', ax=ax, alpha=0.5, zorder=2)

        # Punto de tiro coloreado por resultado
        shot_colors = {
            'Goal':        goal_color,
            'SavedShot':   saved_color,
            'MissedShots': missed_color,
            'ShotOnPost':  post_color,
        }
        shot_markers = {
            'Goal':        '*',
            'SavedShot':   'o',
            'MissedShots': 'x',
            'ShotOnPost':  'D',
        }
        for stype, scolor in shot_colors.items():
            sub = trans_df[trans_df['shot_type'] == stype]
            if len(sub) > 0:
                pitch.scatter(sub.shot_x, sub.shot_y,
                              s=200 if stype == 'Goal' else 120,
                              marker=shot_markers[stype],
                              color=scolor, edgecolor=line_color,
                              linewidth=1.5, zorder=4, ax=ax)

    total    = len(trans_df)
    avg_s    = round(trans_df['seconds'].mean(), 1) if total > 0 else 0
    n_goals  = len(trans_df[trans_df['shot_type'] == 'Goal']) if total > 0 else 0

    # Leyenda
    ax.scatter([], [], s=80, marker='*', color=goal_color,    label='Gol')
    ax.scatter([], [], s=80, marker='o', color=saved_color,   label='A puerta')
    ax.scatter([], [], s=80, marker='x', color=missed_color,  label='Fuera')
    ax.scatter([], [], s=80, marker='D', color=post_color,    label='Al palo')
    ax.legend(loc='lower center', ncol=4, facecolor=bg_color,
              labelcolor=line_color, fontsize=10, edgecolor=line_color)

    stats = f"Transiciones: {total}   Goles: {n_goals}   T. medio: {avg_s}s"

    if not is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.text(52.5, -3, stats, color=col, fontsize=12, ha='center', path_effects=path_eff)
        ax.set_title("Transiciones concedidas - Equipo local", color=line_color,
                     fontsize=24, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.text(52.5, 71, stats, color=col, fontsize=12, ha='center', path_effects=path_eff)
        ax.set_title("Transiciones concedidas - Equipo visitante", color=line_color,
                     fontsize=24, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = build_transition_df(df, hteamID)
    adf = build_transition_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_transitions(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_transitions(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_transiciones_defensivas.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
