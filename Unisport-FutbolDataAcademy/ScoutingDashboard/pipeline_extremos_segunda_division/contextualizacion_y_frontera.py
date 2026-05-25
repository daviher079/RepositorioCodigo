import pandas as pd
import numpy as np
import os

BASE_COMPLETO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos.csv")
BASE_FILTRADO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado.csv")
OUTPUT_COMPLETO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_contextualizados.csv")
OUTPUT_FILTRADO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado_contextualizado.csv")


def contextualizar(df):
    df = df.copy()
    df['grandes_ocasiones_creadas_por_minuto'] = df['grandes_ocasiones_creadas'] / df['minutos_jugados']
    df['pases_ultimo_tercio_por_minuto'] = df['pases_ultimo_tercio'] / df['minutos_jugados']
    df['grandes_ocasiones_falladas_por_minuto'] = df['grandes_ocasiones_falladas'] / df['minutos_jugados']
    df['GeneradorDePeligro'] = np.where(
        (df["pases_clave"] > 6) & (df["porcentaje_regates_exitosos"] > 43.0), 1, 0)
    return df




df_completo = contextualizar(pd.read_csv(BASE_COMPLETO))
df_filtrado = contextualizar(pd.read_csv(BASE_FILTRADO))

print(pd.read_csv(BASE_FILTRADO)['valor_mercado'].head())

print("=== DATASET COMPLETO (109 extremos — training) ===")
print("Shape:", df_completo.shape)
print(df_completo['GeneradorDePeligro'].value_counts())

print("\n=== DATASET FILTRADO (21 targets — predicción) ===")
print("Shape:", df_filtrado.shape)
print(df_filtrado['GeneradorDePeligro'].value_counts())

df_completo.to_csv(OUTPUT_COMPLETO, index=False)
df_filtrado.to_csv(OUTPUT_FILTRADO, index=False)

print("\nArchivos generados:")
print(" ", OUTPUT_COMPLETO)
print(" ", OUTPUT_FILTRADO)
