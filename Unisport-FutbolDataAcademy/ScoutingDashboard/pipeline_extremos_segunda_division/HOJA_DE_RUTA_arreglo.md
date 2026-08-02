# Hoja de ruta — arreglo del Scouting Dashboard

> Aplicar la metodología de proyectos de datos (`CLAUDE.md`, fases 3-6) sobre el pipeline
> de extremos, **en orden de ejecución**. David implementa; la metodología pregunta.
> Diagnóstico medido el 16/07 y reconfirmado en el código el 23/07: el modelo es **circular**.
>
> Marca `[x]` según avanzas. Cada tarea dice **dónde** está y **qué pregunta de la checklist
> la caza** — no la solución.

---

## Decisión 0 — qué sale de este pipeline

**DECIDIDO (02/08): no hay modelo, y tampoco hay índice único. Son PERFILES.**

Cada extremo recibe **tres notas** —regateador, finalizador, creador— sumando sus columnas
ponderadas (positivas suman, negativas restan). Con esas tres notas se le cuelga la etiqueta,
y puede llevar más de una: *"este es regateador"*, *"este es regateador y creador"*.

Lo decide David; el código solo etiqueta según sus reglas. No hay nada que aprenda de los datos.

- [x] **El ML sale del proyecto (02/08).** Y la razón no es técnica: preguntado para qué quería
      aplicar ML, David respondió **"aprender a hacerlo yo"**. Aprender sobre 84 filas —con un
      test de ~17— enseña a ejecutar los pasos y a interpretar números que no significan nada.
      Va como **proyecto aparte, sin cerrar**: candidato, un **xG propio con StatsBomb open data**
      (target real "¿fue gol?", volumen de sobra, y benchmark público contra el que compararse).

### Por qué se cayó la opción C — la pregunta (b), CERRADA el 02/08

*Si la frontera se la ponemos nosotros, ¿no le estamos marcando al modelo el camino de lo que
tiene que decir?* **Sí.** Y por dos vías que el Destilado nombra literalmente:

1. **El 0.682 nunca fue "un modelo flojo pero honrado".**
   > *«La circularidad no siempre se ve como accuracy inflada — si el target es un AND de dos
   > umbrales (una región rectangular) y usas un modelo lineal, saldrá una accuracy mediocre
   > que parece honesta. El árbol lo delata igual.»*

   El `DecisionTree(max_depth=2)` al **1.000** era el **detector**, no un modelo mejor.

2. **Sacar las dos columnas de X —el núcleo mismo de C— no arreglaba nada: lo disfrazaba.**
   Sin ellas, el modelo reconstruye desde otras columnas dos métricas **que ya están medidas
   para los 84**. No infiere nada oculto → es **medición, no predicción**. Un modelo se gana el
   sueldo prediciendo lo que **no puedes observar**, y aquí estaba todo observado.

> [!contradicción] Decisión 0 anterior (23/07) — sustituida, se conserva como historia
> Decía: **«DECIDIDO (23/07): el ML se queda. Descartada la opción "índice sin ML". Con ML, la
> pregunta que queda no es el algoritmo, es el target.»** Con las opciones marcadas así:
> - ~~A · Índice de percentiles sin ML~~ — descartado por David.
> - ~~B · ML con target externo real~~ — descartado: `soccerdata` no cubre Segunda, no hay dos
>   temporadas para construir el target externo.
> - **C · ML con el mismo target inventado, saneado** ← ELEGIDO. Sacar de X las 2 features que
>   definen el target, correr baseline, mirar coeficientes.
>
> **Por qué era fácil equivocarse:** C parecía la opción prudente —conservaba el ML sin negar el
> diagnóstico de circularidad— y su remedio (prohibir las dos columnas en X) suena a corrección
> de libro. El fallo estaba un nivel más abajo: no en **cómo** se entrenaba, sino en que la
> pregunta *"¿es generador de peligro?"* ya tenía la respuesta escrita en las columnas. Ninguna
> higiene de features arregla eso.
>
> El **"techo de C"** que se anotó aquí el 23/07 —(1) el target sigue sesgado por minutos aunque
> saques la feature; (2) la accuracy va a bajar hacia el baseline y eso es lo correcto— sigue
> siendo cierto como diagnóstico. Simplemente ya no aplica: no hay modelo cuya accuracy mirar.

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

