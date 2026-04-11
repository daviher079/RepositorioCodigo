import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "eurocopa_sub23.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

# El dataset cuenta con 98 jugadores y 75 variables. Se verifica la estructura
# general del dataframe, los tipos de datos de cada columna y si existen
# valores nulos que requieran atención antes del análisis.
print(df.shape)
df.info()

# Resumen estadístico de las variables numéricas. Permite detectar rangos,
# medias y posibles anomalías como valores mínimos de cero en variables
# donde no sería esperable.
print(df.describe())

# Vista previa de los primeros registros para verificar que la carga
# del dataset es correcta y los datos tienen el formato esperado.
print(df.head())

# Detección de valores nulos por columna. Se identifican 4 valores nulos
# en posicion_clasificada que corresponden a jugadores cuya posición
# no pudo clasificarse automáticamente y requerirán corrección manual.
print(df.isna().sum())
print(df[df.isna().any(axis=1)].head())

# Verificación de registros duplicados. El resultado confirma que no
# existen jugadores duplicados en el dataset.
print("Hay " + str(df.duplicated().sum()) + " valores duplicados.")
print(df[df.duplicated()])

# Análisis de la distribución de minutos jugados, variable clave del análisis
# ya que todas las métricas están normalizadas en base a ella.
# La media es de 276 minutos con una desviación estándar de 145,
# lo que indica una dispersión elevada entre jugadores.
print(df["minutos"].describe())

# Distribución por rangos que muestra que 34 jugadores han jugado menos
# de 190 minutos, aproximadamente un tercio del dataset. Estos jugadores
# pueden generar métricas distorsionadas al normalizarlas por tiempo,
# por lo que será necesario establecer un umbral mínimo antes del análisis.
print(df["minutos"].value_counts(bins=5).sort_index())