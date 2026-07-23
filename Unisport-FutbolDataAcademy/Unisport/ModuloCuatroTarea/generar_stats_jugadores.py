import pandas as pd
import numpy as np
import os

np.random.seed(42)

BASE = os.path.join(os.path.dirname(__file__), "redes_sociales_unisport_limpio.xlsx")

df_partidos = pd.read_excel(BASE, sheet_name=0)

jugadores = ['Delgado', 'Navarro', 'Rubio', 'Herrera', 'Castillo', 'Álvarez']
pesos_goles = [0.25, 0.22, 0.20, 0.15, 0.10, 0.08]

registros = []

for _, partido in df_partidos.iterrows():
    partido_id = partido['partido_id']
    goles_favor = int(partido['goles_favor'])

    goles_dist = np.random.multinomial(goles_favor, pesos_goles) if goles_favor > 0 else [0] * 6

    # Asistencias totales del partido: entre 0 y goles_favor
    asist_totales = np.random.randint(0, goles_favor + 1) if goles_favor > 0 else 0
    asist_dist = np.random.multinomial(asist_totales, pesos_goles)

    for i, jugador in enumerate(jugadores):
        registros.append({
            'partido_id': partido_id,
            'jugador': jugador,
            'goles': int(goles_dist[i]),
            'asistencias': int(asist_dist[i]),
        })

df_stats = pd.DataFrame(registros)

# Verificar coherencia
check = (
    df_stats.groupby('partido_id')['goles'].sum()
    .reset_index()
    .merge(df_partidos[['partido_id', 'goles_favor']], on='partido_id')
)
assert (check['goles'] == check['goles_favor']).all(), "Error: goles no cuadran con goles_favor"
print("Verificación OK — goles individuales cuadran con goles_favor")

print(df_stats.groupby('jugador')[['goles', 'asistencias']].sum().sort_values('goles', ascending=False))

with pd.ExcelWriter(BASE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_stats.to_excel(writer, sheet_name='estadisticas_jugadores', index=False)

print("Hoja 'estadisticas_jugadores' añadida a", BASE)