## 2 · `limpieza_de_datos.py`  ✅ HECHO

- [x] **Sin cambios.** Una sola fuente → Fase 2 (merge / entity resolution) no aplica. Formateos
      correctos. No arreglar de más.

## 3 · `contextualización_y_filtrado.py`  ✅ HECHO (25/07 – 31/07)

*(Antes `filtrado_jugadores.py` + la mitad de `contextualizacion_y_frontera.py`.)*

- [x] **`valor_mercado` numérico preservado.** El `fmt_valor` escribe en columna nueva
      `valor_mercado_fmt`; `valor_mercado` se queda numérico → ya se puede correr
      `corr(mi_ranking, valor_mercado)`.
      - *Pendiente aguas abajo (apartado 6):* `dashboard_extremos.py` lee `valor_mercado` esperando
        el string → apuntarlo a `valor_mercado_fmt`, o mostrará el número crudo.
- [x] **Filtro de minutos `>= 450`** (≈5 partidos), **criterio de ojeador declarado** — la distribución
      es lisa, no hay salto natural. Barrido de sensibilidad impreso en el pipeline. **109 → 84.**
      - *Pendiente aguas abajo (Fase 6):* enseñar los minutos al lado del percentil. El filtro es
        binario (449 fuera, 451 dentro y tratado igual que uno de 3.000) y no cierra la fiabilidad.
- [x] **Normalización por 90** de 15 conteos, `/minutos*90`, sin pisar el conteo crudo.
- [x] **Filtros de mercado FUERA (31/07).** Contrato y `valor < 500k` eran resto del marco Zamora:
      **medido, solo 2 de los 21 positivos sobrevivían** (mediana 790k, máximo 23M). Truncaban justo
      el eje donde vive la discrepancia, que **es el producto**. Son Fase 6 (sliders), no Fase 2.
- [x] **Opción A — una sola población.** Todo aguas abajo son los 84.

## 4 · `frontera_metricas_generacion_de_peligro.py` → **A REESCRIBIR como script de perfiles**

El script deja de fabricar una etiqueta. **Los barridos se conservan** —el andamio de exploración
no se borra— porque son el registro de cómo se eligieron las métricas. Lo que sale es el `np.where`
y la columna `GeneradorDePeligro`. Probablemente también cambie de nombre.

- [x] **Columnas de los tres perfiles CERRADAS (02/08).** David las define, Claude verifica solo lo
      objetivo: que la columna exista, el solape medido, el sesgo con minutos y la muestra que
      respalda cada porcentaje.

      | Perfil | Columnas |
      |---|---|
      | **Regateador** | `regates_intentados_por_90` (+), `porcentaje_regates_exitosos` (+), `perdidas_de_balon_por_90` (−) |
      | **Finalizador** | `tiros_totales_por_90` (+), `porcentaje_tiros_a_puerta` (+), `goles_por_90` (+), `grandes_ocasiones_falladas_por_90` (−), `perdidas_de_balon_por_90` (−) |
      | **Creador** | `pases_clave_por_90` (+), `porcentaje_pases_clave` (+), `grandes_ocasiones_creadas_por_90` (+), `asistencias_por_90` (+), `perdidas_de_balon_por_90` (−) |

- [x] **Regla de columnas (02/08).** De cada métrica entra la `_por_90`, **nunca el conteo crudo**
      (0.61–0.93 con minutos). Los porcentajes entran tal cual, ya son tasas. **`minutos_jugados`
      no puntúa**: su sitio es el filtro de 450 y luego ir al lado del número en el dashboard. Los
      conteos crudos sobreviven **solo como muestra** del porcentaje que respaldan.
