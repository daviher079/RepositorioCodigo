import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def get_shots_df(df):
    mask = (
        (df['type'] == 'Goal') |
        (df['type'] == 'MissedShots') |
        (df['type'] == 'SavedShot') |
        (df['type'] == 'ShotOnPost')
    )
    return df[mask].copy().reset_index(drop=True)


def draw_goalkeeper_performance(ax, shots_df, hteamID, ateamID, hteamName, ateamName, path_eff, hxgot=None, axgot=None):
    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.75, corner_arcs=True,
                  pitch_color=bg_color, line_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)

    hShotsdf = shots_df[shots_df['teamId'] == hteamID].copy()
    aShotsdf = shots_df[shots_df['teamId'] == ateamID].copy()

    hShotsdf['goalMouthZ'] = hShotsdf['goalMouthZ'] * 0.75
    aShotsdf['goalMouthZ'] = (aShotsdf['goalMouthZ'] * 0.75) + 38
    hShotsdf['goalMouthY'] = (37.66 - hShotsdf['goalMouthY']) * 12.295
    aShotsdf['goalMouthY'] = (37.66 - aShotsdf['goalMouthY']) * 12.295

    ax.plot([0, 0],   [-1, 30],  color=line_color, linewidth=5)
    ax.plot([0, 90],  [30, 30],  color=line_color, linewidth=5)
    ax.plot([90, 90], [30, -1],  color=line_color, linewidth=5)
    ax.plot([-2, 92], [-2, -2],  color=line_color, linewidth=3)
    ax.plot([0, 0],   [37, 68],  color=line_color, linewidth=5)
    ax.plot([0, 90],  [68, 68],  color=line_color, linewidth=5)
    ax.plot([90, 90], [68, 37],  color=line_color, linewidth=5)
    ax.plot([-2, 92], [36, 36],  color=line_color, linewidth=3)

    hSavedf = hShotsdf[(hShotsdf['type'] == 'SavedShot') & (~hShotsdf['qualifiers'].str.contains(': 82,', na=False))]
    hGoaldf = hShotsdf[(hShotsdf['type'] == 'Goal')      & (~hShotsdf['qualifiers'].str.contains('OwnGoal', na=False))]
    hPostdf = hShotsdf[hShotsdf['type'] == 'ShotOnPost']
    aSavedf = aShotsdf[(aShotsdf['type'] == 'SavedShot') & (~aShotsdf['qualifiers'].str.contains(': 82,', na=False))]
    aGoaldf = aShotsdf[(aShotsdf['type'] == 'Goal')      & (~aShotsdf['qualifiers'].str.contains('OwnGoal', na=False))]
    aPostdf = aShotsdf[aShotsdf['type'] == 'ShotOnPost']

    pitch.scatter(hSavedf.goalMouthY, hSavedf.goalMouthZ, marker='o',       c='None', edgecolor=acol,     hatch='/////', s=400, ax=ax)
    pitch.scatter(hGoaldf.goalMouthY, hGoaldf.goalMouthZ, marker='football', c='None', edgecolors='green', s=550, ax=ax)
    pitch.scatter(hPostdf.goalMouthY, hPostdf.goalMouthZ, marker='o',        c='None', edgecolors='orange', hatch='/////', s=400, ax=ax)
    pitch.scatter(aSavedf.goalMouthY, aSavedf.goalMouthZ, marker='o',        c='None', edgecolor=hcol,     hatch='/////', s=400, ax=ax)
    pitch.scatter(aGoaldf.goalMouthY, aGoaldf.goalMouthZ, marker='football', c='None', edgecolors='green', s=550, ax=ax)
    pitch.scatter(aPostdf.goalMouthY, aPostdf.goalMouthZ, marker='o',        c='None', edgecolors='orange', hatch='/////', s=400, ax=ax)

    ax.text(0, 70, f"Paradas - Portero local ({hteamName})",     color=hcol, fontsize=25, ha='left', fontweight='bold', path_effects=path_eff)
    ax.text(0, -3, f"Paradas - Portero visitante ({ateamName})", color=acol, fontsize=25, ha='left', va='top', fontweight='bold', path_effects=path_eff)

    axgot_text = f"xGOT = {axgot}\nGoles evitados = {round(axgot - len(aGoaldf), 2)}\n" if axgot is not None else ""
    ax.text(92, 68, f"{axgot_text}Paradas = {len(hSavedf)}\nGoles concedidos = {len(hGoaldf)}", color=hcol, fontsize=15, va='top', ha='left')

    hxgot_text = f"xGOT = {hxgot}\nGoles evitados = {round(hxgot - len(hGoaldf), 2)}\n" if hxgot is not None else ""
    ax.text(92, 30, f"{hxgot_text}Paradas = {len(aSavedf)}\nGoles concedidos = {len(aGoaldf)}", color=acol, fontsize=15, va='top', ha='left')

    pitch.scatter(94, 53, marker='football', c='None', edgecolors='green',  s=150, ax=ax)
    pitch.scatter(94, 48, marker='o',        c='None', edgecolor=hcol,      hatch='/////', s=150, ax=ax)
    pitch.scatter(94, 43, marker='o',        c='None', edgecolors='orange', hatch='/////', s=150, ax=ax)
    pitch.scatter(94, 15, marker='football', c='None', edgecolors='green',  s=150, ax=ax)
    pitch.scatter(94, 10, marker='o',        c='None', edgecolor=acol,      hatch='/////', s=150, ax=ax)
    pitch.scatter(94, 5,  marker='o',        c='None', edgecolors='orange', hatch='/////', s=150, ax=ax)

    ax.text(96, 53, "Goles concedidos", color='green',  fontsize=15, va='center')
    ax.text(96, 48, "Tiros parados",    color=hcol,     fontsize=15, va='center')
    ax.text(96, 43, "Tiros al poste",   color='orange', fontsize=15, va='center')
    ax.text(96, 15, "Goles concedidos", color='green',  fontsize=15, va='center')
    ax.text(96, 10, "Tiros parados",    color=acol,     fontsize=15, va='center')
    ax.text(96, 5,  "Tiros al poste",   color='orange', fontsize=15, va='center')


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    # xGOT manual desde FotMob — dejar None si no se dispone
    hxgot = None
    axgot = None

    shots_df = get_shots_df(df)

    fig, ax = plt.subplots(figsize=(20, 12))
    fig.patch.set_facecolor(bg_color)

    draw_goalkeeper_performance(ax, shots_df, hteamID, ateamID, hteamName, ateamName, path_eff,
                                hxgot=hxgot, axgot=axgot)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_portero_rendimiento.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
