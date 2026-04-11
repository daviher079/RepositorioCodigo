import pandas as pd
import numpy as np
import os

BASE = os.path.join(os.path.dirname(__file__), "defensas_limpio_eurocopa.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

print(df.shape)
df.info()
print(df.head())

df['mins_por_perdida'] = (df['minutos'] / df['perdidas']).fillna(0).replace(float('inf'), 0).round(2)
df['mins_por_intercepcion'] = (df['minutos'] / df['intercepciones']).fillna(0).replace(float('inf'), 0).round(2)
df['mins_por_despeje'] = (df['minutos'] / df['despejes']).fillna(0).replace(float('inf'), 0).round(2)
df['mins_por_regateado'] = (df['minutos'] / df['regateado']).fillna(0).replace(float('inf'), 0).round(2)
df['ratio_duelos_ganados'] = (df['duelos_totales'] / df['duelos_ganados']).fillna(0).replace(float('inf'), 0).round(2)
df['ratio_pases_fallados'] = (df['pases_totales'] / df['pases_fallados']).fillna(0).replace(float('inf'), 0).round(2)
df['ratio_recuperaciones_fallidas'] = (df['recuperaciones'] / df['recuperaciones_fallidas']).fillna(0).replace(float('inf'), 0).round(2)
df['mins_por_falta'] = (df['minutos'] / df['faltas_cometidas']).fillna(0).replace(float('inf'), 0).round(2)
df['faltas_por_tarjeta'] = (df['faltas_cometidas'] / df['tarjetas_faltas']).fillna(0).replace(float('inf'), 0).round(2)
df['pct_despejes_aereos'] = ((df['despejes_aereos'] / df['despejes'])*100).fillna(0).replace(float('inf'), 0).round(2)
df['pct_despejes_pie_izq'] = ((df['despejes_pie_izq'] / df['despejes'])*100).fillna(0).replace(float('inf'), 0).round(2)
df['pct_despejes_pie_der'] = ((df['despejes_pie_der'] / df['despejes'])*100).fillna(0).replace(float('inf'), 0).round(2)

columnas_identidad = ['player', 'pais', 'edad', 'posicion','posicion_clasificada', 'minutos']
columnas_metricas = [
    'mins_por_perdida', 'mins_por_intercepcion', 'mins_por_despeje', 'mins_por_regateado',
    'ratio_duelos_ganados', 'ratio_pases_fallados', 'ratio_recuperaciones_fallidas',
    'mins_por_falta', 'faltas_por_tarjeta',
    'pct_despejes_aereos', 'pct_despejes_pie_izq', 'pct_despejes_pie_der'
]
df_definitivo = df[columnas_identidad + columnas_metricas]

print(df_definitivo.shape)
df_definitivo.info()
print(df_definitivo.head())

ruta_salida = os.path.join(os.path.dirname(__file__), "defensas_sub23_contextualizado.xlsx")
df_definitivo.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)
