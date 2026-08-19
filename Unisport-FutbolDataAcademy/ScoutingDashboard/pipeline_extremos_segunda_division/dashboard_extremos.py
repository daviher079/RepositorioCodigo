import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import ast
import os
from mplsoccer import PyPizza
import math
from scipy import stats


st.set_page_config(
    page_title="Análisis de Mercado Posición de Extremo",
    page_icon="🏃",
    layout="wide"
)

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_perfiles.csv")
RECOMENDADOS = os.path.join(os.path.dirname(__file__), "..", "dataset_recomendados.csv")
INFORMES = os.path.join(os.path.dirname(__file__), "..", "informes_recomendados.csv")

df = pd.read_csv(BASE)
# Los 8 del apartado de recomendaciones, con su texto pegado al lado. Los produce
# analisis_posicion_extremo.py; aquí solo se leen.
df_reco = pd.read_csv(RECOMENDADOS).merge(pd.read_csv(INFORMES), on="nombre", how="left")



st.title("Dashboard de Análisis de la posición de extremo de Segunda División Española")

st.markdown("""<style>
div[data-baseweb="select"] input {
    pointer-events: none !important;
    caret-color: transparent !important;
}
/* El "delta" de st.metric se usa aquí para colgar el por 90 bajo el bruto, no para indicar
   una variación: se le quita la flecha, que sugeriría que el dato ha subido. */
div[data-testid="stMetricDelta"] svg {
    display: none !important;
}
div[data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 6px !important;
    font-size: 18px !important;
}
div[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.08) !important;
}
</style>""", unsafe_allow_html=True)


# --- PESOS DE CADA PERFIL (solo para EXPLICARLOS en pantalla) ---
# OJO: estos números son una COPIA de los de clasificacion_por_perfiles.py, que es quien
# calcula las notas de verdad. Si allí se mueve un peso y aquí no, el dashboard seguirá
# explicando el viejo sin dar ningún error. Al tocar uno, tocar el otro.
PESOS_PERFIL = {
    "REGATEADOR": [
        ("Regates intentados por 90",                    50, False),
        ("% de regates exitosos",                        30, False),
        ("Pérdidas de balón por 90",                     20, True),
    ],
    "FINALIZADOR": [
        ("Goles por 90",                                 35, False),
        ("Tiros totales por 90",                         25, False),
        ("% de tiros a puerta",                          15, False),
        ("Grandes ocasiones falladas por 90",            15, True),
        ("Pérdidas de balón por 90",                     10, True),
    ],
    "CREADOR": [
        ("Pases clave por 90",                           30, False),
        ("Grandes ocasiones creadas por 90",             25, False),
        ("% de pases clave",                             15, False),
        ("Asistencias por 90",                           15, False),
        ("Pérdidas de balón por 90",                     15, True),
    ],
}


@st.dialog("Cómo se calcula la nota")
def modal_nota(perfil):
    st.markdown(f"**Nota de {perfil}** — de 0 a 100.")
    st.markdown(
        "Cada métrica se convierte en **percentil** dentro de los 84 extremos del pool "
        "(el mejor, 100; el peor, 0), se multiplica por su peso y se suman. "
        "Los pesos de cada perfil **suman 100**."
    )
    st.markdown("**Qué pesa, y cuánto:**")
    for etiqueta, peso, invertida in PESOS_PERFIL[perfil]:
        vuelta = " · *invertida: cuantas menos, mejor*" if invertida else ""
        st.markdown(f"- **{peso}** — {etiqueta}{vuelta}")
    if perfil == "CREADOR":
        st.markdown(
            "**Y un escalón aparte, fuera de esos 100:** −10 puntos si acierta menos del "
            "**75%** de sus pases. Un creador que no da bien el pase sencillo no es un creador, "
            "por bien que reparta los difíciles."
        )
    st.caption("Las métricas negativas no restan: se les da la vuelta antes de sumar, para que "
               "el techo de cada perfil no dependa de cuánto peso sea negativo.")


# --- EJES DEL RADAR: 3 fijas + 3 del perfil (6 en total) ---
# Las FIJAS describen lo que hace cualquier extremo, gane el perfil que gane, y son las
# que permiten comparar a un creador con un regateador. Se eligieron por cobertura
# (las tres tienen valor en 83-84 de los 84) y por no pisarse entre ellas.
# Goles y asistencias quedaron fuera de las fijas: 12 y 13 extremos las tienen a cero,
# y un eje pegado al centro no compara, deja un hueco que se lee como "malo".
RADAR_FIJAS = [
    ("pases_ultimo_tercio_por_90",          "Pases último tercio/90"),
    ("porcentaje_pases_acertados",          "% pases acertados"),
    ("perdidas_de_balon_por_90_invertido",  "Pérdidas de balón/90 (inv.)"),   # invertida: más lejos = pierde menos
]

