import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "participacion_en_el_juego.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

limpiezaDataFrame = df[
    (df["Minutos"]>800) &
    ~(df.select_dtypes(include="number") == 0).any(axis=1)
    ]

ruta_salida = os.path.join(os.path.dirname(__file__), "participacion_limpio.xlsx")
limpiezaDataFrame.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)