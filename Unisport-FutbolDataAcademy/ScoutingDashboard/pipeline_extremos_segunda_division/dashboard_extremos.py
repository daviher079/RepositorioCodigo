import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import ast
import os
from mplsoccer import PyPizza, Pitch
import math
from scipy import stats
import matplotlib.patheffects as path_effects


st.set_page_config(
    page_title="Análisis de Mercado Posición de Extremo",
    page_icon="🏃",
    layout="wide"
)

BASE = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_filtrado_modelado.csv")
df = pd.read_csv(BASE)

BASE_REF = os.path.join(os.path.dirname(__file__), "..", "dataset_extremos_contextualizados.csv")
df_ref = pd.read_csv(BASE_REF)

st.title("Dashboard de Análisis Zamora Club de Futbol")
st.markdown("Criterios aplicados para posibles fichajes en la posición de extremo: contrato expira 2026/27 · valor de mercado < 500.000 € · mínimo 200 min jugados")

st.markdown("""<style>
div[data-baseweb="select"] input {
    pointer-events: none !important;
    caret-color: transparent !important;
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
.element-container:has(.informe-btn) ~ .element-container [data-testid="stButton"] button {
    background: rgba(0, 153, 230, 0.15) !important;
    border: 2px solid rgb(0, 153, 230) !important;
    border-radius: 8px !important;
    color: rgb(0, 153, 230) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 6px 14px !important;
    width: 100% !important;
}
.element-container:has(.informe-btn) ~ .element-container [data-testid="stButton"] button:hover {
    background: rgba(0, 153, 230, 0.28) !important;
}
</style>""", unsafe_allow_html=True)


TABLA_COMPARADOR_JUGADORES = {
    "tiros_a_puerta": "tiros a puerta",
    "grandes_ocasiones_creadas": "grandes ocasiones creadas",
    "asistencias": "asistencias",
    "goles": "goles",
    "pases_ultimo_tercio": "pases ultimo tercio",
    "pases_clave": "pases clave",
    "porcentaje_regates_exitosos": "porcentaje regates exitosos",
    "regates_exitosos": "regates exitosos"
}

variables_radar = [
    "tiros_a_puerta",
    "grandes_ocasiones_creadas",
    "asistencias",
    "goles",
    "pases_ultimo_tercio",
    "pases_clave",
    "porcentaje_regates_exitosos",
    "regates_exitosos"
]

