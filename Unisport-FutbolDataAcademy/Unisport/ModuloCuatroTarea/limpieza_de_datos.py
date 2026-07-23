import pandas as pd
import os

BASE = os.path.join(os.path.dirname(__file__), "dataset_unisport_fc.xlsx")

df_partidos = pd.read_excel(BASE, sheet_name=0)
df_metricas_rrss = pd.read_excel(BASE, sheet_name=1)



#Verificacion inicial
print("Shape bruto:", df_metricas_rrss.shape)
print(df_metricas_rrss.isna().sum())          
print("Hay " + str(df_metricas_rrss.duplicated().sum()) + " valores duplicados")    
print(df_metricas_rrss.describe())  

print(df_metricas_rrss['likes'].sort_values(ascending=False).head(10))
print(df_metricas_rrss[df_metricas_rrss['comentarios'].isna() | df_metricas_rrss['compartidos'].isna()])

print(df_metricas_rrss['comentarios'].median())
print(df_metricas_rrss['likes'].median())
print(df_metricas_rrss['compartidos'].median())

# Eliminacion de duplicados
df_metricas_rrss = df_metricas_rrss.drop_duplicates() 

mediana_likes = df_metricas_rrss['likes'].median()
df_metricas_rrss.loc[df_metricas_rrss['likes'] > 2696, 'likes'] = mediana_likes
df_metricas_rrss['likes'] = df_metricas_rrss['likes'].astype(int)

df_metricas_rrss['comentarios'] = df_metricas_rrss['comentarios'].fillna(df_metricas_rrss['comentarios'].median())
df_metricas_rrss['comentarios'] = df_metricas_rrss['comentarios'].astype(int)

df_metricas_rrss['compartidos'] = df_metricas_rrss['compartidos'].fillna(df_metricas_rrss['compartidos'].median())
df_metricas_rrss['compartidos'] = df_metricas_rrss['compartidos'].astype(int)

#Verificacion final
print("Shape final:", df_metricas_rrss.shape)
print(df_metricas_rrss.isna().sum())          
print("Hay " + str(df_metricas_rrss.duplicated().sum()) + " valores duplicados")    
print(df_metricas_rrss.describe()) 

print(df_metricas_rrss.head(10))

ruta_salida = os.path.join(os.path.dirname(__file__), "redes_sociales_unisport_limpio.xlsx")
with pd.ExcelWriter(ruta_salida) as writer:
    df_partidos.to_excel(writer, sheet_name='partidos', index=False)
    df_metricas_rrss.to_excel(writer, sheet_name='metricas_rrss', index=False)

print("Archivo generado en:", ruta_salida)