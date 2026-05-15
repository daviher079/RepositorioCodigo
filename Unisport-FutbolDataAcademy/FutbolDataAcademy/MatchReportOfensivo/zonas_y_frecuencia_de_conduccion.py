import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color   = '#1a1a2e'
line_color = 'white'
hcol       = '#FFFFFF'
acol       = '#F50900'

CARRY_TYPES = ['TakeOn', 'BallTouch']


def get_carry_df(df, team_id):
    mask = (df['teamId'] == team_id) & (df['type'].isin(CARRY_TYPES))
    return df[mask].copy()


def get_takeon_success_df(df, team_id):
    mask = (
        (df['teamId'] == team_id) &
        (df['type'] == 'TakeOn') &
        (df['outcomeType'] == 'Successful')
    )
    return df[mask].copy()


def draw_carry_zones(ax, carry_df, takeon_df, team_name, away_team_name, col, path_eff):
    pitch = Pitch(pitch_type='uefa', pitch_color=bg_color, line_color=line_color,
                  linewidth=2, corner_arcs=True, goal_type='box', goal_alpha=.5,
                  line_zorder=2)
    pitch.draw(ax=ax)

    if team_name == away_team_name:
        ax.invert_xaxis()
        ax.invert_yaxis()

    cmap = LinearSegmentedColormap.from_list('carry_cmap', [bg_color, col], N=100)

    if len(carry_df) >= 5:
        pitch.kdeplot(carry_df.x, carry_df.y, ax=ax,
                      fill=True, levels=100, thresh=0.05, cut=4, cmap=cmap, alpha=0.7)

    pitch.scatter(carry_df.x, carry_df.y, s=20,
                  color='gray', alpha=0.4, zorder=3, ax=ax)

    if len(takeon_df) > 0:
        pitch.scatter(takeon_df.x, takeon_df.y, s=120,
                      color=col, edgecolors=bg_color, linewidth=1,
                      zorder=4, ax=ax, marker='*')

    total     = len(carry_df)
    takeon_ok = len(takeon_df)
    takeon_all = len(carry_df[carry_df['type'] == 'TakeOn'])
    pct_takeon = int((takeon_ok / takeon_all) * 100) if takeon_all > 0 else 0

    stats = f"Conducciones: {total}  ·  Regates exitosos: {takeon_ok}/{takeon_all} ({pct_takeon}%)"

    if team_name == away_team_name:
        ax.text(0, 73, "<--- Dirección ataque", color=col, size=13, ha='right', va='center')
        ax.text(52.5, -4, stats, color=line_color, fontsize=12, ha='center', va='center')
        ax.set_title("Equipo visitante — Zonas y frecuencia de conducción",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)
    else:
        ax.text(0, -5, "Dirección ataque --->", color=col, size=13, ha='left', va='center')
        ax.text(52.5, 72, stats, color=line_color, fontsize=12, ha='center', va='center')
        ax.set_title("Equipo local — Zonas y frecuencia de conducción",
                     color=line_color, fontsize=24, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    hdf_carry   = get_carry_df(df, hteamID)
    adf_carry   = get_carry_df(df, ateamID)
    hdf_takeon  = get_takeon_success_df(df, hteamID)
    adf_takeon  = get_takeon_success_df(df, ateamID)

    fig, axes = plt.subplots(1, 2, figsize=(24, 12))
    fig.patch.set_facecolor(bg_color)

    draw_carry_zones(axes[0], hdf_carry, hdf_takeon, hteamName, ateamName, hcol, path_eff)
    draw_carry_zones(axes[1], adf_carry, adf_takeon, ateamName, ateamName, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_conduccion.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
