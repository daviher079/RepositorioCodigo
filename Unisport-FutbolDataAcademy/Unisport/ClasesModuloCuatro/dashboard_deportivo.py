import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Análisis Deportivo con IA",
    page_icon="🏃",
    layout="wide"
)

# Función para generar datos simulados de jugadores
def generar_datos_jugadores(num_jugadores=10, semanas=12):
    jugadores = []
    
    posiciones = ["Delantero", "Centrocampista", "Defensa", "Portero"]
    roles = ["Velocista", "Creador", "Finalizador", "Defensor"]
    
    for i in range(1, num_jugadores + 1):
        # Valores base para cada jugador
        edad = random.randint(15, 19)
        posicion = random.choice(posiciones)
        rol_principal = random.choice(roles)
        # Asegurar rol secundario diferente
        rol_secundario = random.choice([r for r in roles if r != rol_principal])
        potencial_score = random.randint(60, 95)
        
        # Valores base para métricas
        base_fisico = random.uniform(70, 95)
        base_tecnico = random.uniform(65, 90)
        base_tactico = random.uniform(65, 90)
        base_mental = random.uniform(75, 90)
        
        # Tendencia de mejora
        mejora_semanal = random.uniform(0.4, 0.9)
        
        # Datos semanales
        datos_semanales = []
        for semana in range(1, semanas + 1):
            # Factor de mejora progresiva
            factor_semana = 1 + (semana * mejora_semanal / 100)
            variacion = lambda: random.uniform(-5, 5)
            
            # Calcular métricas de la semana
            fisico = min(100, base_fisico * factor_semana + variacion())
            tecnico = min(100, base_tecnico * factor_semana + variacion())
            tactico = min(100, base_tactico * factor_semana + variacion())
            mental = min(100, base_mental * factor_semana + variacion())
            asimetria = max(0, random.uniform(20, 40) - semana * 0.5)
            riesgo_lesion = max(5, random.uniform(10, 40) - semana * 0.8)
            
            # Puntuación general
            overall = (
                fisico * 0.25 +
                tecnico * 0.25 +
                tactico * 0.25 +
                mental * 0.25
            )
            
            datos_semanales.append({
                "semana": semana,
                "overall": overall,
                "fisico": fisico,
                "tecnico": tecnico,
                "tactico": tactico,
                "mental": mental,
                "asimetria": asimetria,
                "riesgo_lesion": riesgo_lesion
            })
        
        # Datos de la última semana para métricas actuales
        ultima_semana = datos_semanales[-1]
        
        # Calcular potencial basado en mejora y nivel actual
        potencial_calculado = min(100, ultima_semana["overall"] + mejora_semanal * 10)
        
        # Calcular puntuación de rol
        rol_score = 0
        if rol_principal == "Velocista":
            rol_score = ultima_semana["fisico"] * 0.6 + ultima_semana["tecnico"] * 0.4
        elif rol_principal == "Creador":
            rol_score = ultima_semana["tactico"] * 0.5 + ultima_semana["tecnico"] * 0.5
        elif rol_principal == "Finalizador":
            rol_score = ultima_semana["tecnico"] * 0.6 + ultima_semana["fisico"] * 0.4
        elif rol_principal == "Defensor":
            rol_score = ultima_semana["tactico"] * 0.5 + ultima_semana["fisico"] * 0.5
        
        # Añadir jugador a la lista
        jugadores.append({
            "id": i,
            "nombre": f"Jugador {i}",
            "edad": edad,
            "posicion": posicion,
            "puntuacion_actual": ultima_semana["overall"],
            "potencial": potencial_calculado,
            "tendencia_mejora": mejora_semanal,
            "rol_principal": rol_principal,
            "rol_secundario": rol_secundario,
            "puntuacion_rol": rol_score,
            "riesgo_lesion": ultima_semana["riesgo_lesion"],
            "metricas_actuales": {
                "fisico": ultima_semana["fisico"],
                "tecnico": ultima_semana["tecnico"],
                "tactico": ultima_semana["tactico"],
                "mental": ultima_semana["mental"],
                "asimetria": ultima_semana["asimetria"]
            },
            "datos_semanales": datos_semanales
        })
    
    return jugadores

# Generar datos simulados
jugadores = generar_datos_jugadores()

# Función para crear dataframe de datos semanales
def crear_df_semanal(jugador):
    return pd.DataFrame(jugador["datos_semanales"])

