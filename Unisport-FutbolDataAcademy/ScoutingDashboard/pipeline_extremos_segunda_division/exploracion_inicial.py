import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos.csv")

df = pd.read_csv(BASE)

# Exploración inicial
print(df.shape)
df.info()
print(df.describe())
print(df.head())

# Detección de valores NaN
print(df.isna().sum())              
print(df[df.isna().any(axis=1)].head()) 

# Detección de duplicados
print("Hay " + str(df.duplicated().sum()) + " valores duplicados.")
print(df[df.duplicated()])