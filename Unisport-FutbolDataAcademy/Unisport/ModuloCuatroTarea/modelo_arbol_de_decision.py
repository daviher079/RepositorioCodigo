import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "redes_sociales_unisport_limpio.xlsx")

df_metricas_rrss = pd.read_excel(BASE, sheet_name=1)
df_partidos = pd.read_excel(BASE, sheet_name=0)

df_union = df_metricas_rrss.merge(df_partidos, on='partido_id', how = 'left')

  

features = df_union[['plataforma', 'tipo_contenido', 'momento', 'resultado', 'jugador_mencionado']]
print(features.isna().sum())   

features_encoded = pd.get_dummies(features, drop_first=True, dtype=int)
print(features_encoded.head(10))

df_union['engagement_total'] = df_union['likes'] + df_union['comentarios'] + df_union['compartidos']


mediana = df_union['engagement_total'].median()
y = (df_union['engagement_total'] > mediana).astype(int)


modelo = DecisionTreeClassifier(max_depth=3, random_state=42)

modelo.fit(features_encoded, y)

importancias = modelo.feature_importances_      # array con un valor por columna
indices = np.argsort(importancias)               # índices ordenados de menor a mayor
nombres = features_encoded.columns                # nombres en el mismo orden que las columnas

importancias_ordenadas = {}

for i in indices[::-1]:
    if(importancias[i]>0): 
        importancias_ordenadas[nombres[i]] = importancias[i]*100                          # invertido: de mayor a menor
    print(f"{nombres[i]:<25}: {importancias[i]*100:.1f}%")

print("Suma total:", importancias.sum())


y_pred = modelo.predict(features_encoded)
accuracy = accuracy_score(y, y_pred)
print(f"Accuracy (entrenamiento): {accuracy:.2%}")

df_union['engagement_inicial'] = y
df_union['engagement_predicho'] = y_pred
df_union['engagement_inicial'] = df_union['engagement_inicial'].map({1: 'Alto', 0: 'Bajo'})
df_union['engagement_predicho'] = df_union['engagement_predicho'].map({1: 'Alto', 0: 'Bajo'})
print(df_union[['engagement_inicial', 'engagement_predicho']].head(10))


fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xticks(range(0, 60, 5))
bars = ax.barh(importancias_ordenadas.keys(), importancias_ordenadas.values())

for bar in bars:
    ancho = bar.get_width()
    if ancho < 10:
        # barra corta → texto fuera, a la derecha, en negro
        ax.text(ancho + 1, bar.get_y() + bar.get_height()/2, f'{ancho:.1f}%',
                 va='center', ha='left', color='black')
    else:
        # barra larga → texto dentro, pegado al borde derecho, en blanco
        ax.text(ancho - 1, bar.get_y() + bar.get_height()/2, f'{ancho:.1f}%',
                 va='center', ha='right', color='white')
        
ax.set_xlabel('Importancia (%)')
ax.set_title('Variables con más engagement')
plt.tight_layout()
plt.savefig(os.path.join(os.path.dirname(__file__), 'barras_engagement.png'), dpi=150, bbox_inches='tight')