JUGADORES_INFORME = {
    "José Corpas":{
        "perfil": "extremo que destaca por su capacidad para crear peligro, generando gran cantidad de pases clave y una gran capacidad de regates exitosos, pese a su edad 34 años de edad se encuentra por encima del 63% de los extremos generando grandes ocasiones cada 90 minutos y estando por encima del 72% de los jugadores de su posicion repartiendo asistencias. Se justifican con sus 58 pases clave y sus 12 grandes oportunidades creadas, además de tener un porcentaje alto de regates exitosos de 40,8%, sus 3168 minutos jugados lo avalan como jugador importante para su entrenador y teniendo una capacidad de G + A por 90 de 0,31 muy cercano a la media de la categoria que son 0,37.", 
        "situación contractual": "Su situación contractual es atractiva ya que su contrato termina este año y su valor es inferior a 500K€",
        "recomendacion": "Prioritario"
    },
    "Jastin García":{
       "perfil": "extremo que destaca por su gran capacidad para generar peligro y mucho desborde, destaca por su gran cantidad de pases al último tercio (143), sus pases claves(21) y su buen porcentaje de regates exitosos(53,8%) lo que lo lleva a estar por encima del 94% de extremos por 90 min, pese a su edad 22 años, suma un total de 1368 minutos, y ha generado 3 goles y 2 asistencias y está cerca de la media de la categoría con un G + A por 90 de 0,33 muy cercano a la media de la categoria que son 0,37.",
        "situación contractual": "Su situación contractual  es atractiva ya que su contrato termina este año y su valor es inferior a 500K€",
        "recomendacion": "Recomendable"
    },
    "Salim El Jebari":{
        "perfil": "Extremo que destaca por su gran capacidad para generar peligro y mucho desborde, destaca por su gran cantidad de pases al último tercio (103), sus pases claves(24) y su buen porcentaje de regates exitosos(53,9%) lo que lo lleva a estar por encima del 81% de extremos por 90 min, pese a su edad 22 años, suma un total de 1371 minutos, y ha generado 1 gol y 4 asistencias y está cerca de la media de la categoría con un G + A por 90 de 0,33 muy cercano a la media de la categoria que son 0,37. ",
        "situación contractual": "Su situación contractual  es atractiva ya que su contrato termina este año y su valor es inferior a 500K€",
        "recomendacion": "Recomendable"
    },
    "Francisco Portillo":{
        "perfil": "Jugador que puede jugar en la posicion de extremo que destaca por su capacidad de generar juego siendo su mejor faceta la cantidad de pases al último tercio(364) y los pases clave(44) que es capaz de dar, por lo tanto su capacidad de generar peligro es alta para la categoría, tiene una gran capacidad para el regate teniendo un 45,1% de exito en sus intentos lo que lo lleva a estar por encima del 48% de los jugadores de su posicion, pero lo intenta pocas veces por partido ya que se encuentra por encima de solo el 23% de los jugadores de esa posicion. Su capacidad de G + A por 90 min es 0,14. Es baja y está lejos de la media de la categoría(0,37). Sin embargo es un buen generador de asistencias con 3 asistencias lo que lo situa por encima del 91% de jugadores de su posición y ha aportado un gol.",
        "situación contractual": "Su situación contractual  es atractiva ya que su contrato termina este año y su valor es inferior a 200K€",
        "recomendacion": "Recomendable"
    },
    "Toni Villa":{
        "perfil": "Jugador que puede jugar en la posición de extremo que destaca por su capacidad de generar juego, siendo su mejor faceta la cantidad de pases al último tercio(46) y los pases clave que es capaz de dar(11), aunque su capacidad de generar peligro es alta para la categoría, estos datos hay que cogerlos con cuidado ya que sus minutos de juego han sido tan solo 286. Lo que le hace tener una alta G + A por 90 Min de 0.63, pero esto es debido a su baja participación en el equipo. El fichaje puede ser interesante ya que es un jugador con experiencia en categorías superiores como puede ser primera división. Aunque esta temporada ha sumado pocos minutos.",
        "situación contractual": "Su situación contractual  es atractiva ya que su contrato termina este año y su valor es inferior a 300K€",
        "recomendacion": "Interesante"
    },
    "Stoichkov":{
      "perfil": "Jugador que puede jugar tanto en la posición de extremo como en la posición de delantero, destaca por su capacidad de finalización y de generación de asistencias; sus 5 goles y sus 3 asistencias lo hacen situarse por encima de la media de los extremos de la categoría ya que tiene un G + A por 90 Min de 0,44 en 1633 minutos jugados. Es un gran generador de ocasiones cada 90 minutos con 8 grandes ocasiones creadas y lo sitúa por encima del 79% de los jugadores de su posición. Aunque no es un extremo al uso, ya que sus 11 regates exitosos en la temporada (0,6 por 90) lo sitúan solo por encima del 14% de los extremos, y sus 95 pases al último tercio en la temporada (5,2 por 90) solo superan al 12% de los extremos. Puede ser más interesante en un perfil de delantero que de extremo.",
      "situación contractual": "Su situación contractual es atractiva ya que su contrato termina este año y su valor es inferior a 500K€",
      "recomendacion": "Interesante"
  },

    "Ali Houary":{
      "perfil": "Extremo joven de 20 años con solo 642 minutos en la temporada, lo que hace que cualquier dato deba interpretarse con cautela. Su mayor activo es el porcentaje de regates exitosos (52,6%), que lo sitúa en el percentil alto de los extremos de la categoría y sugiere una buena capacidad técnica en el uno contra uno. Ha aportado 1 asistencia y 0 goles, con un G + A por 90 Min de 0,14, lejos de la media de la categoría (0,37), aunque la baja participación hace que este dato no sea representativo. Sus 10 regates exitosos y 61 pases al último tercio en la temporada muestran un perfil de desborde más que de creación. Es una apuesta de futuro, no una solución inmediata.",
      "situación contractual": "Su situación contractual es atractiva ya que su contrato termina este año y su valor es ligeramente superior a 300K€",
      "recomendacion": "A vigilar"
  }
}



