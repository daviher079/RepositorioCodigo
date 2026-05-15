import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch

from estadisticas_pases import get_pass_stats


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def get_defensive_stats(df, hteamID, ateamID):
    hdf = df[df['teamId'] == hteamID]
    adf = df[df['teamId'] == ateamID]

    return {
        'htkl':  len(hdf[hdf['type'] == 'Tackle']),
        'htklw': len(hdf[(hdf['type'] == 'Tackle') & (hdf['outcomeType'] == 'Successful')]),
        'hintc': len(hdf[hdf['type'] == 'Interception']),
        'hclr':  len(hdf[hdf['type'] == 'Clearance']),
        'harl':  len(hdf[hdf['type'] == 'Aerial']),
        'harlw': len(hdf[(hdf['type'] == 'Aerial') & (hdf['outcomeType'] == 'Successful')]),
        'hblrc': len(hdf[hdf['type'] == 'BallRecovery']),
        'hblkp': len(hdf[hdf['type'] == 'BlockedPass']),
        'hofs':  len(hdf[hdf['type'] == 'OffsideGiven']),
        'hfoul': len(hdf[hdf['type'] == 'Foul']),

        'atkl':  len(adf[adf['type'] == 'Tackle']),
        'atklw': len(adf[(adf['type'] == 'Tackle') & (adf['outcomeType'] == 'Successful')]),
        'aintc': len(adf[adf['type'] == 'Interception']),
        'aclr':  len(adf[adf['type'] == 'Clearance']),
        'aarl':  len(adf[adf['type'] == 'Aerial']),
        'aarlw': len(adf[(adf['type'] == 'Aerial') & (adf['outcomeType'] == 'Successful')]),
        'ablrc': len(adf[adf['type'] == 'BallRecovery']),
        'ablkp': len(adf[adf['type'] == 'BlockedPass']),
        'aofs':  len(adf[adf['type'] == 'OffsideGiven']),
        'afoul': len(adf[adf['type'] == 'Foul']),
    }


def _safe_bar(a, b, scale=45):
    total = a + b
    return (-(a / total) * scale, (b / total) * scale) if total > 0 else (0.0, 0.0)


def plot_match_stats(ax, ps, ds, path_eff):
    pitch = Pitch(pitch_type='uefa', goal_type='box', goal_alpha=.75, corner_arcs=True,
                  pitch_color=bg_color, line_color=bg_color, linewidth=2)
    pitch.draw(ax=ax)

    ax.fill([0, 0, 105, 105], [62, 68, 68, 62], 'yellow')
    ax.text(52.5, 64.5, "Estadísticas", ha='center', va='center',
            color=line_color, fontsize=25, fontweight='bold', path_effects=path_eff)

    rows = [
        ("Posesión",                ps['hposs'],       ps['aposs'],
         f"{int(ps['hposs'])}%",                       f"{int(ps['aposs'])}%"),
        ("Inclinación",             ps['hft'],          ps['aft'],
         f"{int(ps['hft'])}%",                          f"{int(ps['aft'])}%"),
        ("Pases (Buenos)",          ps['htotal_pass'],  ps['atotal_pass'],
         f"{ps['htotal_pass']}({ps['hacc_pass']})",     f"{ps['atotal_pass']}({ps['aacc_pass']})"),
        ("Balones Largos (Buenos)", ps['hlong_b'],      ps['along_b'],
         f"{ps['hlong_b']}({ps['hacc_long_b']})",       f"{ps['along_b']}({ps['aacc_long_b']})"),
        ("Córners",                 ps['hcor'],         ps['acor'],
         f"{ps['hcor']}",                               f"{ps['acor']}"),
        ("Distancia Pases portero", ps['hglkl'],        ps['aglkl'],
         f"{ps['hglkl']}",                              f"{ps['aglkl']}"),
        ("Entradas (Ganadas)",      ds['htkl'],         ds['atkl'],
         f"{ds['htkl']}({ds['htklw']})",                f"{ds['atkl']}({ds['atklw']})"),
        ("Anticipaciones",          ds['hintc'],        ds['aintc'],
         f"{ds['hintc']}",                              f"{ds['aintc']}"),
        ("Despejes",                ds['hclr'],         ds['aclr'],
         f"{ds['hclr']}",                               f"{ds['aclr']}"),
        ("Duelos aéreos (Ganados)", ds['harl'],         ds['aarl'],
         f"{ds['harl']}({ds['harlw']})",                f"{ds['aarl']}({ds['aarlw']})"),
        ("Recuperaciones",          ds['hblrc'],        ds['ablrc'],
         f"{ds['hblrc']}",                              f"{ds['ablrc']}"),
    ]

    for i, (label, hval, aval, h_txt, a_txt) in enumerate(rows):
        y = 58 - i * 6
        hn, an = _safe_bar(hval, aval)
        ax.barh(y, hn, height=4, color=hcol, left=52.5)
        ax.barh(y, an, height=4, color=acol,  left=52.5)
        ax.text(52.5, y, label,  color=line_color, fontsize=17, ha='center', va='center',
                fontweight='bold', path_effects=path_eff)
        ax.text(7.5,  y, h_txt, color=line_color, fontsize=20, ha='right',  va='center', fontweight='bold')
        ax.text(97.5, y, a_txt, color=line_color, fontsize=20, ha='left',   va='center', fontweight='bold')

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(bottom=False, top=False, left=False, right=False)
    ax.set_xticks([])
    ax.set_yticks([])


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    ps = get_pass_stats(df, hteamID, ateamID)
    ds = get_defensive_stats(df, hteamID, ateamID)

    fig, ax = plt.subplots(figsize=(12, 14))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    plot_match_stats(ax, ps, ds, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_defensive_stats.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