# Función para obtener color según nivel de riesgo
def color_riesgo(valor):
    if valor <= 15:
        return "green"
    elif valor <= 30:
        return "orange"
    else:
        return "red"

# Título y descripción
st.title("Dashboard de Análisis Deportivo con IA")
st.markdown("Sistema de análisis avanzado para el desarrollo de atletas utilizando inteligencia artificial")

# Menú de navegación
tabs = st.tabs(["Resumen General", "Análisis Individual", "Comparativa"])

# === TAB 1: RESUMEN GENERAL ===
with tabs[0]:
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Atletas", 
            value=len(jugadores)
        )
    
    with col2:
        promedio_potencial = sum(j["potencial"] for j in jugadores) / len(jugadores)
        st.metric(
            label="Potencial Promedio", 
            value=f"{promedio_potencial:.1f}"
        )
    
    with col3:
        promedio_mejora = sum(j["tendencia_mejora"] for j in jugadores) / len(jugadores)
        st.metric(
            label="Tasa de Mejora Promedio", 
            value=f"{promedio_mejora:.1f}%"
        )
    
    with col4:
        atletas_alto_riesgo = sum(1 for j in jugadores if j["riesgo_lesion"] > 30)
        st.metric(
            label="Atletas en Alto Riesgo", 
            value=atletas_alto_riesgo
        )
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Potencial vs Rendimiento Actual")
        
        # Crear dataframe para el gráfico
        df_potencial = pd.DataFrame({
            'Jugador': [j["nombre"] for j in jugadores],
            'Rendimiento Actual': [j["puntuacion_actual"] for j in jugadores],
            'Potencial': [j["potencial"] for j in jugadores]
        })
        
        fig = px.bar(
            df_potencial, 
            x='Jugador', 
            y=['Rendimiento Actual', 'Potencial'],
            barmode='group',
            title="Comparación de Potencial y Rendimiento Actual",
            color_discrete_sequence=['#636EFA', '#00CC96']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribución de Roles")
        
        # Conteo de roles
        conteo_roles = {}
        for j in jugadores:
            conteo_roles[j["rol_principal"]] = conteo_roles.get(j["rol_principal"], 0) + 1
        
        df_roles = pd.DataFrame({
            'Rol': list(conteo_roles.keys()),
            'Jugadores': list(conteo_roles.values())
        })
        
        fig = px.pie(
            df_roles, 
            values='Jugadores', 
            names='Rol',
            title="Distribución por Rol Principal",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabla de jugadores
    st.subheader("Listado de Atletas")
    
    # Convertir datos a dataframe
    df_jugadores = pd.DataFrame([
        {
            "ID": j["id"],
            "Nombre": j["nombre"],
            "Edad": j["edad"],
            "Posición": j["posicion"],
            "Rendimiento": round(j["puntuacion_actual"], 1),
            "Potencial": round(j["potencial"], 1),
            "Mejora Semanal": f"{j['tendencia_mejora']:.1f}%",
            "Rol Principal": j["rol_principal"],
            "Riesgo Lesión": f"{j['riesgo_lesion']:.1f}%"
        } for j in jugadores
    ])
    
    # Mostrar tabla con estilos
    st.dataframe(
        df_jugadores,
        column_config={
            "Rendimiento": st.column_config.ProgressColumn(
                "Rendimiento",
                format="%f",
                min_value=0,
                max_value=100,
            ),
            "Potencial": st.column_config.ProgressColumn(
                "Potencial",
                format="%f",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True
    )

# === TAB 2: ANÁLISIS INDIVIDUAL ===
with tabs[1]:
    # Selector de jugador
    jugador_seleccionado = st.selectbox(
        "Seleccionar Jugador",
        options=[j["nombre"] for j in jugadores],
        index=0
    )
    
    # Encontrar datos del jugador seleccionado
    jugador = next(j for j in jugadores if j["nombre"] == jugador_seleccionado)
    
    # Información básica del jugador
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.header(jugador["nombre"])
        st.write(f"**Edad:** {jugador['edad']} años | **Posición:** {jugador['posicion']} | **Rol Óptimo:** {jugador['rol_principal']}")
    
    with col2:
        st.metric(
            label="Rendimiento Actual", 
            value=f"{jugador['puntuacion_actual']:.1f}"
        )
    
    with col3:
        st.metric(
            label="Potencial IA", 
            value=f"{jugador['potencial']:.1f}"
        )
    
    # Subtabs para detalles
    subtabs = st.tabs(["Resumen", "Progresión", "Plan de Entrenamiento"])
    
    # Subtab de Resumen
    with subtabs[0]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Perfil de Rendimiento")
            
            # Datos para gráfico radar
            categorias = ['Físico', 'Técnico', 'Táctico', 'Mental', 'Riesgo Lesión (inv)']
            valores = [
                jugador["metricas_actuales"]["fisico"],
                jugador["metricas_actuales"]["tecnico"],
                jugador["metricas_actuales"]["tactico"],
                jugador["metricas_actuales"]["mental"],
                100 - jugador["riesgo_lesion"]  # Invertido para que valores altos sean mejores
            ]
            
            # Crear gráfico radar
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias,
                fill='toself',
                name=jugador["nombre"]
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Análisis de Fortalezas y Áreas de Mejora")
            
            # Determinar fortalezas (valores más altos)
            metricas = [
                ("Condición física", jugador["metricas_actuales"]["fisico"]),
                ("Habilidades técnicas", jugador["metricas_actuales"]["tecnico"]),
                ("Comprensión táctica", jugador["metricas_actuales"]["tactico"]),
                ("Fortaleza mental", jugador["metricas_actuales"]["mental"]),
                ("Resiliencia lesiones", 100 - jugador["riesgo_lesion"])
            ]
            
            metricas_ordenadas = sorted(metricas, key=lambda x: x[1], reverse=True)
            
            # Fortalezas (top 2)
            st.markdown("**Fortalezas:**")
            for i in range(2):
                nombre, valor = metricas_ordenadas[i]
                st.markdown(f"- {nombre} ({valor:.1f}/100)")
            
            # Áreas de mejora (bottom 2)
            st.markdown("**Áreas de Mejora:**")
            for i in range(-1, -3, -1):
                nombre, valor = metricas_ordenadas[i]
                st.markdown(f"- {nombre} ({valor:.1f}/100)")
            
            # Métricas clave
            st.subheader("Métricas Clave")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Tasa de Mejora", 
                    value=f"{jugador['tendencia_mejora']:.1f}%",
                    delta="semanal"
                )
                st.metric(
                    label="Puntuación de Rol", 
                    value=f"{jugador['puntuacion_rol']:.1f}",
                    delta=f"como {jugador['rol_principal']}"
                )
            
            with col2:
                st.metric(
                    label="Riesgo de Lesión", 
                    value=f"{jugador['riesgo_lesion']:.1f}%",
                    delta="basado en biomecánica",
                    delta_color="inverse"
                )
                st.metric(
                    label="Índice de Asimetría", 
                    value=f"{jugador['metricas_actuales']['asimetria']:.1f}%",
                    delta="desbalance corporal",
                    delta_color="inverse"
                )
    
    # Subtab de Progresión
    with subtabs[1]:
        st.subheader("Evolución de Rendimiento")
        
        # Crear dataframe con datos semanales
        df_semanal = crear_df_semanal(jugador)
        
        # Gráfico de evolución
        fig = px.line(
            df_semanal, 
            x="semana", 
            y=["overall", "fisico", "tecnico", "tactico", "mental"],
            labels={"value": "Puntuación", "variable": "Métrica", "semana": "Semana"},
            title="Evolución de Métricas por Semana",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        fig.update_layout(yaxis_range=[50, 100])
        st.plotly_chart(fig, use_container_width=True)
        
        # Análisis de tendencia
        st.subheader("Análisis de Tendencia")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Proyección de Rendimiento**
            
            Basado en la tasa de mejora actual de **{jugador['tendencia_mejora']:.1f}%** semanal, 
            el rendimiento proyectado en 4 semanas sería de aproximadamente 
            **{min(100, jugador['puntuacion_actual'] + (jugador['tendencia_mejora'] * 4)):.1f}**.
            
            El análisis de IA indica un potencial máximo de **{jugador['potencial']:.1f}**, 
            que podría alcanzarse en aproximadamente 
            **{max(1, int((jugador['potencial'] - jugador['puntuacion_actual']) / jugador['tendencia_mejora'])):.0f}** 
            semanas con el entrenamiento adecuado.
            """)
        
        with col2:
            st.info(f"""
            **Comparación con Cohorte**
            
            El jugador muestra una tasa de mejora 
            **{'superior' if jugador['tendencia_mejora'] > 0.6 else 'similar' if jugador['tendencia_mejora'] > 0.4 else 'inferior'}** 
            al promedio de su grupo de edad.
            
            Su desarrollo 
            **{'sobresale significativamente' if jugador['tendencia_mejora'] > 0.7 else 'progresa favorablemente' if jugador['tendencia_mejora'] > 0.5 else 'requiere atención adicional'}** 
            comparado con jugadores similares.
            """)
    
    # Subtab de Plan de Entrenamiento
    with subtabs[2]:
        st.subheader("Plan de Entrenamiento Personalizado IA")
        
        # Generar sesiones de entrenamiento basadas en datos del jugador
        entrenamientos = []
        
        # Determinar áreas débiles
        metricas = [
            ("física", jugador["metricas_actuales"]["fisico"]),
            ("técnica", jugador["metricas_actuales"]["tecnico"]),
            ("táctica", jugador["metricas_actuales"]["tactico"]),
            ("mental", jugador["metricas_actuales"]["mental"])
        ]
        
        metricas_ordenadas = sorted(metricas, key=lambda x: x[1])
        areas_debiles = [m[0] for m in metricas_ordenadas[:2]]
        
        # Sesiones para áreas débiles
        for area in areas_debiles:
            if area == "física":
                entrenamientos.append({
                    "titulo": "Desarrollo de capacidades físicas",
                    "descripcion": "Enfoque en velocidad, resistencia y fuerza",
                    "tipo": "física",
                    "intensidad": "Media-Alta",
                    "duracion": 60,
                    "ejercicios": [
                        "Sprints de alta intensidad con monitoreo GPS",
                        "Entrenamiento de fuerza funcional",
                        "Trabajo de pliometría monitoreado con sensores"
                    ]
                })
            elif area == "técnica":
                entrenamientos.append({
                    "titulo": "Perfeccionamiento técnico",
                    "descripcion": "Mejora de fundamentos técnicos específicos",
                    "tipo": "técnica",
                    "intensidad": "Media",
                    "duracion": 60,
                    "ejercicios": [
                        "Ejercicios de precisión con análisis de video",
                        "Patrones de movimiento con feedback inmediato",
                        "Simulaciones técnicas con resistencia variable"
                    ]
                })
            elif area == "táctica":
                entrenamientos.append({
                    "titulo": "Comprensión táctica",
                    "descripcion": "Desarrollo de lectura de juego y posicionamiento",
                    "tipo": "táctica",
                    "intensidad": "Media",
                    "duracion": 60,
                    "ejercicios": [
                        "Simulaciones tácticas en realidad virtual",
                        "Análisis de posicionamiento con heatmaps",
                        "Ejercicios de toma de decisiones bajo presión"
                    ]
                })
            elif area == "mental":
                entrenamientos.append({
                    "titulo": "Preparación mental",
                    "descripcion": "Fortalecimiento psicológico y concentración",
                    "tipo": "mental",
                    "intensidad": "Media",
                    "duracion": 45,
                    "ejercicios": [
                        "Entrenamiento de atención con neurofeedback",
                        "Manejo de presión con simulaciones inmersivas",
                        "Estrategias de autorregulación emocional"
                    ]
                })
        
        # Sesión preventiva si hay riesgo de lesión
        if jugador["riesgo_lesion"] > 15:
            entrenamientos.append({
                "titulo": "Prevención de lesiones",
                "descripcion": f"Reducción de riesgo de lesión (actual: {jugador['riesgo_lesion']:.1f}%)",
                "tipo": "preventiva",
                "intensidad": "Baja",
                "duracion": 45,
                "ejercicios": [
                    "Corrección de patrones biomecánicos",
                    "Equilibrio y propiocepción avanzada",
                    "Activación neuromuscular específica"
                ]
            })
        
        # Sesión específica para rol
        rol_sesion = None
        if jugador["rol_principal"] == "Velocista":
            rol_sesion = {
                "titulo": "Potenciación de rol: Velocista",
                "descripcion": "Desarrollo de capacidades específicas para el rol principal",
                "tipo": "física",
                "intensidad": "Alta",
                "duracion": 50,
                "ejercicios": [
                    "Entrenamiento de aceleración con sensores",
                    "Desarrollo de velocidad máxima",
                    "Explosividad en cambios de dirección"
                ]
            }
        elif jugador["rol_principal"] == "Creador":
            rol_sesion = {
                "titulo": "Potenciación de rol: Creador",
                "descripcion": "Desarrollo de capacidades específicas para el rol principal",
                "tipo": "táctica",
                "intensidad": "Media",
                "duracion": 50,
                "ejercicios": [
                    "Ejercicios de visión periférica y toma de decisiones",
                    "Pases de precisión bajo presión con análisis",
                    "Simulación de situaciones de juego con RA"
                ]
            }
        elif jugador["rol_principal"] == "Finalizador":
            rol_sesion = {
                "titulo": "Potenciación de rol: Finalizador",
                "descripcion": "Desarrollo de capacidades específicas para el rol principal",
                "tipo": "técnica",
                "intensidad": "Media-Alta",
                "duracion": 50,
                "ejercicios": [
                    "Precisión de finalización con análisis de video",
                    "Situaciones de definición bajo presión",
                    "Movimientos off-ball para optimizar posiciones"
                ]
            }
        elif jugador["rol_principal"] == "Defensor":
            rol_sesion = {
                "titulo": "Potenciación de rol: Defensor",
                "descripcion": "Desarrollo de capacidades específicas para el rol principal",
                "tipo": "táctica",
                "intensidad": "Media-Alta",
                "duracion": 50,
                "ejercicios": [
                    "Posicionamiento defensivo con análisis IA",
                    "Anticipación y lectura de jugadas ofensivas",
                    "Trabajo de coordinación defensiva grupal"
                ]
            }
        
        if rol_sesion:
            entrenamientos.append(rol_sesion)
        
        # Mostrar plan de entrenamiento
        for i, sesion in enumerate(entrenamientos, 1):
            tipo_color = {
                "física": "blue",
                "técnica": "green",
                "táctica": "purple",
                "mental": "orange",
                "preventiva": "red"
            }.get(sesion["tipo"], "gray")
            
            st.markdown(f"""
            <div style="
                border-left: 5px solid {tipo_color}; 
                padding: 15px; 
                margin-bottom: 15px; 
                background-color: rgba(240, 240, 240, 0.5);
                border-radius: 5px;
            ">
                <h3 style="margin: 0;">{sesion['titulo']}</h3>
                <p style="color: #666; margin: 5px 0;">{sesion['descripcion']}</p>
                <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                    <span style="background-color: #eff; padding: 3px 8px; border-radius: 10px; font-size: 12px;">
                        {sesion['intensidad']}
                    </span>
                    <span style="background-color: #eff; padding: 3px 8px; border-radius: 10px; font-size: 12px;">
                        {sesion['duracion']} min
                    </span>
                </div>
                <h4 style="margin: 10px 0 5px 0; font-size: 14px;">Ejercicios:</h4>
                <ul style="margin: 0; padding-left: 20px;">
                    {''.join([f'<li>{ej}</li>' for ej in sesion['ejercicios']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

# === TAB 3: COMPARATIVA ===
with tabs[2]:
    st.subheader("Selección de Jugadores para Comparar")
    
    # Multiselect para elegir jugadores a comparar
    jugadores_seleccionados = st.multiselect(
        "Seleccionar jugadores (máx. 3)",
        options=[j["nombre"] for j in jugadores],
        default=[jugadores[0]["nombre"]]
    )
    
    # Limitar a máximo 3 jugadores
    if len(jugadores_seleccionados) > 3:
        st.warning("Por favor selecciona máximo 3 jugadores para comparar")
        jugadores_seleccionados = jugadores_seleccionados[:3]
    
    # Verificar que hay al menos un jugador seleccionado
    if not jugadores_seleccionados:
        st.warning("Por favor selecciona al menos un jugador para analizar")
    else:
        # Filtrar datos de los jugadores seleccionados
        datos_jugadores = [j for j in jugadores if j["nombre"] in jugadores_seleccionados]
        
        # Comparativa radar
        st.subheader("Comparativa de Perfiles")
        
        # Preparar datos para gráfico radar
        fig = go.Figure()
        
        categorias = ['Físico', 'Técnico', 'Táctico', 'Mental', 'Riesgo Lesión (inv)']
        
        for i, jugador in enumerate(datos_jugadores):
            valores = [
                jugador["metricas_actuales"]["fisico"],
                jugador["metricas_actuales"]["tecnico"],
                jugador["metricas_actuales"]["tactico"],
                jugador["metricas_actuales"]["mental"],
                100 - jugador["riesgo_lesion"]
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias,
                fill='toself',
                name=jugador["nombre"]
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
        
        # Evolución de rendimiento
        if len(datos_jugadores) > 0:
            st.subheader("Evolución de Rendimiento")
            
            # Preparar datos para gráfico de línea
            df_evolucion = pd.DataFrame()
            
            for semana in range(1, 13):
                fila = {"Semana": semana}
                
                for jugador in datos_jugadores:
                    datos_semana = next((s for s in jugador["datos_semanales"] if s["semana"] == semana), None)
                    if datos_semana:
                        fila[jugador["nombre"]] = datos_semana["overall"]
                
                df_evolucion = pd.concat([df_evolucion, pd.DataFrame([fila])], ignore_index=True)
            
            # Gráfico de evolución
            fig = px.line(
                df_evolucion, 
                x="Semana", 
                y=[j["nombre"] for j in datos_jugadores],
                title="Evolución de Rendimiento General",
                labels={"value": "Puntuación General", "variable": "Jugador"},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            
            fig.update_layout(yaxis_range=[60, 100])
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla comparativa
            st.subheader("Tabla Comparativa")
            
            # Crear dataframe para tabla
            df_comparativa = pd.DataFrame([
                {
                    "Jugador": j["nombre"],
                    "Edad": j["edad"],
                    "Posición": j["posicion"],
                    "Rendimiento": round(j["puntuacion_actual"], 1),
                    "Potencial": round(j["potencial"], 1),
                    "Mejora": f"{j['tendencia_mejora']:.1f}%",
                    "Rol Principal": j["rol_principal"],
                    "Riesgo Lesión": f"{j['riesgo_lesion']:.1f}%"
                } for j in datos_jugadores
            ])
            
            st.dataframe(df_comparativa, hide_index=True)
            
            # Análisis comparativo
            st.subheader("Análisis Comparativo")
            
            # Generar texto de análisis comparativo
            if len(datos_jugadores) > 1:
                # Nombres de los jugadores
                nombres = ", ".join([j["nombre"] for j in datos_jugadores])
                
                # Comparar roles
                roles = [j["rol_principal"] for j in datos_jugadores]
                mismo_rol = len(set(roles)) == 1
                
                # Ordenar por potencial
                por_potencial = sorted(datos_jugadores, key=lambda j: j["potencial"], reverse=True)
                mejor_potencial = por_potencial[0]
                
                # Ordenar por mejora
                por_mejora = sorted(datos_jugadores, key=lambda j: j["tendencia_mejora"], reverse=True)
                mejor_mejora = por_mejora[0]
                peor_mejora = por_mejora[-1]
                
                # Generar análisis
                analisis = f"""
                Al comparar {nombres}, se observa que {'todos tienen el mismo rol principal' if mismo_rol else 'presentan roles principales diferentes'}: {', '.join(set(roles))}.
                
                {mejor_potencial['nombre']} muestra el mayor potencial según los análisis predictivos de IA ({mejor_potencial['potencial']:.1f}).
                
                En términos de progresión, {mejor_mejora['nombre']} muestra la mayor tasa de mejora ({mejor_mejora['tendencia_mejora']:.1f}%), 
                mientras que {peor_mejora['nombre']} presenta una evolución más gradual ({peor_mejora['tendencia_mejora']:.1f}%).
                """
                
                st.info(analisis)
                
                # Recomendaciones
                recomendaciones = [
                    f"Priorizar el desarrollo de {mejor_potencial['nombre']} con un plan avanzado de entrenamiento dada su alta proyección.",
                    f"Establecer un sistema de monitoreo comparativo continuo para evaluar la efectividad de los planes de entrenamiento individualizados."
                ]
                
                # Verificar riesgo de lesiones
                jugadores_riesgo = [j for j in datos_jugadores if j["riesgo_lesion"] > 25]
                if jugadores_riesgo:
                    nombres_riesgo = ", ".join([j["nombre"] for j in jugadores_riesgo])
                    recomendaciones.insert(1, f"Implementar programa preventivo especializado para {nombres_riesgo} para reducir su riesgo de lesión.")
                
                # Mostrar recomendaciones
                st.subheader("Recomendaciones")
                for rec in recomendaciones:
                    st.markdown(f"- {rec}")