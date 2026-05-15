# -*- coding: utf-8 -*-

# Paso 1: Importar la librería pandas
# Pandas es una herramienta muy usada en Python para trabajar con datos en tablas.
# La importamos y le damos un nombre corto 'pd' para usarla más fácilmente.
import pandas as pd

# Paso 2: Crear datos de ejemplo
# Imaginemos una pequeña lista de jugadores jóvenes con algunas métricas.
# Usamos un formato llamado 'diccionario': las palabras entre comillas son los nombres
# de las columnas, y las listas de valores son las filas de esa columna.
datos = {
    'Nombre': ['Jugador A', 'Jugador B', 'Jugador C', 'Jugador D', 'Jugador E', 'Jugador F'],
    'Edad': [17, 18, 19, 17, 20, 18],
    'Posicion': ['Delantero', 'Medio', 'Defensa', 'Delantero', 'Medio', 'Defensa'],
    'Velocidad': [9, 7, 6, 8, 9, 7],  # Puntuación sobre 10
    'Agilidad': [8, 8, 7, 9, 7, 6],    # Puntuación sobre 10
    'Resistencia': [7, 8, 9, 8, 6, 9]   # Puntuación sobre 10
}

# Paso 3: Crear un DataFrame de pandas
# Un DataFrame es la estructura principal de pandas, como una tabla o una hoja de cálculo.
# Creamos uno a partir de nuestros 'datos'. Lo llamamos 'df'.
df = pd.DataFrame(datos)

# Mostramos la tabla original para verla
print("--- Tabla Original de Jugadores ---")
print(df)
print("\n" + "="*30 + "\n") # Separador para claridad

# Paso 4: Definir los criterios de filtrado
# Queremos encontrar talentos que cumplan VARIAS condiciones a la vez:
# - Ser joven (menor de 19 años)
# - Tener buena velocidad (más de 8)
# - Tener buena resistencia (más de 7)

# Creamos las condiciones separadas para que sea más claro:
condicion_edad = df['Edad'] < 19
condicion_velocidad = df['Velocidad'] > 8
condicion_resistencia = df['Resistencia'] > 7

# Combinamos todas las condiciones usando el símbolo '&' (significa 'Y', deben cumplirse todas)
condiciones_completas = condicion_edad & condicion_velocidad & condicion_resistencia

# Paso 5: Aplicar el filtro al DataFrame
# Seleccionamos solo las filas de la tabla 'df' donde se cumplen TODAS las condiciones.
# Guardamos el resultado en una nueva tabla llamada 'talentos_filtrados'.
talentos_filtrados = df[condiciones_completas]

# Paso 6: Mostrar el resultado
# Imprimimos la nueva tabla que contiene solo los jugadores que pasaron el filtro.
print("--- Talentos Identificados (Edad < 19, Vel > 8, Res > 7) ---")
if talentos_filtrados.empty:
  print("No se encontraron jugadores que cumplan todos los criterios.")
else:
  print(talentos_filtrados)