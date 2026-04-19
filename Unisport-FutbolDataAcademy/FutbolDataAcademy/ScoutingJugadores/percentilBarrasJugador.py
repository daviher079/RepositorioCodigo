import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import LanusStats as ls
from io import StringIO
from mplsoccer import FontManager

import warnings
warnings.filterwarnings("ignore")

# buscamos el jugador que nos interesa en fbref: https://fbref.com/en/
# en el menú de arriba -en player o jugador-, selecciona el que te interese
# abajo aparece otro menú, selecciona 'informe de reclutamiento' o 'scouting report'
# aparecerá otro sub menú en el que tendrás que escoger la competición de la que quieres datos del jugador
# copia ese enlace de abajo -nosotros hemos hecho la prueba con Alex Baena-

# Usamos el navegador headless de LanusStats para evitar el bloqueo de Cloudflare
fbref = ls.Fbref()
html = fbref.fbref_request('/es/jugadores/518f2234/scout/12538/Informe-de-reclutamiento-de-Alex-Baena')
dfs = pd.read_html(StringIO(html))[2]


# Guardamos la tabla con los datos descargados de la web en la variable 'df_percentil'
# esta tabla es una estructura tipo hoja de cálculo, con filas y columnas,
# que nos permite analizar y manipular fácilmente la información y que python la comprenda

df_percentil = dfs

print(df_percentil.columns)

# Guardamos la tabla de datos en la variable 'df_percentiles'
# Esta tabla tiene filas y columnas con la información que vamos a usar para analizar

df_percentiles = dfs

# mejoramos los nombres de las columnas para facilitar el acceso
# porque las columnas de la web vienen con dos niveles y así dejamos solo el segundo nivel (el nombre real del dato)

df_percentiles.columns = df_percentiles.columns.droplevel(0)

# Simplificamos el nombre de una estadística larga para que sea más fácil de leer y usar
# Cambiamos "npxG: Goles esperados (xG) sin contar penaltis" por "npxG"

df_percentiles['Estadísticas'] = df_percentiles['Estadísticas'].replace(
    'npxG: Goles esperados (xG) sin contar penaltis', 'npxG'
)

# Definimos tres grupos de estadísticas que se usan según la posición del jugador:
#  - stats_defensores: métricas importantes para defensores
#  - stats_medios: métricas para centrocampistas
#  - stats_delanteros: métricas para delanteros

# Cada grupo está organizado en categorías como 'Defensa', 'Pases' o 'Acciones ofensivas',
# y dentro de cada categoría listamos las estadísticas relevantes para esa posición.

# Además, el diccionario 'reemplazos' sirve para cambiar nombres largos o técnicos
# por etiquetas más cortas y fáciles de leer, que luego usamos para mostrar en el gráfico.

stats_defensores = {
    'Defensa': ['% de Dribladores Derribados', 'Intercepciones', 'Recuperación de pelotas', 'Derribos conseguidos', 'Bloqueos', 'Faltas cometidas'],
    'Pases': ['xA: Asistencias Esperadas', 'Pases progresivos'],
    'Acciones ofensivas': ['npxG + xAG','npxG: Goles esperados (xG) sin contar penaltis', 'Acarreos progresivos', 'Acciones para la creación de tiros', 'Tomas exitosas', '% de toma exitosa']
}

stats_medios = {
    'Pases': ['Pases progresivos', 'xA: Asistencias Esperadas', '% de pase completo', 'Pases al área de penalización', 'xAG: Exp. Assisted Goals'],
    'Acciones ofensivas': ['npxG: Goles esperados (xG) sin contar penaltis', 'Acarreos progresivos', '% de toma exitosa', 'Toques (Ataq. pen.)'],
    'Acciones defensivas': ['% de Dribladores Derribados', 'Intercepciones', 'Recuperación de pelotas', 'Faltas cometidas']
}

stats_delanteros = {
    'Acciones ofensivas': ['npxG', 'npxG + xAG', 'Total de disparos','Disparos en el Objetivo %', 'npxG/Shot', 'Acciones para la creación de tiros', 'Toques (Ataq. pen.)', 'Acarreos progresivos'],
    'Pases': ['xA: Asistencias Esperadas', 'Pases progresivos', 'Pases al área de penalización', 'Pases progresivos Rec'],
    'Defensa': ['Tkl+Int', 'Bloqueos','Derribos (3.º ataq.)']
}

reemplazos = {
    'Recuperación de pelotas': 'Recuperación\nde pelotas',
    '% de Dribladores Derribados': '% de amagues\nevitados',
    'xA: Asistencias Esperadas': 'xA',
    '% de toma exitosa': '% de amagues\ncompletados',
    'Acciones para la creación de tiros': 'Acciones de\ncreación tiros',
    'Pases al área de penalización': 'Pases\nal área',
    'Disparos en el Objetivo %': '% de tiros\nal arco',
    'Pases progresivos Rec': 'Pases prog\nrecibidos',
    'Derribos (3.º ataq.)': 'Derribos\n(3.º ataq.)',
    'Toques (Ataq. pen.)': 'Toques en\nárea rival',
    'Tkl+Int': 'Entradas +\nIntercepciones',
    'Total de disparos': 'Tiros\ntotales',
    '% de pase completo': '% de pases',
    'xAG: Exp. Assisted Goals': 'xGChain'
}

# Convertimos la columna 'Percentil' a números (enteros o decimales)
# Esto es importante porque a veces los datos pueden venir como texto
# y para poder hacer cálculos o comparaciones necesitamos que sean números.
# Si algún valor no se puede convertir, se marcará como NaN (dato faltante).

