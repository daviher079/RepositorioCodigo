# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Master Brain — Consulta obligatoria

Antes de responder cualquier pregunta sobre el proyecto, decisiones anteriores o preferencias del usuario, **debes consultar el notebook Master Brain de NotebookLM** usando el siguiente comando:

```
/notebooklm ask --notebook-id 4c8a5e68-6af7-4f5e-8388-bd77ae54a18c "<tu pregunta aquí>"
```

Este notebook contiene el historial de decisiones, preferencias y contexto acumulado del proyecto. Úsalo como primera fuente de verdad antes de asumir o responder desde cero.

## Repository Overview

This is a learning portfolio repository containing three distinct project areas:

- **DAW/** — Web development coursework (PHP, HTML, CSS)
- **SERBATIC/** — Frontend training projects (React.js with Firebase, REST APIs)
- **Unisport-FutbolDataAcademy/** — Football (soccer) data analytics (Python)

The most active and mature area is `Unisport-FutbolDataAcademy/`, which is a real data pipeline project for player scouting and analysis.

## Python Environment

A virtual environment is at `venv/` (Python 3.14). Activate before running any Python scripts:

```bash
source venv/bin/activate
```

Key installed libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `statsbombpy`, `understat`, `openpyxl`, `mplsoccer`, `scipy`, `requests`, `aiohttp`.

Run any Python script from its own directory to avoid path issues:

```bash
cd Unisport-FutbolDataAcademy/Unisport/ModuloTres
python estadisticas_descriptivas_basicas.py
```

## React Projects (SERBATIC/)

Each subdirectory is an independent React app with its own `package.json`. To run:

```bash
cd SERBATIC/<project-name>
npm install
npm start
```

Projects: `practica-semana-tres-david-vicente` (Firebase auth), `apiPokemon`, `Rick-and-Morty`, `tienda_react_david_vicente` (e-commerce).

## Football Analytics Architecture (Unisport-FutbolDataAcademy/)

There are two parallel tracks:

### FutbolDataAcademy/ — Training modules (standalone scripts)
Each module is a self-contained script teaching a specific technique:
- `ModuloUno` → Understat web scraping (async, outputs CSV)
- `ModuloDos` → StatsBomb API exploration
- `ModuloTres` → Shot maps with `mplsoccer`
- `ModuloCuatro` → Pass networks
- `ModuloCinco/Seis` → Heat maps (team and individual)

### Unisport/ — Scouting pipeline (sequential modules)
This is a multi-step data pipeline where each module builds on the previous:
1. `ModuloUno/crearResumenDatos.py` — Filters raw stats, computes derived metrics (e.g., total duels = won + lost), categorizes by position, exports to Excel
2. `ModuloDos/` — Initial EDA and data cleaning
3. `ModuloTres/` — Descriptive statistics, visualizations (boxplots, correlation heatmaps, histograms), contextualization, age filtering, sub-23 filters for Eurocopa 2024

Data flows as Excel files (`.xlsx`) between modules. PNG visualizations are saved alongside the scripts.

### Data Sources
- **StatsBomb**: Free open data via `statsbombpy` — use `sb.competitions()`, `sb.matches()`, `sb.events()` for access
- **Understat**: Async scraping via `understat` library — fetches xG, shot coordinates, player info per match
- Input Excel files contain player-level statistics from tournaments (e.g., Eurocopa 2024)

## Language
All code comments, variable names, and file names are in **Spanish**.