COLORES_NIVEL = {
    "verde": {
        "bg":         "rgba(0, 204, 150, 0.2)",
        "border":     "rgb(0, 204, 150)",
        "puntuacion": "rgb(0, 204, 150)",
        "mpl":        (0/255, 204/255, 150/255),
        "mpl_oscuro": (0/255, 163/255, 120/255),
        "mpl_claro":  (102/255, 255/255, 204/255),
        "css_oscuro": "#00A378",
        "css_claro":  "#66FFCC",
    },
    "ambar": {
        "bg":         "rgba(255, 165, 0, 0.2)",
        "border":     "rgb(255, 165, 0)",
        "puntuacion": "rgb(255, 165, 0)",
        "mpl":        (255/255, 165/255, 0/255),
        "mpl_oscuro": (204/255, 132/255, 0/255),
        "mpl_claro":  (255/255, 210/255, 120/255),
        "css_oscuro": "#CC8400",
        "css_claro":  "#FFD278",
    },
    "rojo": {
        "bg":         "rgba(254, 1, 1, 0.2)",
        "border":     "rgb(254, 1, 1)",
        "puntuacion": "rgb(254, 1, 1)",
        "mpl":        (254/255, 1/255, 1/255),
        "mpl_oscuro": (204/255, 0/255, 0/255),
        "mpl_claro":  (255/255, 110/255, 110/255),
        "css_oscuro": "#CC0000",
        "css_claro":  "#FF6E6E",
    },
}

def umbrales_puntuacion(puntuacion):
    if pd.isna(puntuacion):
        nivel = "rojo"
    elif puntuacion >= 5.6:
        nivel = "verde"
    elif puntuacion >= 4:
        nivel = "ambar"
    return nivel



@st.dialog("Cómo se calcula la puntuación")
def modal_puntuacion():
    st.markdown("**Modelo:** Regresión Logística")
    st.markdown("**Criterios positivos:**")
    st.markdown("""
- Pases clave
- Grandes ocasiones creadas / minuto
- Pases al último tercio / minuto
- % regates exitosos
- Minutos jugados
    """)
    st.markdown("**Criterio negativo:**")
    st.markdown("- Grandes ocasiones falladas / minuto")


@st.dialog("Informe del Jugador seleccionado")
def modal_informe(jugador_seleccionado):
    jugador = JUGADORES_INFORME[jugador_seleccionado]
    st.markdown(f"**Jugador:** {jugador_seleccionado}")
    st.markdown(f"**Recomendación:** {jugador['recomendacion']}")
    st.markdown(f"**Situación Contractual:** {jugador['situación contractual']}")
    st.markdown(f"**Informe:** {jugador['perfil']}")


def calcular_percentiles(jugador, df_ref):
    values = []
    for col in variables_radar:
        if col == "porcentaje_regates_exitosos":
            p = math.floor(
                stats.percentileofscore(
                    df_ref[col],
                    jugador[col]
                )
            )
        else:
            p = math.floor(
                stats.percentileofscore(
                    df_ref[col] / (df_ref['minutos_jugados'] / 90),
                    jugador[col] / (jugador['minutos_jugados'] / 90)
                )
            )

        values.append(p)
    return values