# Las PROPIAS son las tres de mayor peso de cada perfil, para que el radar se parezca
# a la nota. Del finalizador cae grandes_ocasiones_falladas y del creador asistencias:
# mismo peso (15) que las que se quedan, pero peor cobertura (74/84 y 71/84).
RADAR_PERFIL = {
    "REGATEADOR": [
        ("regates_intentados_por_90",        "Regates intentados/90"),      # peso 50
        ("porcentaje_regates_exitosos",      "% regates exitosos"),         # peso 30
        ("tiros_a_puerta_por_90",            "Tiros a puerta/90"),          # complemento: ¿el desborde acaba en algo?
    ],
    "FINALIZADOR": [
        ("goles_por_90",                     "Goles/90"),                   # peso 35
        ("tiros_totales_por_90",             "Tiros totales/90"),           # peso 25
        ("porcentaje_tiros_a_puerta",        "% tiros a puerta"),           # peso 15
    ],
    "CREADOR": [
        ("pases_clave_por_90",               "Pases clave/90"),             # peso 30
        ("grandes_ocasiones_creadas_por_90", "Grandes ocasiones creadas/90"),# peso 25
        ("porcentaje_pases_clave",           "% pases clave"),              # peso 15
    ],
}


def nota_y_sello(jugador, color, perfil):
    """El círculo de la nota y el sello, con el mismo formato que la ficha del Tab 2.

    Sin los botones de info: los dos modales explican el CONCEPTO, no al jugador, y aquí
    se repetirían hasta cuatro veces diciendo lo mismo.
    """
    c_nota, c_seguro = st.columns([1, 1])

    with c_nota:
        st.markdown(f"""
        <div style="
            width:110px; height:110px; border-radius:50%;
            background-color:{color['bg']};
            border:2px solid {color['border']};
            display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            text-align:center;
        ">
            <span style="font-size:26px; font-weight:bold; color:{color['puntuacion']};">{jugador[perfil]:.2f}</span>
            <span style="font-size:11px; color:{color['puntuacion']};">Nota Perfil</span>
        </div>
        """, unsafe_allow_html=True)

    with c_seguro:
        st.markdown(
            "<div style='font-size:13px; font-weight:600; white-space:nowrap; padding-top:10px;'>"
            "Jugador Seguro:</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div style='font-size:34px; text-align:center; line-height:1.2;'>"
            f"{'🛡️' if bool(jugador['jugador_seguro']) else '❌'}</div>",
            unsafe_allow_html=True
        )


def ejes_radar(perfil):
    """Los 6 ejes del radar de ese perfil: primero las 3 fijas, luego las 3 suyas."""
    return RADAR_FIJAS + RADAR_PERFIL[perfil]

TEXTO_PERFIL = {
    "CREADOR": {
        "columna_dos":    ("Pases clave por 90", "pases_clave_por_90"),
        "columna_tres":   ("Grandes ocasiones creadas por 90", "grandes_ocasiones_creadas_por_90"),
        "columna_cuatro": ("Asistencias por 90", "asistencias_por_90"),
    },
    "FINALIZADOR": {
        "columna_dos":    ("Goles por 90", "goles_por_90"),
        "columna_tres":   ("Tiros totales por 90", "tiros_totales_por_90"),
        "columna_cuatro": ("Porcentaje tiros a puerta", "porcentaje_tiros_a_puerta"),
    },
    "REGATEADOR": {
        "columna_dos":    ("Regates intentados por 90", "regates_intentados_por_90"),
        "columna_tres":   ("Porcentaje regates exitosos", "porcentaje_regates_exitosos"),
        "columna_cuatro": ("Perdidas de balon por 90", "perdidas_de_balon_por_90"),
    },
}

TEXTO_VERTICAL_BARS = {
    "CREADOR":{
        "texto": "Grandes ocasiones creadas por 90 vs Asistencias por 90",
        "variables": ("grandes_ocasiones_creadas_por_90", "asistencias_por_90")
    },
    "FINALIZADOR":{
        "texto": "Goles por 90 vs Tiros a puerta por 90",
        "variables": ("goles_por_90", "tiros_a_puerta_por_90")
    },
    "REGATEADOR":{
        "texto": "Regates intentados por 90 vs perdidas de balón por 90",
        "variables": ("regates_intentados_por_90", "perdidas_de_balon_por_90") 
    } 
    
}


