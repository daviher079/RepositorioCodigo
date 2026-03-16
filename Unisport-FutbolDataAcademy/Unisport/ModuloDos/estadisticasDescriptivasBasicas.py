import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "participacion_limpio_betis.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

# Exploración inicial
print(df.shape)
df.info()
print(df.head())

columnasEnteros = ['Minutos', 'Toques en area rival', 'Perdidas', 
                'Oportunidades creadas', 'Regates Realizados con éxito']
columnasDecimales = ['Porcentaje de pases completados', 'Porcentaje de regates realizados']

columnasCompletas = columnasEnteros + columnasDecimales

estadisticas = df[columnasCompletas]
print("Columnas completas:")
print(estadisticas)

estadisticasCalculadas = pd.DataFrame({
    'Media':    estadisticas.mean(),
    'Mediana':  estadisticas.median(),
    'Desviación estándar':  estadisticas.std(),
    'Mínimo':   estadisticas.min(),
    'Máximo':   estadisticas.max()
})

print("estadisticas Calculadas:")
print(estadisticasCalculadas)

estadisticasCalculadas.loc[columnasEnteros, 'Media'] = (
    estadisticasCalculadas.loc[columnasEnteros, 'Media']
    .round(0)
    .astype('Int64') 
)

estadisticasCalculadas.loc[columnasDecimales, 'Media'] = (
    estadisticasCalculadas.loc[columnasDecimales, 'Media']
    .round(2)
)
print("\nestadisticas Calculadas redondeadas:")
print(estadisticasCalculadas)

# Boxplots
plt.figure(figsize=(14, 5))
for i, col in enumerate(columnasCompletas, 1):
    plt.subplot(1, len(columnasCompletas), i)
    sns.boxplot(y=df[col], color="salmon")
    plt.title(col, fontsize=8)
plt.tight_layout()

plt.savefig(os.path.join(os.path.dirname(__file__), "boxplots.png"))
print("Gráfico guardado")

# Matriz de correlación
plt.figure(figsize=(8, 6))
sns.heatmap(df[columnasCompletas].corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Matriz de correlación")
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "correlacion.png"))
print("Matriz de correlación guardada")