- [x] **El "eslabón del medio" se corta.** Cuando tres columnas están unidas por
      `producto = volumen × %`, la de en medio es redundante: fuera `regates_exitosos_por_90` (0.94
      con intentos) y `tiros_a_puerta_por_90` (0.81 / 0.72 / 0.70 con las otras tres).
      **En el creador, `pases_clave_por_90` se mantiene por decisión declarada de David** pese al
      0.76: al pasar a percentiles el producto **no** es reconstruible desde sus factores, y premia
      específicamente a quien combina volumen y calidad en vez de dejar que uno compense al otro.
- [ ] **Crear las tres columnas nuevas:** `regates_intentados_por_90`, `porcentaje_tiros_a_puerta`
      (`tiros_a_puerta / tiros_totales`), `porcentaje_pases_clave` (`pases_clave / pases_totales`).
- [ ] **Pasar cada columna a percentil ANTES de ponderar.** Sin esto los pesos no pintan nada:
      `pases_totales` va de 57 a 1927 y `goles_por_90` de 0 a 0,7 — la de mayor rango decide sola.
      - *Caza (regla transversal 4):* percentil antes que z-score en scouting.
- [ ] **Los pesos.** 100 puntos dentro de cada perfil, **mismo total en los tres**: como las tres
      notas se comparan entre sí para colgar la etiqueta, un perfil que reparta más peso daría notas
      más altas por construcción y saldrían todos de ese perfil.
      - *Caza (Fase 5):* si no hay modelo, ¿cómo he elegido las métricas y con qué pesos? Sin target
        no hay feature importance: la elección **es** el análisis, y hay que escribir el porqué.
- [ ] **El corte de muestra de los tres porcentajes.** El `regates_intentados >= 60` se eligió sobre
      una subpoblación ya filtrada; **sobre los 84 se lleva 51**. Hay que redecidirlo, y hacer el
      equivalente para tiros y para pases.
      - *Medido (02/08):* **Diego Bri lidera dos porcentajes distintos con muestra corta** — 70,6% de
        tiros a puerta sobre **17 tiros**, y 61,5% de regates sobre 26. El filtro de 450 no lo tapa.
      - *Caza (Fase 5):* ¿todas mis estimaciones tienen la misma fiabilidad?
- [ ] **El umbral de etiqueta.** A partir de qué nota un extremo "es" regateador, y si puede llevar dos.
      - *Caza (regla transversal 1):* todo umbral se declara, y se sabe si sale de la distribución o de ti.

### Hallazgos medidos el 02/08 sobre los 84

- **Cadena anidada CONFIRMADA, cero excepciones en los 84:**
  `grandes_ocasiones_creadas ⊆ pases_clave ⊆ pases_ultimo_tercio ⊆ pases_totales`.
  No son cuatro métricas: es la misma acción contada con el listón cada vez más alto.
- `pases_totales_por_90 ~ pases_acertados_por_90` = **0.97**, la correlación más alta del dataset.
- Las columnas nuevas salen limpias de sesgo: `regates_intentados_por_90` **−0.03** con minutos,
  `porcentaje_tiros_a_puerta` **0.01**, `porcentaje_pases_clave` 0.28.

> [!contradicción] El target binario (30/07 – 02/08) — sustituido, se conserva como historia
> ```python
> GeneradorDePeligro = (pases_clave_por_90 > 1.59) AND (porcentaje_regates_exitosos > 40.68)
> ```
> Partía los 84 en **21 positivos / 63 negativos**. Los dos umbrales salieron de **barrido con
> nombres** sobre distribución lisa (no había salto natural) y se fijaron **como número, no como
> `.quantile()`** — un umbral que se recalcula se mueve en silencio al cambiar los datos.
>
> **Por qué era fácil equivocarse:** el trabajo de elegir esos umbrales fue riguroso —barrido,
> nombres, muestra mínima de 60 intentos, todo declarado— y precisamente por eso costó ver que el
> problema no era **dónde** se cortaba, sino **que se cortara**. Un umbral impecablemente elegido
> sigue siendo una frontera que dibujas tú y que después le pides al modelo que adivine.
>
> **`1.59` y `40.68` dejan de usarse.** De aquel trabajo sobreviven dos cosas: el corte de muestra
> `regates_intentados >= 60` (era fiabilidad, nunca fue target) y **la elección de qué métricas
> mirar** — el % de regates y los pases clave siguen en los perfiles.

