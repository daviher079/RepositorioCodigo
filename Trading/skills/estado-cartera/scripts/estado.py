"""/estado-cartera — el examen del Playbook (definido con David el 04/11/2026).

Uso:
    python estado.py                      # sábado más reciente, cartera + banquillo
    python estado.py --sabado 2026-10-31  # un sábado concreto (cierre del viernes anterior)
    python estado.py --nuevo XLU          # examen de un candidato nuevo (+ historia para zona y stop)
    python estado.py --nuevo AWK:empresa  # empresa: añade el filtro 4 (resultados)

Lee del vault:
    trading-plan.md        tabla "Parámetros del examen"
    trading-posiciones.md  tabla "Abiertas"
Escribe:
    trading/sabados/estado-AAAA-MM-DD.md   (solo el modo sábado)

El script INFORMA: no compra, no vende y no cambia el Plan. Las reglas salen de
trading-playbook.md; donde el Playbook no da un número, se enseña el dato y se
marca para que lo confirme David (no se inventan cortes).
"""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

VAULT = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/Downloads/Obsidian/david_brain"
TRADING = VAULT / "02_Wiki/projects/trading"
FILTRO = Path.home() / "Desktop/Mis Cosas/RepositorioCodigo/Trading/filtro/filtro_candidatos.py"
VENV_PY = Path.home() / "Desktop/Mis Cosas/RepositorioCodigo/venv/bin/python"

CARTERA_TOTAL = 10_000          # valor de partida de la simulación (se suma lo realizado si hay posiciones cerradas)
TOPE_RIESGO = 0.01              # Playbook, sección 6
RIESGO_ABIERTO_MAX = 0.04       # Playbook, sección 6
SEMANAS_AVISO = 5               # filtro de candidatos, 03/11
CORR_MAX = 0.8                  # filtro 3
LAT_PEND, LAT_SEMANAS = 2.0, 4  # lateral, 04/11
FIN_LAT_VOL = 1.25              # fin del lateral, 04/11
RATIO_MIN = 2.0                 # 1:2 hasta 20 operaciones


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------

