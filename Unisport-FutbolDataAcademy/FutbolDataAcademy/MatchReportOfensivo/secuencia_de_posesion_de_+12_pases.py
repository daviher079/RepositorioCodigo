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

MIN_PASSES = 12

PERIOD_ORDER = {'FirstHalf': 1, 'SecondHalf': 2, 'FirstPeriodOfExtraTime': 3, 'SecondPeriodOfExtraTime': 4}

SEQ_COLORS = ['#FFD700', '#00E5FF', '#FF6B35', '#00FF87', '#C77DFF', '#FF69B4', '#7FFF00', '#FF4500']


def sort_events(df):
    df = df.copy()
    df['period_order'] = df['period'].map(PERIOD_ORDER).fillna(5)
    return df.sort_values(['period_order', 'expandedMinute', 'second']).reset_index(drop=True)


def find_long_sequences(df_sorted, team_id):
    sequences = []
    current_passes = []

    for _, row in df_sorted.iterrows():
        if row['teamId'] != team_id:
            if len(current_passes) >= MIN_PASSES:
                sequences.append(current_passes.copy())
            current_passes = []
        else:
            if row['type'] == 'Pass' and row['outcomeType'] == 'Successful':
                current_passes.append(row)
            elif row['type'] == 'Pass' and row['outcomeType'] != 'Successful':
                if len(current_passes) >= MIN_PASSES:
                    sequences.append(current_passes.copy())
                current_passes = []

    if len(current_passes) >= MIN_PASSES:
        sequences.append(current_passes.copy())

    return sequences


def draw_sequences(ax, sequences, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    if not sequences:
        ax.text(52.5, 34, 'Sin secuencias\nde 12+ pases', color=line_color,
                fontsize=28, ha='center', va='center', path_effects=path_eff)
    else:
        for i, passes in enumerate(sequences):
            seq_col = SEQ_COLORS[i % len(SEQ_COLORS)]
            pass_df = pd.DataFrame(passes)
            pitch.lines(pass_df.x, pass_df.y, pass_df.endX, pass_df.endY,
                        lw=2.5, transparent=True, comet=True, color=seq_col, alpha=0.8, ax=ax)
            pitch.scatter(pass_df.endX, pass_df.endY, s=25, edgecolor=seq_col,
                          linewidth=1, color=bg_color, zorder=2, ax=ax)
            ax.text(pass_df.iloc[-1]['endX'], pass_df.iloc[-1]['endY'],
                    str(len(passes)), color=seq_col, fontsize=11, fontweight='bold',
                    ha='center', va='center', zorder=3, path_effects=path_eff)

    n_seq = len(sequences)
    max_len = max((len(s) for s in sequences), default=0)

    stats_text = f"{n_seq} secuencia{'s' if n_seq != 1 else ''} · máx. {max_len} pases" if sequences else ""

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=13, ha='right', va='center')
        ax.set_title(f"Equipo visitante — Posesiones +{MIN_PASSES} pases\n{stats_text}",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=13, ha='left', va='center')
        ax.set_title(f"Equipo local — Posesiones +{MIN_PASSES} pases\n{stats_text}",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df      = pd.read_csv(PROCESSED_FILE)
    df_sort = sort_events(df)

    hteamID   = df_sort['teamId'].dropna().unique()[0]
    ateamID   = df_sort['teamId'].dropna().unique()[1]
    hteamName = df_sort[df_sort['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df_sort[df_sort['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    h_sequences = find_long_sequences(df_sort, hteamID)
    a_sequences = find_long_sequences(df_sort, ateamID)

    print(f"{hteamName}: {len(h_sequences)} secuencias de {MIN_PASSES}+ pases")
    print(f"{ateamName}: {len(a_sequences)} secuencias de {MIN_PASSES}+ pases")

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_sequences(axes[0], h_sequences, hteamName, ateamName, hcol, path_eff)
    draw_sequences(axes[1], a_sequences, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_posesion_mas12_pases.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
