"""Fuente única de los pesos de los tres perfiles de extremo.

Los pesos vivían escritos a mano en DOS sitios: `PESOS` en `clasificacion_por_perfiles.py`
(donde se CALCULA la nota) y `PESOS_PERFIL` en `dashboard_extremos.py` (donde el modal
EXPLICA cómo se calcula). Coincidían, pero nada lo garantizaba: el día que un peso cambiara
en el pipeline y no en el dashboard, la nota cambiaría y la explicación no, sin dar error.

Este módulo es solo datos. No importa pandas, no lee ficheros y no escribe nada — para poder
importarse desde el dashboard sin efectos. (`clasificacion_por_perfiles.py` no sirve para eso:
ejecuta el pipeline al importarse y termina en `base.to_csv(...)`, así que importarlo desde
Streamlit regeneraría el dataset en cada recarga.)

Cada fila es:  (columna_pipeline, etiqueta_dashboard, peso, invertida)
  - columna_pipeline   nombre real de la columna, lo que necesita el cálculo
  - etiqueta_dashboard texto legible, lo que necesita el modal
  - peso               entero; los de cada perfil SUMAN 100
  - invertida          True si cuantas menos, mejor (ya viene invertida como percentil)
"""

PERFILES = {
    "REGATEADOR": [
        ("regates_intentados_por_90_pctl",              "Regates intentados por 90",         50, False),
        ("porcentaje_regates_exitosos_pctl",            "% de regates exitosos",             30, False),
        ("perdidas_de_balon_por_90_invertido",          "Pérdidas de balón por 90",          20, True),
    ],
    "FINALIZADOR": [
        ("goles_por_90_pctl",                           "Goles por 90",                      35, False),
        ("tiros_totales_por_90_pctl",                   "Tiros totales por 90",              25, False),
        ("porcentaje_tiros_a_puerta_pctl",              "% de tiros a puerta",               15, False),
        ("grandes_ocasiones_falladas_por_90_invertido", "Grandes ocasiones falladas por 90", 15, True),
        ("perdidas_de_balon_por_90_invertido",          "Pérdidas de balón por 90",          10, True),
    ],
    "CREADOR": [
        ("pases_clave_por_90_pctl",                     "Pases clave por 90",                30, False),
        ("grandes_ocasiones_creadas_por_90_pctl",       "Grandes ocasiones creadas por 90",  25, False),
        ("porcentaje_pases_clave_pctl",                 "% de pases clave",                  15, False),
        ("asistencias_por_90_pctl",                     "Asistencias por 90",                15, False),
        ("perdidas_de_balon_por_90_invertido",          "Pérdidas de balón por 90",          15, True),
    ],
}


def pesos_por_columna():
    """{perfil: {columna: peso}} — la vista que necesita el pipeline para calcular."""
    return {p: {col: peso for col, _, peso, _ in filas} for p, filas in PERFILES.items()}


def pesos_por_etiqueta():
    """{perfil: [(etiqueta, peso, invertida)]} — la vista que necesita el modal del dashboard."""
    return {p: [(etq, peso, inv) for _, etq, peso, inv in filas] for p, filas in PERFILES.items()}


# Red de seguridad: si alguien edita un peso y deja de sumar 100, salta aquí y no en la nota.
for _perfil, _filas in PERFILES.items():
    _suma = sum(peso for _, _, peso, _ in _filas)
    assert _suma == 100, f"Los pesos de {_perfil} suman {_suma}, no 100"
