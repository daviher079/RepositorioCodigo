import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "defensas_sub23_contextualizado.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

# Exploración inicial
print(df.shape)
df.info()
print(df.head())

columnasEnteros = ['minutos', 'edad']
columnasDecimales = ['mins_por_perdida', 'mins_por_intercepcion', 'mins_por_despeje', 
                    'mins_por_regateado', 'ratio_duelos_ganados', 'ratio_pases_fallados', 'ratio_recuperaciones_fallidas',
                    'mins_por_falta', 'faltas_por_tarjeta', 'pct_despejes_aereos', 'pct_despejes_pie_izq', 'pct_despejes_pie_der']

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

fig, ax = plt.subplots(figsize=(7, 4))
ax.axis('off')

tabla = ax.table(
    cellText=estadisticasCalculadas.round(2).values,
    rowLabels=estadisticasCalculadas.index,
    colLabels=estadisticasCalculadas.columns,
    cellLoc='center',
    loc='center'
)

tabla.scale(1, 1.5)
tabla.auto_set_font_size(False)
tabla.set_fontsize(9)
tabla.auto_set_column_width(col=list(range(len(estadisticasCalculadas.columns) + 1)))

plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "estadisticas_descriptivas.png"), dpi=150, bbox_inches='tight')
print("Tabla guardada como imagen")

# Boxplots
plt.figure(figsize=(14, 5))
for i, col in enumerate(columnasCompletas, 1):
    plt.subplot(1, len(columnasCompletas), i)
    sns.boxplot(y=df[col], color="salmon")
    #plt.title(col, fontsize=8)
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

plt.figure(figsize=(8, 5))
sns.histplot(df['minutos'], bins=10, color='salmon')
plt.title("Distribución de minutos jugados")
plt.xlabel("Minutos")
plt.ylabel("Número de jugadores")
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "histograma_minutos.png"))
print("Histograma guardado")