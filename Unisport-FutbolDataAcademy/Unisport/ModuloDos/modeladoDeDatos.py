import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import os

BASE = os.path.join(os.path.dirname(__file__), "participacion_contextualizado.xlsx")


df = pd.read_excel(BASE, sheet_name=0)

print(df.head())

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

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

modelo = LogisticRegression()

modelo.fit(X_train_scaled, y_train)

y_pred = modelo.predict(X_test_scaled)

precision = accuracy_score(y_test, y_pred)

print(f"Precisión del modelo: {precision:.2f}")


X_scaled = scaler.transform(X)

df["prob_alta_participacion"] = modelo.predict_proba(X_scaled)[:, 1]

ranking = (
    df[["Jugador", "prob_alta_participacion"]]
    .sort_values("prob_alta_participacion", ascending=False)
    .reset_index(drop=True)
)

ranking["ranking"] = ranking.index + 1

print("\nTop 15 jugadores por probabilidad de alta participación:")
print(ranking.head(15))