---
name: estado-cartera
description: Examen del Playbook de bolsa de David a la cartera y al banquillo. Segundo paso del sábado, después de /analisis-situacion-semanal y antes de /analisis-semanal-cava-hopla. Dice cómo va cada posición, cómo está cada candidato del banquillo y qué hay que ajustar. Con "nuevo <ticker>" examina un ETF o una empresa nuevos. Activar con /estado-cartera [AAAA-MM-DD del sábado] o /estado-cartera nuevo <ticker>[:empresa].
---

# Skill: /estado-cartera

Hace **una sola cosa: el examen del Playbook** (`02_Wiki/projects/trading/trading-playbook.md`). Lo definió
David el 04/11/2026:

1. **Un ETF o una empresa nuevos** se examinan con el Playbook: si cumplen, a la cartera; si no, al banquillo.
2. **Cada sábado**, el mismo examen a todo lo que está en la cartera y en el banquillo → cómo va la
   cartera, cómo está el banquillo y qué hay que ajustar (bloques A/B/C, Playbook sección 8).

**Informa, no decide.** No compra, no vende y no cambia el Plan ni las Posiciones sin el visto bueno de
David. La conclusión de David puede ser más prudente que lo que diga la regla, nunca más atrevida.

## Qué lee y qué escribe

| | Fichero (vault, `02_Wiki/projects/trading/`) |
|---|---|
| Reglas | `trading-playbook.md` (el script las lleva dentro; si cambia una regla, se cambia el script) |
| Qué se examina | `trading-plan.md`, tabla **"Parámetros del examen"** (zona, stop e importe de cada uno) |
| Qué está comprado | `trading-posiciones.md`, tabla **"Abiertas"** |
| Sale | `sabados/estado-AAAA-MM-DD.md` (solo el modo sábado) |

## Pasos (modo sábado)

1. **Ejecutar** (fecha del sábado; sin fecha, el último):
   ```bash
   cd ~/.claude/skills/estado-cartera/scripts
   "/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --sabado AAAA-MM-DD
   ```
   Tarda unos minutos (descarga ~25 series de Yahoo y DBnomics con curl).

2. **Leer el informe entero** y abrirlo en Obsidian:
   `open "obsidian://open?vault=david_brain&file=02_Wiki%2Fprojects%2Ftrading%2Fsabados%2Festado-AAAA-MM-DD&paneType=tab"`

3. **Decir a David, en pocas líneas:**
   - El color del semáforo y qué lo enciende.
   - Lo que hay que **hacer el lunes** (compras con gatillo confirmado, ventas por stop, EMA o semáforo rojo).
   - Lo que hay que **confirmar en el gráfico** (cada "posible gatillo") y las casillas marcadas con ⚠️.
   - Los **ajustes** del bloque C.
   - Nada más: el resto está en el informe.

4. **Con el visto bueno de David**, y solo entonces:
   - Si compra o vende: proponer la línea de `trading-posiciones.md` y escribirla cuando la confirme.
   - Anotar el valor de la especulación de ese sábado en `trading-posiciones.md` (para el freno del 10%).
   - Si un candidato sube o baja: cambiar la fila en "Parámetros del examen" y en el banquillo del Plan.
   - Subir lo que cambie al Master Brain con `~/.claude/nlm-upsert.sh "<ruta>"`.

## Modo nuevo

```bash
"/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --nuevo TICKER        # ETF
"/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --nuevo TICKER:empresa # empresa (filtro 4: resultados)
```

Saca el examen (filtro, correlación con la cartera, tendencia, lateral, estocástico; resultados si es
empresa) y **la historia de retrocesos con sus huecos**, para medir zona y stop. Después:
- **Réplica UCITS:** comprobarla en justETF. Sin réplica UCITS no entra.
- **La zona la elige David**, con esa historia, su gráfico y los niveles de Cava.
- **Stop:** por nivel si hay hueco natural; si no, % de ruido en la réplica.
- Con zona y stop: **ratio** (≥ 1:2) y **tope del 1%**. Si cumple todo → cartera (con la paridad
  recalculada sobre el 38% del valor actual); si no → banquillo. En los dos casos, una fila en
  "Parámetros del examen" y, si es nuevo, su ficha en `trading-fichas-etf.md`. Todo con visto bueno.

## Lo que el script NO decide (y cómo lo dice)

- **Gatillo de agotamiento:** lo mira con números (volumen bajo la media de la caída + cuerpo < mitad del
  rango o mecha inferior > cuerpo) y dice *"posible gatillo: confírmalo en el gráfico"*. Lo confirma David.
- **Escape falso del S&P:** se mira en el gráfico.
- **Oro:** usa el futuro GC=F; cerca de 3.201 se comprueba GOLD en TradingView.
- **Stop por nivel:** la propuesta de subida (escalón nuevo) se revisa en el gráfico.
- **Descarte del banquillo por 13 semanas:** sin decidir, no lo propone.

## Decisiones del código (declaradas)

- Velas semanales agrupadas desde el diario con cierre en viernes (el semanal de Yahoo desplaza la etiqueta).
- "EMA subiendo" = la EMA de esta semana por encima de la de la anterior.
- "Acercándose" = por encima de la zona y con el cierre por debajo del de la semana anterior.
- "Siguiente resistencia" del ratio = el máximo de las últimas 52 semanas.
- Si no está en zona, el ratio se calcula con la entrada en el centro de la zona.
- Correlación del filtro 3: rentabilidades semanales de 2 años contra las posiciones de la cartera.
- Valor de partida de la cartera: 10.000 € (simulación).
- "HYG/IEI en nuevo mínimo" = cierre del cociente en su mínimo de 52 semanas y por debajo de su EMA 50 (definición de David, 04/11).

## Prueba

Primera ejecución: sábado 31/10/2026 (ensayo del 04/11). Los dos primeros sábados reales (07/11 y 14/11)
son la prueba: David comprueba en TradingView lo que dice el informe.

Código en `~/.claude/skills/estado-cartera/` y copia en git en `RepositorioCodigo/Trading/skills/estado-cartera/`.
