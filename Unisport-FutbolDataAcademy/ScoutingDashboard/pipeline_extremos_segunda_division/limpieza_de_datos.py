import pandas as pd
import os
from datetime import date

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_limpio.csv")

df = pd.read_csv(BASE)

# Eliminación de duplicados
df = df.drop_duplicates()

# Edad: de ISO timestamp a "X años"
def calcular_edad(fecha_str):
    if pd.isna(fecha_str):
        return "N/D"
    nacimiento = pd.to_datetime(fecha_str).date()
    hoy = date.today()
    edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
    return f"{edad} años"

df["edad"] = df["edad"].apply(calcular_edad)

# Contrato: de Unix timestamp a fecha legible (DD/MM/YYYY)
def fmt_contrato(v):
    if pd.isna(v):
        return "N/D"
    return pd.to_datetime(v, unit="s").strftime("%d/%m/%Y")

df["contrato_hasta"] = df["contrato_hasta"].apply(fmt_contrato)



# Pie dominante: de inglés a español
def traducir_pie(valor):
    if pd.isna(valor):
        return "N/D"
    traducciones = {"Right": "Derecho", "Left": "Zurdo", "Both": "Ambidiestro"}
    return traducciones.get(valor, valor)

df["pie_dominante"] = df["pie_dominante"].apply(traducir_pie)

# Guardar dataset limpio
df.to_csv(OUTPUT, index=False)
print(f"Dataset limpio guardado: {OUTPUT}")
print(f"Jugadores: {len(df)} | Columnas: {len(df.columns)}")
print("\nMuestra:")
print(df[["nombre", "equipo", "edad", "contrato_hasta", "valor_mercado"]].head(10).to_string())
