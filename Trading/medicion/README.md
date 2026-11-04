# Medición del Playbook único (04/11/2026)

Scripts con los que se enfrentó el Playbook al Plan de cartera. Son la base de la futura skill del estado de la cartera (bloques A/B/C del sábado). Se dejan tal cual, en el orden en que se usaron, incluido el que falló.

| Script | Qué hace | Resultado del 04/11 |
|---|---|---|
| `datos.py` | Descarga diarios de Yahoo con curl y los agrupa en semanas con `resample("W-FRI")` (el semanal de Yahoo desplaza la etiqueta) | Base de todo lo demás |
| `huecos.py` | Primer intento de medir retrocesos (desde máximos acumulados) | **No reproducía** los 9 retrocesos de CIBR del 03/11: método descartado |
| `med2.py` | Método del 03/11: retrocesos que empiezan con el ETF ≥10% sobre su EMA 50 subiendo, del cierre del pico al mínimo semanal, 26 semanas como máximo. `python med2.py <ticker> <desde_epoch> <profundidad_%>` | Reproduce CIBR (9 casos, hueco −15,3% a −22,5%). XLE sin hueco; EXXY sin hueco real; XLV con hueco −17,8% a −26,4% |
| `real.py` | Primera simulación del "ratio real" (entradas en zona → stop que sube, EMA 50 y 1 año) | Salud con 0 entradas: exigía comprar sobre la EMA y la zona está en la EMA |
| `real2.py` | La misma sin filtro de EMA en la entrada, en dos versiones (solo stop / stop + EMA) | Ninguna de las tres llega a 2:1; esperanza de −0,3R a +0,6R. Pista, no veredicto: pocos casos y sin gatillo. Modela mal los stops por nivel (CIBR) |

Uso: `venv/bin/python <script>` desde esta carpeta (importan `datos.py`). Descargan con curl porque el Python del venv no tiene certificados SSL.

Contexto: `david_brain/02_Wiki/projects/trading/trading-playbook.md` (sección "Lo que falta medir o decidir").
| `lateral.py` | Pendiente de la EMA 50 en 13 semanas y banda de cierres de 26 semanas en los 19 de cartera y banquillo (cierre del 30/10) | Salto natural entre +1,6% y +3,4%: regla del lateral (±2%, banda bajo su mediana, 4 semanas) |
| `finlat.py` | Roturas al alza de laterales en 20 ETF desde 2005: volumen frente a la media del lateral y si aguantan 8 semanas | 1,25 veces es el corte que más separa (78% frente a 61%) |
