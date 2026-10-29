"""Vídeos de la semana de José Luis Cava y HOPLA Finance, con su transcripción.

A partir del sábado calcula la semana (lunes a viernes, hora de España),
busca en la pestaña Vídeos de cada canal (los shorts quedan fuera) y guarda
la transcripción de cada vídeo con el minuto delante de cada frase.

Uso:
    python videos.py                  # sábado de esta semana (o el último)
    python videos.py 2026-10-31
    python videos.py 2026-10-31 --carpeta "<ruta>"
"""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from youtube_transcript_api import YouTubeTranscriptApi

MADRID = ZoneInfo("Europe/Madrid")
BASE = Path("~/Desktop/cartera/analisis semanal").expanduser()

# Feed de la pestaña Vídeos: playlist "UULF" + el id del canal sin "UC".
CANALES = [
    ("José Luis Cava", "UCvCCLJkQpRg0NdT3zNcI08A"),
    ("HOPLA Finance", "UC6cpU68F1BiwwXoAC3sgcGQ"),
]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def videos_del_canal(canal_id):
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id=UULF{canal_id[2:]}"
    xml = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text
    for e in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", e).group(1)
        titulo = re.search(r"<title>(.*?)</title>", e).group(1)
        titulo = titulo.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
        pub = dt.datetime.fromisoformat(re.search(r"<published>(.*?)</published>", e).group(1)).astimezone(MADRID)
        yield vid, titulo, pub


def minuto(seg):
    seg = int(seg)
    return f"{seg // 3600}:{seg % 3600 // 60:02d}:{seg % 60:02d}" if seg >= 3600 else f"{seg // 60:02d}:{seg % 60:02d}"


def transcripcion(vid):
    api = YouTubeTranscriptApi()
    try:
        t = api.fetch(vid, languages=["es", "es-ES", "es-419"])
    except Exception:
        lista = api.list(vid)
        t = next(iter(lista)).fetch()
    return [(s.start, s.text.replace("\n", " ")) for s in t.snippets]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sabado", nargs="?")
    ap.add_argument("--carpeta", help="Carpeta del informe (por defecto la del sábado en cartera)")
    a = ap.parse_args()
    hoy = dt.datetime.now(MADRID).date()
    sabado = dt.date.fromisoformat(a.sabado) if a.sabado else hoy - dt.timedelta(days=(hoy.weekday() - 5) % 7)
    if sabado.weekday() != 5:
        sys.exit(f"{sabado} no es sábado.")
    lunes, viernes = sabado - dt.timedelta(days=5), sabado - dt.timedelta(days=1)

    carpeta = Path(a.carpeta) if a.carpeta else BASE / f"informe semanal {sabado.strftime('%d-%m-%Y')}"
    if not carpeta.exists():
        sys.exit(f"No existe la carpeta {carpeta}. La crea David.")
    salida = carpeta / "transcripciones"
    salida.mkdir(exist_ok=True)

    print(f"Semana: lunes {lunes:%d/%m/%Y} a viernes {viernes:%d/%m/%Y} (hora de España)")
    if hoy <= viernes:
        print(f"AVISO: la semana no ha terminado (hoy es {hoy:%d/%m/%Y}); pueden faltar vídeos.")
    indice = []
    for canal, cid in CANALES:
        encontrados = sorted((v for v in videos_del_canal(cid) if lunes <= v[2].date() <= viernes), key=lambda v: v[2])
        if not encontrados:
            print(f"\n{canal}: sin vídeos esta semana.")
        for vid, titulo, pub in encontrados:
            dia = f"{DIAS[pub.weekday()]} {pub:%d/%m}"
            fich = salida / f"{pub:%Y-%m-%d}_{'cava' if 'Cava' in canal else 'hopla'}_{vid}.txt"
            try:
                frases = transcripcion(vid)
                cab = f"{canal} — {dia} — {titulo}\nhttps://www.youtube.com/watch?v={vid}\n\n"
                fich.write_text(cab + "\n".join(f"[{minuto(s)}] {x}" for s, x in frases))
                estado = f"{len(frases)} frases, dura {minuto(frases[-1][0])}"
            except Exception as e:
                fich, estado = None, f"SIN TRANSCRIPCIÓN ({type(e).__name__})"
            print(f"\n{canal} · {dia} · {titulo}\n  {estado}" + (f"\n  {fich}" if fich else ""))
            indice.append(dict(canal=canal, dia=dia, fecha=pub.isoformat(), titulo=titulo,
                               url=f"https://www.youtube.com/watch?v={vid}",
                               transcripcion=str(fich) if fich else None, estado=estado))
    (salida / "indice.json").write_text(json.dumps(dict(lunes=str(lunes), viernes=str(viernes), videos=indice),
                                                   ensure_ascii=False, indent=2))
    print(f"\nÍndice: {salida / 'indice.json'}")


if __name__ == "__main__":
    main()
