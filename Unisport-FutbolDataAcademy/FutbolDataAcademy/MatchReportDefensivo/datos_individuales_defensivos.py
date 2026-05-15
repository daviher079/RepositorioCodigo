import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

TOP_N = 8

STAT_COLS  = ['Tackles', 'Interc.', 'Recup.', 'Despejes', 'Aéreos']
COL_COLORS = ['#9b59b6', '#e91e63', '#2ecc71', '#607d8b', '#3498db']


def get_short_name(full_name):
    parts = str(full_name).strip().split()
    return full_name if len(parts) == 1 else f"{parts[0][0]}. {' '.join(parts[1:])}"


def get_individual_def_stats(df, team_id):
    players = df[df['teamId'] == team_id]['name'].dropna().unique()
    rows = []
    for name in players:
        pdf = df[df['name'] == name]
        rows.append({
            'name':      name,
            'Tackles':   len(pdf[(pdf['type'] == 'Tackle')  & (pdf['outcomeType'] == 'Successful')]),
            'Interc.':   len(pdf[ pdf['type'] == 'Interception']),
            'Recup.':    len(pdf[ pdf['type'] == 'BallRecovery']),
            'Despejes':  len(pdf[ pdf['type'] == 'Clearance']),
            'Aéreos':    len(pdf[(pdf['type'] == 'Aerial')  & (pdf['outcomeType'] == 'Successful')]),
        })
    result = pd.DataFrame(rows)
    result['Total'] = result[STAT_COLS].sum(axis=1)
    result = result[result['Total'] > 0].sort_values('Total', ascending=False).head(TOP_N).reset_index(drop=True)
    result['shortName'] = result['name'].apply(get_short_name)
    return result


def draw_individual_stats(ax, stats_df, team_name, col, path_eff):
    ax.set_facecolor(bg_color)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(stats_df) - 0.3)
    ax.invert_yaxis()
    ax.axis('off')

    # Encabezado
    headers = ['Jugador'] + STAT_COLS + ['Total']
    x_positions = [0.01, 0.32, 0.44, 0.56, 0.68, 0.80, 0.92]
    for j, (h, x) in enumerate(zip(headers, x_positions)):
        ha = 'left' if j == 0 else 'center'
        color = COL_COLORS[j - 1] if 1 <= j <= len(STAT_COLS) else line_color
        ax.text(x, -0.3, h, color=color, fontsize=12, fontweight='bold',
                ha=ha, va='center', transform=ax.transData)

    ax.axhline(y=0.2, color='gray', linewidth=0.5, alpha=0.5)

    max_total = stats_df['Total'].max() if len(stats_df) > 0 else 1

    for i, row in stats_df.iterrows():
        y = i
        # Fondo de fila alternado
        if i % 2 == 0:
            ax.axhspan(y - 0.45, y + 0.45, color='white', alpha=0.03)

        # Nombre
        ax.text(x_positions[0], y, row['shortName'], color=line_color,
                fontsize=12, ha='left', va='center')

        # Valores por columna
        for j, (col_name, x, bar_color) in enumerate(zip(STAT_COLS, x_positions[1:], COL_COLORS)):
            val = int(row[col_name])
            ax.text(x, y, str(val), color=bar_color, fontsize=13,
                    fontweight='bold', ha='center', va='center')

        # Total con mini-barra
        total = int(row['Total'])
        bar_w = (total / max_total) * 0.07
        ax.barh(y, bar_w, height=0.55, left=x_positions[-1] - 0.01,
                color=col, alpha=0.35)
        ax.text(x_positions[-1], y, str(total), color=col, fontsize=13,
                fontweight='bold', ha='center', va='center')

    ax.set_title(f"Datos individuales defensivos — {team_name}",
                 color=line_color, fontsize=16, fontweight='bold',
                 pad=12, path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf = get_individual_def_stats(df, hteamID)
    adf = get_individual_def_stats(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(22, 8))
    fig.patch.set_facecolor(bg_color)

    draw_individual_stats(axes[0], hdf, hteamName, hcol, path_eff)
    draw_individual_stats(axes[1], adf, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_datos_individuales_defensivos.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
