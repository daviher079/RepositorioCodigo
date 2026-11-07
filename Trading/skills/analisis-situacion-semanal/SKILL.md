---
name: analisis-situacion-semanal
description: Informe semanal de trading de David. Calcula las 8 filas de Datos macro semanales (Fed, MOVE, HYG, Russell, SPY, SPY/GLD, VIX, KOSPI) con el cierre de la semana y escribe el Word con ficha, veredicto, recorrido, qué ha cambiado y resumen con frases fijas por tramo. Claude escribe después las conclusiones (como especulador con 30 años de bolsa) y David las revisa. Activar con /analisis-situacion-semanal [AAAA-MM-DD del sábado].
---

# Skill: /analisis-situacion-semanal

Primer paso del sábado. Todo lo que hace sale de la **Especificación — Análisis semanal automatizado**
(vault, `~/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Obsidian/david_brain/02_Wiki/projects/trading/trading-especificacion.md`; desde el 04/11/2026 — la copia de Drive
`1npxghc2JILV_VT534GFiZtEbDYzFNx9wI5kKOAHnzOs` ya no es la viva). Si la especificación y el script no
coinciden, manda la especificación: se corrige el script, no la lectura.

**El script NO escribe conclusiones ni une filas: las escribe Claude en el paso 7** (decidido por David
el 07/11/2026; hasta entonces las escribía él) y David las revisa. Mientras no se haya llegado al paso 7,
no interpretes los números en el chat: enseña lo que dice el informe y para.

## Pasos

1. **Sábado del informe.** El argumento, si lo hay (`AAAA-MM-DD`, tiene que ser sábado). Si no, el script
   coge el sábado de esta semana (si es sábado o domingo) o el último. La semana es de lunes a viernes antes de ese sábado.

2. **Carpeta.** `~/Desktop/cartera/analisis semanal/informe semanal DD-MM-AAAA/`. Las carpetas las crea David.
   Si no existe, el script para y lo dice: pregunta a David si la crea él o si la creas tú; solo en ese
   caso vuelve a lanzar con `--crear-carpeta` (solo crea la del sábado, nunca la base).

3. **Lanzar:**
   ```bash
   "/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" ~/.claude/skills/analisis-situacion-semanal/scripts/analisis.py [AAAA-MM-DD]
   ```
   `--sin-docx` solo imprime. Si la semana aún no ha cerrado (se lanza antes del sábado), el informe lo avisa arriba.

4. **Enseñar a David**, sin opinar:
   - el veredicto de cada fila y la línea de "qué ha cambiado";
   - los **dos números para comprobar en TradingView** (cierre y EMA del SPY, distancia del HYG);
   - la ruta del Word (todavía **sin abrir**: se abre al final, en el paso 8).

5. **Si un número no coincide con TradingView**, no se da el informe por bueno: se busca la causa en el
   script (fuente, semana, EMA) antes de seguir.

6. **Actualizar el dashboard** (vista rápida; el Word sigue siendo el detalle). El enlace es siempre el mismo:
   https://claude.ai/artifact/XRnA8ugw3pKRFi8LZ9D1Ea

   El script deja `filas.json` y `cabecera.json` en `~/.claude/skills/analisis-situacion-semanal/dashboard/`,
   con las últimas 53 semanas. Para cada archivo: `Artifact` con `asset: true`, `url` y `file_path`, y después
   `ArtifactData` `update` en `datasets/filas` y `datasets/cabecera` con `source` (`url` nueva) y
   `updated` (`at` + `by`), usando el `if_version` leído. Luego borrar el asset anterior.
   **Con `--sin-docx` no se generan esos archivos.** Relanzar el script reescribe el Word: si David ya ha
   escrito sus conclusiones, no relanzarlo sin preguntarle.

