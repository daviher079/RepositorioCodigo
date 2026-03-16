import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "Datos_Alta_Participacion_Betis.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

# Exploración inicial
print(df.shape)
df.info()
print(df.describe())
print(df.head())

# Detección de valores NaN
print(df.isna().sum())              
print(df[df.isna().any(axis=1)].head()) 

# Detección de duplicados
print("Hay " + str(df.duplicated().sum()) + " valores duplicados.")
print(df[df.duplicated()])

# Revisión de rangos imposibles
mask_pases = (df["Porcentaje de pases completados"] < 0) | (df["Porcentaje de pases completados"] > 100)
mask_regates = (df["Porcentaje de regates realizados"] < 0) | (df["Porcentaje de regates realizados"] > 100)

print("Porcentajes de pases imposibles:", mask_pases.sum())
print("Porcentajes de regates imposibles:", mask_regates.sum())