df_percentiles['Percentil'] = pd.to_numeric(df_percentiles['Percentil'], errors='coerce')

# Con esto vamos a crear una nueva columna llamada 'color' para asignar colores según el percentil
# Usamos condiciones para clasificar el rendimiento en rangos:
#   - Menor a 20 → rojo (bajo rendimiento)
#   - Entre 20 y 39 → naranja (rendimiento bajo-medio)
#   - Entre 40 y 59 → amarillo (rendimiento medio)
#   - Entre 60 y 79 → verde claro (rendimiento bueno)
#   - 80 o más → verde (rendimiento excelente)
# Esto ayuda a mostrar visualmente en el gráfico qué tan bien lo hace el jugador en cada estadística
# comparado con los jugadores de su competición y de su posición

df_percentiles['color'] = np.where(df_percentiles['Percentil'] < 20, 'red',
    np.where((df_percentiles['Percentil'] >= 20) & (df_percentiles['Percentil'] < 40), 'orange',
    np.where((df_percentiles['Percentil'] >= 40) & (df_percentiles['Percentil'] < 60), 'yellow',
    np.where((df_percentiles['Percentil'] >= 60) & (df_percentiles['Percentil'] < 80), 'lightgreen', 'green'))))

# Aquí convertiremos los percentiles a números enteros y asignará colores según el valor

# Nota: Si el jugador que analizas es defensor o delantero, reemplaza 'stats_medios' 
# por 'stats_defensores' o 'stats_delanteros' para usar las estadísticas adecuadas según la posición.
# es la manera de que el percentil compare al jugador con los de su misma posición


dataframes = []

for key in stats_medios.keys(): 
    placeholder = df_percentiles[df_percentiles['Estadísticas'].isin(stats_medios[key])]  # usar valores de stats_medios
    placeholder = placeholder.drop_duplicates().reset_index(drop=True)
    placeholder['Percentil'] = placeholder['Percentil'].astype(int)
    placeholder['color'] = np.where(placeholder['Percentil'] < 20, 'red',
        np.where((placeholder['Percentil'] >= 20) & (placeholder['Percentil'] < 40), 'orange',
        np.where((placeholder['Percentil'] >= 40) & (placeholder['Percentil'] < 60), 'yellow',
        np.where((placeholder['Percentil'] >= 60) & (placeholder['Percentil'] < 80), 'lightgreen', 'green'))))
    dataframes.append(placeholder)

dataframes.reverse()

# '.values' convierte la columna 'Percentil' en un arreglo de números sin etiquetas ni nombres,
# es decir, solo una lista de los datos para usarlos fácilmente en cálculos o gráficos. 
# lo que aparece nos confirma si está todo bien convertido antes de mostrar el gráfico

df_percentiles['Percentil'].values


# Nombre del jugador que vamos a analizar y mostrar en el título del gráfico
jugador_nombre = "Alex Baena"  # Cámbialo por el nombre del jugador que estés analizando

# Inicializamos variables para controlar posiciones, etiquetas y datos del gráfico
contador = 0  # Contador para ubicar filas en el eje Y
yticks_positions = []  # Posiciones verticales para las etiquetas
yticks_labels = []     # Nombres de las estadísticas que se mostrarán en el eje Y
lineas_punteadas = []  # Posiciones donde pondremos líneas divisorias entre categorías
valores_estadisticas = []  # Valores "Por 90 minutos" para cada estadística
valores_percentiles = []   # Percentiles de rendimiento para cada estadística

# Creamos la figura y el eje donde se dibujará el gráfico con un tamaño personalizado
fig, ax = plt.subplots(figsize=(16, 9))

# Definimos rangos de percentiles y los colores asociados para codificar el rendimiento
intervalos = [0, 20, 40, 60, 80, 100]
colores = ['red', 'orange', 'yellow', 'lightgreen', 'green']

# Recorremos cada grupo de estadísticas para dibujarlas en el gráfico
for df in dataframes:
    for i in range(len(df)):
        plt.hlines(y=contador+i, xmin=0, xmax=df['Percentil'][i], colors=df['color'][i], linewidth=3.5)
        plt.plot(df['Percentil'][i], contador+i, "o", color=df['color'][i], markersize=10)
    
    yticks_positions.extend(np.arange(contador, contador + df.shape[0]))
    yticks_labels.extend(df['Estadísticas'])
    valores_estadisticas.extend(df['Por 90'])
    valores_percentiles.extend(df['Percentil'])
    
    # Dibujamos una línea punteada para separar las categorías en el gráfico
    plt.axhline(contador + df.shape[0], ls=':', color='black', lw=1.3)
    lineas_punteadas.append(contador + df.shape[0])
    
    # Establecemos el límite máximo del eje X en 100 (percentil máximo)
    ax.set_xlim(0, 100)
    
    contador += df.shape[0] + 1

# Aplicamos las etiquetas personalizadas en el eje Y (reemplazando nombres largos)
lista_reemplazada = [reemplazos.get(label, label) for label in yticks_labels]
plt.yticks(yticks_positions, lista_reemplazada)

# Quitamos los bordes y ticks innecesarios para dejar el gráfico más limpio
ax = plt.gca()
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.tick_params(axis='y', which='both', left=False, right=False)

# Mostramos el valor numérico del percentil al lado derecho de cada barra
for i in range(len(yticks_positions)):
    ax.text(105, yticks_positions[i], f"{valores_percentiles[i]:.0f}")

# Agregamos un título al gráfico con el nombre del jugador (saldrá automáticamente)
plt.title(f"Perfil de Rendimiento de {jugador_nombre}", fontsize=18, fontweight='bold')

# Mostramos el gráfico en pantalla
plt.show()