def render_radar(values, color): 
    for n, i in enumerate(values):
        if i == 100:
            values[n] = 99

    baker = PyPizza(
        params= variables_radar,
        straight_line_color= (0.7, 0.7, 0.7, 0.5),
        straight_line_lw = 0.5,
        last_circle_color= (0.7, 0.7, 0.7, 0.5),
        last_circle_lw = 0.5,
        other_circle_color= (0.7, 0.7, 0.7, 0.5),
        other_circle_lw = 0.5,
        other_circle_ls = "-."
        )

    colores_slices = [color['mpl_oscuro']] * 4 + [color['mpl_claro']] * 4

    fig, ax = baker.make_pizza(
        values,
        figsize=(3, 3),
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

    st.pyplot(fig, transparent=True)


tabs = st.tabs(["Resumen General", "Análisis Individual", "Comparativa"])

# === TAB 1: RESUMEN GENERAL ===
with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Extremos recomendados", value=len(df))
    with col2:
        st.metric(label="G + A por 90 (media categoría)", value=f"{(df_ref['goles'].sum() + df_ref['asistencias'].sum()) / df_ref['minutos_jugados'].sum() * 90:.2f}")
    with col3:
        st.metric(label="% Regates exitosos (media categoría)", value=f"{df_ref['porcentaje_regates_exitosos'].mean():.1f}%")
    with col4:
        st.metric(label="Grandes ocasiones creadas / 90 (media categoría)", value=f"{(df_ref['grandes_ocasiones_creadas'] / (df_ref['minutos_jugados'] / 90)).mean():.2f}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Grandes oportunidades Creadas vs Falladas")
        fig = px.bar(
            df,
            x="nombre",
            y=["grandes_ocasiones_creadas", "grandes_ocasiones_falladas"],
            barmode="group",
            title="Grandes oportunidades creadas y falladas",
            color_discrete_sequence=["#00CC96", "#FE0101"]
        )
        fig.update_layout(xaxis_tickangle=-45, xaxis_title="", legend_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Distribución del pie dominante")
        df_pie = df["pie_dominante"].value_counts().reset_index()
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

    df_tabla = pd.DataFrame({
        "Nombre": df["nombre"],
        "Equipo": df["equipo"],
        "Goles + Asistencias": df["goles"] + df["asistencias"],
        "Minutos Jugados": df["minutos_jugados"],
        "Regates Exitosos %": df["porcentaje_regates_exitosos"].round(1),
        "Tiros a Puerta %": (
            df["tiros_a_puerta"] / df["tiros_totales"].replace(0, np.nan) * 100
        ).round(1),
        "Pases Clave": df["pases_clave"],
        "Pases al Último Tercio": df["pases_ultimo_tercio"],
    })

    st.dataframe(
        df_tabla,
        column_config={
            "Regates Exitosos %": st.column_config.ProgressColumn(
                "Regates Exitosos %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Tiros a Puerta %": st.column_config.ProgressColumn(
                "Tiros a Puerta %",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True
    )


    # === TAB 2: ANÁLISIS INDIVIDUAL ===
with tabs[1]:
    jugador_seleccionado = st.selectbox(
        "Seleccionar Jugador",
        options=df["nombre"].tolist(),
        index=0,
        key="jugador_selector"
    )

    jugador = df[df["nombre"] == jugador_seleccionado].iloc[0]
    color = COLORES_NIVEL[umbrales_puntuacion(jugador['Puntuacion'])]

    col_nombre, col_informe, col_circulo = st.columns([2, 5, 1])

    with col_nombre:
        st.markdown(f"<h2 style='margin:0; padding-top:10px;'>{jugador_seleccionado}</h2>",
                    unsafe_allow_html=True)

    with col_informe:
        st.markdown('<div class="informe-btn">', unsafe_allow_html=True)
        if st.button("Ver Informe", key="btn_informe"):
            modal_informe(jugador_seleccionado)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_circulo:
        if st.button("ℹ️", key="btn_info"):
            modal_puntuacion()

        st.markdown(f"""
        <div style="
            width:110px; height:110px; border-radius:50%;
            background-color:{color['bg']};
            border:2px solid {color['border']};
            display:flex; flex-direction:column;
            align-items:center; justify-content:center;
            text-align:center;
        ">
            <span style="font-size:26px; font-weight:bold; color:{color['puntuacion']};">{jugador['Puntuacion']:.2f}</span>
            <span style="font-size:11px; color:{color['puntuacion']};">Puntuación</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    posiciones = ', '.join(ast.literal_eval(jugador['posicion_detallada']))

    col_radar, col_ficha = st.columns([3, 2])


    with col_radar:
        values = calcular_percentiles(jugador, df_ref)
        render_radar(values, color)
       

    with col_ficha:
        f1, f2 = st.columns(2)
        with f1:
            st.metric(label="Equipo",            value= jugador['equipo'])
            st.metric(label="Altura",            value= f"{jugador['altura']} cm")
            st.metric(label="Posiciones",        value= posiciones)
            st.metric(label="Valor de Mercado",  value= jugador['valor_mercado'])
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
        </div>
        """, unsafe_allow_html=True)
        
        col_ofensiva, col_creacion = st.columns([1, 1])

        with col_ofensiva:
                st.markdown(f"""
                    <div style="font-size:15px; line-height:2.3;">
                        <span style="background:{color['css_oscuro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Tiros a puerta/90 — <b>{values[0]}</b><br>
                        <span style="background:{color['css_oscuro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Grandes ocasiones/90 — <b>{values[1]}</b><br>
                        <span style="background:{color['css_oscuro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Asistencias/90 — <b>{values[2]}</b><br>
                        <span style="background:{color['css_oscuro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Goles/90 — <b>{values[3]}</b><br>
                    </div>
                """, 
                    unsafe_allow_html=True)
                
        with col_creacion:
                st.markdown(f"""
                    <div style="font-size:15px; line-height:2.3;">
                        <span style="background:{color['css_claro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Pases último tercio/90 — <b>{values[4]}</b><br>
                        <span style="background:{color['css_claro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Pases clave/90 — <b>{values[5]}</b><br>
                        <span style="background:{color['css_claro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> % Regates exitosos — <b>{values[6]}</b><br>
                        <span style="background:{color['css_claro']}; border-radius:3px; padding:2px 10px; margin-right:8px;">&nbsp;</span> Regates exitosos/90 — <b>{values[7]}</b>
                    </div>
                """, 
                    unsafe_allow_html=True)
    st.divider()

    st.subheader("Estadísticas Ofensivas")
    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Goles",                          int(jugador["goles"]))
    o2.metric("Asistencias",                    int(jugador["asistencias"]))
    o3.metric("Tiros",                          int(jugador["tiros_totales"]))
    o4.metric("G + A por 90 Min",               f"{(int(jugador['goles']) + int(jugador['asistencias'])) / int(jugador['minutos_jugados']) * 90:.2f}")
    o4, o5, o6 = st.columns(3)
    o4.metric("Tiros a Puerta",                 int(jugador["tiros_a_puerta"]))
    o5.metric("Grandes Oport. Creadas",         int(jugador["grandes_ocasiones_creadas"]))
    o6.metric("Grandes Oport. Falladas",        int(jugador["grandes_ocasiones_falladas"]))

    st.divider()

    st.subheader("Creación y Conducción")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pases Clave",                    int(jugador["pases_clave"]))
    c2.metric("Pases Último Tercio",            int(jugador["pases_ultimo_tercio"]))
    c3.metric("Pases Totales",                  int(jugador["pases_totales"]))
    c4.metric("Pases Acertados",                int(jugador["pases_acertados"]))
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("% Pases Acertados",              f"{jugador['porcentaje_pases_acertados']:.1f}%")
    c6.metric("Regates Exitosos",               int(jugador["regates_exitosos"]))
    c7.metric("% Regates Exitosos",             f"{jugador['porcentaje_regates_exitosos']:.1f}%")
    c8.metric("Pérdidas de Balón",              int(jugador["perdidas_de_balon"]))

    st.divider()

    st.subheader("Trabajo Defensivo")
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Intercepciones",                 int(jugador["intercepciones"]))
    d2.metric("Entradas",                       int(jugador["entradas"]))
    d3.metric("Duelos Aéreos Perdidos",         int(jugador["duelos_aereos_perdidos"]))
    d4.metric("Tarjetas Amarillas",             int(jugador["tarjetas_amarillas"]))
    d5.metric("Tarjetas Rojas",                 int(jugador["tarjetas_rojas"]))


# === TAB 3: COMPARATIVA ===
with tabs[2]:
    st.subheader("Selección de Jugadores para Comparar")
    
    # Multiselect para elegir jugadores a comparar
    jugadores_seleccionados = st.multiselect(
        "Seleccionar jugadores (máx. 2)",
        options=df["nombre"].tolist(),
        default=df["nombre"].iloc[0],
        max_selections=2        
    )
    
    
    # Verificar que hay al menos un jugador seleccionado
    if not jugadores_seleccionados:
        st.warning("Por favor selecciona al menos un jugador para analizar")
    else:
        # Filtrar datos de los jugadores seleccionados
        datos_jugadores =  df[df["nombre"].isin(jugadores_seleccionados)]
        
        # Comparativa radar
        st.subheader("Comparativa de Perfiles")

        st.divider()

        col_radar_comparativo, col_tabla = st.columns([2, 2])

        jugador1 = datos_jugadores.iloc[0]
        jugador2 = datos_jugadores.iloc[1] if len(datos_jugadores) > 1 else None
        color1 = COLORES_NIVEL[umbrales_puntuacion(jugador1['Puntuacion'])]
        color2 = COLORES_NIVEL[umbrales_puntuacion(jugador2['Puntuacion'])] if jugador2 is not None else None
        with col_radar_comparativo:

            fig = go.Figure()

            st.subheader("Radar Jugadores:")
            for i, (_, jugador) in enumerate(datos_jugadores.iterrows()):
                values = calcular_percentiles(jugador, df_ref)
                color = COLORES_NIVEL[umbrales_puntuacion(jugador['Puntuacion'])]

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=variables_radar,
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
                        [f"<b>{jugador1[v]}</b>" for v in variables_radar],
                        [TABLA_COMPARADOR_JUGADORES[var] for var in variables_radar],
                        [f"<b>{jugador2[v]}</b>" for v in variables_radar],
                    ],
                    font=dict(size=16, color=[color1['border'], 'black', color2['border']]),
                    fill_color='white',
                    line=dict(width=0),
                    height=35
                )))
                tabla.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=390)

                st.plotly_chart(tabla, use_container_width=True)
                st.markdown(f"""
                <div style="margin-top:0; padding:0;">
                    <p style="margin:0; font-weight:600; font-size:16px;">Puntuación:</p>
                    <div style="display:flex; justify-content:space-around; margin-top:4px;">
                        <span style="font-size:38px;  color:{color1['puntuacion']};">{jugador1['Puntuacion']:.2f}</span>
                        <span style="font-size:38px; color:{color2['puntuacion']};">{jugador2['Puntuacion']:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                col_m1, col_m2 = st.columns(2)
                for i, var in enumerate(variables_radar):
                    col = col_m1 if i < 4 else col_m2
                    with col:
                        st.metric(TABLA_COMPARADOR_JUGADORES[var], int(jugador1[var]))
                