def _get(url):
    out = subprocess.run(["curl", "-s", "-m", "30", "-A", "Mozilla/5.0", url],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def semanal(ticker, viernes, desde=1104537600):
    """Velas semanales (viernes) hasta `viernes` incluido, agrupadas desde el diario."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={desde}&period2=9999999999&interval=1d")
    r = _get(url)["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    d = pd.DataFrame({k: q[k.lower()] for k in ["Open", "High", "Low", "Close", "Volume"]},
                     index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna(subset=["Close"])
    w = d.resample("W-FRI").agg({"Open": "first", "High": "max", "Low": "min",
                                 "Close": "last", "Volume": "sum"}).dropna(subset=["Close"])
    return w[w.index <= pd.Timestamp(viernes)]


def dbnomics(serie):
    d = _get(f"https://api.db.nomics.world/v22/series/{serie}?observations=1")
    doc = d["series"]["docs"][0]
    dias = doc.get("period_start_day") or doc["period"]   # las semanales vienen como "1998-W53"
    s = pd.Series({pd.Timestamp(p): v for p, v in zip(dias, doc["value"])
                   if isinstance(v, (int, float))}).sort_index()
    return s


def ema(s):
    return s.ewm(span=50, adjust=False).mean()


# ---------------------------------------------------------------------------
# Lectura del vault
# ---------------------------------------------------------------------------

def tabla_md(texto, titulo):
    """Filas de la primera tabla markdown que aparece después de `titulo`."""
    i = texto.index(titulo)
    filas = []
    for linea in texto[i:].splitlines()[1:]:
        if linea.startswith("|"):
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if set("".join(celdas)) <= set(":- "):
                continue
            filas.append(celdas)
        elif filas:
            break
    return filas[0], filas[1:]


def parametros():
    cab, filas = tabla_md((TRADING / "trading-plan.md").read_text(), "## Parámetros del examen")
    return [dict(zip(cab, f)) for f in filas]


def posiciones():
    cab, filas = tabla_md((TRADING / "trading-posiciones.md").read_text(), "## Abiertas")
    return [dict(zip(cab, f)) for f in filas if any(f)]


def zona(txt):
    if txt.startswith("≤"):
        return (0.0, float(txt[1:].replace(",", ".")))
    m = re.match(r"([\d.,]+)-([\d.,]+)", txt)
    return (float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))) if m else None


def stop_param(txt):
    if txt.startswith("nivel"):
        return ("nivel", float(txt.split()[1].replace(",", ".")))
    if txt.endswith("%"):
        return ("pct", float(txt[:-1].replace(",", ".")) / 100)
    return None


# ---------------------------------------------------------------------------
# Las reglas del Playbook
# ---------------------------------------------------------------------------

def lateral(w):
    """Sección 3: EMA ±2% en 13 semanas + banda de 26 semanas bajo su mediana, 4 semanas seguidas."""
    c = w.Close
    e = ema(c)
    pend = (e / e.shift(13) - 1).abs() * 100
    b26 = (c.rolling(26).max() / c.rolling(26).min() - 1) * 100
    med = b26.expanding(104).median()
    raw = ((pend <= LAT_PEND) & (b26 <= med)).fillna(False)
    ahora = bool(raw.iloc[-LAT_SEMANAS:].all())
    return ahora, round(pend.iloc[-1], 1), round(b26.iloc[-1], 1), round(med.iloc[-1], 1) if not np.isnan(med.iloc[-1]) else None


def fin_lateral(w):
    """Si la semana anterior estaba en lateral: ¿esta cierra fuera de la banda con 1,25x volumen?"""
    prev = w.iloc[:-1]
    if len(prev) < 130 or not lateral(prev)[0]:
        return None
    banda = prev.Close.iloc[-26:]
    vm = prev.Volume.iloc[-26:].mean()
    c, v = w.Close.iloc[-1], w.Volume.iloc[-1]
    if banda.min() <= c <= banda.max():
        return "sigue dentro de la banda"
    vr = v / vm if vm else float("nan")
    lado = "arriba" if c > banda.max() else "abajo"
    if vr >= FIN_LAT_VOL:
        return f"**rotura hacia {lado} con {vr:.2f}x volumen → fin del lateral**"
    return f"cierra fuera ({lado}) pero con {vr:.2f}x volumen (< {FIN_LAT_VOL}) → el lateral sigue"


def tendencia(w):
    e = ema(w.Close)
    return bool(w.Close.iloc[-1] > e.iloc[-1] and e.iloc[-1] > e.iloc[-2]), round((w.Close.iloc[-1] / e.iloc[-1] - 1) * 100, 1)


def estocastico(w):
    lo, hi = w.Low.iloc[-14:].min(), w.High.iloc[-14:].max()
    k = (w.Close.iloc[-1] - lo) / (hi - lo) * 100 if hi > lo else 50
    if k < 20:
        txt = "en la parte baja de su rango de 14 semanas: el retroceso ya ha recorrido casi todo el rango reciente"
    elif k > 80:
        txt = "en la parte alta de su rango de 14 semanas: viene de subir (en tendencia fuerte puede quedarse ahí meses; no es señal de venta)"
    else:
        txt = "en mitad de su rango de 14 semanas: sin lectura"
    return round(k), txt


def gatillo(w):
    """Sección 3: volumen < media de las semanas de caída anteriores, y cuerpo < mitad del rango o mecha inferior > cuerpo."""
    o, h, l, c, v = w.iloc[-1][["Open", "High", "Low", "Close", "Volume"]]
    cierres = w.Close
    caida = []
    for i in range(len(w) - 2, max(len(w) - 10, 0), -1):
        if cierres.iloc[i] < cierres.iloc[i - 1]:
            caida.append(w.Volume.iloc[i])
        else:
            break
    ref = np.mean(caida) if caida else w.Volume.iloc[-5:-1].mean()
    cuerpo, rango = abs(c - o), h - l
    mecha_inf = min(o, c) - l
    vol_ok = bool(v < ref) if ref else False
    pequeña = bool(rango > 0 and cuerpo < 0.5 * rango)
    mecha = bool(mecha_inf > cuerpo)
    hay = vol_ok and (pequeña or mecha)
    datos = (f"volumen {v / ref:.2f}x la media de la caída ({'menor' if vol_ok else 'no menor'}); "
             f"cuerpo {cuerpo / rango * 100 if rango else 0:.0f}% del rango; mecha inferior {'>' if mecha else '≤'} cuerpo")
    return hay, datos


def ratio(w, entrada, stop):
    maximo = w.High.iloc[-52:].max()   # siguiente resistencia: el máximo reciente (52 semanas), no uno de hace años
    riesgo = entrada - stop
    return (maximo - entrada) / riesgo if riesgo > 0 else float("nan"), maximo


def filtro_12(w, spy):
    df = pd.concat({"c": w.Close, "s": spy.Close}, axis=1).dropna()
    r = df.c / df.s
    pasa = (df.c > ema(df.c)) & (r > ema(r))
    n = 0
    for x in reversed(pasa.values):
        if x:
            n += 1
        else:
            break
    return bool(pasa.iloc[-1]), n


def correlacion(w, otros):
    ret = w.Close.pct_change().iloc[-104:]
    peor = (None, 0)
    for nombre, wo in otros.items():
        c = pd.concat([ret, wo.Close.pct_change().iloc[-104:]], axis=1).dropna().corr().iloc[0, 1]
        if c > peor[1]:
            peor = (nombre, c)
    return peor


def resultados_empresa(ticker):
    """Filtro 4: lo calcula filtro_candidatos.py; se copia su sección de resultados."""
    out = subprocess.run([str(VENV_PY), str(FILTRO), f"{ticker}:empresa"], capture_output=True, text=True).stdout
    i = out.find("## 4.")
    return out[i:].split("\n> Informa")[0].strip() if i >= 0 else "Resultados: sin datos (revisar a mano)"


def semaforo(viernes):
    """Sección 2. Devuelve color, lista de bloqueos y notas."""
    tnx = semanal("^TNX", viernes)
    hyg, iei = semanal("HYG", viernes), semanal("IEI", viernes)
    spy, gld = semanal("SPY", viernes), semanal("GLD", viernes)
    ks, vix = semanal("^KS11", viernes), semanal("^VIX", viernes)
    b = []
    bono = tnx.Close.iloc[-1]
    b.append(("Bono a 10 años por encima del 5,3%", bono > 5.3, f"{bono:.2f}%"))
    hi = (hyg.Close / iei.Close).dropna()
    hi_bajo = hi.iloc[-1] < ema(hi).iloc[-1]
    hi_min = hi.iloc[-1] <= hi.iloc[-53:-1].min()
    b.append(("HYG/IEI en nuevo mínimo por debajo de su EMA", hi_bajo and hi_min,
              f"{'bajo' if hi_bajo else 'sobre'} su EMA ({(hi.iloc[-1] / ema(hi).iloc[-1] - 1) * 100:+.1f}%); "
              f"{'en' if hi_min else 'no en'} mínimo de 52 semanas (definición de David, 04/11)"))
    sg = (spy.Close / gld.Close).dropna()
    dist = (sg / ema(sg) - 1) * 100
    b.append(("SPY/GLD 3 semanas por debajo del 5,2% de distancia a su EMA", bool((dist.iloc[-3:] < 5.2).all()),
              f"distancias {', '.join(f'{x:+.1f}%' for x in dist.iloc[-3:])}"))
    k = ks.Close.iloc[-1]
    b.append(("KOSPI por debajo de 5.377-5.439", k < 5377, f"{k:,.0f}"))
    spy_bajo = spy.Close.iloc[-1] < ema(spy.Close).iloc[-1]
    b.append(("SPY cierra por debajo de su EMA 50", spy_bajo,
              f"{spy.Close.iloc[-1]:.2f} frente a {ema(spy.Close).iloc[-1]:.2f}"))
    vix3 = bool((vix.Close.iloc[-3:] > 20).all())
    activos = [x for x in b if x[1]]
    rojo = spy_bajo and hi_bajo and hi_min
    color = "🔴 ROJO" if rojo else ("🟡 AMARILLO" if activos or vix3 else "🟢 VERDE")
    return color, b, (vix3, vix.Close.iloc[-3:].round(2).tolist()), spy, vix


# ---------------------------------------------------------------------------
# El examen
# ---------------------------------------------------------------------------

def examen_etf(p, w, spy, cartera_w, pos, total):
    """Las preguntas del Playbook para un ETF o empresa de la especulación (cartera o banquillo)."""
    out = {}
    c = w.Close.iloc[-1]
    f12, sem = filtro_12(w, spy)
    out["filtro"] = (f"{'✅' if f12 else '❌'} tendencia y fuerza frente al SPY · {sem} semanas seguidas"
                     + (" → **aviso (5 semanas)**" if sem >= SEMANAS_AVISO else ""))
    if p["Lugar"] == "banquillo" and cartera_w:
        nom, cr = correlacion(w, cartera_w)
        out["correlacion"] = f"máxima {cr:.2f} con {nom}" + (" ⚠️ repite lo que ya hay (> 0,8)" if cr > CORR_MAX else "")
        out["repite"] = cr > CORR_MAX
    t_ok, dist = tendencia(w)
    out["tendencia"] = f"{'✅' if t_ok else '❌'} {dist:+.1f}% de su EMA 50" + ("" if t_ok else " (sin tendencia: no hay entrada)")
    lat, pend, b26, med = lateral(w)
    out["lateral"] = (f"{'⛔ EN LATERAL' if lat else 'no'} (EMA {pend:+.1f}% en 13 sem; banda 26 sem {b26}% frente a su mediana {med}%)")
    fl = fin_lateral(w)
    if fl:
        out["lateral"] += f" · {fl}"
    k, ktxt = estocastico(w)
    out["estocastico"] = f"{k}: {ktxt}"
    z = zona(p["Zona"]) if p["Zona"] not in ("—", "") else None
    st = stop_param(p["Stop"]) if p["Stop"] not in ("—", "") else None
    estado = "sin medir (falta zona y stop: pasar por `--nuevo`)"
    entra = False
    if z:
        lo, hi = z
        prev = w.Close.iloc[-2]
        if c > hi:
            estado = f"acercándose ({c:.2f}, baja hacia {lo}-{hi})" if c < prev else f"fuera de zona ({c:.2f}, {((c / hi) - 1) * 100:+.1f}% sobre la zona)"
        elif c < lo:
            estado = f"por debajo de la zona ({c:.2f})"
        else:
            hay, gdat = gatillo(w)
            estado = ("**posible gatillo: confírmalo en el gráfico**" if hay else "en zona, sin gatillo") + f" ({c:.2f}; {gdat})"
            entra = hay
    if lat:
        estado = "en lateral: no se hace nada" + (f" · {estado}" if z else "")
        entra = False
    out["estado"] = estado
    if z and st:
        entrada = c if z[0] <= c <= z[1] else (z[0] + z[1]) / 2
        stop = st[1] if st[0] == "nivel" else entrada * (1 - st[1])
        rt, mx = ratio(w, entrada, stop)
        out["ratio"] = f"{'✅' if rt >= RATIO_MIN else '❌'} {rt:.2f}:1 (entrada {entrada:.2f}, stop {stop:.2f}, máximo {mx:.2f})"
        imp = float(p["Importe"]) if p["Importe"] not in ("—", "") else 0
        riesgo = imp * (entrada - stop) / entrada if st[0] == "nivel" else imp * st[1]
        out["riesgo"] = riesgo
        out["tope"] = f"{'✅' if riesgo <= TOPE_RIESGO * total else '❌'} {riesgo:.0f} € (tope {TOPE_RIESGO * total:.0f} €)"
        entra = entra and rt >= RATIO_MIN and riesgo <= TOPE_RIESGO * total
    out["entra"] = entra and t_ok
    if pos:
        out["dentro"] = examen_dentro(p, w, pos, st)
    return out


def examen_dentro(p, w, pos, st):
    c = w.Close.iloc[-1]
    stop = float(pos["Stop actual"].replace(",", "."))
    e = ema(w.Close).iloc[-1]
    lineas = []
    if c < stop:
        lineas.append(f"**SALTA EL STOP** ({c:.2f} < {stop}) → se vende el lunes")
    if c < e:
        lineas.append(f"**PIERDE LA EMA 50** ({c:.2f} < {e:.2f}) → se vende el lunes (Cinturón de Seguridad)")
    if st and st[0] == "pct":
        compra = pd.Timestamp(dt.datetime.strptime(pos["Fecha"], "%d/%m/%Y"))
        mx = w.Close[w.index >= compra].max()
        prop = mx * (1 - st[1])
        if prop > stop:
            lineas.append(f"propuesta de subida del stop: {prop:.2f} ({st[1] * 100:.0f}% bajo el máximo cierre {mx:.2f}) — decides tú")
    elif st:
        lineas.append("stop por nivel: si ha hecho un escalón nuevo (retrocede, deja suelo y supera el máximo), proponer subirlo bajo ese suelo — revísalo en el gráfico")
    return lineas or ["sigue: ningún stop ni salida"]


def bloque_nucleo(p, w, viernes, sem_color, spy, vix):
    c = w.Close.iloc[-1] if w is not None else None
    if p["Tipo"] == "nucleo-sp":
        lim = zona(p["Zona"])[1]
        bloqueado = sem_color != "🟢 VERDE"
        o, h, l, cc, v = w.iloc[-1][["Open", "High", "Low", "Close", "Volume"]]
        cuerpo, rango = abs(cc - o), h - l
        agot = rango > 0 and (cuerpo < 0.5 * rango or (min(o, cc) - l) > cuerpo)
        mas_vol = v > w.Volume.iloc[-2]
        vix_gira = vix.Close.iloc[-1] < vix.Close.iloc[-2]
        if c > lim:
            return f"fuera de zona: SPY {c:.2f} (zona {lim}, {((c / lim) - 1) * 100:+.1f}%)"
        return (f"en zona ({c:.2f}). Bloqueos: {'alguno activo (ver semáforo)' if bloqueado else 'ninguno'}. "
                f"Gatillo: agotamiento {'sí' if agot else 'no'}, más volumen {'sí' if mas_vol else 'no'}, VIX girando {'sí' if vix_gira else 'no'} "
                "(el escape falso se mira en el gráfico)")
    if p["Tipo"] == "nucleo-oro":
        lim = zona(p["Zona"])[1]
        return (f"{'**se compra el lunes**' if c <= lim else 'espera'}: GC=F {c:,.0f} (entrada en {lim:,.0f} o menos)"
                " — *futuro, comprobar GOLD en TradingView si está cerca*")
    if p["Tipo"] == "nucleo-btc":
        fed = dbnomics("FED/H41/RESPPA_N.WW")
        bce = dbnomics("ECB/ILM/W.U2.C.T000000.Z5.Z01")
        fed, bce = fed[fed.index <= pd.Timestamp(viernes)], bce[bce.index <= pd.Timestamp(viernes)]
        rf, rb = (fed.iloc[-1] / fed.iloc[-14] - 1) * 100, (bce.iloc[-1] / bce.iloc[-14] - 1) * 100
        ok = rf > 1 and rb > 1
        return f"{'**se compra el lunes**' if ok else 'espera'}: Fed {rf:+.2f}%, BCE {rb:+.2f}% en 13 semanas (entrada con los dos por encima de +1%)"
    return "—"


def sabado_por_defecto(hoy):
    return hoy - dt.timedelta(days=(hoy.weekday() - 5) % 7)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sabado", help="AAAA-MM-DD (por defecto, el último sábado)")
    ap.add_argument("--nuevo", help="TICKER o TICKER:empresa (examen de un candidato nuevo)")
    a = ap.parse_args()
    sab = dt.date.fromisoformat(a.sabado) if a.sabado else sabado_por_defecto(dt.date.today())
    vie = sab - dt.timedelta(days=1)

    params = parametros()
    abiertas = {x["Nombre"]: x for x in posiciones()}
    total = CARTERA_TOTAL
    spy = semanal("SPY", vie)
    cartera_esp = [p for p in params if p["Lugar"] == "cartera" and p["Tipo"] in ("etf", "empresa")]
    cartera_w = {}
    for p in cartera_esp:
        cartera_w[p["Nombre"]] = semanal(p["Gráfico"], vie)
    cartera_w["S&P 500"] = spy

    if a.nuevo:
        examen_nuevo(a.nuevo, vie, spy, cartera_w, total)
        return

    color, bloqueos, (vix3, vix_ult), _, vix = semaforo(vie)
    L = [f"---\nfecha: {dt.date.today():%Y-%m-%d}\ntags: [trading, estado-cartera, sabado]\n---\n",
         f"# Estado de la cartera — sábado {sab:%d/%m/%Y}\n",
         f"Cierre del viernes {vie:%d/%m/%Y}. Examen del [[trading-playbook]] sobre [[trading-plan]] y [[trading-posiciones]]. "
         "**Informa, no decide:** la conclusión de David puede ser más prudente, nunca más atrevida.\n",
         f"## Semáforo: {color}\n"]
    for nombre, activo, dato in bloqueos:
        L.append(f"- {'⛔' if activo else '·'} {nombre}: {dato}")
    L.append(f"- {'⛔' if vix3 else '·'} VIX 3 semanas por encima de 20: últimas {vix_ult}\n")

    # A. Cartera
    L.append("## A. Cartera\n")
    riesgo_abierto = 0
    for p in [x for x in params if x["Lugar"] == "cartera"]:
        w = semanal(p["Gráfico"], vie) if p["Tipo"] != "nucleo-btc" else None
        pos = abiertas.get(p["Nombre"])
        L.append(f"### {p['Nombre']} ({p['Gráfico']} → {p['Réplica']}){' — DENTRO' if pos else ''}\n")
        if p["Tipo"].startswith("nucleo"):
            L.append(f"- {bloque_nucleo(p, w, vie, color, spy, vix)}")
            if pos and w is not None:
                for x in examen_dentro(p, w, pos, stop_param(p["Stop"])):
                    L.append(f"- {x}")
            L.append("")
            continue
        r = examen_etf(p, w, spy, {}, pos, total)
        riesgo_abierto += r.get("riesgo", 0) if pos else 0
        decision = ("**se compra el lunes** (si confirmas el gatillo)" if r["entra"] and color == "🟢 VERDE"
                    else "no se compra esta semana")
        for k, et in (("estado", "Estado"), ("tendencia", "Tendencia"), ("lateral", "Lateral"),
                      ("estocastico", "Estocástico"), ("ratio", "Ratio"), ("tope", "Tope del 1%")):
            if k in r:
                L.append(f"- **{et}:** {r[k]}")
        if pos:
            for x in r["dentro"]:
                L.append(f"- {x}")
        else:
            L.append(f"- **→ {decision}**" + ("" if color == "🟢 VERDE" or not r["entra"] else f" (semáforo {color}: no se abre nada nuevo)"))
        L.append("")
    L.append(f"**Riesgo abierto (posiciones compradas):** {riesgo_abierto:.0f} € de {RIESGO_ABIERTO_MAX * total:.0f} € · "
             "**Freno del 10%:** sin serie todavía (el valor de la especulación se anota cada sábado en Posiciones)\n")

    # B. Banquillo
    L.append("## B. Banquillo\n")
    L.append("| Candidato | Filtro (1-2) | Correlación | Tendencia | Lateral | Estado | Ratio hoy |")
    L.append("|---|---|---|---|---|---|---|")
    ajustes, empresas = [], []
    for p in [x for x in params if x["Lugar"] == "banquillo"]:
        try:
            w = semanal(p["Gráfico"], vie)
        except Exception as ex:
            L.append(f"| {p['Nombre']} | sin datos ({ex.__class__.__name__}) | | | | | |")
            continue
        r = examen_etf(p, w, spy, cartera_w, None, total)
        L.append(f"| {p['Nombre']} ({p['Gráfico']}) | {r['filtro']} | {r.get('correlacion', '')} | {r['tendencia']} | {r['lateral']} | {r['estado']} | {r.get('ratio', '—')} |")
        if p["Tipo"] == "empresa":
            empresas.append(p["Gráfico"])
        aviso = "aviso (5 semanas)" in r["filtro"]
        if aviso and "EN LATERAL" not in r["lateral"] and not r.get("repite"):
            if "sin medir" in r["estado"]:
                ajustes.append(f"**{p['Nombre']}** lleva 5+ semanas pasando el filtro → medir zona y stop con `--nuevo {p['Gráfico']}` para ver si puede subir")
            elif "✅" in r.get("ratio", ""):
                ajustes.append(f"**{p['Nombre']}** pasa el filtro y el ratio → **puede subir a la cartera**: recalcular la paridad sobre el 38% del valor actual")
        time.sleep(0.3)
    L.append("")
    for t in empresas:
        L.append(f"### Resultados de {t} (filtro 4)\n\n{resultados_empresa(t)}\n")

    # C. Ajustes
    L.append("## C. Ajustes\n")
    L += [f"- {x}" for x in ajustes] if ajustes else ["- Ninguno esta semana."]
    L.append("\n> Reglas de ajuste: [[trading-playbook]], sección 8. Nada se cambia en el Plan ni en Posiciones sin el visto bueno de David.")

    destino = TRADING / "sabados" / f"estado-{sab:%Y-%m-%d}.md"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text("\n".join(L) + "\n")
    print(destino)


def examen_nuevo(arg, vie, spy, cartera_w, total):
    t, _, tipo = arg.partition(":")
    w = semanal(t, vie, desde=915148800)
    p = {"Nombre": t, "Lugar": "banquillo", "Tipo": "empresa" if tipo == "empresa" else "etf",
         "Gráfico": t, "Réplica": "?", "Zona": "—", "Stop": "—", "Importe": "—"}
    r = examen_etf(p, w, spy, cartera_w, None, total)
    print(f"# Examen de un candidato nuevo: {t} (cierre {vie:%d/%m/%Y})\n")
    print("- **Réplica UCITS:** comprobar en justETF (https://www.justetf.com) — sin réplica UCITS no entra")
    for k, et in (("filtro", "Filtro (1-2)"), ("correlacion", "Correlación con la cartera"), ("tendencia", "Tendencia"),
                  ("lateral", "Lateral"), ("estocastico", "Estocástico")):
        if k in r:
            print(f"- **{et}:** {r[k]}")
    if p["Tipo"] == "empresa":
        print("\n" + resultados_empresa(t))
    # Historia para que David elija zona y stop (Playbook, sección 3 y 5)
    c, l = w.Close.values, w.Low.values
    e = ema(w.Close).values
    dist = c / e - 1
    sl = np.r_[[False] * 4, e[4:] > e[:-4]]
    rows, i = [], 50
    while i < len(c):
        if dist[i] >= 0.10 and sl[i]:
            pk = j = i
            while j < len(c) - 1 and c[j + 1] >= c[pk] * 0.97:
                j += 1
                if c[j] > c[pk]:
                    pk = j
            k, lo, lo_i = pk + 1, np.inf, None
            while k < len(c) and k <= pk + 26 and c[k] <= c[pk]:
                if l[k] < lo:
                    lo, lo_i = l[k], k
                k += 1
            if lo_i is not None and k < len(c):
                rows.append(float(round((lo / c[pk] - 1) * 100, 1)))
            i = max(k, pk + 1)
        else:
            i += 1
    print(f"\n**Retrocesos de su historia** (desde ≥10% sobre su EMA 50 subiendo; caída del cierre del pico al mínimo): "
          f"{len(rows)} casos, ordenados: {', '.join(f'{x:+.1f}%' for x in sorted(rows, reverse=True))}")
    orden = sorted(rows, reverse=True)
    saltos = sorted(((orden[i] - orden[i + 1], orden[i], orden[i + 1]) for i in range(len(orden) - 1)), reverse=True)[:3]
    print("- **Huecos más grandes** (tramos donde no paró ninguno): " +
          "; ".join(f"entre {a:+.1f}% y {b:+.1f}% ({g:.1f} puntos)" for g, a, b in saltos))
    print("- La **zona** sale de aquí y de su gráfico (techos anteriores, niveles de Cava): **la eliges tú**.")
    print("- Si hay un **hueco** en esa lista (un tramo donde no paró ninguno), el stop puede ir por **nivel**; si no, por **% de ruido** en la réplica.")
    print("- Con zona y stop, se calcula el **ratio** (≥ 1:2) y el **tope del 1%**, y se añade una fila a 'Parámetros del examen' del Plan.")


if __name__ == "__main__":
    main()
