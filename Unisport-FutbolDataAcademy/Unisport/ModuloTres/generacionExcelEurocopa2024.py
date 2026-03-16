import warnings
from statsbombpy.api_client import NoAuthWarning
warnings.filterwarnings("ignore", category=NoAuthWarning)

from statsbombpy import sb
import pandas as pd
import time
import os

# Obtener partidos de la Eurocopa
eurocopa = sb.matches(competition_id=55, season_id=282)

# Descargar todos los eventos
todos_eventos = []
for i, match_id in enumerate(eurocopa["match_id"]):
    try:
        eventos = sb.events(match_id=match_id)
        todos_eventos.append(eventos)
        print(f"Partido {i+1}/{len(eurocopa)} descargado")
        time.sleep(1)
    except Exception as e:
        print(f"Error en partido {match_id}: {e}")
        continue

df_eventos = pd.concat(todos_eventos, ignore_index=True)

# Descargar lineups para posiciones y país
lineups_todos = []
for match_id in eurocopa["match_id"]:
    try:
        lineup = sb.lineups(match_id=match_id)
        for equipo, df_lineup in lineup.items():
            df_lineup["match_id"] = match_id
            lineups_todos.append(df_lineup)
    except Exception as e:
        print(f"Error en lineup {match_id}: {e}")
        continue

df_lineups = pd.concat(lineups_todos, ignore_index=True)

# Extraer posiciones y país por jugador
df_posiciones = df_lineups[["player_id", "player_name", "positions", "country"]].drop_duplicates(subset="player_id")

def extraer_posiciones(positions):
    if isinstance(positions, list) and len(positions) > 0:
        return ", ".join([p["position"] for p in positions if "position" in p])
    return None

df_posiciones["posicion"] = df_posiciones["positions"].apply(extraer_posiciones)
df_posiciones["pais"] = df_posiciones["country"]
df_posiciones = df_posiciones[["player_name", "posicion", "pais"]]

# Minutos aproximados por jugador y partido
minutos_por_partido = (
    df_eventos.groupby(["match_id", "player"])["minute"]
    .max()
    .reset_index()
)

minutos_totales = (
    minutos_por_partido.groupby("player")["minute"]
    .sum()
    .reset_index()
    .rename(columns={"minute": "minutos"})
)

