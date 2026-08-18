# Scouting Dashboard — Segunda División

Análisis de la posición de extremo en Segunda División española: clasifica a cada jugador en tres perfiles y publica el resultado en un dashboard interactivo, desplegado en producción con Docker en un VPS.

**Demo en vivo:** [https://scouting.davidvh.com](https://scouting.davidvh.com)

---

## Qué hace

Describe y clasifica la posición de extremo en Segunda División. Cada jugador recibe tres notas independientes de 0 a 100 —**regateador**, **finalizador** y **creador**— construidas como índices de percentiles con pesos declarados.

- **109 extremos** extraídos de La Liga 2 2025-26 (Sofascore API)
- **84 en el pool** tras el corte de muestra (450 minutos ≈ 5 partidos), elegido barriendo el coste de cada umbral
- **Tres notas por jugador**, no una: los pesos de cada perfil suman 100 y están declarados en `clasificacion_por_perfiles.py`
- **Sello `jugador_seguro`** (18 de 84): atributo que se cuelga encima del perfil, no un cuarto perfil — pocas pérdidas *relativas al pool* y ≥75% de acierto en el pase, *absoluto*
- **Percentiles** calculados sobre los 84 del pool, que es el grupo de referencia declarado

**Sin modelo, a propósito.** El proyecto tuvo una regresión logística y se retiró: el target se construía con las mismas columnas que alimentaban las features —e incluía los minutos jugados como criterio positivo— así que premiaba haber jugado mucho. Sin target real no hay nada que predecir, y un índice no puede equivocarse porque no predice: su validez descansa en que los pesos estén declarados.

**Contraste con el mercado** (`baseline_extremos.py`): correlación de Spearman de cada nota contra el valor de mercado — **0,14 / 0,22 / 0,15**. No es un detector de precio.

---

## Pipeline

| Script | Descripción |
|---|---|
| `get_dataset.py` | Extracción de métricas vía Sofascore API (tournament_id=54, season_id=77558) |
| `limpieza_de_datos.py` | Duplicados, fechas legibles, tipos de dato · 109 filas |
| `contextualización_y_filtrado.py` | Normalización por 90 y corte de muestra en 450 minutos · 109 → **84** |
| `clasificacion_por_perfiles.py` | Percentiles, inversión de las métricas negativas, pesos y sello · produce las tres notas |
| `baseline_extremos.py` | Contraste de cada nota con el valor de mercado (Spearman) |
| `dashboard_extremos.py` | Dashboard Streamlit con 3 pestañas |

Los scripts `exploracion_inicial.py`, `frontera_metricas_generacion_de_peligro.py` y `modelado_de_datos.py` están **fuera del flujo** y se conservan a propósito: son el andamio del que salió el diagnóstico del sesgo de minutos y del target circular.

---

## Dashboard

Un selector de **perfil** y otro de **tramo de nota** viven fuera de las pestañas: las tres comparten la misma selección.

- **Tab 1 — Resumen general:** medias del perfil elegido, distribución por pie dominante y listado de extremos con su nota, sus minutos y el sello
- **Tab 2 — Análisis individual:** radar de seis ejes (tres comunes a todo extremo y tres del perfil activo), ficha del jugador, y sus estadísticas con el valor bruto y el por 90 juntos
- **Tab 3 — Comparativa:** dos jugadores sobre los mismos ejes, tabla enfrentada y la nota y el sello de cada uno

Los números del radar son **percentiles** dentro de los 84, y las etiquetas lo dicen. Dos botones de información explican en pantalla cómo se calcula la nota del perfil activo —con sus pesos— y qué es un jugador seguro.

---

## Stack técnico

- **Python 3.11** — lenguaje principal
- **Streamlit** — framework del dashboard web
- **pandas / NumPy / SciPy** — procesamiento y estadísticas
- **scikit-learn** — modelo de clasificación
- **mplsoccer / matplotlib / plotly** — visualizaciones
- **Docker** — empaquetado y despliegue
- **Nginx** — proxy inverso (puerto 80/443 → 8501)
- **Let's Encrypt** — certificado HTTPS gratuito con renovación automática

---

## Despliegue

### Qué es un VPS

Un VPS (Virtual Private Server) es un servidor Linux en la nube con recursos dedicados (CPU, RAM, disco). A diferencia de un hosting compartido, tienes acceso root completo y puedes instalar lo que necesites. Este proyecto corre en un VPS KVM1 de Hostinger (1 vCPU, 4 GB RAM, Ubuntu 24.04) ubicado en Francia.

### Qué es Docker

Docker empaqueta la aplicación junto con su entorno de ejecución (Python, librerías, configuración) en una **imagen** portable. Esa imagen se despliega como un **contenedor** que funciona igual en cualquier máquina, independientemente del sistema operativo del servidor. Elimina el problema de "en mi máquina funciona".

### Arquitectura de producción

```
Usuario
  ↓ HTTPS (443)
Nginx (proxy inverso)
  ↓ HTTP interno (8501)
Docker container
  └── streamlit run dashboard_extremos.py
        └── lee CSVs incluidos en la imagen
```

### Comandos de gestión

```bash
# Ver estado del contenedor
docker ps

# Ver logs en tiempo real
docker logs -f scouting-dashboard

# Parar el dashboard
docker stop scouting-dashboard

# Arrancar de nuevo
docker start scouting-dashboard

# Rebuild tras cambios en el código
docker build -t scouting-dashboard . && docker stop scouting-dashboard && docker rm scouting-dashboard
docker run -d -p 8501:8501 --restart unless-stopped --name scouting-dashboard scouting-dashboard
```

---

## Estructura del proyecto

```
ScoutingDashboard/
├── pipeline_extremos_segunda_division/
│   ├── dashboard_extremos.py                  # Dashboard principal
│   ├── limpieza_de_datos.py                   # 1 · duplicados, fechas, tipos
│   ├── contextualización_y_filtrado.py        # 2 · por 90 y corte de muestra
│   ├── clasificacion_por_perfiles.py          # 3 · percentiles, pesos y sello
│   ├── baseline_extremos.py                   # contraste con el valor de mercado
│   ├── frontera_metricas_generacion_de_peligro.py   # andamio (fuera del flujo)
│   ├── modelado_de_datos.py                   # andamio (fuera del flujo)
│   └── exploracion_inicial.py                 # andamio (fuera del flujo)
├── get_dataset.py                     # Extracción vía Sofascore API
├── dataset_extremos.csv               # crudo de la API (109)
├── dataset_extremos_limpio.csv        # tras limpieza (109)
├── dataset_extremos_filtrado.csv      # el pool, tras el corte de muestra (84)
├── dataset_extremos_perfiles.csv      # con las tres notas y el sello — lo que lee el dashboard
├── .streamlit/config.toml             # Tema visual
├── Dockerfile
└── requirements.txt
```
