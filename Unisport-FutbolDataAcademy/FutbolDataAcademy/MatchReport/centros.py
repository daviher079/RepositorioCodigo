import os
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def get_crosses(df, hteamID, ateamID):
    mask = (df['type'] == 'Pass') & \
           (df['qualifiers'].str.contains('Cross',  na=False)) & \
          (~df['qualifiers'].str.contains('Corner', na=False))

    home_cross = df[(df['teamId'] == hteamID) & mask]
    away_cross = df[(df['teamId'] == ateamID) & mask]

    return home_cross, away_cross


def _draw_cross_arrows(ax, cross_df, invert):
    suc = 0
    unsuc = 0
    for _, row in cross_df.iterrows():
        if invert:
            x0, y0 = 105 - row['x'],    68 - row['y']
            x1, y1 = 105 - row['endX'], 68 - row['endY']
        else:
            x0, y0 = row['x'],    row['y']
            x1, y1 = row['endX'], row['endY']

        if row['outcomeType'] == 'Successful':
            arrow = patches.FancyArrowPatch((x0, y0), (x1, y1),
                                            arrowstyle='->', mutation_scale=15,
                                            color='green', linewidth=1.5, alpha=1)
            suc += 1
        else:
            arrow = patches.FancyArrowPatch((x0, y0), (x1, y1),
                                            arrowstyle='->', mutation_scale=10,
                                            color='red', linewidth=1.5, alpha=.65)
            unsuc += 1
        ax.add_patch(arrow)

    return suc, unsuc


def draw_crosses(ax, home_cross, away_cross, path_eff):
    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.75, corner_arcs=True,
                  pitch_color=bg_color, line_color=line_color, linewidth=2)
    pitch.draw(ax=ax)
    ax.set_ylim(-0.5, 68.5)
    ax.set_xlim(-0.5, 105.5)

    hsuc, hunsuc = _draw_cross_arrows(ax, home_cross, invert=False)
    asuc, aunsuc = _draw_cross_arrows(ax, away_cross, invert=True)

    home_left  = len(home_cross[home_cross['y'] >= 34])
    home_right = len(home_cross[home_cross['y'] <  34])
    away_left  = len(away_cross[away_cross['y'] >= 34])
    away_right = len(away_cross[away_cross['y'] <  34])

    ax.text(51, 2,  f"Centros desde\nIzquierda: {home_left}",  color=hcol, fontsize=15, va='bottom', ha='right')
    ax.text(51, 66, f"Centros desde\nDerecha: {home_right}",   color=hcol, fontsize=15, va='top',    ha='right')
    ax.text(54, 66, f"Centros desde\nIzquierda: {away_left}",  color=acol, fontsize=15, va='top',    ha='left')
    ax.text(54, 2,  f"Centros desde\nDerecha: {away_right}",   color=acol, fontsize=15, va='bottom', ha='left')

    ax.text(0,   -2,   f"Eficaces: {hsuc}",    color='green', fontsize=20, ha='left',  va='top')
    ax.text(0,   -5.5, f"Ineficaces: {hunsuc}", color='red',   fontsize=20, ha='left',  va='top')
    ax.text(105, -2,   f"Eficaces: {asuc}",    color='green', fontsize=20, ha='right', va='top')
    ax.text(105, -5.5, f"Ineficaces: {aunsuc}", color='red',   fontsize=20, ha='right', va='top')

    ax.text(0,   70, "Centros Equipo local",     color=hcol, size=25, ha='left',  fontweight='bold', path_effects=path_eff)
    ax.text(105, 70, "Centros Equipo visitante", color=acol, size=25, ha='right', fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    home_cross, away_cross = get_crosses(df, hteamID, ateamID)

    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    draw_crosses(ax, home_cross, away_cross, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_centros.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
