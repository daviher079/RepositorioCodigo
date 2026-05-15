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

CONN_COLORS = ['#FFD700', '#C0C0C0', '#CD7F32']  # oro, plata, bronce
CONN_WIDTHS = [9, 6, 4]


def get_top_connections(df, team_id, top_n=3):
    team_passes = df[
        (df['teamId'] == team_id) &
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful')
    ].copy()

    team_passes['receiver']      = df['shortName'].shift(-1)
    team_passes['receiver_team'] = df['teamId'].shift(-1)

    team_passes = team_passes[team_passes['receiver_team'] == team_id]
    team_passes = team_passes.dropna(subset=['shortName', 'receiver'])
    team_passes = team_passes[team_passes['shortName'] != team_passes['receiver']]

    connections = (
        team_passes
        .groupby(['shortName', 'receiver'])
        .size()
        .reset_index(name='pass_count')
        .nlargest(top_n, 'pass_count')
        .reset_index(drop=True)
    )
    return connections


def get_avg_positions(df, team_id):
    team_df = df[df['teamId'] == team_id]
    return team_df.groupby('shortName').agg(
        avg_x=('x', 'median'),
        avg_y=('y', 'median')
    )


def draw_top_connections(ax, connections, positions, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    # todos los jugadores en gris tenue
    for name, row in positions.iterrows():
        pitch.scatter(row['avg_x'], row['avg_y'], s=150, color=bg_color,
                      edgecolor='gray', linewidth=1, alpha=0.4, zorder=2, ax=ax)

    drawn_players = {}

    for i, conn in connections.iterrows():
        passer   = conn['shortName']
        receiver = conn['receiver']

        if passer not in positions.index or receiver not in positions.index:
            continue

        p1        = positions.loc[passer]
        p2        = positions.loc[receiver]
        conn_col  = CONN_COLORS[i]
        lw        = CONN_WIDTHS[i]

        pitch.lines(p1['avg_x'], p1['avg_y'], p2['avg_x'], p2['avg_y'],
                    lw=lw, color=conn_col, alpha=0.85, zorder=3, ax=ax)

        mid_x = (p1['avg_x'] + p2['avg_x']) / 2
        mid_y = (p1['avg_y'] + p2['avg_y']) / 2
        ax.text(mid_x, mid_y, str(conn['pass_count']),
                color=conn_col, fontsize=14, fontweight='bold',
                ha='center', va='center', zorder=6, path_effects=path_eff)

        for name, pos in [(passer, p1), (receiver, p2)]:
            drawn_players[name] = (pos['avg_x'], pos['avg_y'], conn_col)

    for name, (x, y, c) in drawn_players.items():
        pitch.scatter(x, y, s=700, color=bg_color, edgecolor=c,
                      linewidth=2.5, zorder=4, ax=ax)
        ax.text(x, y, name, color=c, fontsize=8, fontweight='bold',
                ha='center', va='center', zorder=5, path_effects=path_eff)

    medal_labels = ['🥇', '🥈', '🥉']
    for i, conn in connections.iterrows():
        ax.text(2, 66 - i * 6,
                f"{medal_labels[i]}  {conn['shortName']} ↔ {conn['receiver']}  ({conn['pass_count']} pases)",
                color=CONN_COLORS[i], fontsize=13, va='center', path_effects=path_eff)

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=13, ha='right', va='center')
        ax.set_title(f"Top 3 conexiones — Equipo visitante",
                     color=line_color, fontsize=28, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=13, ha='left', va='center')
        ax.set_title(f"Top 3 conexiones — Equipo local",
                     color=line_color, fontsize=28, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf_conn = get_top_connections(df, hteamID)
    adf_conn = get_top_connections(df, ateamID)
    hdf_pos  = get_avg_positions(df, hteamID)
    adf_pos  = get_avg_positions(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_top_connections(axes[0], hdf_conn, hdf_pos, hteamName, ateamName, hcol, path_eff)
    draw_top_connections(axes[1], adf_conn, adf_pos, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_top3_conexiones.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
