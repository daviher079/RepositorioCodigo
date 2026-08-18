import pandas as pd
import os
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_limpio.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado.csv")


# ─────────────────────────────────────────────────────────────────────────────
# 1 · CONTEXTUALIZAR — fila a fila, sin mirar a los demás
# ─────────────────────────────────────────────────────────────────────────────

def normalizar(df):
    df = df.copy()
    # Normalización por 90: cada conteo se acumula con los minutos (apartado 1: correlaciones 0.61-0.93,
    # pases_clave 0.83). Se crea la versión _por_90 al lado, sin pisar el conteo crudo.
    # Fuera de la lista a propósito: los % (ya son tasas), valoracion (media por partido),
    # tarjetas (evento raro, no talento) y valoracion_total/conteo_valoraciones (bookkeeping).

    # Intentos de regate: no viene en el dataset, se despeja del %. El replace(0) evita
    # dividir por cero → NaN = "no se sabe". Cumple DOS papeles, y por eso aparece en dos
    # sitios: el conteo crudo es la MUESTRA que respalda la tasa (fiabilidad — ese no se
    # toca), y su _por_90, que sale de la lista de abajo, es el volumen de regate con el
    # que puntúa el perfil regateador. El .round() es correcto aquí: medio regate no existe.
    df['regates_intentados'] = (
            df['regates_exitosos'] / df['porcentaje_regates_exitosos'].replace(0, np.nan) * 100
        ).round()

    df['porcentaje_tiros_a_puerta'] = (
            df['tiros_a_puerta'] / df['tiros_totales'].replace(0, np.nan) * 100
        )

    df['porcentaje_pases_clave'] = (
            df['pases_clave'] / df['pases_totales'].replace(0, np.nan) * 100
        )

    conteos_por_90 = [
        'goles', 'asistencias', 'regates_exitosos', 'pases_clave',
        'tiros_totales', 'tiros_a_puerta', 'grandes_ocasiones_creadas',
        'grandes_ocasiones_falladas', 'pases_ultimo_tercio', 'pases_totales',
        'pases_acertados', 'duelos_aereos_perdidos', 'intercepciones',
        'entradas', 'perdidas_de_balon', 'regates_intentados'
    ]
    for c in conteos_por_90:
        df[f'{c}_por_90'] = df[c] / df['minutos_jugados'] * 90

    return df



def fmt_valor(v):
    if pd.isna(v):
        return "N/D"
    return f"{int(v):,}".replace(",", ".") + " €"

df_completo = normalizar(pd.read_csv(BASE))
df_completo["valor_mercado_fmt"] = df_completo["valor_mercado"].apply(fmt_valor)

# ─────────────────────────────────────────────────────────────────────────────
# 2 · FILTRAR — el corte de muestra, mirando a los 109 enteros
# ─────────────────────────────────────────────────────────────────────────────

# Barrido sobre los 109 crudos: cuánto cuesta cada corte. La distribución de minutos
# es lisa, sin salto natural, así que el número no lo dan los datos: se elige viendo
# quién se cae en cada paso.
for t in [200, 300, 450, 600, 900]:
    s = (df_completo['minutos_jugados'] > t).sum()
    print(t, s, len(df_completo) - s)

# 450 ≈ 5 partidos. Es criterio de ojeador DECLARADO (regla transversal 1), no un
# hallazgo de la distribución. Cuesta 25 de 109. Un por_90 sobre 200 minutos no es un
# dato en el que fiarse, y la frontera del script siguiente se mira sobre este pool.
# La fiabilidad NO la cierra este filtro, que es binario (449 fuera, 451 dentro y
# tratado igual que uno de 3.000): se cubre enseñando los minutos al lado del
# percentil en el dashboard (Fase 6).
MINUTOS_MUESTRA = 450


# El pool: la población que sale de aquí y sobre la que se etiqueta y se entrena.
base = df_completo[df_completo['minutos_jugados'] >= MINUTOS_MUESTRA]
print(f"Pool con muestra: {len(base)} de {len(df_completo)} extremos")

#Verificacion final
print("Shape final:", base.shape)
print(base.isna().sum())          
print("Hay " + str(base.duplicated().sum()) + " valores duplicados")    
print(base.describe())   

# Guardar dataset filtrado
base.to_csv(OUTPUT, index=False)