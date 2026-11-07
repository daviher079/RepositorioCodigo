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
| Cómo se salió | `trading-posiciones.md`, tabla **"Cerradas"**: la última salida de cada nombre decide el **Gatillo de Recompra** (solo si el motivo dice "EMA 50") |
| Sale | `sabados/estado-AAAA-MM-DD.md` (solo el modo sábado) |

## Pasos (modo sábado)

1. **Ejecutar** (fecha del sábado; sin fecha, el último):
   ```bash
   cd ~/.claude/skills/estado-cartera/scripts
   "/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --sabado AAAA-MM-DD
   ```
   Tarda unos minutos (descarga ~25 series de Yahoo y DBnomics con curl).

2. **Leer el informe entero.**

   **Actualizar el dashboard** (vista de la semana, pedida por David el 07/11; el informe sigue siendo el detalle):
   https://claude.ai/artifact/GawoWnGADBEb2gC8pqmjuq — tipo Dashboard. El script deja en
   `~/.claude/skills/estado-cartera/dashboard/` cinco JSON: `cabecera`, `semaforo`, `cartera`, `banquillo` y
   `ajustes`. Para cada uno: `Artifact` con `asset: true`, `url` y `file_path`; después **un solo**
   `ArtifactData` `batch` con un `update` por `datasets/<nombre>` (`source.url` nueva, `updated` con `at` + `by`,
   `edit: {via: "claude", at}`), usando el `version` leído como `if_version`. Luego borrar los assets anteriores.

   **Abrir las dos cosas a la vez, sin que David lo pida** (como en `/analisis-situacion-semanal`):
   ```bash
   open "obsidian://open?vault=david_brain&file=02_Wiki%2Fprojects%2Ftrading%2Fsabados%2Festado-AAAA-MM-DD&paneType=tab"
   open "https://claude.ai/artifact/GawoWnGADBEb2gC8pqmjuq"
   ```

3. **Decir a David, en pocas líneas:**
   - El color del semáforo y qué lo enciende.
   - Lo que hay que **hacer el lunes** (compras con gatillo confirmado, ventas por stop, EMA o semáforo rojo).
   - Lo que hay que **confirmar en el gráfico** (cada "posible gatillo") y las casillas marcadas con ⚠️.
   - Los **ajustes** del bloque C.
   - Nada más: el resto está en el informe.

4. **Con el visto bueno de David**, y solo entonces:
   - Si compra o vende: proponer la línea de `trading-posiciones.md` y escribirla cuando la confirme.
   - **Si vende por el stop** (añadido 2, 05/11): en "Parámetros del examen" del Plan, su **Zona y Stop pasan a «—»**. Así el sábado siguiente sale como *"sin medir"* y no vuelve a dar gatillo en la zona que falló. Solo vuelve a la cartera con una zona nueva medida con `--nuevo`. Si vende por la EMA 50, la zona se conserva (vale el Gatillo de Recompra).
   - **Zona fallida sin comprar** (David, 07/11): si el bloque C lo dice (cierre bajo el stop sin estar dentro), lo mismo: **Zona y Stop a «—»** y también la "Pérdida real", que estaba medida con esa zona. Solo vuelve con `--nuevo`.
   - **Al cerrar una posición**, el "Motivo de salida" en "Cerradas" se escribe **literal**: `Stop`, `EMA 50` o `Semáforo rojo`. El script busca "EMA" en ese texto para saber si vigila el Gatillo de Recompra; con otro texto no lo vigilaría.
   - Anotar el valor de la especulación de ese sábado en `trading-posiciones.md` (para el freno del 10%).
   - Si un candidato sube o baja: cambiar la fila en "Parámetros del examen" y en el banquillo del Plan.
   - Subir lo que cambie al Master Brain con `~/.claude/nlm-upsert.sh "<ruta>"`.

## Modo medir (05/11)

```bash
"/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --medir CIBR    # o --medir todos
```

Con la zona y el stop del Plan, simula cada retroceso de su historia (entra con un cierre en la zona, sale con el primer cierre semanal bajo el stop) y da la **pérdida real media en R** y cuántas veces saltó. Ese `2.1 (5)` se escribe, con visto bueno de David, en la columna **"Pérdida real"** de "Parámetros del examen", y el `g/n` (ganadoras / entradas) en la columna **"Acierto"** (07/11). Con los dos, el sábado calcula la **esperanza** = acierto × ratio sobre papel − (1 − acierto) × pérdida real: si es negativa no entra aunque pase el 1:2; con menos de 5 entradas solo avisa (Playbook, sección 4). Se corre al poner zona y stop a un ETF y al cambiarlos, no cada sábado. El sábado, el ratio que manda (filtro 1:2, home run, prioridad) es el **real** = papel ÷ pérdida real; con menos de 5 stops saltados, el de papel con ⚠️.

