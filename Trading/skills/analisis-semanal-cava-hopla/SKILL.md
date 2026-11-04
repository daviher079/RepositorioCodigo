---
name: analisis-semanal-cava-hopla
description: Segundo paso del sábado de trading de David. Busca los vídeos largos de lunes a viernes de José Luis Cava y HOPLA Finance, saca su transcripción con minuto y escribe en Word un resumen de los puntos relevantes de cada vídeo y de la semana. Además lleva el vídeo del jueves de Cava al cuaderno CAVA AGENT y propone (con visto bueno de David) los cambios en las Fichas de ETF. Se lanza DESPUÉS de que David haya escrito sus conclusiones de /analisis-situacion-semanal. Activar con /analisis-semanal-cava-hopla [AAAA-MM-DD del sábado].
---

# Skill: /analisis-semanal-cava-hopla

Parte de la **Especificación — Análisis semanal automatizado** (vault,
`~/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Obsidian/david_brain/02_Wiki/projects/trading/trading-especificacion.md`, sección 2; desde el 04/11/2026 — la copia de Drive ya no es la viva).

## Antes de empezar: el orden

Este comando va **después** de que David haya leído `/analisis-situacion-semanal` y **cerrado sus
conclusiones**. Si no las ha escrito, pregúntaselo antes de lanzar nada: si lee primero a Cava, su
análisis acaba siendo el de Cava y el contraste deja de servir.

## Pasos

1. **Vídeos y transcripciones:**
   ```bash
   "/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" ~/.claude/skills/analisis-semanal-cava-hopla/scripts/videos.py [AAAA-MM-DD]
   ```
   - Calcula la semana (lunes a viernes antes del sábado, **hora de España**).
   - Lee la pestaña **Vídeos** de cada canal (feed `playlist_id=UULF…`): **los shorts quedan fuera**.
   - Guarda cada transcripción en `<carpeta del sábado>/transcripciones/` con el minuto delante de cada
     frase, y un `indice.json`.
   - Si un canal no ha publicado vídeos largos, lo dice ("sin vídeos esta semana"); es normal en Hopla,
     que suele publicar uno o dos por semana.
   - La carpeta del sábado la crea David; si no existe, para.

2. **Leer cada transcripción ENTERA** con Read. No resumir desde el título ni desde un trozo.

3. **Escribir `transcripciones/resumen.md`** con esta estructura exacta:

   ```markdown
   # Análisis Cava y Hopla — semana del DD/MM al DD/MM/AAAA

   ## José Luis Cava

   ### Lunes DD/MM — <título del vídeo>
   <url>
   - **<idea en pocas palabras>:** <lo que dice, con sus modales> «cita literal» [mm:ss]
   - ...

   ## HOPLA Finance

   ### ...

   ## Resumen de la semana
   - <lo que se repite entre vídeos, lo que cambia de un día a otro, niveles y fechas que menciona>
   ```

   **Reglas de contenido ("no source, no note"):**
   - Solo lo que **dicen** en el vídeo. Lo que sea inferencia tuya se marca: `> Nota (no en el vídeo): …`.
   - **Copia sus modales.** Si dice "podría caer", no es "va a caer". Si dice "yo creo", no es un hecho.
     Es la cicatriz de `/unisport-resumen`: al resumir se endurecen los modales sin darse cuenta.
   - Cada punto relevante lleva **una cita literal con su minuto** `[mm:ss]` sacada de la transcripción.
     La transcripción automática tiene errores: si una cifra o un nombre no se entiende, se dice
     ("se oye «…», dudoso") en vez de corregirlo a lo que parece lógico.
   - **Prioriza lo que toca las filas del sábado**: S&P 500, bonos basura, oro, VIX, bonos y tipos,
     KOSPI, Russell, Fed. Los niveles, soportes y fechas que dé, con la cifra exacta.
   - **No compares con el análisis de David.** El contraste lo hace él con los dos informes delante.
     Tampoco digas si Cava acierta o no.
   - Lo que hayan escrito otras IAs (las conversaciones de Gemini del cuaderno CAVA AGENT) **no es fuente**.
   - Un vídeo sin transcripción se lista con su título y "sin transcripción", sin resumir.

4. **Pasar a Word:**
   ```bash
   "/Users/davidvh10/Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python" ~/.claude/skills/analisis-semanal-cava-hopla/scripts/informe_docx.py "<carpeta>/transcripciones/resumen.md" "<carpeta>/Análisis Cava y Hopla DD-MM-AAAA.docx"
   ```
   Abrirlo con `open` y decir a David cuántos vídeos hay de cada canal.