COLORES_NIVEL = {
    "verde": {
        "bg":         "rgba(0, 204, 150, 0.2)",
        "border":     "rgb(0, 204, 150)",
        "puntuacion": "rgb(0, 204, 150)",
        "mpl_oscuro": (0/255, 163/255, 120/255),
        "mpl_claro":  (102/255, 255/255, 204/255),
        "css_oscuro": "#00A378",
        "css_claro":  "#66FFCC",
    },
    "ambar": {
        "bg":         "rgba(255, 165, 0, 0.2)",
        "border":     "rgb(255, 165, 0)",
        "puntuacion": "rgb(255, 165, 0)",
        "mpl_oscuro": (204/255, 132/255, 0/255),
        "mpl_claro":  (255/255, 210/255, 120/255),
        "css_oscuro": "#CC8400",
        "css_claro":  "#FFD278",
    },
    "rojo": {
        "bg":         "rgba(254, 1, 1, 0.2)",
        "border":     "rgb(254, 1, 1)",
        "puntuacion": "rgb(254, 1, 1)",
        "mpl_oscuro": (204/255, 0/255, 0/255),
        "mpl_claro":  (255/255, 110/255, 110/255),
        "css_oscuro": "#CC0000",
        "css_claro":  "#FF6E6E",
    },
}

def umbrales_puntuacion(puntuacion):
    if pd.isna(puntuacion):
        nivel = "rojo"
    elif puntuacion >= 70:
        nivel = "verde"
    elif (puntuacion >= 50) & (puntuacion <70):
        nivel = "ambar"
    else:
        nivel = "rojo"
    return nivel



def calcular_percentiles(jugador, df_ref, ejes):
    """Sitúa al jugador dentro del pool, eje por eje.

    NO normaliza por minutos: las columnas que llegan aquí ya vienen normalizadas del
    pipeline (_por_90, porcentaje_ o _invertido). Dividir otra vez sería contarlo dos veces.
    """
    return [
        math.floor(stats.percentileofscore(df_ref[col], jugador[col]))
        for col, _ in ejes
    ]

def render_radar(values, color, ejes):
    for n, i in enumerate(values):
        if i == 100:
            values[n] = 99

    baker = PyPizza(
        params=[etiqueta for _, etiqueta in ejes],
        straight_line_color= (0.7, 0.7, 0.7, 0.5),
        straight_line_lw = 0.5,
        last_circle_color= (0.7, 0.7, 0.7, 0.5),
        last_circle_lw = 0.5,
        other_circle_color= (0.7, 0.7, 0.7, 0.5),
        other_circle_lw = 0.5,
        other_circle_ls = "-."
        )

    # 3 fijas en claro, 3 propias del perfil en oscuro: el color separa contexto de nota
    colores_slices = [color['mpl_claro']] * 3 + [color['mpl_oscuro']] * 3

    fig, ax = baker.make_pizza(
        values,
        figsize=(2.6, 2.6),
        param_location=110,
        kwargs_slices=dict(
            facecolor=colores_slices,
            edgecolor=colores_slices,
            zorder=2, linewidth=1, alpha=0.6
        ),
        kwargs_params=dict(
            color=(0, 0, 0, 0), fontsize=7,
            va="center"
        ),
        kwargs_values=dict(
            color="#ffffff",
            fontsize=7,
            zorder=3,
            bbox=dict(
                edgecolor="#ffffff",
                facecolor=(0.1, 0.1, 0.1, 0.6),
                boxstyle="round,pad=0.2",
                lw=0.5
            )
        )
    )

    st.pyplot(fig, transparent=True, width='content')


@st.dialog("Qué es un jugador seguro")
def modal_jugador_seguro():
    st.markdown("Un extremo que, además de lo que haga en ataque, **no regala el balón**. "
                "Se cumplen **las dos** condiciones a la vez:")
    st.markdown(
        "**1. Pierde pocos balones** — está en el **40% que menos pierde** por cada 90 minutos, "
        "dentro de los 84 extremos del pool.\n\n"
        "Es una condición **relativa**: se mide contra los demás extremos de la categoría, "
        "así que *pocas pérdidas* significa pocas para un extremo de Segunda."
    )
    st.markdown(
        "**2. Acierta al menos el 75% de sus pases.**\n\n"
        "Es una condición **absoluta**: no depende del pool. Un 75% es un 75% aquí y en "
        "cualquier otra categoría, así que el sello significa lo mismo si algún día entra otra liga."
    )
    st.markdown("Lo cumplen **18 de los 84** extremos.")
    st.markdown("No es un cuarto perfil: es una etiqueta que se cuelga **encima** del que ya tenga "
                "el jugador — *regateador, y además seguro*.")


