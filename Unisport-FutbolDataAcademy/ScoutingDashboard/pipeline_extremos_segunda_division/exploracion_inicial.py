import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos.csv")

df = pd.read_csv(BASE)

# Exploración inicial
print(df.shape)
df.info()
print(df.describe())
print(df.head())

columns_corr = df.loc[:, 'goles':]
columns_corr_dp_mins = columns_corr.drop(columns='minutos_jugados')
m = columns_corr_dp_mins.corrwith(df['minutos_jugados']).sort_values(ascending=False)
print(m)
print(m.diff())

# Pregunta B — redundancia: qué métricas miden lo mismo entre sí
matriz = columns_corr.corr()
plt.figure(figsize=(14, 12))
sns.heatmap(matriz, annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Correlación entre métricas (redundancia)")
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), "correlacion_heatmap.png"))
print("Heatmap guardado: correlacion_heatmap.png")

# Detección de valores NaN
print(df.isna().sum())              
print(df[df.isna().any(axis=1)].head()) 

# Detección de duplicados
print("Hay " + str(df.duplicated().sum()) + " valores duplicados.")
print(df[df.duplicated()])
