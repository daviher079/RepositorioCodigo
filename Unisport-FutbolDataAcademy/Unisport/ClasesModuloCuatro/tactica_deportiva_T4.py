# ── IMPORTS ─────────────────────────────────────────────────────────────────
# Ejecuta esta celda primero (Shift + Enter)
# statsbombpy ya debe estar instalado desde Anaconda Prompt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import warnings
warnings.filterwarnings('ignore')

from statsbombpy import sb
print('✅ Librerías cargadas correctamente')
print('   → pandas, numpy, matplotlib, statsbombpy')

# Cargar todas las competiciones disponibles
competitions = sb.competitions()

print(f'📁 Total de competiciones/temporadas disponibles: {len(competitions)}')
print()

# Mostrar lista única de competiciones
lista = competitions[['competition_name', 'season_name']].drop_duplicates().sort_values('competition_name')
print(lista.to_string(index=False))

# Filtrar solo Champions League
champions = competitions[
    competitions['competition_name'].str.contains('Champions', na=False)
]
print('Champions League disponible:')
print(champions[['competition_id', 'competition_name', 'season_id', 'season_name']].to_string(index=False))

# Seleccionar la temporada 2018/19
temporada = champions[champions['season_name'].str.contains('2018', na=False)]

if len(temporada) == 0:
    temporada = champions.iloc[[0]]  # Usar la primera disponible
    
comp_id = temporada['competition_id'].values[0]
seas_id = temporada['season_id'].values[0]
nombre_temp = temporada['season_name'].values[0]

print(f'\n⚽ Cargando partidos: Champions League {nombre_temp}...')
matches = sb.matches(competition_id=comp_id, season_id=seas_id)
print(f'✅ Partidos encontrados: {len(matches)}')
print()
print(matches[['home_team', 'away_team', 'home_score', 'away_score']].head(12).to_string(index=False))

# Buscar Liverpool vs Barcelona
lfc_barca = matches[
    ((matches['home_team'] == 'Liverpool') & (matches['away_team'] == 'Barcelona')) |
    ((matches['home_team'] == 'Barcelona') & (matches['away_team'] == 'Liverpool'))
]

if len(lfc_barca) > 0:
    partido = lfc_barca.iloc[0]
    print(f'🎯 Partido encontrado:')
    print(f'   {partido["home_team"]} {partido["home_score"]} - {partido["away_score"]} {partido["away_team"]}')
else:
    # Usar el primer partido disponible si no encontramos ese
    partido = matches.iloc[0]
    print(f'ℹ️  Usando partido: {partido["home_team"]} vs {partido["away_team"]}')

match_id = partido['match_id']

print('\n⏳ Cargando eventos del partido (puede tardar unos segundos)...')
events = sb.events(match_id=match_id)
print(f'✅ Total de eventos cargados: {len(events)}')
print()
print('📋 Tipos de eventos registrados:')
print(events['type'].value_counts().head(12).to_string())

# Ver la estructura de un evento individual
print('🔬 Estructura de un evento de tipo Pass:')
ejemplo_pase = events[events['type'] == 'Pass'].iloc[0]
print(ejemplo_pase[['type', 'minute', 'player', 'team', 'location', 'pass_recipient', 'pass_outcome']].to_string())
print()

# Ver jugadores disponibles
equipos = events['team'].dropna().unique()
print(f'\n🏟️  Equipos: {equipos[0]} vs {equipos[1]}')
print()

for equipo in equipos:
    print(f'─── {equipo} ───────────────────')
    jugadores_eq = events[events['team'] == equipo]['player'].dropna().unique()
    for j in sorted(jugadores_eq):
        n = len(events[events['player'] == j])
        print(f'  {j}: {n} acciones')
    print()

# ─────────────────────────────────────────────────────────────────────────────
# 👉 CAMBIA ESTE NOMBRE por el jugador que quieras analizar
#    (copia el nombre exactamente como aparece en la lista de arriba)
# ─────────────────────────────────────────────────────────────────────────────
equipos = events['team'].dropna().unique()
JUGADOR = events[events['team'] == equipos[0]]['player'].dropna().unique()[0]  # jugador por defecto
# Ejemplo: JUGADOR = 'Mohamed Salah'

print(f'📍 Analizando: {JUGADOR}')

# Filtrar acciones del jugador con coordenadas
acc = events[(events['player'] == JUGADOR) & (events['location'].notna())].copy()
acc['x'] = acc['location'].apply(lambda loc: loc[0] if isinstance(loc, list) and len(loc) == 2 else None)
acc['y'] = acc['location'].apply(lambda loc: loc[1] if isinstance(loc, list) and len(loc) == 2 else None)
acc = acc.dropna(subset=['x', 'y'])
print(f'   Acciones con coordenadas: {len(acc)}')

# ── Función para dibujar campo ───────────────────────────────────────────────
def dibujar_campo(ax, color_cesped='#1a472a'):
    ax.set_facecolor(color_cesped)
    kw = dict(edgecolor='white', linewidth=1.8, fill=False)
    ax.add_patch(patches.Rectangle((0, 0), 120, 80, **kw))
    ax.plot([60, 60], [0, 80], 'white', lw=1.8)
    ax.plot(60, 40, 'o', color='white', ms=4)
    ax.add_patch(patches.Circle((60, 40), 10, **kw))
    ax.add_patch(patches.Rectangle((0, 18), 18, 44, **kw))
    ax.add_patch(patches.Rectangle((0, 30), 6, 20, **kw))
    ax.add_patch(patches.Rectangle((102, 18), 18, 44, **kw))
    ax.add_patch(patches.Rectangle((114, 30), 6, 20, **kw))
    ax.set_xlim(-2, 122); ax.set_ylim(-2, 82)
    ax.set_aspect('equal'); ax.axis('off')

