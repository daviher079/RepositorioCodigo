# CHECKLIST MAESTRO — Tarea M4 Unisport

Referencia combinada de: Actividad evaluable M4.pdf + Caso práctico _m4_UNI100.pdf

---

## ESTRUCTURA DEL DOCUMENTO — distribución de páginas

| Sección | Contenido | Extensión |
|---|---|---|
| **1. Introducción** | Contexto Unisport FC temporada 2025-26, rol de consultor externo, qué se analiza y con qué objetivo | 1 página |
| **2. Marco teórico** | Berraquero et al. (2024) + Einsle e Izquierdo (2022) + contexto análisis datos en clubes | 2 páginas |
| **3.1 Recopilación y almacenamiento** | Dataset sintético, variables elegidas, justificación de fuentes | ~1 página |
| **3.2 Análisis descriptivo + visualizaciones Power BI** | Media/mediana/desv. estándar + las 3 visualizaciones con capturas y explicación | ~1.5 páginas |
| **3.3 Modelo descriptivo básico** | Análisis de correlación RRSS-rendimiento e interpretación | ~0.5-1 página |
| **3.4 Dashboard interactivo Power BI** | Captura del dashboard, métricas incluidas y justificación | ~1 página |
| **4. Conclusiones** | Hallazgos principales, recomendaciones estratégicas, desafíos y próximos pasos | 1 página |
| **5. Bibliografía** | Formato establecido | — |

**Total estimado: 7-8 páginas** (dentro del rango obligatorio de 5-10 sin bibliografía)

---

## ESTRUCTURA DEL DOCUMENTO (Actividad evaluable)
- [ ] **Introducción** — máx. 1 página. Contextualización del caso (Unisport FC como consultor externo)
- [ ] **Marco teórico** — máx. 2 páginas. Usar ambas referencias: Berraquero et al. (2024) y Einsle e Izquierdo (2022)
- [ ] **Respuesta a las preguntas** — mín. 2 páginas:
  - [ ] Recopilación y almacenamiento: explicar qué datos, de dónde y por qué esas fuentes
  - [ ] Análisis Power BI: visualizaciones para el equipo directivo
  - [ ] Modelo descriptivo básico (ML)
  - [ ] Dashboard interactivo Power BI con métricas justificadas
- [ ] **Conclusiones** — máx. 1 página. Beneficios, desafíos y recomendaciones prácticas
- [ ] **Bibliografía** — formato establecido
- [ ] **Extensión total:** 5-10 páginas sin bibliografía
- [ ] **Entrega:** PDF, rellenando el mismo documento de la actividad

## DATOS (Caso práctico)
- [x] Mínimo 50 registros de interacciones RRSS + resultados partidos — **254 filas metricas_rrss + 38 partidos generados en dataset_unisport_fc.xlsx**
- [x] Datos coherentes y relevantes — dataset sintético generado con generar_dataset.py

## ANÁLISIS DESCRIPTIVO (Caso práctico)
- [ ] Calcular y presentar **media, mediana y desviación estándar** explícitamente en el informe
- [ ] Eliminar valores atípicos, duplicados y faltantes
- [ ] Documentar el proceso de limpieza

## VISUALIZACIONES — las tres obligatorias (Caso práctico)
- [ ] **Gráfico de barras:** interacciones RRSS por jugador antes/después del partido
- [ ] **Gráfico de líneas:** evolución moral del equipo (comentarios positivos) vs rendimiento en partidos
- [ ] **Mapa de calor o dispersión:** menciones RRSS vs estadísticas de rendimiento (goles, asistencias)
- [ ] Todas comprensibles para audiencia **no técnica** (directivos, entrenadores)

## DASHBOARD POWER BI (Actividad evaluable)
- [ ] Métricas clave incluidas
- [ ] Justificar por qué cada métrica es relevante para toma de decisiones
- [ ] Interactivo

## RECOMENDACIONES (Caso práctico)
- [ ] Basadas en los hallazgos reales del análisis, no genéricas
- [ ] Orientadas a mejorar rendimiento del equipo Y compromiso de aficionados

## CRITERIOS DE EVALUACIÓN (puntuación máxima 10 pts)
- [ ] CA1: Sistema de recopilación y almacenamiento bien justificado **(2 pts)**
- [ ] CA2: Visualizaciones Power BI claras y útiles **(2 pts)**
- [ ] CA3: Modelo descriptivo correctamente aplicado y explicado **(2 pts)**
- [ ] CA4: Dashboard interactivo con métricas justificadas **(2 pts)**
- [ ] CA5: Conclusiones con pensamiento crítico profundo **(2 pts)**
