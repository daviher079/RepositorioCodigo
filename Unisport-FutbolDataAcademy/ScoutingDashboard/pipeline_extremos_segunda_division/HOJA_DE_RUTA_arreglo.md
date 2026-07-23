# Hoja de ruta — arreglo del Scouting Dashboard

> Aplicar la metodología de proyectos de datos (`CLAUDE.md`, fases 3-6) sobre el pipeline
> de extremos, **en orden de ejecución**. David implementa; la metodología pregunta.
> Diagnóstico medido el 16/07 y reconfirmado en el código el 23/07: el modelo es **circular**.
>
> Marca `[x]` según avanzas. Cada tarea dice **dónde** está y **qué pregunta de la checklist
> la caza** — no la solución.

---

## Decisión 0 — antes de tocar una línea (es la raíz, decide el resto)

**DECIDIDO (23/07): el ML se queda.** La primera versión tiene ML y esta también. Descartada la
opción "índice sin ML". Con ML, la pregunta que queda **no es el algoritmo, es el target** — porque
el problema nunca fue el ML, fue el target inventado con `np.where` a partir de sus propias features.

- [x] ~~A · Índice de percentiles sin ML~~ — **descartado por David.**
- [x] ~~B · ML con target externo real~~ — **descartado (23/07): soccerdata no cubre Segunda; no hay
      datos de dos temporadas para construir el target externo.**
- [x] **C · ML con el mismo target inventado, saneado** ← **ELEGIDO (23/07).** Sacas de X las 2
      features que definen el target, corres baseline, miras coeficientes.

### El techo de C — leer antes de implementar el bloque 5

C deja de ser circular estricto, pero tiene dos trampas que la metodología caza:

1. **El target sigue sesgado por minutos aunque saques la feature.** El target es `pases_clave > 6`
   **crudo** → premia a quien juega mucho. Y `minutos_jugados` sigue en X (`modelado:33`). El modelo
   usará `minutos_jugados` para reconstruir un target que es, en el fondo, minutos. **Decidir:**
   (a) ¿el `pases_clave` del target va crudo o por 90? · (b) ¿`minutos_jugados` se queda en X?
2. **La accuracy va a BAJAR, y es lo correcto.** Sin las 2 features circulares, las demás
   probablemente no predigan bien tu regla → caes del 0.68 hacia el baseline 0.64. **No es un fallo:**
   es el diagnóstico honesto de que el target no era predecible sin trampa. Es la historia vendible
   ("quité la circularidad y el modelo perdió la información falsa que lo inflaba").

---

## 1 · `exploracion_inicial.py`  ✅ HECHO (23/07)

- [x] **Matriz de correlación añadida.** Dos lecturas, ambas corridas e interpretadas:
      - **A — sesgo de minutos** (`corrwith(minutos)` + `.diff()`): casi TODOS los conteos mienten
        (0.61–0.93). Salto natural limpísimo, hueco de 0.34 en la zona 0.28–0.61 (vacía). Solo los
        dos porcentajes se salvan (0.08 y 0.18 = el control). El 0.7 fijo habría dejado escapar goles
        (0.66) y asistencias (0.68) → por eso el salto gana. Llevado a la metodología (Fase 3) como cicatriz.
      - **B — redundancia** (heatmap `correlacion_heatmap.png`): pares idénticos (`pases_totales` =
        `pases_acertados`; `valoracion_total` = `conteo_valoraciones`); bloque de "juego de pase" todo
        pegado (0.85–0.97). Los dos % son las únicas columnas independientes.
      - **Conclusión para el 4:** todo conteo → normalizar por 90 sin excepción; los % ya están limpios.

## 2 · `limpieza_de_datos.py`

- [x] **Sin cambios.** Una sola fuente → Fase 2 (merge / entity resolution) no aplica. Formateos
      correctos. No arreglar de más.

## 3 · `filtrado_jugadores.py`

- [ ] **`valor_mercado` se convierte a string** `"775.000 €"` (`:94`). Rompe el baseline de
      dominio. Guardar una copia numérica para poder correr `corr(mi_ranking, valor_mercado)`.
      - *Caza (Fase 5):* ¿bate mi resultado a lo que el club ya tiene gratis? La discrepancia es el producto.
- [ ] **`minutos > 200`** (`:85`) es un umbral de muestra bajo (hay fichas de 286 min). Decidir si
      es defendible, y enseñar los minutos al lado del percentil en vez de tratar el filtro como binario.
      - *Caza (Fase 5):* ¿todas mis estimaciones tienen la misma fiabilidad?

## 4 · `contextualizacion_y_frontera.py`  ← donde nace el daño

- [ ] **Target `np.where` se mantiene** (C), pero **declarar los umbrales 6 y 43.0** (`:17`): de dónde
      salen, distribución o criterio de ojeador.
      - *Caza (regla transversal 1):* todo umbral se declara, pero se sabe cuál es.
- [ ] **Decidir el `pases_clave` del target** (`:17`): ¿crudo o por 90? Si crudo, el target sigue
      sesgado por minutos aunque saques la feature de X (ver *techo de C*, trampa 1).
      - *Caza (Fase 4):* ¿he revisado también las columnas que definen el target?

## 5 · `modelado_de_datos.py`

- [ ] **Sacar de X `pases_clave` y `porcentaje_regates_exitosos`** (`:34-35`) — las que definen el
      target. Es el núcleo de C.
- [ ] **Decidir sobre `minutos_jugados` en X** (`:33`): si el target sigue sesgado por minutos, esta
      feature es el nuevo atajo circular (trampa 1).
- [ ] **Baseline `DummyClassifier` ANTES de entrenar** (medido: 0.64; el modelo actual 0.68 = empata).
      - *Caza (Fase 5):* comparar en aciertos absolutos, no en %. Con n_test≈22, 0.68 vs 0.64 = 1 jugador.
- [ ] **Medir accuracy en train Y test** (`:63`), no solo test → distinguir underfitting.
- [ ] **Mirar los coeficientes** de la LogReg (su feature importance).
- [ ] **Umbral `Puntuacion >= 4`** (`:103`) sin declarar.
- [ ] **Esperar que la accuracy baje hacia el baseline** — es el diagnóstico correcto, no un fallo
      (ver *techo de C*, trampa 2).

## 6 · `dashboard_extremos.py`

- [ ] **Radar y modelo se contradicen.** `calcular_percentiles` normaliza por 90 (`:307-311`); el
      modelo puntúa con `pases_clave` crudo. Un jugador puede salir alto en Puntuación y bajo en el
      radar. Que rankeen con la misma vara.
- [ ] **El modal confiesa el sesgo** (`:272-284`): lista "Minutos jugados" como criterio positivo.
      Actualizar qué se le dice al club cuando cambie el criterio.
- [ ] **Umbrales de color 5.6 y 4** (`:264-267`) sin declarar.
- [ ] **Bug latente** ahí mismo: `umbrales_puntuacion` da `UnboundLocalError` si `Puntuacion < 4` y
      no-NaN. Hoy no revienta solo por el filtro previo. Añadir rama `else`.
- [ ] **Llevar "minutos al lado del número"** al listado general (tab 1) y al radar. En la ficha
      individual ya está (`:511`).

---

## El hilo que lo cose

El **sesgo de minutos** atraviesa cinco de los seis scripts: no se caza en (1), entra crudo en (4),
se hornea en (5), y sale a la cara del club en (6) —el modal y la contradicción del radar—.
Arreglar `pases_clave` de raíz en (4) desactiva medio dashboard de golpe.
