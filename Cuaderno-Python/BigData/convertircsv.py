import pandas as pd
import os
from fractions import Fraction

# ================================
# RUTA AL EXCEL
# ================================
BASE = os.path.dirname(os.path.abspath(__file__))
ruta_excel = os.path.join(BASE, "ficheros", "BetisModulo1.xlsx")

print("Leyendo desde:", ruta_excel)

df = pd.read_excel(ruta_excel, sheet_name="Union")
tipos = pd.read_excel(ruta_excel, sheet_name="Tipos")

# ================================
# DICCIONARIO DE TIPOS
# ================================
tipo_por_estadistica = dict(zip(tipos["Estadistica"], tipos["Tipo"]))

# ================================
# FUNCIONES LIMPIEZA
# ================================
def limpiar_valor(valor):
    valor = str(valor).strip()

    # Si es entero
    if valor.isdigit():
        return valor

    # Si es fracción "24/30 (75 %)"
    if "/" in valor:
        return valor.split("(")[0].strip()

    return valor


def calcular_porcentaje(valor):
    valor = str(valor).strip()

    # Si es entero → porcentaje NULL
    if valor.isdigit():
        return None

    try:
        return float(Fraction(valor))   # 24/30 → 0.8
    except:
        return None


# ================================
# CREAR LISTA DE FILAS (rápido y sin warnings)
# ================================
filas = []

no_estadisticas = ["Jugador", "Posicion", "Rival"]
cols_estadisticas = [col for col in df.columns if col not in no_estadisticas]
jugadores = df["Jugador"].unique()

for jugador in jugadores:
    filas_jugador = df[df["Jugador"] == jugador]

    for _, fila in filas_jugador.iterrows():
        rival = fila["Rival"]
        posicion = fila["Posicion"]

        for estadistica in cols_estadisticas:
            valor_original = fila[estadistica]
            valor_limpio = limpiar_valor(valor_original)
            porcentaje = calcular_porcentaje(valor_limpio)
            tipo = tipo_por_estadistica.get(estadistica, None)

            # Aquí agregamos tu fila como diccionario
            filas.append({
                "jugador": jugador,
                "rival": rival,
                "estadistica": estadistica,
                "valor": valor_limpio,
                "tipo": tipo,
                "posicion": posicion,
                "porcentaje": porcentaje
            })

# Ahora construimos el DataFrame sin warnings
dato = pd.DataFrame(filas)

# ================================
# GUARDAR
# ================================
ruta_salida = os.path.join(BASE, "ficheros", "dato.xlsx")
dato.to_excel(ruta_salida, index=False)

print("Archivo guardado en:", ruta_salida)
