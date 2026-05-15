import os
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd


PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

bg_color = '#1a1a2e'
line_color = 'white'
hcol = "#FFFFFF"
acol = '#F50900'


def get_momentum_df(df, ateamID):
    # .copy() evita el bug del original: multiplicar por -1 dos veces daba valores incorrectos
    momentum = df[df['xT'].notna()].copy()
    momentum.loc[momentum['teamId'] == ateamID, 'xT'] *= -1
    momentum = momentum.groupby('minute')['xT'].mean().reset_index()
    momentum.columns = ['minute', 'average_xT']
    momentum['average_xT'] = momentum['average_xT'].fillna(0)
    return momentum


def draw_momentum(ax, momentum_df, df, hteamID, ateamID, hcol, acol, path_eff):
    homedf = df[df['teamId'] == hteamID]
    awaydf = df[df['teamId'] == ateamID]

    hxT = round(homedf['xT'].sum(), 3)
    axT = round(awaydf['xT'].sum(), 3)

    colors = [hcol if x > 0 else acol for x in momentum_df['average_xT']]

    hgoal_list = homedf[(homedf['type'] == 'Goal') & (~homedf['qualifiers'].str.contains('OwnGoal', na=False))]['minute'].tolist()
    agoal_list = awaydf[(awaydf['type'] == 'Goal') & (~awaydf['qualifiers'].str.contains('OwnGoal', na=False))]['minute'].tolist()
    hog_list   = homedf[(homedf['type'] == 'Goal') & (homedf['qualifiers'].str.contains('OwnGoal', na=False))]['minute'].tolist()
    aog_list   = awaydf[(awaydf['type'] == 'Goal') & (awaydf['qualifiers'].str.contains('OwnGoal', na=False))]['minute'].tolist()

    highest_xT     = momentum_df['average_xT'].max()
    lowest_xT      = momentum_df['average_xT'].min()
    highest_minute = momentum_df['minute'].max()

    if hgoal_list:
        ax.scatter(hgoal_list, [highest_xT] * len(hgoal_list), s=250, c='None', edgecolor='green',  hatch='////', marker='o')
    if agoal_list:
        ax.scatter(agoal_list, [lowest_xT]  * len(agoal_list), s=250, c='None', edgecolor='green',  hatch='////', marker='o')
    if hog_list:
        ax.scatter(hog_list,   [lowest_xT]  * len(hog_list),   s=250, c='None', edgecolor='orange', hatch='////', marker='o')
    if aog_list:
        ax.scatter(aog_list,   [highest_xT] * len(aog_list),   s=250, c='None', edgecolor='orange', hatch='////', marker='o')

    ax.bar(momentum_df['minute'], momentum_df['average_xT'], color=colors)
    ax.axvline(45, color='gray', linewidth=2, linestyle='dashed')
    ax.axhline(y=0, color=line_color, linewidth=2)

    ax.set_facecolor(bg_color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='x', colors=line_color)
    ax.tick_params(axis='y', colors=line_color)

    ax.set_xlabel('Minuto', color=line_color, fontsize=20)
    ax.set_ylabel('xT medio por minuto', color=line_color, fontsize=20)

    ax.text(highest_minute + 1, highest_xT, f"Equipo local\nxT: {hxT}",     color=hcol, fontsize=20, va='bottom', ha='left')
    ax.text(highest_minute + 1, lowest_xT,  f"Equipo visitante\nxT: {axT}", color=acol, fontsize=20, va='top',    ha='left')

    ax.set_title('xT — Control y dominio del juego', color=line_color, fontsize=30, fontweight='bold', path_effects=path_eff)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID   = df['teamId'].dropna().unique()[0]
    ateamID   = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    path_eff = [path_effects.Stroke(linewidth=3, foreground=bg_color), path_effects.Normal()]

    momentum_df = get_momentum_df(df, ateamID)

    fig, ax = plt.subplots(figsize=(24, 8))
    fig.patch.set_facecolor(bg_color)

    draw_momentum(ax, momentum_df, df, hteamID, ateamID, hcol, acol, path_eff)

    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_momentum_xT.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
