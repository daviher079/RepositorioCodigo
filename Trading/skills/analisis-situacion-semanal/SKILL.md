---
name: analisis-situacion-semanal
description: Informe semanal de trading de David. Calcula las 8 filas de Datos macro semanales (Fed, MOVE, HYG, Russell, SPY, SPY/GLD, VIX, KOSPI) con el cierre de la semana y escribe el Word con ficha, veredicto, recorrido, qué ha cambiado y resumen con frases fijas por tramo. No escribe conclusiones. Activar con /analisis-situacion-semanal [AAAA-MM-DD del sábado].
---

# Skill: /analisis-situacion-semanal

Primer paso del sábado. Todo lo que hace sale de la **Especificación — Análisis semanal automatizado**
(Google Drive, `1npxghc2JILV_VT534GFiZtEbDYzFNx9wI5kKOAHnzOs`). Si la especificación y el script no
coinciden, manda la especificación: se corrige el script, no la lectura.

**El informe NO escribe conclusiones ni une filas.** Eso lo hace David después de leerlo. Tampoco
interpretes tú los números en el chat: enseña lo que dice el informe y para.

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
   - la ruta del Word, y abrirlo con `open`.

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
