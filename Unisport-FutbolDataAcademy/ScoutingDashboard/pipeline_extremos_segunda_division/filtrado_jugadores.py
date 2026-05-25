import pandas as pd
import os
from datetime import date

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_limpio.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado.csv")

df = pd.read_csv(BASE)

filtradoDataFrame = df[
    ((df["contrato_hasta"]=="30/06/2026") | (df["contrato_hasta"]=="30/06/2027")) &
    (df["valor_mercado"] < 500001.0) & 
    (df["minutos_jugados"] > 200)
].copy()

# Valor de mercado: de número a formato europeo (775.000)
def fmt_valor(v):
    if pd.isna(v):
        return "N/D"
    return f"{int(v):,}".replace(",", ".") + " €"

filtradoDataFrame["valor_mercado"] = filtradoDataFrame["valor_mercado"].apply(fmt_valor)

#Verificacion final
print("Shape final:", filtradoDataFrame.shape)
print(filtradoDataFrame.isna().sum())          
print("Hay " + str(filtradoDataFrame.duplicated().sum()) + " valores duplicados")    
print(filtradoDataFrame.describe())   

# Guardar dataset filtrado
filtradoDataFrame.to_csv(OUTPUT, index=False)