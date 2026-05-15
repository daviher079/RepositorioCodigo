# RepositorioCodigo — David Vicente Hernández

Scripts y pipelines de análisis de datos aplicados al fútbol. Desarrollados durante el Máster en Big Data e Inteligencia Artificial Aplicado al Deporte (Unisport Management School) y el curso Objetivo Analista de Datos 360.

## Tecnologías

Python · Power BI · pandas · matplotlib · mplsoccer · statsbombpy · scikit-learn · Playwright · NumPy · SciPy

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

### Pipeline Jugadores — Módulo 2 Unisport

Pipeline completo de datos de jugadores: limpieza, exploración, contextualización por minutos jugados y modelo ML de predicción de participación. Dashboard interactivo en Power BI.

| | |
|---|---|
| [![Dashboard jugadores 1](assets/powerbi_jugadores_1.png)](https://app.powerbi.com/view?r=eyJrIjoiY2MzYjQyNDUtZDQ0Zi00YmRhLTllODctOWQwZDU4MjFiM2RjIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) | [![Dashboard jugadores 2](assets/powerbi_jugadores_2.png)](https://app.powerbi.com/view?r=eyJrIjoiY2MzYjQyNDUtZDQ0Zi00YmRhLTllODctOWQwZDU4MjFiM2RjIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) |

> Haz clic en las imágenes para abrir el dashboard interactivo

---

### Pipeline Defensas Sub-23 — Eurocopa 2024

Pipeline con datos open-data de StatsBomb: generación de métricas, filtro sub-23, enriquecimiento con edad via API y análisis estadístico descriptivo. Dashboard interactivo en Power BI.

| | |
|---|---|
| [![Dashboard defensas 1](assets/powerbi_defensas_1.png)](https://app.powerbi.com/view?r=eyJrIjoiZDMyZDc1NWItYjkxMC00OTViLWFlYjYtZDk1YThlNGY2MDkxIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) | [![Dashboard defensas 2](assets/powerbi_defensas_2.png)](https://app.powerbi.com/view?r=eyJrIjoiZDMyZDc1NWItYjkxMC00OTViLWFlYjYtZDk1YThlNGY2MDkxIiwidCI6IjMxNTI1NWE3LTk2NDMtNDYyYy04MGRkLTRjODk1NTgwZDg0NSIsImMiOjh9) |

> Haz clic en las imágenes para abrir el dashboard interactivo

---

### Módulo 4 Unisport

Scripts del caso práctico del Módulo 4: dashboard deportivo, segmentación de fans, análisis de sentimiento y modelo táctico.

---

## Fuentes de datos

StatsBomb Open Data · WhoScored · Understat · FBref · football-data.org API