# Estadísticas por jugador
estadisticas_jugadores = df_eventos.groupby(["player"]).agg(

    # Pases
    pases_totales=("type", lambda x: (x == "Pass").sum()),
    pases_completados=("pass_outcome", lambda x: x.isna().sum()),
    pases_clave=("pass_shot_assist", lambda x: x.sum()),
    asistencias=("pass_goal_assist", lambda x: x.sum()),
    pases_largos=("pass_switch", lambda x: x.sum()),
    centros=("pass_cross", lambda x: x.sum()),
    pases_profundidad=("pass_through_ball", lambda x: x.sum()),
    pases_aereos_ganados=("pass_aerial_won", lambda x: x.sum()),
    pases_desviados=("pass_deflected", lambda x: x.sum()),
    pases_inswinging=("pass_inswinging", lambda x: x.sum()),
    pases_outswinging=("pass_outswinging", lambda x: x.sum()),
    pases_cutback=("pass_cut_back", lambda x: x.sum()),
    pases_sin_toque=("pass_no_touch", lambda x: x.sum()),

    # Tiros
    tiros_totales=("type", lambda x: (x == "Shot").sum()),
    tiros_a_puerta=("shot_outcome", lambda x: (x == "Saved").sum()),
    goles=("shot_outcome", lambda x: (x == "Goal").sum()),
    xg_total=("shot_statsbomb_xg", "sum"),
    tiros_primera=("shot_first_time", lambda x: x.sum()),
    tiros_aereos=("shot_aerial_won", lambda x: x.sum()),
    tiros_desviados=("shot_deflected", lambda x: x.sum()),
    tiros_uno_contra_uno=("shot_one_on_one", lambda x: x.sum()),
    tiros_porteria_abierta=("shot_open_goal", lambda x: x.sum()),
    tiros_tras_regate=("shot_follows_dribble", lambda x: x.sum()),
    tiros_al_palo=("shot_saved_to_post", lambda x: x.sum()),
    tiros_fuera_poste=("shot_saved_off_target", lambda x: x.sum()),
    tiros_redirigidos=("shot_redirect", lambda x: x.sum()),

    # Duelos
    duelos_totales=("type", lambda x: (x == "Duel").sum()),
    duelos_ganados=("duel_outcome", lambda x: x.isin(["Won", "Success In Play", "Success Out"]).sum()),

    # Regates
    regates_totales=("type", lambda x: (x == "Dribble").sum()),
    regates_completados=("dribble_outcome", lambda x: (x == "Complete").sum()),
    regates_cano=("dribble_nutmeg", lambda x: x.sum()),
    regates_overrun=("dribble_overrun", lambda x: x.sum()),
    regates_sin_toque=("dribble_no_touch", lambda x: x.sum()),

    # Presiones
    presiones=("type", lambda x: (x == "Pressure").sum()),
    contrapresiones=("counterpress", lambda x: x.sum()),
    bajo_presion=("under_pressure", lambda x: x.sum()),

    # Recuperaciones
    recuperaciones=("type", lambda x: (x == "Ball Recovery").sum()),
    recuperaciones_fallidas=("ball_recovery_recovery_failure", lambda x: x.sum()),
    recuperaciones_ofensivas=("ball_recovery_offensive", lambda x: x.sum()),

    # Pérdidas
    perdidas=("type", lambda x: (x == "Dispossessed").sum()),
    descontroles=("type", lambda x: (x == "Miscontrol").sum()),
    descontroles_aereos=("miscontrol_aerial_won", lambda x: x.sum()),

    # Defensivo
    intercepciones=("type", lambda x: (x == "Interception").sum()),
    bloqueos=("type", lambda x: (x == "Block").sum()),
    bloqueos_desviados=("block_deflection", lambda x: x.sum()),
    bloqueos_parada=("block_save_block", lambda x: x.sum()),
    bloqueos_ofensivos=("block_offensive", lambda x: x.sum()),
    despejes=("type", lambda x: (x == "Clearance").sum()),
    despejes_aereos=("clearance_aerial_won", lambda x: x.sum()),
    despejes_cabeza=("clearance_head", lambda x: x.sum()),
    despejes_pie_izq=("clearance_left_foot", lambda x: x.sum()),
    despejes_pie_der=("clearance_right_foot", lambda x: x.sum()),
    despejes_otros=("clearance_other", lambda x: x.sum()),
    regateado=("type", lambda x: (x == "Dribbled Past").sum()),

    # Faltas
    faltas_cometidas=("type", lambda x: (x == "Foul Committed").sum()),
    faltas_penalty_cometido=("foul_committed_penalty", lambda x: x.sum()),
    tarjetas_faltas=("foul_committed_card", lambda x: x.notna().sum()),
    faltas_recibidas=("type", lambda x: (x == "Foul Won").sum()),
    faltas_penalty_recibido=("foul_won_penalty", lambda x: x.sum()),
    faltas_defensivas=("foul_won_defensive", lambda x: x.sum()),

    # Portero
    acciones_portero=("type", lambda x: (x == "Goal Keeper").sum()),
    paradas_al_palo=("goalkeeper_shot_saved_to_post", lambda x: x.sum()),
    paradas_fuera=("goalkeeper_shot_saved_off_target", lambda x: x.sum()),
    exito_en_juego=("goalkeeper_success_in_play", lambda x: x.sum()),
    penalty_al_palo=("goalkeeper_penalty_saved_to_post", lambda x: x.sum()),
    punetazos=("goalkeeper_punched_out", lambda x: x.sum()),

    # Mala conducta
    tarjetas=("bad_behaviour_card", lambda x: x.notna().sum()),

    # 50/50
    disputas_50_50=("type", lambda x: (x == "50/50").sum()),

).reset_index()

# Añadir minutos totales
estadisticas_jugadores = estadisticas_jugadores.merge(
    minutos_totales,
    on="player",
    how="left"
)

# Unir posiciones y país
estadisticas_jugadores = estadisticas_jugadores.merge(
    df_posiciones[["player_name", "posicion", "pais"]],
    left_on="player",
    right_on="player_name",
    how="left"
).drop(columns=["player_name"])

# Reordenar columnas
columnas_inicio = ["player", "pais", "minutos", "posicion"]
resto = [col for col in estadisticas_jugadores.columns if col not in columnas_inicio]
estadisticas_jugadores = estadisticas_jugadores[columnas_inicio + resto]

# Exportar
BASE = os.path.join(os.path.dirname(__file__), "eurocopa_estadisticas_jugadores.xlsx")
estadisticas_jugadores.to_excel(BASE, index=False)

print("Archivo generado en:", BASE)
print("Shape:", estadisticas_jugadores.shape)
print(estadisticas_jugadores.head())