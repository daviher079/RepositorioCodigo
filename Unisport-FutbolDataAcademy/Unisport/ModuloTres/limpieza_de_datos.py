import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "eurocopa_sub23.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

# Eliminacion de duplicados
df = df.drop_duplicates() 

#Limpieza
#limpiezaDataFrame = df[
#    (df["Minutos"]>800) &
#    ~(df.select_dtypes(include="number") == 0).any(axis=1)
#    ]
defensas_limpio = df[(df["minutos"] > 180) & (df["posicion_clasificada"] == "Defensa")]

#Verificacion final
print("Shape final:", defensas_limpio.shape)
print(defensas_limpio.isna().sum())          
print("Hay " + str(defensas_limpio.duplicated().sum()) + " valores duplicados")    
print(defensas_limpio.describe())   

ruta_salida = os.path.join(os.path.dirname(__file__), "defensas_limpio_eurocopa.xlsx")
defensas_limpio.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)