## 5 · `modelado_de_datos.py` → **SE SUSTITUYE, no se arregla**

Ya no modela nada, así que ni el nombre se queda: pasa a ser algo como
`clasificacion_por_perfiles.py`. Hoy está **roto a propósito** (`FileNotFoundError`) porque los CSV
huérfanos que leía se neutralizaron como `HUERFANO_*.bak` — antes corría **sin error** sobre datos
muertos, que es el fallo silencioso que había que convertir en ruidoso.

- [ ] **Escribirlo de cero:** leer `dataset_extremos_filtrado.csv` (los 84), crear las tres columnas
      nuevas, pasar todo a percentil, aplicar los pesos, sacar las tres notas y colgar la etiqueta.
- [ ] **Validar por NOMBRES, no por número.** Un sistema de perfiles no tiene accuracy: no predice,
      no puede equivocarse. Su única auditoría es que los umbrales estén declarados y que los
      jugadores que caen en cada perfil sean gente que, viendo Segunda, dirías que se parece.
- [ ] **Correr el baseline de dominio**, que ahora sí se puede: `corr(nota, valor_mercado)`. ~0.9 →
      eres un detector de precio con pasos extra; ~0.3 → dices algo que el mercado no dice. **Los
      altos en tu nota y baratos en Transfermarkt son la shortlist.** Llevas desde el 25/07 con el
      gate montado (`valor_mercado` numérico) y sin haberlo usado nunca.

> [!contradicción] Lista de tareas anterior del apartado 5 — sustituida, se conserva como historia
> Decía: sacar de X `pases_clave` y `porcentaje_regates_exitosos` (el núcleo de C); decidir sobre
> `minutos_jugados` en X; `DummyClassifier` antes de entrenar (medido: 0.64, y el modelo 0.68 =
> empate de un jugador con `n_test≈22`); accuracy en train **y** test para distinguir underfitting;
> mirar los coeficientes de la LogReg; declarar el umbral `Puntuacion >= 4`; y esperar que la
> accuracy bajara hacia el baseline como diagnóstico correcto.
>
> Todo eso era buena higiene **para un modelo que ya no existe**. Se conserva porque es la lista
> exacta que hay que correr el día que se haga ML de verdad, en el proyecto aparte con target real.

## 6 · `dashboard_extremos.py`

- [ ] **Reapuntar `BASE` y `df_ref`** al CSV que salga del apartado 5.
- [ ] **`valor_mercado` → `valor_mercado_fmt`** (`:22` del script viejo lo dejó numérico a propósito).
- [ ] **El Tab 3 enseña "resultados del modelo ML"** y ya no habrá modelo. Rehacerlo sobre las tres
      notas de perfil.
- [ ] **El modal confiesa el sesgo** (`:272-284`): lista "Minutos jugados" como criterio positivo.
      Actualizar qué se le dice al club ahora que los minutos **no puntúan**.
- [ ] **Radar y notas con la misma vara.** `calcular_percentiles` normaliza por 90 (`:307-311`);
      que el radar y los perfiles rankeen igual.
- [ ] **Umbrales de color 5.6 y 4** (`:264-267`) sin declarar.
- [ ] **Bug latente** ahí mismo: `umbrales_puntuacion` da `UnboundLocalError` si `Puntuacion < 4` y
      no-NaN. Hoy no revienta solo por el filtro previo. Añadir rama `else`.
- [ ] **"Minutos al lado del número"** en el listado general (tab 1) y en el radar. En la ficha
      individual ya está (`:511`).

---

## El hilo que lo cose

El **sesgo de minutos** atraviesa el pipeline entero: no se cazaba en (1), entraba crudo en (4), se
horneaba en (5) y salía a la cara del club en (6) —el modal y la contradicción del radar—.

A 02/08 está cortado en origen: los conteos crudos no entran en ningún perfil y `minutos_jugados`
no puntúa. Lo que queda vivo del mismo problema es su **hermano pequeño**, el de la muestra: los
porcentajes premian a quien jugó poco dentro del pool, y eso el filtro de 450 no lo tapa.
