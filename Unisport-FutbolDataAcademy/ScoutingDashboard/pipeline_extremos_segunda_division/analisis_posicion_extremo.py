import pandas as pd
import os

pd.set_option('display.width', 220)
pd.set_option('display.max_columns', 40)

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_perfiles.csv")
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "dataset_recomendados.csv")
OUTPUT_INFORMES = os.path.join(os.path.dirname(__file__), "..", "informes_recomendados.csv")
PERFILES = ['REGATEADOR', 'FINALIZADOR', 'CREADOR']

MIN_MINUTOS = 900       # MEDIDO, no tecleado: es el codo donde la dispersión se aplana.
TOP_DESTACADOS = 5      # Corte por número de filas, lo que el bloque 3 prohíbe. Se admite
                        # SOLO aquí porque es una vitrina, no una selección: nadie queda
                        # excluido de nada por no estar en el top 5.
NOTA_ALTA = 75          # CRITERIO: qué se considera tramo alto de la categoría.

df = pd.read_csv(BASE)

# Sin valor de mercado no hay resta que calcular: fuera desde el principio, y NOMBRADO.
# Un NaN no da error, da False: si se dejara pasar, desaparecería en silencio de todos
# los bloques posteriores sin que nadie lo notara.
sin_precio = df[df['valor_mercado'].isna()]
if len(sin_precio):
    print(f"Fuera por no tener valor de mercado ({len(sin_precio)}): "
          f"{', '.join(sin_precio['nombre'])}")
df = df.dropna(subset=['valor_mercado']).reset_index(drop=True)

df['edad_n'] = df['edad'].str.extract(r'(\d+)').astype(float)
df['nota']   = df[PERFILES].max(axis=1)     # le juzga por su mejor faceta: premia al especialista
df['perfil'] = df[PERFILES].idxmax(axis=1)

COLS = ['nombre', 'equipo', 'edad_n', 'minutos_jugados', 'valor_mercado',
        'contrato_hasta', 'perfil', 'nota', 'discrepancia', 'jugador_seguro']



# --- 1. LOS DESTACADOS -------------------------------------------------------
# Sin filtrar por precio, contrato, edad ni minutos: incluye a los que no puede fichar
# nadie, que son los que dicen el techo de la categoría. La muestra va al lado.
print(f"\n=== 1. LOS DESTACADOS — {TOP_DESTACADOS} por perfil, sin filtrar ===")
for perfil in PERFILES:
    print(f"\n-- {perfil} --")
    print(df.nlargest(TOP_DESTACADOS, perfil)[
        ['nombre', 'equipo', 'edad_n', 'minutos_jugados', perfil]].to_string(index=False))

altos = df[df['nota'] >= NOTA_ALTA]
print(f"\nDe los {len(altos)} con nota >= {NOTA_ALTA}, solo "
      f"{(altos['minutos_jugados'] >= MIN_MINUTOS).sum()} pasan de {MIN_MINUTOS} minutos.")


# --- 2. LA RESTA -------------------------------------------------------------
# Los dos ejes en percentil del mismo pool: en euros absolutos metería un comprador
# concreto sin declararlo.
df['pctl_nota']    = df['nota'].rank(pct=True) * 100
df['pctl_precio']  = df['valor_mercado'].rank(pct=True) * 100
df['discrepancia'] = (df['pctl_nota'] - df['pctl_precio']).round(0)

# Control: una resta hereda los sesgos de sus dos mitades.
t15 = df.nlargest(15, 'discrepancia')
print("\n=== 2. LA RESTA — sesgo heredado ===")
print("corr(valor_mercado, minutos) Spearman:",
      round(df['valor_mercado'].corr(df['minutos_jugados'], method='spearman'), 2))
print(f"Muestras cortas (<{MIN_MINUTOS}) entre los 15 de mayor discrepancia: "
      f"{(t15['minutos_jugados'] < MIN_MINUTOS).sum()} de 15, contra "
      f"{(df['minutos_jugados'] < MIN_MINUTOS).sum()} de {len(df)} en el pool.")


# --- 3. LAS PEPITAS ----------------------------------------------------------
# Por condición, nunca por número de filas: cortar por cantidad tira al 13 por ser el 13.
# Las dos condiciones de calidad son definiciones, no umbrales ajustados.
es_pepita = ((df['discrepancia'] > 0) &
             (df['pctl_nota'] > 50) &
             (df['minutos_jugados'] >= MIN_MINUTOS))