# ── Dibujar heatmap ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#0D1B2A')
dibujar_campo(ax)

hb = ax.hexbin(acc['x'], acc['y'], gridsize=16, cmap='YlOrRd', alpha=0.80, mincnt=1)
cb = fig.colorbar(hb, ax=ax, shrink=0.55, pad=0.02)
cb.set_label('Densidad de acciones', color='white', fontsize=11)
plt.setp(cb.ax.yaxis.get_ticklabels(), color='white')

ax.set_title(f'🔥 Mapa de Calor — {JUGADOR}', color='white', fontsize=15, fontweight='bold', pad=18)
ax.text(3, -0.5, '← Portería propia', color='#aaaaaa', fontsize=9)
ax.text(88, -0.5, 'Portería rival →', color='#aaaaaa', fontsize=9)

plt.tight_layout()
plt.savefig('heatmap.png', dpi=150, bbox_inches='tight', facecolor='#0D1B2A')
plt.show()
print('✅ Guardado como heatmap.png')

# ─────────────────────────────────────────────────────────────────────────────
# 👉 CAMBIA equipos[0] por equipos[1] para ver el otro equipo
# ─────────────────────────────────────────────────────────────────────────────
equipos = events['team'].dropna().unique()
EQUIPO = equipos[0]

print(f'🕸️  Generando red de pases para: {EQUIPO}')

# Pases completados del equipo
pases = events[
    (events['type'] == 'Pass') &
    (events['team'] == EQUIPO) &
    (events['pass_outcome'].isna())  # Solo pases completados
].copy()
print(f'   Pases completados: {len(pases)}')

# Extraer coordenadas de cada pase
pases['x'] = pases['location'].apply(lambda l: l[0] if isinstance(l, list) else None)
pases['y'] = pases['location'].apply(lambda l: l[1] if isinstance(l, list) else None)
pases = pases.dropna(subset=['x', 'y', 'pass_recipient'])

# Top 9 jugadores por número de pases realizados
top9 = pases.groupby('player').size().nlargest(9).index.tolist()
pases_top = pases[pases['player'].isin(top9) & pases['pass_recipient'].isin(top9)]

# Posición media de cada jugador (donde inician sus pases)
pos_media = pases_top.groupby('player')[['x', 'y']].mean()

# Conteo de combinaciones
combis = pases_top.groupby(['player', 'pass_recipient']).size().reset_index(name='n')

# Función apellido
def apellido(nombre):
    if pd.isna(nombre): return ''
    p = str(nombre).split()
    return p[-1] if len(p) > 1 else p[0]

# Cuántos pases recibió cada jugador (para tamaño del nodo)
recibidos = pases_top.groupby('pass_recipient').size()

# ── Dibujar ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#0D1B2A')
dibujar_campo(ax)

max_n = combis['n'].max()

# Líneas de conexión
for _, row in combis.iterrows():
    if row['player'] in pos_media.index and row['pass_recipient'] in pos_media.index:
        x0, y0 = pos_media.loc[row['player'], ['x', 'y']]
        x1, y1 = pos_media.loc[row['pass_recipient'], ['x', 'y']]
        grosor = 0.8 + (row['n'] / max_n) * 5.5
        alpha  = 0.25 + 0.55 * (row['n'] / max_n)
        ax.plot([x0, x1], [y0, y1], color='#AAEE00', lw=grosor, alpha=alpha, zorder=2)

# Nodos y nombres
for jugador, row in pos_media.iterrows():
    tamaño = 350 + recibidos.get(jugador, 0) * 10
    ax.scatter(row['x'], row['y'], s=tamaño,
               color='#AAEE00', edgecolors='white', linewidth=1.5, zorder=3)
    ax.text(row['x'], row['y'] - 4.8, apellido(jugador),
            color='white', fontsize=9, fontweight='bold', ha='center', va='top', zorder=4)

ax.set_title(f'🕸️ Red de Pases — {EQUIPO}', color='white', fontsize=15, fontweight='bold', pad=18)
ax.text(3, -0.5, '← Portería propia', color='#aaaaaa', fontsize=9)
ax.text(88, -0.5, 'Portería rival →', color='#aaaaaa', fontsize=9)

plt.tight_layout()
plt.savefig('red_pases.png', dpi=150, bbox_inches='tight', facecolor='#0D1B2A')
plt.show()
print('✅ Guardado como red_pases.png')

# ── BONUS: Estadísticas comparadas del partido ────────────────────────────────
equipos = events['team'].dropna().unique()
print('=' * 55)
print(f'  RESUMEN ESTADÍSTICO DEL PARTIDO')
print('=' * 55)

metricas = [
    ('Pases totales', 'Pass', None),
    ('Tiros', 'Shot', None),
    ('Duelos', 'Duel', None),
    ('Recuperaciones', 'Ball Recovery', None),
    ('Faltas recibidas', 'Foul Won', None),
]

for nombre, tipo, _ in metricas:
    vals = [len(events[(events['team'] == eq) & (events['type'] == tipo)]) for eq in equipos]
    print(f'  {nombre:<22} {equipos[0][:12]:>12}: {vals[0]:>4}   |   {equipos[1][:12]:<12}: {vals[1]:>4}')

print()
for equipo in equipos:
    top = events[events['team'] == equipo].groupby('player').size().idxmax()
    n   = events[events['team'] == equipo].groupby('player').size().max()
    print(f'  Jugador más activo ({equipo[:15]}): {top} ({n} acciones)')

print('=' * 55)
print('\n💬 ¿Qué conclusión táctica extraes de estos datos?')
