# Scouting Dashboard — Segunda División

Dashboard interactivo de scouting de extremos para Segunda División española, desplegado en producción con Docker en un VPS.

**Demo en vivo:** [https://scouting.davidvh.com](https://scouting.davidvh.com)

---

## Qué hace

Identifica extremos fichables en Segunda División aplicando tres filtros de contexto (contrato expira 2026/27, valor de mercado < 500.000 €, mínimo 200 minutos jugados) y los evalúa con métricas técnicas y un modelo de clasificación ML.

- **109 extremos** analizados de La Liga 2 2025-26 (Sofascore API)
- **7 jugadores** recomendados tras aplicar el pipeline completo (Puntuacion >= 4)
- **Modelo ML:** regresión logística con 68% de accuracy
- **Percentiles** calculados sobre el universo completo de 109 extremos

---

## Pipeline

| Script | Descripción |
|---|---|
| `get_dataset.py` | Extracción de métricas vía Sofascore API (tournament_id=54, season_id=77558) |
| `limpieza_de_datos.py` | Normalización, tratamiento de nulos, tipos de dato |
| `filtrado_jugadores.py` | Aplicación de filtros de contexto (contrato, valor mercado, minutos) |
| `contextualizacion_y_frontera.py` | Cálculo de percentiles y definición de frontera de rendimiento |
| `modelado_de_datos.py` | Modelo ML + puntuación final (Puntuacion >= 4 → recomendado) |
| `dashboard_extremos.py` | Dashboard Streamlit con 3 tabs y generador de informes |

---

## Dashboard

- **Tab 1 — Resumen de mercado:** KPIs del universo (109 extremos), distribuciones de valor y rendimiento, top extremos recomendados
- **Tab 2 — Comparativa de jugadores:** radar bicolor, tabla de métricas detalladas, comparativa directa entre jugadores
- **Tab 3 — Modelo e informes:** resultados del modelo ML, umbrales de decisión, generación de informe por jugador

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
│   ├── dashboard_extremos.py          # Dashboard principal
│   ├── limpieza_de_datos.py
│   ├── filtrado_jugadores.py
│   ├── contextualizacion_y_frontera.py
│   ├── modelado_de_datos.py
│   └── exploracion_inicial.py
├── get_dataset.py                           # Extracción vía Sofascore API
├── dataset_extremos_filtrado_modelado.csv   # Datos del dashboard (109 extremos)
├── dataset_extremos_contextualizados.csv    # Dataset de referencia para percentiles
├── .streamlit/config.toml                   # Tema visual
├── Dockerfile
└── requirements.txt
```
