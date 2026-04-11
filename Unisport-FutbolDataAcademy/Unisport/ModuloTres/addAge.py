import pandas as pd
import requests
import os
from thefuzz import process
from datetime import date
from bs4 import BeautifulSoup
import time

api_key = "738f90a55f0644a4a63b6337dc1eae81"
headers = {"X-Auth-Token": api_key}

url = "https://api.football-data.org/v4/competitions/EC/teams"
response = requests.get(url, headers=headers)
data = response.json()

jugadores = []
for equipo in data["teams"]:
    for jugador in equipo["squad"]:
        jugadores.append({
            "nombre": jugador["name"],
            "fecha_nacimiento": jugador["dateOfBirth"],
            "posicion_api": jugador["position"]
        })

df_edades = pd.DataFrame(jugadores)

BASE = os.path.join(os.path.dirname(__file__), "eurocopa_estadisticas_jugadores.xlsx")
df = pd.read_excel(BASE)

# Coincidencia aproximada
nombres_api = df_edades["nombre"].tolist()

def buscar_datos(nombre):
    match, score = process.extractOne(nombre, nombres_api)
    if score >= 80:
        fila = df_edades[df_edades["nombre"] == match].iloc[0]
        return fila["fecha_nacimiento"], fila["posicion_api"]
    return None, None

df[["fecha_nacimiento", "posicion_api"]] = df["player"].apply(
    lambda x: pd.Series(buscar_datos(x))
)

# Correcciones manuales de fecha
fechas_manuales = {
    'Barış Alper Yılmaz': '1997-07-07',
    'Bertuğ Özgür Yıldırım': '2002-07-12',
    'Jorge Luiz Frello Filho': '1991-12-20',
    'Joshua Zirkzee': '2001-05-22',
    'Kléper Laveran Lima Ferreira': '1983-02-26',
    'Matěj Kovář': '2000-05-17',
    'Solomon Kverkvelia': '1992-02-06',
    'Taulant Sulejmanov': '1996-11-15',
    'Valentin Mihai Mihăilă': '2000-02-02',
    'Vitor Machado Ferreira': '2000-02-13'
}

for nombre, fecha in fechas_manuales.items():
    df.loc[df["player"] == nombre, "fecha_nacimiento"] = fecha

# Rellenar posiciones vacías con las de la API
df["posicion"] = df["posicion"].fillna(df["posicion_api"])
df = df.drop(columns=["posicion_api"])

# Corrección manual de posición
df.loc[df["player"] == "Bertuğ Özgür Yıldırım", "posicion"] = "Centre-Forward"

# Calcular edad durante la Eurocopa 2024
fecha_torneo = date(2024, 6, 14)
df["fecha_nacimiento"] = pd.to_datetime(df["fecha_nacimiento"])
df["edad"] = df["fecha_nacimiento"].apply(
    lambda x: fecha_torneo.year - x.year - ((fecha_torneo.month, fecha_torneo.day) < (x.month, x.day))
)

# Reordenar columnas
columnas_inicio = ["player", "pais", "edad", "posicion"]
resto = [col for col in df.columns if col not in columnas_inicio + ["fecha_nacimiento"]]
df = df[columnas_inicio + resto]

print("NaN en posicion:", df["posicion"].isna().sum())
print(df[["player", "pais", "edad", "posicion"]].head(10))

BASE_SALIDA = os.path.join(os.path.dirname(__file__), "eurocopa_estadisticas_jugadores.xlsx")
df.to_excel(BASE_SALIDA, index=False)
print("Archivo actualizado")
