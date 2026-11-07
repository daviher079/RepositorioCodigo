"""Escribe las conclusiones de Claude en los cuatro apartados vacíos del Word del análisis semanal.

Uso:
    python conclusiones.py "<ruta del .docx>" "<ruta del .json>"

El JSON es un objeto con las cuatro claves (el texto exacto de cada título de apartado):
    "Conclusión del lado de la Fed (FED + MOVE + HYG)"
    "El Russell, entre los dos lados"
    "Conclusión del lado de la bolsa (SPY + VIX + SPY/GLD + KOSPI)"
    "Conclusión final"
Cada valor es una lista de párrafos (texto plano). Antes de escribir guarda una copia .bak del Word.
Si un apartado ya tiene texto (David lo ha escrito), para sin tocar nada.
"""
import json
import shutil
import sys

import docx

APARTADOS = ["Conclusión del lado de la Fed (FED + MOVE + HYG)", "El Russell, entre los dos lados",
             "Conclusión del lado de la bolsa (SPY + VIX + SPY/GLD + KOSPI)", "Conclusión final"]


def main(ruta_docx, ruta_json):
    with open(ruta_json, encoding="utf-8") as f:
        textos = json.load(f)
    faltan = [a for a in APARTADOS if a not in textos]
    assert not faltan, f"Faltan apartados en el JSON: {faltan}"

    doc = docx.Document(ruta_docx)
    ps = doc.paragraphs
    huecos = {}
    for i, p in enumerate(ps):
        if p.text.strip() in APARTADOS:
            assert i + 1 < len(ps), f"El apartado '{p.text}' no tiene párrafo detrás"
            siguiente = ps[i + 1]
            if siguiente.text.strip():
                sys.exit(f"El apartado '{p.text}' ya tiene texto: no se toca nada.")
            huecos[p.text.strip()] = siguiente
    assert set(huecos) == set(APARTADOS), f"No se encuentran en el Word: {set(APARTADOS) - set(huecos)}"

    shutil.copy2(ruta_docx, ruta_docx + ".bak")
    for apartado in APARTADOS:
        parrafos = textos[apartado]
        hueco = huecos[apartado]
        hueco.text = parrafos[0]
        ancla = hueco
        for texto in parrafos[1:]:
            nuevo = ancla.insert_paragraph_before("")  # se crea delante y se mueve detrás del ancla
            ancla._p.addnext(nuevo._p)
            nuevo.text = texto
            nuevo.style = hueco.style
            ancla = nuevo
    doc.save(ruta_docx)

    comprobado = docx.Document(ruta_docx)
    todo = "\n".join(p.text for p in comprobado.paragraphs)
    for apartado in APARTADOS:
        for texto in textos[apartado]:
            assert texto in todo, f"No ha quedado escrito en '{apartado}': {texto[:60]}…"
    print(f"Conclusiones escritas en {ruta_docx} (copia en .bak)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
