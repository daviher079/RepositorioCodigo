import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, Sbopen
import pandas as pd

#Sbopen() es un parser (lector) que permite acceder a los datos open-data de StatsBomb.
parser = Sbopen()
datos_partido, related, freeze, tactics = parser.event(3923881)


#avisamos a python de donde empiezan los substitutos para que no los añada al gráfico de pases
#.loc lo que hace es un filtro en el que te quedas solo con las filas en las que tu le indiques la condición que quieres que se cumpla
#.iloc[0]["index"] acceso a la linea 0 de la columna index
primera_sustitucion_cote = datos_partido.loc[datos_partido["type_name"]=="Substitution"].loc[datos_partido["team_name"]=="Côte d'Ivoire"].iloc[0]["index"]

#Convertimos el archivo al dato de pases correctos de Costa de Marfil antes de los cambios
#datosPartido.outcome_name.isnull() los pases se reflejan en la columna outcome con el valor NaN osea sin valor si ha sido completado con exito 
#datosPartido.sub_type_name != "Throw-in" excluye los saques de banda
#este filtro tiene un nombre llamado mascara, y va comprobando fila a fila si va cumpliendo todas las condiciones, 
#en el momento que una de esas condiciones de false el registro ya no será incluido en el filtro
mascara_pases_cote = (
    (datos_partido.type_name == 'Pass') & 
    (datos_partido.team_name == "Côte d'Ivoire") & 
    (datos_partido.index < primera_sustitucion_cote) & 
    (datos_partido.outcome_name.isnull()) & 
    (datos_partido.sub_type_name != "Throw-in")
)

#Añadimos las columnas que son necesarias para crear la red de pases
#Estamos aplicando la mascara al DataFrame y hacemos que se cumplan las condiciones que tiene la mascara y que solamente devuelvan 
#las estadisticas que le pasamos dentro de la lista por lo tanto es un filtro con las condicones que le hemos pedidos y con las columnas
#que queremos mostrar
pases_datos_partido = datos_partido.loc[
    mascara_pases_cote, 
    ['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name"]
]
#Mostrar solo los apellidos de los jugadores
pases_datos_partido["player_name"] = pases_datos_partido["player_name"].apply(lambda x: str(x).split()[-1])
pases_datos_partido["pass_recipient_name"] = pases_datos_partido["pass_recipient_name"].apply(lambda x: str(x).split()[-1])

#Creación de un DataFrame vacio scatter es un grafico de dispersión un grafico de dispersion es un mapa para representar coordenadas X Y
scatter_df = pd.DataFrame()


#En la eunumeracion guardamos sin que se repita los nombres de cada jugador
#i indice para rellenar el DataFrame vacio
#el nombre del jugador en cada iteración está en name porque una enumeracion siempre devuelve dos valores, 
# siempre el indice, que en caso de no usarlo se debe de representar de las siguiente forma for _, name
for i, nombre_jugador in enumerate(pases_datos_partido["player_name"].unique()):

    #Con loc seleccionamos las filas donde la mascara es True
    #Lo que estamos cogiendo la posicion x desde donde ha dado el pase el jugador que estamos recorriendo 
    # generamos un array con to_numpy() con el objetivo de procesar los datos mas rapido gracias a to_numpy()
    #Contiene todas las posiciones X donde el jugador hizo un pase.
    posicion_pasador_x = pases_datos_partido.loc[pases_datos_partido["player_name"] == nombre_jugador]["x"].to_numpy()
    posicion_receptor_x = pases_datos_partido.loc[pases_datos_partido["pass_recipient_name"] == nombre_jugador]["end_x"].to_numpy()
    posicion_pasador_y = pases_datos_partido.loc[pases_datos_partido["player_name"] == nombre_jugador]["y"].to_numpy()
    posicion_receptor_y = pases_datos_partido.loc[pases_datos_partido["pass_recipient_name"] == nombre_jugador]["end_y"].to_numpy()

    #.at sirve para asignar un valor en una celda concreta
    scatter_df.at[i, "player_name"] = nombre_jugador

    #para calcular la posición media del jugador en el campo, no basta con mirar solo los pases que hizo.
    #También debes considerar dónde recibió el balón.
    #np.concatenate() es la unión de dos arrays 
    #np.mean() Calcula la media aritmética (el promedio) de los valores de un array.
    scatter_df.at[i, "x"] = np.mean(np.concatenate([posicion_pasador_x, posicion_receptor_x]))
    scatter_df.at[i, "y"] = np.mean(np.concatenate([posicion_pasador_y, posicion_receptor_y]))
    #Calcular cuántos pases ha realizado ese jugador
    #obtienes un dataFrame del filtro, de la cantidad de pases que ha realizado ese jugador aunque el DataFrame venga completo 
    #con todas sus columnas al añadirle el metodo count() en cada registro siempre viene el valor de el numero de pases que ha dado
    #en cada columna el registro siempre es el mismo por eso usamos .iloc[0] para coger el primer valor de la primera columna
    scatter_df.at[i, "numero_de_pases"] = pases_datos_partido.loc[pases_datos_partido["player_name"] == nombre_jugador].count().iloc[0]

    #Ajustamos el tamaño del circulo para que sea más grande cuando más pases da ese jugador
    scatter_df["tamaño_circulo"] = (scatter_df["numero_de_pases"] / scatter_df["numero_de_pases"].max() * 1500)

#Contar los pases entre un jugador y otro para aumentar el grosor de la linea según los pases realizados
#genera un identificador único para cada pareja de jugadores. Por ejemplo. Aurier -> Fofana // Fofana -> Aurier
#sorted ordena por orden alfabetico o numerico
#.apply(axis=1) significa fila a fila
pases_datos_partido["pair_key"] = pases_datos_partido.apply(
    lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])),  
    axis = 1)

# Agrupamos todos los pases por pareja de jugadores usando 'pair_key'.
# En cada grupo contamos cuántos pases hay (cada fila es un pase),
# usando count() sobre la columna 'x' porque cada pase tiene una coordenada 'x'.
# El resultado de groupby es una Serie, y con reset_index() lo convertimos
# en un DataFrame normal para poder manipularlo más adelante.
lines_df = pases_datos_partido.groupby(["pair_key"]).x.count().reset_index()

# renombramos la columna de nombre 'x' por 'pass_count', con el metodo rename, 
#a rename se le pueden añadir varios parametros, entre ellos le decimos que lo que 
#queremos es hacer el cambio en las columnas y no en un registro, para eso axis='columns'
#axis='index' cambia registros, inplace=True le estamos diciendo que haga el cambio en el DataFrame
# original y que no nos devuelva una copia
lines_df.rename({'x':'pass_count'}, axis='columns', inplace=True)
#Filtra el DataFrame lines_df para quedarse solo con las parejas de jugadores 
#que se pasaron el balón MÁS DE 2 veces.
lines_df = lines_df[lines_df['pass_count']>2]



pitch = Pitch(line_color='black')

fig, ax = pitch.grid(grid_heid = 0.9, title_heid = 0.06, axis = False, endnote_height = 0.04, title_space = 0, 
endnote_space = 0)

pitch.scatter(scatter_df.x, scatter_df.y, s = scatter_df.marker_size)
