import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, classification_report
import numpy as np
import os


BASE_COMPLETO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_contextualizados.csv")
BASE_FILTRADO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado_contextualizado.csv")
OUTPUT_FILTRADO = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado_modelado.csv")

df_completo = pd.read_csv(BASE_COMPLETO)
df_filtrado = pd.read_csv(BASE_FILTRADO)


# Exploración inicial
print(df_completo.shape)
df_completo.info()
print(df_completo.head())

# Exploración inicial
print(df_filtrado)
df_filtrado.info()
print(df_filtrado)

y = df_completo["GeneradorDePeligro"]

X = df_completo[
    [
        "minutos_jugados",
        "porcentaje_regates_exitosos",
        "pases_clave",
        "grandes_ocasiones_creadas_por_minuto",
        "pases_ultimo_tercio_por_minuto",
        "grandes_ocasiones_falladas_por_minuto"
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
print(f"TN (True Negative): Jugador de baja Generación De Peligro bien clasificado: {tn}")
print(f"TP (True Positive): Jugador de alta Generación De Peligro bien clasificado: {tp}")
print(f"FP (False Positive): Jugador clasificado como alta Generación De Peligro pero no lo es: {fp}")
print(f"FN (False Negative): Jugador de alta Generación De Peligro clasificado como baja: {fn}")

print("\nReporte completo:")
print(classification_report(y_test, y_pred))

X_scaled = scaler.transform(X)

df_completo["Puntuacion"] = np.floor(modelo.predict_proba(X_scaled)[:, 1]*10000)/1000

X_filtrado = df_filtrado[
    [
        "minutos_jugados",
        "porcentaje_regates_exitosos",
        "pases_clave",
        "grandes_ocasiones_creadas_por_minuto",
        "pases_ultimo_tercio_por_minuto",
        "grandes_ocasiones_falladas_por_minuto"
    ]
]

X_filtrado_scaled = scaler.transform(X_filtrado)
df_filtrado["Puntuacion"] = np.floor(modelo.predict_proba(X_filtrado_scaled)[:, 1]*10000)/1000
df_filtrado = df_filtrado.drop(columns=['conteo_valoraciones', 'valoracion_total', 'valoracion'])

df_filtrado = df_filtrado[
    (df_filtrado["Puntuacion"]>=4)
].copy()


print(df_filtrado)


df_filtrado.to_csv(OUTPUT_FILTRADO, index=False)

print("Archivo generado en:", OUTPUT_FILTRADO)