5. **El vídeo del jueves de Cava → Fichas de ETF** (añadido el 02/11/2026). Los jueves Cava dedica el
   vídeo a ETF concretos, y de ahí salen las Fichas de ETF (vault, `~/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Obsidian/david_brain/02_Wiki/projects/trading/trading-fichas-etf.md`;
   desde el 04/11/2026 — la copia de Drive ya no es la viva) y la lista a vigilar. **Un ETF nuevo entra como
   candidato del banquillo, nunca directo a la cartera** (Playbook único, sección 8). Solo ese vídeo; Hopla no entra en este paso.

   a. **Localizarlo** en `indice.json`: el vídeo de Cava cuyo `dia` empieza por "Jueves". Si no hay vídeo
      el jueves, o no tiene transcripción, se dice y el paso termina.

   b. **Añadirlo al cuaderno CAVA AGENT** para que no se quede atrás:
      ```bash
      notebooklm source add -n 864fab44-6bd0-4c78-8bed-175f1540d5f8 "<url>"
      ```
      Antes, comprobar con `notebooklm source list -n 864fab44-6bd0-4c78-8bed-175f1540d5f8 --json` que el
      título no está ya. Solo vale la línea `Added source: <id>`: los errores de RPC salen antes y el
      código de salida es 0 igualmente.

   c. **Separar lo que nombra**, leyendo la transcripción ENTERA (la del paso 1, con minutos):
      - **ETF con ficha** → ampliar su **Tesis**, sus **Niveles** o sus **Notas propias**. No se borra lo que hay.
      - **ETF sin ficha** → ficha completa en "Parte especulativa", estado "Vigilando", sistema "Por decidir
        con las reglas de la especulativa". Los datos de la réplica (nombre, ISIN, índice, TER,
        acumulación, réplica, ticker de Xetra) salen de **justETF**
        (`https://www.justetf.com/en/etf-profile.html?isin=<ISIN>`), **nunca del vídeo ni de memoria**;
        si Cava da un dato que no coincide, se anota en Notas propias. Ticker del gráfico: el
        equivalente americano, y en "¿Mismo índice?" se dice si coincide.
      - **Acciones sueltas** → a "Acciones sueltas" en Descartados, con la fecha.
      - Si no nombra ningún ETF ni nivel aprovechable, se dice y no se toca el documento.

   d. **Enseñar el borrador a David ANTES de escribir.** Cada cambio con el texto exacto que irá al
      documento y, al lado, la cita literal con su `[mm:ss]` para que pueda comprobarla. Mismas reglas
      que el resumen: copiar modales, "no source, no note", Gemini no es fuente. En la ficha el texto va
      con la fecha del vídeo entre paréntesis, sin minuto (como las demás fichas). **Nada se escribe sin
      su visto bueno.**

   e. **Con el visto bueno, escribir en el documento** (`trading-fichas-etf.md` del vault, con la
      herramienta Edit; desde el 04/11/2026 ya no se escribe en Google Docs):
      - Textos sueltos: Edit con un trozo único del fichero. No se borra lo que hay: se amplía.
      - Ficha nueva: copiar la estructura de una ficha existente de "Parte especulativa" (título `###`,
        tabla de 12 filas `| **Etiqueta** | valor |` y los cuatro párrafos **Tesis de Cava**, **Niveles de
        Cava**, **Riesgos** y **Notas propias**) y pegarla al final de esa parte, antes de "## Descartados".
      - Actualizar la cabecera: "Versión del <sábado>" y el último jueves del rango de vídeos.
      - **Releer el fichero** y comprobar el texto. Subirlo al Master Brain con
        `~/.claude/nlm-upsert.sh "<ruta>"` y decir a David qué ha cambiado.
      - *Hasta el 03/11 se escribía en Google Docs (receta de `read_doc`, `replaceAllText` y tabla de 12×2):
        queda en el historial de git de RepositorioCodigo.*

## Por qué el resumen lo escribe Claude y no un script

Resumir es criterio: qué es relevante, qué cita lo prueba. Por eso no hay "gate" automático que diga
que el resumen está bien. Las citas con minuto son lo que permite a David comprobar cualquier punto en
diez segundos: son el ancla externa.
