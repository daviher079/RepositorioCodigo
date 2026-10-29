---
name: analisis-semanal-cava-hopla
description: Segundo paso del sábado de trading de David. Busca los vídeos largos de lunes a viernes de José Luis Cava y HOPLA Finance, saca su transcripción con minuto y escribe en Word un resumen de los puntos relevantes de cada vídeo y de la semana. Se lanza DESPUÉS de que David haya escrito sus conclusiones de /analisis-situacion-semanal. Activar con /analisis-semanal-cava-hopla [AAAA-MM-DD del sábado].
---

# Skill: /analisis-semanal-cava-hopla

Parte de la **Especificación — Análisis semanal automatizado** (Google Drive,
`1npxghc2JILV_VT534GFiZtEbDYzFNx9wI5kKOAHnzOs`, sección 2).

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

## Por qué el resumen lo escribe Claude y no un script

Resumir es criterio: qué es relevante, qué cita lo prueba. Por eso no hay "gate" automático que diga
que el resumen está bien. Las citas con minuto son lo que permite a David comprobar cualquier punto en
diez segundos: son el ancla externa.
