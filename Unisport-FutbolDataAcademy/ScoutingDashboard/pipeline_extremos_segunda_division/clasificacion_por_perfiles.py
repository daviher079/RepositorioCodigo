import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_perfiles.csv")

PESOS = {
    'REGATEADOR': {
        'regates_intentados_por_90_pctl':          50,
        'porcentaje_regates_exitosos_pctl':        30,
        'perdidas_de_balon_por_90_invertido':      20,
    },
    'FINALIZADOR': {
        'goles_por_90_pctl':                       35,
        'tiros_totales_por_90_pctl':               25,
        'porcentaje_tiros_a_puerta_pctl':          15,
        'grandes_ocasiones_falladas_por_90_invertido': 15,
        'perdidas_de_balon_por_90_invertido':      10,
    },
    'CREADOR': {
        'pases_clave_por_90_pctl':                 30,
        'grandes_ocasiones_creadas_por_90_pctl':   25,
        'porcentaje_pases_clave_pctl':             15,
        'asistencias_por_90_pctl':                 15,
        'perdidas_de_balon_por_90_invertido':      15,
    },
}

UMBRAL_PERDIDAS = 60.0   # percentil de pocas pérdidas
UMBRAL_PASES = 75.0      # % de acierto real, NO percentil

base = pd.read_csv(BASE)

def invertir(df):
    columnas_a_invertir = ['perdidas_de_balon_por_90', 'grandes_ocasiones_falladas_por_90']

    for c in columnas_a_invertir:
       df[f'{c}_invertido'] = df[c].rank(pct=True, ascending= False) * 100

    return df

def percentiles(df):
    percentiles_columnas = ['regates_intentados_por_90', 'porcentaje_regates_exitosos', 
                            'tiros_totales_por_90', 'porcentaje_tiros_a_puerta', 'goles_por_90', 
                            'pases_clave_por_90', 'porcentaje_pases_clave', 
                            'grandes_ocasiones_creadas_por_90', 'asistencias_por_90']

    for c in percentiles_columnas:
        df[f'{c}_pctl'] = df[c].rank(pct=True, ascending= True) * 100

    return df


def sello_seguridad(df, UMBRAL_PERDIDAS, UMBRAL_PASES):
    # La seguridad NO es un perfil: es un atributo que se cuelga encima del perfil que el
    # jugador ya tenga ("regateador, y además seguro"). Por eso es un booleano al lado y no
    # una nota más. Nace del caso Valery Fernández: el que menos pierde de los 84 no tenía
    # dónde lucirlo, porque las pocas pérdidas solo entraban como modificador dentro de los tres.
    # Las dos condiciones son de distinta naturaleza A PROPÓSITO, y las dos van declaradas:
    #   - pérdidas: RELATIVA al pool (top 40% de los que menos pierden). Reutiliza el
    #     percentil invertido que ya calcula invertir(), para que no se descuadre con él.
    #   - pases: ABSOLUTA, contra la columna cruda y sin rank(). 75% es 75% en Segunda y
    #     fuera de ella, así que el sello significa lo mismo si algún día entra otra
    #     categoría (regla transversal 5). Es el mismo umbral que el escalón del creador.
    # Con estos dos números el sello lo llevan 18 de los 84.


    df['jugador_seguro'] = (
        (df['perdidas_de_balon_por_90_invertido'] >= UMBRAL_PERDIDAS) &
        (df['porcentaje_pases_acertados'] >= UMBRAL_PASES)
    )

    return df



def perfiles_extremos(df, pesos, UMBRAL_PASES):
    for perfil, columnas in pesos.items():
        df[perfil] = round((sum(df[c] * columnas[c] for c in columnas) / 100), 2)
    df.loc[df['porcentaje_pases_acertados'] < UMBRAL_PASES, 'CREADOR'] -= 10
    return df


base = invertir(base)
base = percentiles(base)
base = sello_seguridad(base, UMBRAL_PERDIDAS, UMBRAL_PASES)
base = perfiles_extremos(base, PESOS, UMBRAL_PASES)


# Guardar dataset filtrado
base.to_csv(OUTPUT, index=False)