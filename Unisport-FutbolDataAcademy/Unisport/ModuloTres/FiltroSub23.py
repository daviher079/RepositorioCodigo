import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "eurocopa_estadisticas_jugadores.xlsx")
df = pd.read_excel(BASE)

print("Total jugadores:", len(df))
print("Edad mínima:", df["edad"].min())
print("Edad máxima:", df["edad"].max())


def clasificar_posicion(posicion):
    if pd.isna(posicion):
        return None

    posicion = posicion.lower()

    if "goalkeeper" in posicion:
        return "Portero"

    elif any(p in posicion for p in [
        "back", "center back", "centre back", "stopper",
        "wing back", "wingback"
    ]):
        return "Defensa"

    elif any(p in posicion for p in [
        "defensive midfield", "center midfield", "centre midfield",
        "left midfield", "right midfield", "left center midfield",
        "right center midfield", "center defensive midfield"
    ]):
        return "Centrocampista"

    elif any(p in posicion for p in [
        "forward", "winger", "wing", "attacking midfield",
        "center attacking midfield", "left attacking midfield",
        "right attacking midfield", "left center forward",
        "right center forward", "center forward",
        "left wing", "right wing"
    ]):
        return "Delantero"

    return None


# Filtro sub23
df_sub23 = df[df["edad"] <= 23]
df_sub23 = df_sub23[df_sub23["player"] != "Berat Djimsiti"].copy()

print("Jugadores sub23:", len(df_sub23))

# Crear nueva columna con la posición clasificada
df_sub23["posicion_clasificada"] = df_sub23["posicion"].apply(clasificar_posicion)

# Ordenar columnas
columnas_principales = ["player", "pais", "edad", "posicion", "posicion_clasificada"]
resto_columnas = [c for c in df_sub23.columns if c not in columnas_principales]

df_sub23 = df_sub23[columnas_principales + resto_columnas]

# Mostrar por pantalla ordenado por edad
print(df_sub23[["player", "pais", "edad", "posicion", "posicion_clasificada"]].sort_values("edad"))

# Correcciones manuales de posicion_clasificada
correcciones_posicion = {
    'Bukayo Saka': 'Delantero',
    'Dan Ndoye': 'Delantero',
    'Mohamed Zeki Amdouni': 'Delantero',
    'Heorhii Tsitaishvili': 'Centrocampista',
    'Joshua Zirkzee': 'Delantero',
    'Semih Kılıçsoy': 'Delantero',
    'Gonçalo Matias Ramos': 'Delantero',
    'Victor Bernth Kristansen': 'Centrocampista',
    'Lukáš Červ': 'Centrocampista',
    'Maksym Talovierov': 'Defensa',
    'Pavel Šulc': 'Centrocampista',
    'Zeno Debast': 'Defensa',
}

for jugador, posicion in correcciones_posicion.items():
    df_sub23.loc[df["player"] == jugador, "posicion_clasificada"] = posicion

print(df_sub23["posicion_clasificada"].value_counts())
print("NaN restantes:", df_sub23["posicion_clasificada"].isna().sum())

# Guardar Excel
BASE_SALIDA = os.path.join(os.path.dirname(__file__), "eurocopa_sub23.xlsx")
df_sub23.to_excel(BASE_SALIDA, index=False)

print("Archivo generado:", BASE_SALIDA)