pepitas = df[es_pepita].sort_values('discrepancia', ascending=False)

print(f"\n=== 3. LAS PEPITAS — {len(pepitas)} de {len(df)} ===")
print(pepitas[COLS].to_string(index=False))


# --- 4. LOS 8 DEL INFORME ----------------------------------------------------
# Selección FIRMADA por el analista, no salida del cálculo. Cuatro por calidad, sin
# mirar el precio, para que el informe diga cuál es el techo de la categoría. Cuatro
# por oportunidad, de las pepitas, con motivos distintos entre sí.
SELECCION = {
    'Arnau Puigmal':   'destacado',
    'Iuri Tabatadze':  'destacado',
    'Iñigo Vicente':   'destacado',
    'Pejiño':          'destacado',
    'Awer Mabil':      'oportunidad',
    'Yeray Cabanzon':  'oportunidad',
    'Salim El Jebari': 'oportunidad',
    'Pablo Sáenz':     'oportunidad',
}

informe = df[df['nombre'].isin(SELECCION)].copy()
informe['bloque'] = informe['nombre'].map(SELECCION)
assert len(informe) == len(SELECCION), set(SELECCION) - set(informe['nombre'])
informe.to_csv(OUTPUT, index=False)


# --- 5. LOS INFORMES ---------------------------------------------------------
# Escritos a mano, jugador a jugador, desde la ficha de cada uno. NO se generan con
# plantillas a propósito: una plantilla convierte el criterio del analista en
# aritmética, que es justo lo que este apartado no debe hacer. Cada uno nombra el
# punto débil del jugador y, si la muestra es corta, lo dice con el número delante.
INFORMES = {
"Arnau Puigmal":
"El mejor creador de la categoría y no está cerca de nadie: su nota de 91,25 es la más alta de los 83 extremos analizados. Reparte 2,80 pases clave por 90 minutos y 14,39 pases al último tercio, ambos registros en el percentil 96, y genera 0,59 grandes ocasiones por 90 (percentil 93) con 9 en total. Sus 5 asistencias en 1.382 minutos lo sitúan en el percentil 93 de la categoría y elevan su G+A por 90 a 0,52, muy por encima de la mediana de 0,33. Lo hace además con un 84,83% de acierto de pase (percentil 92) y solo 0,91 pérdidas por 90, lo que le da el sello de jugador seguro. No es un finalizador: 1,56 tiros por 90 lo dejan en el percentil 27. Su contrato terminó el 30 de junio.",

"Iuri Tabatadze":
"El finalizador más puro de la categoría y también el más extremo en su especialización. Sus 6 goles en 798 minutos dan 0,68 goles por 90, el registro más alto de los 83, y su G+A por 90 de 0,68 lo coloca en el percentil 94 pese a no haber dado ni una asistencia. Tira 2,82 veces por 90 con un 44% de acierto a puerta (percentil 86) y acierta el 57,14% de los regates que intenta. Fuera del área no aporta nada: 2 pases clave en toda la temporada (percentil 1), 0 grandes ocasiones creadas y un 68,53% de acierto de pase que es el percentil 6 de la categoría. El aviso importante es la muestra: 798 minutos son menos de nueve partidos completos, el percentil 18 del grupo. Contrato hasta 2028.",

"Iñigo Vicente":
"El extremo más completo de la categoría y el único cuyos números están respaldados por una temporada entera: 3.050 minutos, percentil 96. Lidera el grupo en las tres métricas de creación —136 pases clave, 705 pases al último tercio y 38 grandes ocasiones creadas—, las tres en el percentil 100, y sus 18 asistencias son también la mejor marca del pool. Suma 8 goles para un G+A por 90 de 0,77 y una valoración media de 7,54, la más alta de los 83. Acierta el 54,12% de sus regates. La contrapartida son sus 56 pérdidas de balón (1,65 por 90, percentil 71), el precio de asumir tantísimo volumen. Su discrepancia con el mercado es exactamente 0: vale 5,6 millones y rinde como el percentil 98. No es una oportunidad, es una referencia.",

"Pejiño":
"El regateador con más volumen de la categoría: 5,76 regates intentados por 90 minutos lo sitúan en el percentil 96, y no los malgasta, porque acierta el 55,17% (percentil 88) con 32 completados. Es desborde puro y poco más: 1 gol en toda la temporada y un 28,57% de acierto en tiros a puerta que lo deja en el percentil 24. Donde sí aparece es en la última acción, con 3 asistencias en 906 minutos (0,30 por 90, percentil 88) y un G+A por 90 de 0,40 por encima de la mediana de 0,33. Mantiene el balón razonablemente bien, con un 80,08% de acierto de pase. Dos avisos que van juntos: 30 años y solo 906 minutos jugados, el percentil 19 del grupo. Su contrato terminó el 30 de junio.",

"Awer Mabil":
"La mayor discrepancia entre rendimiento y precio de todo el pool: rinde en el percentil 89 y su valor de mercado está en el percentil 12. Con 1.731 minutos reparte 13,05 pases al último tercio por 90 (percentil 95) y genera 0,57 grandes ocasiones por 90 (percentil 92, 11 en total), y sus 6 asistencias lo colocan en el percentil 90. Es de los que menos pierde el balón de la categoría, 0,68 pérdidas por 90 en el percentil 13, lo que junto a su acierto de pase le da el sello de jugador seguro. No regatea: 1,82 intentos por 90 y un 37,14% de acierto lo dejan en el percentil 19. Y falla mucho lo que crea, con 8 grandes ocasiones falladas (percentil 92). Está barato porque tiene 30 años, y eso hay que decirlo.",

"Yeray Cabanzon":
"El mejor regateador del grupo en términos de acierto puro: 65,63% de regates exitosos, el percentil 99 de la categoría, aunque sobre un volumen moderado de 3,00 intentos por 90. Añade una capacidad de creación muy alta para sus 959 minutos, con 2,44 pases clave por 90 (percentil 94), 15,39 pases al último tercio (percentil 98) y 0,66 grandes ocasiones creadas (percentil 95). Sus 4 asistencias lo llevan al percentil 98 y su G+A por 90 de 0,56 supera con holgura la mediana de 0,33. Dispara muchísimo, 4,97 tiros por 90, el máximo del pool, pero solo el 30,18% van a puerta. El punto débil es claro: 1,97 pérdidas de balón por 90, el percentil 90 del grupo. Tiene 23 años y su contrato terminó el 30 de junio.",

"Salim El Jebari":
"El caso más limpio de jugador infravalorado del pool: con 22 años y un valor de mercado en el percentil 10 de la categoría, rinde en el percentil 71 y acumula 1.371 minutos que respaldan el dato. No está barato por edad ni por falta de partidos. Su fuerte es el uno contra uno: 4,27 regates intentados por 90 (percentil 75) con un 53,85% de acierto (percentil 84), 35 completados de 65. Y lo hace sin regalar el balón, con 1,25 pérdidas por 90 que están justo en la media del grupo. Reparte 1,58 pases clave por 90 y suma 4 asistencias (percentil 83) para un G+A por 90 de 0,33, exactamente la mediana. Lo que no aporta es tiro: 1,25 disparos por 90, el percentil 11. Su contrato terminó el 30 de junio.",

"Pablo Sáenz":
"El extremo más completo de los ocho: es el único con dos perfiles por encima de 75, creador con 79,94 y finalizador con 75,03, y lleva además el sello de jugador seguro. Crea 1,98 pases clave por 90 (percentil 88) y 0,44 grandes ocasiones (percentil 80), y remata con 2,79 tiros por 90 (percentil 83) y 0,29 goles por 90 (percentil 80), 4 goles en 1.226 minutos. Su G+A por 90 de 0,44 supera la mediana de 0,33. El detalle que lo separa del resto es que no desaprovecha: 0 grandes ocasiones falladas en toda la temporada, el percentil 12 de la categoría, y solo 0,95 pérdidas por 90. Su punto flojo es el regate, con un 44,23% de acierto que lo deja en la media. Su contrato terminó el 30 de junio.",

}

assert set(INFORMES) == set(SELECCION), set(INFORMES) ^ set(SELECCION)
pd.DataFrame({"nombre": list(INFORMES), "informe": list(INFORMES.values())}).to_csv(
    OUTPUT_INFORMES, index=False)