def caracteristicas_perfil(perfil):
    return TEXTO_PERFIL[perfil]



def col_grafica_horizontal(df, perfil, TEXTO_VERTICAL_BARS):
        datos_perfil = TEXTO_VERTICAL_BARS[perfil]
        texto = datos_perfil['texto']
        var1, var2 = datos_perfil['variables']
        st.subheader(texto)
        fig = px.bar(
            df,
            x="nombre",
            y=[var1, var2],
            barmode="group",
            color_discrete_sequence=["#00CC96", "#FE0101"]
        )
        fig.update_layout(xaxis_tickangle=-45, xaxis_title="", legend_title="")
        st.plotly_chart(fig, use_container_width=True)

PERFILES = ["CREADOR", "FINALIZADOR", "REGATEADOR"]
NOTAS = {
    "< 50":    (0,   50),
    "50 - 70": (50,  70),
    "> 70":    (70, 101),
}
perfil = st.segmented_control("Perfil", PERFILES, default=PERFILES[0]) or PERFILES[0]
nota   = st.segmented_control("Nota", list(NOTAS), default="> 70") or "> 70"
minimo, maximo = NOTAS[nota]
df_filtros = df[(df[perfil] >= minimo) & (df[perfil] < maximo)]

tabs = st.tabs(["Resumen General", "Análisis Individual", "Comparativa", "Recomendaciones"])

