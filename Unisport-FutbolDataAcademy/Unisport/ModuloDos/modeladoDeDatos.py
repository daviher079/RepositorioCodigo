import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, classification_report
import numpy as np
import os


BASE = os.path.join(os.path.dirname(__file__), "participacion_contextualizado.xlsx")
BASE_BETIS = os.path.join(os.path.dirname(__file__), "participacion_contextualizado_betis.xlsx")

df = pd.read_excel(BASE, sheet_name=0)
df_betis = pd.read_excel(BASE_BETIS, sheet_name=0)

# Exploración inicial
print(df.shape)
df.info()
print(df.head())

# Exploración inicial
print(df_betis)
df_betis.info()
print(df_betis)

y = df["alta_participacion"]

X = df[
    [
        "Minutos",
        "Porcentaje de pases completados",
        "Toques en area rival",
        "regates exitosos por minuto",
        "oportunidades creadas por minuto",
        "perdidas por minuto"
    ]
]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Verificación de NaN antes de entrenar
print(X_train.isna().sum())
print(y_train.isna().sum())

#fit → SOLO train
#transform → train + test
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

modelo = LogisticRegression()
modelo.fit(X_train_scaled, y_train)
y_pred = modelo.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)

print(f"\nAccuracy:  {accuracy:.2f}")
print(f"Precision: {precision:.2f}")
print(f"Recall:    {recall:.2f}")

cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
print("\nMatriz de confusión:")
print(cm)
print(f"TN (True Negative): Jugador de baja participación bien clasificado: {tn}")
print(f"TP (True Positive): Jugador de alta participación bien clasificado: {tp}")
print(f"FP (False Positive): Jugador clasificado como alta participación pero no lo es: {fp}")
print(f"FN (False Negative): Jugador de alta participación clasificado como baja: {fn}")

print("\nReporte completo:")
print(classification_report(y_test, y_pred))

X_scaled = scaler.transform(X)

df["Puntuacion"] = np.floor(modelo.predict_proba(X_scaled)[:, 1]*10000)/1000

ranking = (
    df[["Jugador", "Puntuacion"]]
    .sort_values("Puntuacion", ascending=False)
    .reset_index(drop=True)
)

ranking["Posicion"] = ranking.index + 1
nuevo_orden = ['Posicion', 'Jugador', 'Puntuacion']
ranking = ranking[nuevo_orden]

print("\nTop 20 jugadores por probabilidad de alta participación:")
print(ranking.head(20))

X_betis = df_betis[
    [
        "Minutos",
        "Porcentaje de pases completados",
        "Toques en area rival",
        "regates exitosos por minuto",
        "oportunidades creadas por minuto",
        "perdidas por minuto"
    ]
]

X_betis_scaled = scaler.transform(X_betis)
df_betis["Puntuacion"] = np.floor(modelo.predict_proba(X_betis_scaled)[:, 1]*10000)/1000

print(df_betis)


ruta_salida = os.path.join(os.path.dirname(__file__), "participacion_modelado_betis.xlsx")
df_betis.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)