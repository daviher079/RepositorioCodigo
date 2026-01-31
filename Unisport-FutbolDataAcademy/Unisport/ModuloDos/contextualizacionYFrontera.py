# contextualizar los datos
# o	Regates exitosos por minuto (regates/minutos)
# o	Oportunidades creadas por minuto (oportunidades/minutos)
# o	Pérdidas por minuto (pérdidas/minuto)

#quitar porcentaje de regates exitosos 
#añadir columna de alta participacion 
#si el jugador supera las 20 oportunidades creadas y si sus pérdidas son inferiores a 15. 

#NOTA sujeto a cambios estos valores antes de empezar con el modelado mirar cuántos jugadores
# cumplen con esta norma o si por el contrario habría que cambiar algún valor


import pandas as pd
import numpy as np
import os

BASE = os.path.join(os.path.dirname(__file__), "participacion_limpio.xlsx")

df = pd.read_excel(BASE, sheet_name=0)

df['regates exitosos por minuto'] = df['Regates Realizados con éxito'] / df['Minutos']
df['oportunidades creadas por minuto'] = df['Oportunidades creadas'] / df['Minutos']
df['perdidas por minuto'] = df['Perdidas'] / df['Minutos']

df['alta_participacion'] = np.where(
    (df["Oportunidades creadas"] > 15) & (df["Perdidas"] < 20), 
    1, 
    0)

df = df.drop(columns=['Porcentaje de regates realizados', 'Perdidas', 'Regates Realizados con éxito', 'Oportunidades creadas'])

ruta_salida = os.path.join(os.path.dirname(__file__), "participacion_contextualizado.xlsx")
df.to_excel(ruta_salida, index=False)

print("Archivo generado en:", ruta_salida)