# === TAB 1: RESUMEN GENERAL ===
with tabs[0]:
    columnas = caracteristicas_perfil(perfil)
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Extremos de ese perfil", value=len(df_filtros))
    with col2:
        key, value = columnas['columna_dos']
        st.metric(label= "Media de " f"{key}", value=f"{round(df_filtros[value].mean(), 2)}")
    with col3:
        key, value = columnas['columna_tres']
        st.metric(label= "Media de " f"{key}", value=f"{round(df_filtros[value].mean(), 2)}")
    with col4:
        key, value = columnas['columna_cuatro']
        st.metric(label="Media de " f"{key}", value=f"{round(df_filtros[value].mean(), 2)}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        col_grafica_horizontal(df_filtros, perfil, TEXTO_VERTICAL_BARS)

    with col2:
        st.subheader("Distribución del pie dominante")
        df_pie = df_filtros["pie_dominante"].value_counts().reset_index()
        df_pie.columns = ["Pie Dominante", "Jugadores"]
        fig = px.pie(
            df_pie,
            values="Jugadores",
            names="Pie Dominante",
            title="Distribución por pie dominante",
            color_discrete_sequence=["#0052A3", "#0099E6", "#66CCFF"]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Listado de Extremos")

    # Informe general: todas las columnas valen para cualquier extremo, gane el perfil que
    # gane. Las de producción van POR 90 y no en crudo: un conteo se acumula, y ordenar por
    # él premia a quien más juega (G+A crudo correlaciona 0,70 con los minutos; por 90, 0,20).
    # Los minutos se quedan al lado para poder leer con cautela a los de poca muestra.
    df_tabla = pd.DataFrame({
        "Nombre": df_filtros["nombre"],
        "Equipo": df_filtros["equipo"],
        "G + A por 90": (
            (df_filtros["goles"] + df_filtros["asistencias"]) / df_filtros["minutos_jugados"] * 90
        ).round(2),
        "Minutos Jugados": df_filtros["minutos_jugados"],
        "Pases al Último Tercio cada 90 mins.": df_filtros["pases_ultimo_tercio_por_90"].round(2),
        "Pases Clave por 90": df_filtros["pases_clave_por_90"].round(2),
        "Pérdidas por 90": df_filtros["perdidas_de_balon_por_90"].round(2),
        "Pases Acertados %": df_filtros["porcentaje_pases_acertados"].round(1),
        # mismo lenguaje visual que la ficha del Tab 2: escudo / aspa roja
        "Jugador Seguro": df_filtros["jugador_seguro"].map({True: "🛡️", False: "❌"}),
        "Nota": df_filtros[perfil],
    })

    st.dataframe(
        df_tabla,
        column_config={
            "Pases Acertados %": st.column_config.ProgressColumn(
                "Pases Acertados %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Jugador Seguro": st.column_config.TextColumn(
                "Jugador Seguro",
                help="Pierde pocos balones (40% que menos pierde del pool) y acierta ≥75% de los pases",
                alignment="center",
            ),
        },
        hide_index=True
    )


    # === TAB 2: ANÁLISIS INDIVIDUAL ===
with tabs[1]:
    jugador_seleccionado = st.selectbox(
        "Seleccionar Jugador",
        options=df_filtros["nombre"].tolist(),
        index=0,
        key="jugador_selector"
    )

    jugador = df_filtros[df_filtros["nombre"] == jugador_seleccionado].iloc[0]
    color = COLORES_NIVEL[umbrales_puntuacion(jugador[perfil])]

   
    st.markdown(f"<h2 style='margin:0; padding-top:10px;'>{jugador_seleccionado}</h2>",
                unsafe_allow_html=True)

    posiciones = ', '.join(ast.literal_eval(jugador['posicion_detallada']))

    col_radar, col_ficha = st.columns([3, 2])


    with col_radar:
        ejes = ejes_radar(perfil)
        values = calcular_percentiles(jugador, df, ejes)
        render_radar(values, color, ejes)
       

    with col_ficha:
        f1, f2 = st.columns(2)
        with f1:
            st.metric(label="Equipo",            value= jugador['equipo'])
            st.metric(label="Altura",            value= f"{jugador['altura']} cm")
            st.metric(label="Posiciones",        value= posiciones)
            st.metric(label="Valor de Mercado",  value= jugador['valor_mercado_fmt'])
        with f2:
            st.metric(label="Edad",              value= jugador['edad'])
            st.metric(label="Pie dominante",     value= jugador['pie_dominante'])
            st.metric(label="Contrato hasta",    value= jugador['contrato_hasta'])
            st.metric(label="Minutos Jugados",   value= jugador['minutos_jugados'])

        st.markdown(f"""
        <div style="
            margin-top:16px;
            border:1px solid rgba(255,255,255,0.15);
            border-radius:8px;
            padding:14px 16px;
        ">
            <div style="font-size:13px; font-weight:600; color:#aaa; letter-spacing:0.08em; margin-bottom:10px;">
                LEYENDA RADAR
            </div>
            <div style="font-size:12px; color:#888; margin-top:-6px;">
                Cada número es el <b>percentil</b> dentro de los 84 extremos del pool, no el valor de la métrica.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_fijas, col_propias = st.columns([1, 1])

        # La leyenda se genera desde los ejes: si cambian las métricas de un perfil,
        # cambia sola. Antes eran ocho líneas escritas a mano.
        def _bloque_leyenda(pares, css):
            filas = "".join(
                f'<span style="background:{css}; border-radius:3px; padding:2px 10px;'
                f' margin-right:8px;">&nbsp;</span> {etiqueta} — <b>{valor}</b><br>'
                for etiqueta, valor in pares
            )
            return f'<div style="font-size:15px; line-height:2.3;">{filas}</div>'

        etiquetas = [e for _, e in ejes]
        fijas   = list(zip(etiquetas[:3], values[:3]))
        propias = list(zip(etiquetas[3:], values[3:]))

        with col_fijas:
            st.markdown(f'<div style="font-size:12px; color:#888;">COMÚN A TODO EXTREMO</div>',
                        unsafe_allow_html=True)
            st.markdown(_bloque_leyenda(fijas, color['css_claro']), unsafe_allow_html=True)

        with col_propias:
            st.markdown(f'<div style="font-size:12px; color:#888;">PESA EN LA NOTA DE {perfil}</div>',
                        unsafe_allow_html=True)
            st.markdown(_bloque_leyenda(propias, color['css_oscuro']), unsafe_allow_html=True)

        st.divider()
        col_nota, col_seguro = st.columns([1, 1])

        with col_nota:
            c_circulo, c_info_nota = st.columns([2, 1])

            with c_info_nota:
                if st.button("ℹ️", key="btn_nota"):
                    modal_nota(perfil)

            with c_circulo:
                st.markdown(f"""
                <div style="
                    width:110px; height:110px; border-radius:50%;
                    background-color:{color['bg']};
                    border:2px solid {color['border']};
                    display:flex; flex-direction:column;
                    align-items:center; justify-content:center;
                    text-align:center;
                ">
                    <span style="font-size:26px; font-weight:bold; color:{color['puntuacion']};">{jugador[perfil]:.2f}</span>
                    <span style="font-size:11px; color:{color['puntuacion']};">Nota Perfil</span>
                </div>
                """, unsafe_allow_html=True)

        with col_seguro:
            seguro = bool(jugador["jugador_seguro"])

            c_sello, c_info = st.columns([2, 1])
            with c_sello:
                st.markdown(
                    "<div style='font-size:13px; font-weight:600; white-space:nowrap; padding-top:10px;'>"
                    "Jugador Seguro:</div>",
                    unsafe_allow_html=True
                )
            with c_info:
                if st.button("ℹ️", key="btn_seguro"):
                    modal_jugador_seguro()

            st.markdown(
                f"<div style='font-size:34px; text-align:center; line-height:1.2;'>"
                f"{'🛡️' if seguro else '❌'}</div>",
                unsafe_allow_html=True
            )

    st.divider()

    # Las tres secciones son el RETRATO del jugador: comunes a los tres perfiles, para poder
    # ver lo que su nota NO mide. Sobre esa base común, cada perfil añade la métrica suya que
    # no estaba en ninguna sección — la del regateador pesa 50, la mitad de su nota.
    # Podadas por duplicar a otra de su misma sección: "Pases Totales" (0,99 con Pases
    # Acertados) y "Tiros a Puerta" (0,95 con Tiros). Las tarjetas se quedan aunque la mayoría
    # tenga 0: ahí la información está en los pocos que NO lo tienen (13 con roja).
    #
    # EL NÚMERO GRANDE ES EL BRUTO, con el por 90 debajo en gris. Ninguno de los dos sobra:
    # 15 de los 16 conteos de estas secciones correlacionan >=0,53 con los minutos jugados
    # (pases_acertados 0,87; pases_ultimo_tercio 0,83; pases_clave 0,79), así que el bruto
    # solo invita a comparar mal. Pero si se deja SOLO el por 90, no queda un sitio en todo
    # el dashboard donde ver lo que el jugador ha hecho de verdad: el radar es percentil,
    # la nota es percentil y la tabla del Tab 1 ya va por 90. El hecho vive aquí.
    EXTRA_PERFIL = {
        "REGATEADOR":  ("CREACIÓN",  "Regates Intentados", "regates_intentados"),
        "FINALIZADOR": ("OFENSIVAS", "% Tiros a Puerta",   "porcentaje_tiros_a_puerta"),
        "CREADOR":     ("OFENSIVAS", "% Pases Clave",      "porcentaje_pases_clave"),
    }

    def _bruto(etiqueta, columna):
        """Conteo: el bruto grande y su por 90 debajo, en gris (delta_color='off')."""
        p90_col = f"{columna}_por_90"
        p90 = jugador[p90_col] if p90_col in jugador.index else jugador[columna] / jugador["minutos_jugados"] * 90
        return (etiqueta, int(jugador[columna]), f"{p90:.2f} /90")

    def _pct(etiqueta, columna):
        """Porcentaje: ya es un ratio, no se acumula con los minutos. Sin por 90."""
        return (etiqueta, f"{jugador[columna]:.1f}%", None)

    def _pinta(metricas, por_fila=4):
        """Reparte en filas, para que el número de columnas no dependa del perfil."""
        for i in range(0, len(metricas), por_fila):
            for col, (etiqueta, valor, delta) in zip(st.columns(por_fila), metricas[i:i + por_fila]):
                col.metric(etiqueta, valor, delta=delta, delta_color="off")

    def _con_extra(seccion, metricas):
        extra = EXTRA_PERFIL.get(perfil)
        if extra and extra[0] == seccion:
            _, etiqueta, columna = extra
            metricas = metricas + [_pct(etiqueta, columna) if columna.startswith("porcentaje_")
                                   else _bruto(etiqueta, columna)]
        return metricas

    st.subheader("Estadísticas Ofensivas")
    _pinta(_con_extra("OFENSIVAS", [
        _bruto("Goles",                   "goles"),
        _bruto("Asistencias",             "asistencias"),
        _bruto("Tiros",                   "tiros_totales"),
        ("G + A por 90 Min",
         f"{(int(jugador['goles']) + int(jugador['asistencias'])) / int(jugador['minutos_jugados']) * 90:.2f}",
         None),
        _bruto("Grandes Oport. Creadas",  "grandes_ocasiones_creadas"),
        _bruto("Grandes Oport. Falladas", "grandes_ocasiones_falladas"),
    ]))

    st.divider()

    st.subheader("Creación y Conducción")
    _pinta(_con_extra("CREACIÓN", [
        _bruto("Pases Clave",         "pases_clave"),
        _bruto("Pases Último Tercio", "pases_ultimo_tercio"),
        _bruto("Pases Acertados",     "pases_acertados"),
        _pct("% Pases Acertados",     "porcentaje_pases_acertados"),
        _bruto("Regates Exitosos",    "regates_exitosos"),
        _pct("% Regates Exitosos",    "porcentaje_regates_exitosos"),
        _bruto("Pérdidas de Balón",   "perdidas_de_balon"),
    ]))

    st.divider()

    st.subheader("Trabajo Defensivo")
    _pinta([
        _bruto("Intercepciones",         "intercepciones"),
        _bruto("Entradas",               "entradas"),
        _bruto("Duelos Aéreos Perdidos", "duelos_aereos_perdidos"),
        _bruto("Tarjetas Amarillas",     "tarjetas_amarillas"),
        _bruto("Tarjetas Rojas",         "tarjetas_rojas"),
    ], por_fila=5)


# === TAB 3: COMPARATIVA ===
with tabs[2]:
    st.subheader("Selección de Jugadores para Comparar")
    
    # Multiselect para elegir jugadores a comparar
    jugadores_seleccionados = st.multiselect(
        "Seleccionar jugadores (máx. 2)",
        options=df_filtros["nombre"].tolist(),
        default=df_filtros["nombre"].iloc[0],
        max_selections=2        
    )
    
    
    # Verificar que hay al menos un jugador seleccionado
    if not jugadores_seleccionados:
        st.warning("Por favor selecciona al menos un jugador para analizar")
    else:
        # Filtrar datos de los jugadores seleccionados
        datos_jugadores =  df_filtros[df_filtros["nombre"].isin(jugadores_seleccionados)]
        
        # Comparativa radar
        st.subheader("Comparativa de Perfiles")

        st.divider()

        col_radar_comparativo, col_tabla = st.columns([2, 2])

        jugador1 = datos_jugadores.iloc[0]
        jugador2 = datos_jugadores.iloc[1] if len(datos_jugadores) > 1 else None
        color1 = COLORES_NIVEL[umbrales_puntuacion(jugador1[perfil])]
        color2 = COLORES_NIVEL[umbrales_puntuacion(jugador2[perfil])] if jugador2 is not None else None
        with col_radar_comparativo:

            fig = go.Figure()

            st.subheader("Radar Jugadores:")
            ejes = ejes_radar(perfil)
            st.caption("Cada eje es el **percentil** dentro de los 84 extremos del pool, no el valor de la métrica.")
            for i, (_, jugador) in enumerate(datos_jugadores.iterrows()):
                values = calcular_percentiles(jugador, df, ejes)
                color = COLORES_NIVEL[umbrales_puntuacion(jugador[perfil])]

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=[etiqueta for _, etiqueta in ejes],
                    fill='toself',
                    name=jugador["nombre"],
                    line=dict(color=color['border']),
                    fillcolor=color['bg']
                ))

            fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True
            )
        
            st.plotly_chart(fig, use_container_width=True)
       

        with col_tabla:
            st.subheader("Tabla comparativa:")
            if jugador2 is not None: 
                tabla = go.Figure()
                tabla.add_trace(go.Table(
                    header=dict(values=[jugador1["nombre"], "Métrica", jugador2["nombre"]],line=dict(width=0),font=dict(size=15)),
                    cells=dict(values=[
                        [f"<b>{jugador1[c]:.2f}</b>" for c, _ in ejes],
                        [etiqueta for _, etiqueta in ejes],
                        [f"<b>{jugador2[c]:.2f}</b>" for c, _ in ejes],
                    ],
                    font=dict(size=16, color=[color1['border'], 'black', color2['border']]),
                    fill_color='white',
                    line=dict(width=0),
                    height=35
                )))
                tabla.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=390)

                st.plotly_chart(tabla, use_container_width=True)
                col_j1, col_j2 = st.columns([1, 1])
                with col_j1:
                    nota_y_sello(jugador1, color1, perfil)
                with col_j2:
                    nota_y_sello(jugador2, color2, perfil)

            else:
                nota_y_sello(jugador1, color1, perfil)

                col_m1, col_m2 = st.columns(2)
                for i, (col_metrica, etiqueta) in enumerate(ejes):
                    col = col_m1 if i < 3 else col_m2
                    with col:
                        st.metric(etiqueta, f"{jugador1[col_metrica]:.2f}")


st.markdown("""<style>
/* La tarjeta es el stVerticalBlock que lleva el marcador reco-card como hijo directo.
   El ">" es imprescindible: sin él, :has() alcanzaría también a los bloques de arriba. */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] span.reco-card) {
    position: relative;
    cursor: pointer;
    transition: border-color .15s ease, box-shadow .15s ease;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] span.reco-card):hover {
    border-color: rgba(120,160,255,.85);
    box-shadow: 0 0 0 2px rgba(120,160,255,.25);
}
/* El botón con clave reco_card_* se estira invisible sobre toda la tarjeta: el clic
   vale en cualquier punto. Streamlit sella la clave del widget como clase st-key-*. */
div[data-testid="stElementContainer"][class*="st-key-reco_card_"] {
    position: absolute; top: 0; left: 0; z-index: 5; margin: 0; padding: 0;
    width: 100% !important; height: 100% !important;
}
div[data-testid="stElementContainer"][class*="st-key-reco_card_"] div[data-testid="stButton"],
div[data-testid="stElementContainer"][class*="st-key-reco_card_"] button {
    width: 100%; height: 100%; opacity: 0; border: none; background: transparent;
}
</style>""", unsafe_allow_html=True)


@st.dialog("Informe del jugador")
def modal_informe_reco(j):
    sello = " · 🛡️ Jugador seguro" if j["jugador_seguro"] else ""
    st.markdown(f"**{j['nombre']}** · {j['equipo']} · {j['edad']} · {j['perfil'].capitalize()}{sello}")
    st.write(j["informe"])


# === TAB 4: RECOMENDACIONES ===
# Selección FIJA de 8 jugadores: no la filtran los selectores de perfil y nota de
# arriba, porque es una opinión firmada y no una consulta.
with tabs[3]:
    st.markdown(
        "Ocho extremos sobre los 83 del pool. **Cuatro por nivel**, sin "
        "mirar el precio, para enseñar cuál es el techo real de la categoría. **Cuatro "
        "por oportunidad**, donde el mercado les pone menos de lo que rinden. "
        "La selección y los informes son criterio del analista, no salida del cálculo."
    )

    with st.container(border=True):
        st.markdown("##### Qué es la discrepancia")
        st.markdown(
            "Se ordena a los 83 extremos **dos veces**: una por su nota de perfil y otra "
            "por su valor de mercado. Cada jugador recibe así dos posiciones de 0 a 100, "
            "y la discrepancia es la **resta** entre ambas."
        )
        st.markdown(
            "- **Positiva** — rinde por encima del puesto que le da el mercado. "
            "Awer Mabil marca **+77**: produce como el 11% mejor de la categoría y cuesta "
            "como el 12% más barato.\n"
            "- **Cero** — el precio coincide con el rendimiento. Iñigo Vicente da **0**: "
            "vale 5,6 millones y rinde en el percentil 98. No es un hallazgo, es un precio justo.\n"
            "- **Negativa** — no significa mal jugador, significa que el mercado le paga "
            "por cosas que este análisis no mide: proyección, edad o recorrido de reventa."
        )
        st.caption(
            "Se mide en percentiles del propio pool y no en euros a propósito: un umbral "
            "en euros daría por supuesto un presupuesto concreto, y lo que es caro para un "
            "club es calderilla para otro. Así el dato vale lo lea quien lo lea."
        )

    BLOQUES = [
        ("destacado",   "Los mejores de la categoría",
         "Los cuatro de más nivel del pool, sin filtro de precio ni de contrato."),
        ("oportunidad", "Las oportunidades",
         "Rinden por encima de lo que el mercado les paga."),
    ]

    for clave, titulo, subtitulo in BLOQUES:
        st.divider()
        st.subheader(titulo)
        st.caption(subtitulo)

        bloque = df_reco[df_reco["bloque"] == clave].sort_values("nota", ascending=False)

        # De dos en dos: se recorre la lista a saltos de 2 y cada pareja va en su fila.
        for inicio in range(0, len(bloque), 2):
            fila = st.columns(2)
            for hueco, (_, j) in zip(fila, bloque.iloc[inicio:inicio + 2].iterrows()):
                with hueco, st.container(border=True):
                    st.markdown('<span class="reco-card"></span>', unsafe_allow_html=True)
                    sello = " · 🛡️ Jugador seguro" if j["jugador_seguro"] else ""
                    st.markdown(f"### {j['nombre']}")
                    st.caption(f"{j['equipo']} · {j['edad']} · {j['perfil'].capitalize()}{sello}")

                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Nota", f"{j['nota']:.2f}")
                    with m2:
                        st.metric("Minutos", f"{int(j['minutos_jugados']):,}".replace(",", "."))
                    with m3:
                        st.metric("Valor", j["valor_mercado_fmt"])
                    with m4:
                        st.metric("Discrepancia", f"{int(j['discrepancia']):+d}")

                    if st.button("Ver informe", key=f"reco_{j['id']}"):
                        modal_informe_reco(j)

                    # Mismo destino, invisible y estirado por CSS sobre la tarjeta entera.
                    if st.button("Ver informe", key=f"reco_card_{j['id']}"):
                        modal_informe_reco(j)
