# RepositorioCodigo — David Vicente Hernández

Scripts y pipelines de análisis de datos aplicados al fútbol. Desarrollados durante el Máster en Big Data e Inteligencia Artificial Aplicado al Deporte (Unisport Management School) y el curso Objetivo Analista de Datos 360.

## Tecnologías

Python · Streamlit · Docker · Power BI · pandas · matplotlib · mplsoccer · statsbombpy · scikit-learn · Playwright · NumPy · SciPy

---

## Proyectos

### Match Report — Pipeline Completo

19 scripts que generan un informe de partido completo a partir de datos de WhoScored: scraping, cálculo de xT, redes de pases, mapa de tiros, bloque defensivo, momentum, rendimiento de portero y estadísticas individuales.

| | |
|---|---|
| ![Red de pases](assets/match_report_pass_network.png) | ![Mapa xT](assets/match_report_xT_pass_map.png) |
| ![Mapa de tiros](assets/match_report_mapa_tiros.png) | ![Momentum xT](assets/match_report_momentum.png) |

---

### Match Report Ofensivo

9 scripts especializados en la fase ofensiva: secuencias de posesión larga, switches de flanco, zonas de recepción, dominio posicional y conexiones entre jugadores.

| | |
|---|---|
| ![Top 3 conexiones](assets/ofensivo_top3_conexiones.png) | ![Secuencia de gol](assets/ofensivo_secuencia_gol.png) |

---

### Match Report Defensivo

9 scripts para el análisis defensivo: zonas de pérdida y recuperación, transiciones defensivas, duelos, red defensiva y ocasiones concedidas.

| | |
|---|---|
| ![Red defensiva](assets/defensivo_red_defensiva.png) | ![Mapa de duelos](assets/defensivo_mapa_duelos.png) |

---

### Informe Alta Participación Real Betis

Pipeline completo de datos de jugadores: limpieza, exploración, contextualización por minutos jugados y modelo ML de predicción de participación. Dashboard interactivo en Power BI.

| | |
|---|---|
| [![Dashboard jugadores 1](assets/powerbi_jugadores_1.png)](https://app.powerbi.com/view?r=eyJrIjoiY2MzYjQyNDUtZDQ0Zi00YmRhLTllODctOWQwZDU4MjFiM2RjIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) | [![Dashboard jugadores 2](assets/powerbi_jugadores_2.png)](https://app.powerbi.com/view?r=eyJrIjoiY2MzYjQyNDUtZDQ0Zi00YmRhLTllODctOWQwZDU4MjFiM2RjIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) |

> 🔗 <a href="https://app.powerbi.com/view?r=eyJrIjoiY2MzYjQyNDUtZDQ0Zi00YmRhLTllODctOWQwZDU4MjFiM2RjIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9" target="_blank">Ver informe completo</a>

---

### Informe Defensas Sub-23 Eurocopa 2024

Pipeline con datos open-data de StatsBomb: generación de métricas, filtro sub-23, enriquecimiento con edad via API y análisis estadístico descriptivo. Dashboard interactivo en Power BI.

| | |
|---|---|
| [![Dashboard defensas 1](assets/powerbi_defensas_1.png)](https://app.powerbi.com/view?r=eyJrIjoiZDMyZDc1NWItYjkxMC00OTViLWFlYjYtZDk1YThlNGY2MDkxIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) | [![Dashboard defensas 2](assets/powerbi_defensas_2.png)](https://app.powerbi.com/view?r=eyJrIjoiZDMyZDc1NWItYjkxMC00OTViLWFlYjYtZDk1YThlNGY2MDkxIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) |

> 🔗 <a href="https://app.powerbi.com/view?r=eyJrIjoiZDMyZDc1NWItYjkxMC00OTViLWFlYjYtZDk1YThlNGY2MDkxIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9" target="_blank">Ver informe completo</a>

---

### Scouting Dashboard Segunda División

Pipeline completo de scouting de extremos para Segunda División española: extracción de métricas vía Sofascore API, 5 scripts de limpieza, filtrado, contextualización y modelado (regresión logística, 68% accuracy), y dashboard Streamlit interactivo con radar bicolor, comparativa de jugadores y generador de informes. Desplegado en producción con Docker en un VPS.

| | |
|---|---|
| ![Resumen de mercado](assets/scouting_tab1_resumen.png) | ![Análisis individual](assets/scouting_tab2_analisis.png) |
| ![Comparativa de jugadores](assets/scouting_tab3_comparativa.png) | |

> 🔗 <a href="https://scouting.davidvh.com" target="_blank">Ver dashboard en vivo</a>

---

## Fuentes de datos

StatsBomb Open Data · WhoScored · Sofascore API · Understat · FBref · football-data.org API
