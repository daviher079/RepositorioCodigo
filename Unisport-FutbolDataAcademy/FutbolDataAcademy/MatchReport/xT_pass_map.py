import os
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# CAMBIA ESTE NOMBRE POR EL ARCHIVO GENERADO CON scraping_datos.py
PROCESSED_FILE = os.path.join(os.path.dirname(__file__), 'Match', 'Real_Madrid_vs_Bayern_2026-04-07_processed.csv')

# Colores equipos
hcol = "#FFFFFF"
acol = '#F50900'

colores = {                                                                                                                                       
    0: '#F50900',  # rojo                                                                                                                         
    1: '#00E5FF',  # cian                                                                                                                         
    2: '#FFD700',  # amarillo dorado    
    3: '#00FF87',  # verde lima                                                                                                                   
    4: '#FF6B35',  # naranja            
    5: '#C77DFF',  # lila                                                                                                                         
    6: '#FF69B4',  # rosa               
    7: '#FFFFFF',  # blanco                                                                                                                       
    8: '#7FFF00',  # verde amarillento                                                                                                            
}


def calcular_valor_pase(df):
    pases = df.copy()
    xT_max = pases['xT'].max()
    pro_max = pases['pro'].max()
    pases['xT_norm'] = pases['xT'] / xT_max if xT_max > 0 else 0
    pases['pro_norm'] = pases['pro'] / pro_max if pro_max > 0 else 0
    pases['valor_pase'] = (pases['xT_norm'] * 0.6) + (pases['pro_norm'] * 0.4)
    return pases


def ranking_por_equipo(pases):
    top20 = pases[['shortName', 'valor_pase', 'x', 'y', 'endX', 'endY']].sort_values('valor_pase', ascending=False).head(20).reset_index(drop=True)
    jugadores = top20['shortName'].unique()
    colores_jugadores = {jugador: list(colores.values())[i % 9] for i, jugador in enumerate(jugadores)}
    top20['color'] = top20['shortName'].apply(lambda x: colores_jugadores[x])  

    color_map = top20.drop_duplicates('shortName').set_index('shortName')['color']
    ranking = top20.groupby('shortName')['valor_pase'].agg(['sum', 'count']).sort_values('sum', ascending=True)
    ranking['color'] = ranking.index.map(color_map)
    return top20, ranking


def plot_xT_pass_map(df, team_id, team_name, ax, pitch):
    pases = df[
        (df['teamId'] == team_id) &
        (df['type'] == 'Pass') &
        (df['outcomeType'] == 'Successful') &
        (df['xT'] > 0) &
        (df['pro'] > 0)
    ].dropna(subset=['x', 'y', 'endX', 'endY', 'xT', 'pro'])

    pases = calcular_valor_pase(pases)
    top20, ranking = ranking_por_equipo(pases)
    max_valor = top20['valor_pase'].max()

    for _, row in top20.iterrows():
        line_width = (row['valor_pase'] / max_valor) * 5
        pitch.arrows(row['x'], row['y'], row['endX'], row['endY'],
                     width=line_width, headwidth=3, headlength=3,
                     color=row['color'], alpha=0.6, ax=ax)

    ax.set_title(f'{team_name}\nxT generado: {pases["xT"].sum().round(2)}',
                 color='white', fontsize=12, pad=10)

    return ranking


def plot_ranking(ranking, ax):
    ax.set_facecolor('#1a1a2e')
    bars = ax.barh(ranking.index, ranking['sum'], color=ranking['color'], alpha=0.8)

    for bar, (_, row) in zip(bars, ranking.iterrows()):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{row['sum']:.2f} ({int(row['count'])} pases)",
                va='center', color='white', fontsize=8)

    ax.tick_params(colors='white', labelsize=9)
    ax.spines[['top', 'right', 'bottom']].set_visible(False)
    ax.set_xlabel('Valor pase acumulado', color='white', fontsize=9)
    ax.set_xlim(0, ranking['sum'].max() * 1.35)


if __name__ == '__main__':
    df = pd.read_csv(PROCESSED_FILE)

    hteamID = df['teamId'].dropna().unique()[0]
    ateamID = df['teamId'].dropna().unique()[1]
    hteamName = df[df['teamId'] == hteamID]['teamName'].iloc[0]
    ateamName = df[df['teamId'] == ateamID]['teamName'].iloc[0]

    pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68,
                  pitch_color='#1a1a2e', line_color='white')

    fig, axes = plt.subplots(2, 2, figsize=(20, 14),
                             gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor('#1a1a2e')

    pitch.draw(ax=axes[0][0])
    pitch.draw(ax=axes[0][1])

    ranking_home = plot_xT_pass_map(df, hteamID, hteamName, axes[0][0], pitch)
    ranking_away = plot_xT_pass_map(df, ateamID, ateamName, axes[0][1], pitch)

    plot_ranking(ranking_home, axes[1][0])
    plot_ranking(ranking_away, axes[1][1])

    fig.suptitle('Mapa de pases por valor (xT + progresividad)', color='white', fontsize=16, y=1.01)
    plt.tight_layout()

    output_img = PROCESSED_FILE.replace('_processed.csv', '_xT_pass_map.png')
    plt.savefig(output_img, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f'Imagen guardada en: {output_img}')
    plt.show()
