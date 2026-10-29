"""Pasa el resumen de Cava y Hopla (Markdown sencillo) a Word.

Entiende: # título, ## canal / resumen de la semana, ### vídeo, líneas "- " como
viñetas, **negrita** dentro del texto y párrafos normales.

Uso:
    python informe_docx.py <resumen.md> <salida.docx>
"""

import re
import sys

from docx import Document
from docx.shared import Pt, RGBColor

AZUL_OSCURO = RGBColor(0x1F, 0x37, 0x63)
AZUL = RGBColor(0x2F, 0x54, 0x96)


def texto_con_negritas(p, texto):
    for i, trozo in enumerate(re.split(r"\*\*(.+?)\*\*", texto)):
        if trozo:
            p.add_run(trozo).bold = bool(i % 2)


def main(origen, destino):
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10)
    for linea in open(origen, encoding="utf-8").read().splitlines():
        if not linea.strip():
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", linea)
        if m:
            nivel = len(m.group(1)) - 1
            h = doc.add_heading(m.group(2), level=nivel)
            for r in h.runs:
                r.font.name = "Calibri"
                r.font.color.rgb = AZUL_OSCURO if nivel <= 1 else AZUL
        elif linea.lstrip().startswith("- "):
            p = doc.add_paragraph()
            p.add_run("• ")
            texto_con_negritas(p, linea.lstrip()[2:])
        else:
            texto_con_negritas(doc.add_paragraph(), linea)
    doc.save(destino)
    print(f"Guardado: {destino}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
