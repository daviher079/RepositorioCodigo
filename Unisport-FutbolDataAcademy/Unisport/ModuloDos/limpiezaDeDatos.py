import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "Datos_Alta_Participacion_Betis.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

# Eliminacion de duplicados
df = df.drop_duplicates() 

#Limpieza
limpiezaDataFrame = df[
    (df["Minutos"]>800) &
    ~(df.select_dtypes(include="number") == 0).any(axis=1)
    ]

#Verificacion final
print("Shape final:", limpiezaDataFrame.shape)
print(limpiezaDataFrame.isna().sum())          
print("Hay " + str(limpiezaDataFrame.duplicated().sum()) + " valores duplicados")    
print(limpiezaDataFrame.describe())   

ruta_salida = os.path.join(os.path.dirname(__file__), "participacion_limpio_betis.xlsx")
limpiezaDataFrame.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)