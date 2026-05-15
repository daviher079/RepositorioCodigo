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

PRESS_WINDOW_S = 10   # segundos máximos entre pérdida y recuperación

LOSS_TYPES = ['Dispossessed', 'Error']
RECOVERY_TYPES = ['BallRecovery', 'Interception']


def build_press_df(df, team_id):
    df = df.copy()
    df['time_s'] = df['expandedMinute'] * 60 + df['second'].fillna(0)

    loss_mask = (
        df['type'].isin(LOSS_TYPES) |
        ((df['type'] == 'TakeOn') & (df['outcomeType'] == 'Unsuccessful')) |
        ((df['type'] == 'Pass')   & (df['outcomeType'] == 'Unsuccessful'))
    )
    rec_mask = (
        df['type'].isin(RECOVERY_TYPES) |
        ((df['type'] == 'Tackle') & (df['outcomeType'] == 'Successful'))
    )

    losses     = df[(df['teamId'] == team_id) & loss_mask]
    recoveries = df[(df['teamId'] == team_id) & rec_mask]

    rows = []
    for _, loss in losses.iterrows():
        t = loss['time_s']
        window = recoveries[
            (recoveries['time_s'] > t) &
            (recoveries['time_s'] <= t + PRESS_WINDOW_S)
        ]
        if len(window) > 0:
            rec = window.iloc[0]
            rows.append({
                'loss_x': loss['x'],   'loss_y': loss['y'],
                'rec_x':  rec['x'],    'rec_y':  rec['y'],
                'seconds': rec['time_s'] - t,
            })

    return pd.DataFrame(rows)


def draw_press_sequences(ax, press_df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    if len(press_df) > 0:
        # Punto de pérdida (círculo hueco gris)
        pitch.scatter(press_df.loss_x, press_df.loss_y,
                      s=120, edgecolor='gray', linewidth=1.5,
                      color=bg_color, zorder=3, ax=ax)
        # Flecha de recuperación (comet hacia el punto de recuperación)
        pitch.lines(press_df.loss_x, press_df.loss_y,
                    press_df.rec_x,  press_df.rec_y,
                    lw=2, transparent=True, comet=True, color=col, ax=ax, alpha=0.7)
        # Punto de recuperación (círculo relleno)
        pitch.scatter(press_df.rec_x, press_df.rec_y,
                      s=120, edgecolor=col, linewidth=1.5,
                      color=col, zorder=4, ax=ax)

    total = len(press_df)
    avg_s = round(press_df['seconds'].mean(), 1) if total > 0 else 0

    # Leyenda manual
    ax.scatter([], [], s=80, edgecolor='gray', color=bg_color, linewidth=1.5, label='Pérdida')
    ax.scatter([], [], s=80, edgecolor=col,   color=col,     linewidth=1.5, label='Recuperación')
    ax.legend(loc='lower center', ncol=2, facecolor=bg_color, labelcolor=line_color,
              fontsize=11, edgecolor=line_color)

    if is_away:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.text(52.5, -3, f"Presses: {total}   Tiempo medio: {avg_s}s",
                color=col, fontsize=13, ha='center', va='center', path_effects=path_eff)
        ax.set_title(f"Press tras pérdida - Equipo visitante", color=line_color,
                     fontsize=25, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.text(52.5, 71, f"Presses: {total}   Tiempo medio: {avg_s}s",
                color=col, fontsize=13, ha='center', va='center', path_effects=path_eff)
        ax.set_title(f"Press tras pérdida - Equipo local", color=line_color,
                     fontsize=25, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = build_press_df(df, hteamID)
    adf = build_press_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_press_sequences(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_press_sequences(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_press_tras_perdida.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
