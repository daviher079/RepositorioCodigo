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

MAX_PASSES = 8  # máximo de pases hacia atrás a buscar por gol

PERIOD_ORDER = {'FirstHalf': 1, 'SecondHalf': 2, 'FirstPeriodOfExtraTime': 3, 'SecondPeriodOfExtraTime': 4}


def sort_events(df):
    df = df.copy()
    df['period_order'] = df['period'].map(PERIOD_ORDER).fillna(5)
    return df.sort_values(['period_order', 'expandedMinute', 'second']).reset_index(drop=True)


def get_goals(df, team_id):
    mask = (
        (df['teamId'] == team_id) &
        (df['type'] == 'Goal') &
        (~df['qualifiers'].str.contains('OwnGoal', na=False))
    )
    return df[mask]


def get_sequence_before_goal(df_sorted, goal_pos, goal_team_id):
    sequence = []
    i = goal_pos - 1
    while i >= 0 and len(sequence) < MAX_PASSES:
        row = df_sorted.iloc[i]
        if row['teamId'] != goal_team_id:
            break  # cambio de posesión: fin de la secuencia
        if row['type'] == 'Pass' and row['outcomeType'] == 'Successful':
            sequence.insert(0, row)
        i -= 1
    return sequence


def draw_sequence(ax, passes, goal_row, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    for i, row in enumerate(passes):
        pitch.lines(row['x'], row['y'], row['endX'], row['endY'],
                    lw=3, transparent=True, comet=True, color=col, alpha=0.8, ax=ax)
        pitch.scatter(row['endX'], row['endY'], s=300, color=bg_color,
                      edgecolor=col, linewidth=1.5, zorder=3, ax=ax)
        ax.text(row['endX'], row['endY'], str(i + 1),
                color=line_color, fontsize=13, ha='center', va='center',
                fontweight='bold', zorder=4, path_effects=path_eff)

    # marcador de gol
    pitch.scatter(goal_row['x'], goal_row['y'], s=500, marker='*',
                  color='gold', zorder=5, ax=ax, edgecolors=bg_color, linewidth=1)

    scorer  = goal_row.get('shortName', '')
    minute  = int(goal_row['expandedMinute'])
    n_passes = len(passes)

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=13, ha='right', va='center')
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=13, ha='left', va='center')

    ax.set_title(
        f"{team_name}  ·  min. {minute}'  ·  {scorer}\n{n_passes} pases previos al gol",
        color=line_color, fontsize=22, fontweight='bold', path_effects=path_eff
    )


if __name__ == '__main__':
    df      = pd.read_csv(PROCESSED_FILE)
    df_sort = sort_events(df)

    hteamID   = df_sort['teamId'].dropna().unique()[0]
    ateamID   = df_sort['teamId'].dropna().unique()[1]
    hteamName = df_sort[df_sort['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df_sort[df_sort['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    h_goals = get_goals(df_sort, hteamID)
    a_goals = get_goals(df_sort, ateamID)

    all_goals = (
        [(row, hteamName, hcol) for _, row in h_goals.iterrows()] +
        [(row, ateamName, acol) for _, row in a_goals.iterrows()]
    )

    if not all_goals:
        print("No hay goles en este partido.")
        exit()

    n = len(all_goals)
    fig, axes = plt.subplots(1, n, figsize=(14 * n, 12))
    fig.patch.set_facecolor(bg_color)
    if n == 1:
        axes = [axes]

    for ax, (goal_row, team_name, col) in zip(axes, all_goals):
        goal_pos = df_sort.index[df_sort.index == goal_row.name][0]
        sequence = get_sequence_before_goal(df_sort, goal_pos, goal_row['teamId'])
        draw_sequence(ax, sequence, goal_row, team_name, ateamName, col, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_secuencia_pases_gol.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
