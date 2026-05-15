import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgba
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

DEF_TYPES = ['BallRecovery', 'Interception', 'Clearance']


def get_defensive_network_df(df, team_id):
    tackle_ok = (df['type'] == 'Tackle') & (df['outcomeType'] == 'Successful')
    def_mask  = df['type'].isin(DEF_TYPES) | tackle_ok
    def_df    = df[(df['teamId'] == team_id) & def_mask].copy()

    node_df = def_df.groupby('playerId').agg(
        actions  = ('x', 'count'),
        avg_x    = ('x', 'median'),
        avg_y    = ('y', 'median'),
    ).reset_index()

    meta = df[df['teamId'] == team_id][['playerId', 'shirtNo', 'name', 'isFirstEleven']].drop_duplicates('playerId')
    node_df = node_df.merge(meta, on='playerId', how='left')

    return node_df


def draw_defensive_network(ax, node_df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5)
    pitch.draw(ax=ax)

    is_away = team_name == away_team_name
    if is_away:
        ax.invert_xaxis()
        ax.invert_yaxis()

    # Tamaño de nodo proporcional a acciones (mín 400, máx 2000)
    max_actions = node_df['actions'].max()
    node_df = node_df.copy().reset_index(drop=True)
    node_df['node_size'] = (node_df['actions'] / max_actions) * 1600 + 400

    # Conexiones: cada jugador con sus 3 vecinos más cercanos por distancia euclídea
    MAX_LINE_WIDTH = 8
    coords = node_df[['avg_x', 'avg_y']].values
    n = len(node_df)
    drawn_pairs = set()

    for i in range(n):
        dists = np.sqrt(((coords - coords[i]) ** 2).sum(axis=1))
        dists[i] = np.inf
        nearest = np.argsort(dists)[:3]
        for j in nearest:
            pair = (min(i, j), max(i, j))
            if pair in drawn_pairs:
                continue
            drawn_pairs.add(pair)
            d = dists[j]
            lw = max(1, MAX_LINE_WIDTH - d / 8)
            alpha = max(0.1, 0.7 - d / 60)
            pitch.lines(coords[i, 0], coords[i, 1],
                        coords[j, 0], coords[j, 1],
                        lw=lw, color=col, alpha=alpha, zorder=1, ax=ax)

    # Transparencia de nodo proporcional a acciones
    color_rgba = np.array(to_rgba(col))
    color_arr  = np.tile(color_rgba, (n, 1))
    transparency = (node_df['actions'] / max_actions) * 0.75 + 0.25
    color_arr[:, 3] = transparency.values

    for i, row in node_df.iterrows():
        marker = 'o' if row['isFirstEleven'] else 's'
        pitch.scatter(row['avg_x'], row['avg_y'],
                      s=row['node_size'], marker=marker,
                      color=color_arr[i], edgecolor=line_color,
                      linewidth=1.5, zorder=3, ax=ax)

    for _, row in node_df.iterrows():
        pitch.annotate(str(int(row['shirtNo'])),
                       xy=(row['avg_x'], row['avg_y']),
                       c=bg_color, ha='center', va='center',
                       size=14, fontweight='bold', ax=ax)

    avg_def_x = node_df['avg_x'].median()
    avg_def_x_show = round(avg_def_x * 1.05, 1)
    ax.axvline(x=avg_def_x, color='gray', linestyle='--', alpha=0.75, linewidth=2)

    total_actions = node_df['actions'].sum()

    if is_away:
        ax.text(avg_def_x + 1, 72, f"{avg_def_x_show}m",
                fontsize=13, color=line_color, ha='right', path_effects=path_eff)
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=15, ha='right', va='center')
        ax.text(2, 2, "○ titular  □ suplente", color=col, size=12, ha='right', va='bottom')
        ax.text(52.5, -3, f"Acciones defensivas totales: {total_actions}",
                color=col, fontsize=13, ha='center', path_effects=path_eff)
        ax.set_title("Red defensiva - Equipo visitante", color=line_color,
                     fontsize=30, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(avg_def_x + 1, -4, f"{avg_def_x_show}m",
                fontsize=13, color=line_color, ha='left', path_effects=path_eff)
        ax.text(0, -5, "Dirección ataque --->", color=col, size=15, ha='left', va='center')
        ax.text(103, 66, "○ titular  □ suplente", color=col, size=12, ha='right', va='top')
        ax.text(52.5, 71, f"Acciones defensivas totales: {total_actions}",
                color=col, fontsize=13, ha='center', path_effects=path_eff)
        ax.set_title("Red defensiva - Equipo local", color=line_color,
                     fontsize=30, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_defensive_network_df(df, hteamID)
    adf = get_defensive_network_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_defensive_network(axes[0], hdf, hteamName, ateamName, hcol, path_eff)
    draw_defensive_network(axes[1], adf, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_red_defensiva.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
