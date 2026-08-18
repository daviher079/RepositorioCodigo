import pandas as pd
import numpy as np
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_contextualizados.csv")

# Entra el pool del script 1: los 84 con >=450 minutos, ya normalizados por 90.
# Aquí no se normaliza ni se filtra nada. Solo se miran los umbrales sobre esta
# población y se etiqueta. Es también la población de referencia del dashboard:
# un percentil aquí significa "top X% de los extremos de Segunda con >=5 partidos".
base = pd.read_csv(BASE)

# 1 · barrido de pases clave por 90.
# Distribución lisa, sin salto natural: el corte no lo dan los datos. Se elige viendo
# quién se cae en cada paso. De q0.65 a q0.70 salen Rober González, José Corpas,
# Jacobo González, Antonio Cordero y Naim García — y esos sí generan peligro.
for q in [0.60, 0.65, 0.70, 0.75, 0.80]:
    u = base['pases_clave_por_90'].quantile(q)
    pos = base['pases_clave_por_90'] > u
    print(f"\nq{q} → {u:.2f} pases clave/90 | {pos.sum()} de {len(base)}")
    print(base.loc[pos, 'nombre'].tolist())

#Corte en 0.65

# 2 · muestra que respalda el % de regates.
# Un 100% sobre 4 intentos no es un dato. Con 20 intentos un 50% real está entre 28% y
# 72%; con 60, entre 37% y 63%. Este filtro es el INSTRUMENTO para elegir el umbral
# del % con muestra fiable — no entra luego en el target.
print(base['regates_intentados'].describe())


for t in [40, 60, 80, 100, 120]:
    s = base['regates_intentados'] >= t
    print(f"\n>= {t} intentos → sobreviven {s.sum()} de {len(base)}")
    print(base.loc[s, ['nombre', 'regates_intentados', 'regates_exitosos', 'porcentaje_regates_exitosos']]
              .sort_values('porcentaje_regates_exitosos', ascending=True)
              .head(12).to_string(index=False))
# Cortamos en 60 intentos


# 3 · barrido del % sobre el pool fiable (>=60 intentos) y ya por encima de pases clave
filtro_sin_porcentaje_regates = base[(base['regates_intentados'] >= 60.0) & (base['pases_clave_por_90'] > 1.59)]

print(len(filtro_sin_porcentaje_regates))
for q in [0.20, 0.30, 0.40, 0.50, 0.55, 0.60]:
    u = filtro_sin_porcentaje_regates['porcentaje_regates_exitosos'].quantile(q)
    pos = filtro_sin_porcentaje_regates['porcentaje_regates_exitosos'] > u
    print(f"\nq{q} → {u:.2f} porcentaje regates exitosos | {pos.sum()} de {len(filtro_sin_porcentaje_regates)}")
    print(filtro_sin_porcentaje_regates.loc[pos, 'nombre'].tolist())



UMBRAL_PASES_CLAVE = 1.59   # q0.65 sobre los 84 con minutos>=450
UMBRAL_PCT_REGATES = 40.68  # q0.2 sobre los 15 con >=60 intentos de regate




# ─────────────────────────────────────────────────────────────────────────────
# 4 · FRONTERA — ahora sí, la etiqueta
# Las dos columnas que definen el target quedan PROHIBIDAS en X: de ahí venía la
# circularidad del modelo viejo (pases_clave crudo, 0.83 de correlación con minutos).
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_frontera(df):
    df = df.copy()
    df['GeneradorDePeligro'] = np.where(
        (df['pases_clave_por_90'] > UMBRAL_PASES_CLAVE) &
        (df['porcentaje_regates_exitosos'] > UMBRAL_PCT_REGATES), 1, 0)
    return df


df_etiquetado = aplicar_frontera(base)
df_etiquetado.to_csv(OUTPUT, index=False)

print(f"\nPool: {len(df_etiquetado)} extremos | {df_etiquetado['GeneradorDePeligro'].sum()} positivos "
      f"({df_etiquetado['GeneradorDePeligro'].mean():.0%}) | "
      f"{(df_etiquetado['GeneradorDePeligro'] == 0).sum()} negativos")
print(df_etiquetado.loc[df_etiquetado['GeneradorDePeligro'] == 1, 'nombre'].tolist())



# y ahora una de las cosas que nos decía el documento de destilado es que estamos haciendo el modelo con una frontera que ya le hemos aplicado nosotros previamente es decir, no le estamos marcando nosotros ya el camino de lo que tiene que decir??
