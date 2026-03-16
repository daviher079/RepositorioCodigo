import pandas as pd
import numpy as np
import os

BASE = os.path.join(os.path.dirname(__file__), "participacion_limpio_betis.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

print(df.shape)
df.info()
print(df.head())

df['regates exitosos por minuto'] = df['Regates Realizados con éxito'] / df['Minutos']
df['oportunidades creadas por minuto'] = df['Oportunidades creadas'] / df['Minutos']
df['perdidas por minuto'] = df['Perdidas'] / df['Minutos']

df['alta_participacion'] = np.where(
    (df["Oportunidades creadas"] > 15) & (df["Perdidas"] < 20), 
    1, 
    0)

df = df.drop(columns=['Porcentaje de regates realizados', 'Perdidas', 'Regates Realizados con éxito', 'Oportunidades creadas'])

print(df.head())
print("Datos de la frontera inicial antes de modelar la alta participacion")
print(df['alta_participacion'].value_counts())

ruta_salida = os.path.join(os.path.dirname(__file__), "participacion_contextualizado_betis.xlsx")
df.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)