7. **Escribir las conclusiones** (Claude, desde el 07/11/2026). Rol: **especulador con 30 años de bolsa**
   que lee el informe para David. Cuatro apartados: lado de la Fed (Fed + MOVE + HYG), el Russell entre
   los dos lados, lado de la bolsa (SPY + VIX + SPY/GLD + KOSPI) y conclusión final.
   - **Antes de escribir**, leer el semáforo de la especulación (sección 2) de
     `02_Wiki/projects/trading/trading-playbook.md` y la conclusión del sábado anterior (su Word).
   - **Unir filas** es el trabajo: qué causa qué, qué confirma a qué y qué se contradice. Si dos filas
     dicen cosas opuestas, se dice.
   - **Cada afirmación con su número del informe.** Ningún dato que no esté en el informe; lo que sea
     criterio propio va marcado como tal ("mi lectura", "en mi experiencia") — regla transversal 1.
   - **Los modales, honestos:** probabilidades, no certezas. Los porcentajes históricos del informe se
     citan como historia, no como predicción.
   - **Conclusión final:** el estado del **semáforo** (verde, amarillo o rojo, con el bloqueo que lo
     activa, o "no lo dice el informe" si falta un dato, como el mínimo de 52 semanas del HYG/IEI), qué
     cambió frente al sábado anterior y **los dos o tres niveles que vigilar la semana que viene**
     (sacados de "Para cambiar de tramo"). Prosa simple, como escribe David; nada de compras ni ventas
     concretas: eso es de `/estado-cartera`.
   - Se escribe en un JSON (las cuatro claves con el título exacto de cada apartado, cada una con una
     lista de párrafos) y se vuelca con:
     ```bash
     osascript -e 'tell application "Microsoft Word" to quit saving no'   # si Word está abierto
     "/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" ~/.claude/skills/analisis-situacion-semanal/scripts/conclusiones.py "<ruta del .docx>" "<ruta del .json>"
     ```
     El script guarda una copia `.bak` y para si algún apartado ya tiene texto.

8. **Abrir las dos cosas, sin que David lo pida** (lo pidió así el 07/11/2026). Cuando los números
   cuadren con TradingView, el dashboard esté actualizado y las conclusiones escritas, abrir el Word y el dashboard a la vez:
   ```bash
   open "<ruta del .docx que imprime el script>"
   open "https://claude.ai/artifact/XRnA8ugw3pKRFi8LZ9D1Ea"
   ```
   Si un número no cuadra (paso 5), no se abre nada hasta resolverlo.

## Qué calcula (resumen; el detalle está en la especificación)

- Datos: Yahoo (`SPY HYG IEI GLD ^VIX ^MOVE ^TNX ^KS11 IWM`) y DBnomics (`FED/H15/RIFSPFF_N.B`,
  `FED/H41/RESPPA_N.WW`, `BEA/NIPA-T10105/A191RC-Q`). EMA 50 semanal sobre el cierre (no el ajustado).
- Orden del informe: **lado de la Fed** (Fed, MOVE, HYG) → **Russell** (puente) → **lado de la bolsa**
  (SPY, SPY/GLD, VIX, KOSPI) → cuatro apartados vacíos para las conclusiones de David.
- Cada fila: ficha · veredicto · recorrido (6 meses, 3, 1 y hoy) · qué ha cambiado · semanas malas · para cambiar de tramo · resumen con frases fijas por tramo.
- Tramos por nivel, tarde lo que tarde: Fed, MOVE, HYG, Russell, SPY, SPY/GLD. Por nivel y por semanas: VIX (3 semanas por encima de 20) y KOSPI (3 semanas o −5%).
- Donde no hay corte medido, solo el número (distancia en pb, contadores, evolución de la distancia).
- **Soporte del KOSPI**: valor fijo en `config.json`. Lo cambia David cuando el KOSPI haga una nueva base.

## Decisiones del código que no están en la especificación (declaradas)

- **PIB publicado**: el trimestre se da por publicado 30 días después de cerrarse (para el recorrido y
  para "PIB nuevo esta semana"). El avance real sale hacia el final del mes siguiente.
- **Casilla de la Fed**: rojo si se cumplen las dos condiciones del test de Cava; aviso si la Fed ha
  recortado más de medio punto en 6 meses o el margen del bono baja de 1; si no, viento a favor.
- **Última decisión de la Fed**: último salto diario del tipo efectivo de al menos 15 pb.
- **Yahoo semanal**: con histórico largo etiqueta cada vela con el sábado anterior a su semana; el
  script la asigna al lunes siguiente. Sin eso, todo sale con una semana de desfase (cazado el 29/10).

## Prueba de referencia

Con `2026-10-24` debe salir lo comprobado a mano el 29/10: SPY 759,97 / EMA 721,21 (+5,4%), MOVE 1,46
(percentil 92, 5 semanas), bono 4,99% (+27 / −26 pb), HYG −2,84% (21 semanas), IWM/SPY −3,99% (6 semanas),
SPY/GLD +10,8%, VIX 19,45 (±2,7%, 739-780), KOSPI −8,9% (2 semanas), Fed +1,3 / +2,4 / +0,09%.