## Esperando suelo (05/11)

Un candidato del banquillo **sin zona** cuya caída desde el máximo de 52 semanas ha pasado del borde alto del hueco más grande de su historia (los mismos retrocesos que enseña `--nuevo`) sale como **esperando suelo**: cuánto cae, dónde suele parar según su historia y si salta el gatillo de la sección 3 (agotamiento + volumen menor que la caída). Con gatillo, dice **posible suelo: medir zona y stop con `--nuevo`**. No mide ni decide: avisa. Decisión de David (05/11), nacida de SMH.

## Modo nuevo

```bash
"/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --nuevo TICKER        # ETF
"/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --nuevo TICKER:empresa # empresa (filtro 4: resultados)
"/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" estado.py --nuevo XLV --replica QDVG.DE  # + tabla de ruido en la réplica
```

Saca el examen (filtro, correlación con la cartera, tendencia, lateral, estocástico; resultados si es
empresa) y **la historia de retrocesos con sus huecos**, para medir zona y stop. Después:
- **Réplica UCITS:** comprobarla en justETF. Sin réplica UCITS no entra.
- **La zona la elige David**, con esa historia, su gráfico y los niveles de Cava.
- **Stop:** por nivel si hay hueco natural; si no, % de ruido en la réplica. La **tabla de ruido** (rehecha el 05/11) sale sola en el modo nuevo, medida en la réplica que se pase con `--replica`. Definición: entrada = cada semana de un retroceso de su historia que cierra por encima de su EMA 50; salta = algún cierre de las 8 semanas siguientes cae un X% o más bajo la entrada. El stop va en el salto, y lo elige David. Comprobada con XLE (10% → 15%, 12% → 8%), EXXY (8% → 11%, 10% → 1%) y QDVG (10% → 3%): los stops elegidos siguen valiendo.
- Con zona y stop: **ratio** (≥ 1:2) y **tope del 1%**. Si cumple todo → cartera (con la paridad
  recalculada sobre el 38% del valor actual); si no → banquillo. En los dos casos, una fila en
  "Parámetros del examen" y, si es nuevo, su ficha en `trading-fichas-etf.md`. Todo con visto bueno.

## Lo que el script NO decide (y cómo lo dice)

- **Gatillo de agotamiento:** lo mira con números (volumen bajo la media de la caída + cuerpo < mitad del
  rango o mecha inferior > cuerpo) y dice *"posible gatillo: confírmalo en el gráfico"*. Lo confirma David.
- **Escape falso del S&P:** se mira en el gráfico.
- **Dinero nuevo del núcleo** (añadido 6, 05/11; plan real desde enero de 2027): bajo el semáforo, una línea dice a dónde iría el dinero nuevo del núcleo según SPY/GLD frente a su EMA 50 (lateral = regla de la sección 3 sobre el cociente). La **banda del oro** (5-15%) no la puede comprobar: la simulación no lleva el valor real del núcleo. La comprueba David.
- **Ratio, home run y prioridad** (añadido 5, 05/11): el ratio se escribe siempre **1:X**. Con 1:4 o más sale marcado ⚾ **home run** (mismo tamaño que los demás). Si dos o más pueden entrar la misma semana, el bloque C dice la **prioridad**: primero el de mayor ratio.
- **Gatillo de Recompra** (añadido el 05/11): tras una salida por la EMA 50, cada sábado dice si está *en espera* (cierre bajo la EMA) o *se cumple*, y en ese caso comprueba el permiso (semáforo, ratio con el cierre como entrada y el stop del Plan, tope del 1% y riesgo abierto). Dos cosas que no decide: el **freno del 10%** (sin serie todavía) y el **lateral** (el permiso del Playbook no lo nombra): las marca para David.
- **Oro:** usa el futuro GC=F; cerca de 3.201 se comprueba GOLD en TradingView.
- **Stop por nivel:** la propuesta de subida (escalón nuevo) se revisa en el gráfico.
- **Descarte del banquillo por 13 semanas:** descartado por David el 05/11. No hay regla de salida del banquillo: no lo propone.

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
