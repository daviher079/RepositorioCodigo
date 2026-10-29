"""Análisis de situación semanal.

Calcula las 8 filas de *Datos macro semanales* con el cierre de la semana
(lunes a viernes antes del sábado indicado) y escribe el informe en Word.
Todo sale de la especificación «Especificación — Análisis semanal
automatizado» (Google Drive): mismos datos, mismos tramos, mismas frases.

El informe NO escribe conclusiones ni une filas: eso lo hace David.
Donde la especificación no tiene un corte medido, solo se da el número.

Uso:
    python analisis.py                 # sábado de esta semana (o el último)
    python analisis.py 2026-10-24      # un sábado concreto
    python analisis.py 2026-10-24 --crear-carpeta
"""

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

AQUI = Path(__file__).resolve().parent
CONFIG = json.loads((AQUI.parent / "config.json").read_text())
MADRID = ZoneInfo("Europe/Madrid")
UA = {"User-Agent": "Mozilla/5.0"}

# Desplazamientos del recorrido, en semanas.
RECORRIDO = [("Hace 6 meses", 26), ("Hace 3 meses", 13), ("Hace 1 mes", 4), ("Hoy", 0)]


# ---------------------------------------------------------------------------
# Formato
# ---------------------------------------------------------------------------

def num(x, nd=2, signo=False, miles=False):
    """Número en formato español: coma decimal y, si se pide, punto de miles."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "s/d"
    s = f"{x:+,.{nd}f}" if signo else f"{x:,.{nd}f}"
    s = s.replace(",", "_").replace(".", ",").replace("_", "." if miles else "")
    return s.replace("-", "−")


def pct(x, nd=1, signo=True):
    return num(x, nd, signo) + "%"


def fecha(d):
    return d.strftime("%d/%m/%Y")


def viernes(lunes):
    return lunes + dt.timedelta(days=4)


# ---------------------------------------------------------------------------
# Descarga
# ---------------------------------------------------------------------------

def _get(url):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()


def yahoo(ticker):
    """Cierres semanales indexados por el lunes de cada semana (hora de la bolsa).

    Yahoo añade una fila suelta con la última cotización: se agrupa por
    semana y se queda el último cierre de cada una. Con un histórico largo
    etiqueta cada vela con el sábado anterior a su semana (con uno corto, con
    el lunes): una etiqueta de sábado o domingo pertenece al lunes siguiente."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?interval=1wk&period1=946684800&period2=4102444800")
    r = _get(url)["chart"]["result"][0]
    tz = ZoneInfo(r["meta"]["exchangeTimezoneName"])
    cierres = {}
    for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
        if c is None:
            continue
        d = dt.datetime.fromtimestamp(t, tz).date()
        lunes = d + dt.timedelta(days=7 - d.weekday()) if d.weekday() >= 5 else d - dt.timedelta(days=d.weekday())
        cierres[lunes] = c
    s = pd.Series(cierres, dtype=float).sort_index()
    s.index = pd.to_datetime(s.index)
    return s


def dbnomics(serie):
    d = _get(f"https://api.db.nomics.world/v22/series/{serie}?observations=1")
    doc = d["series"]["docs"][0]
    pares = [(p, v) for p, v in zip(doc["period"], doc["value"])
             if isinstance(v, (int, float))]
    return pares


# ---------------------------------------------------------------------------
# Utilidades de series semanales
# ---------------------------------------------------------------------------

def ema(s):
    return s.ewm(span=50, adjust=False).mean()


def distancia(s):
    return (s / ema(s) - 1) * 100


def racha(cond, t):
    """Semanas seguidas en las que `cond` es cierta, terminando en la posición t."""
    n = 0
    while t - n >= 0 and bool(cond.iloc[t - n]):
        n += 1
    return n


def racha_igual(valores, t):
    """Semanas seguidas con el mismo valor que en t."""
    v = valores.iloc[t]
    n = 0
    while t - n >= 0 and valores.iloc[t - n] == v:
        n += 1
    return n


def lunes_inicio_racha(s, t, n):
    return s.index[t - n + 1].date()


# ---------------------------------------------------------------------------
# Datos de la semana
# ---------------------------------------------------------------------------

class Datos:
    def __init__(self, lunes):
        self.lunes = pd.Timestamp(lunes)
        tick = {"spy": "SPY", "hyg": "HYG", "iei": "IEI", "gld": "GLD",
                "vix": "%5EVIX", "move": "%5EMOVE", "tnx": "%5ETNX",
                "kospi": "%5EKS11", "iwm": "IWM"}
        crudo = {k: yahoo(v) for k, v in tick.items()}
        faltan = [k for k, s in crudo.items() if self.lunes not in s.index]
        if faltan:
            sys.exit(f"Falta la semana del {fecha(self.lunes)} en: {', '.join(faltan)}")
        self.s = {k: s[s.index <= self.lunes] for k, s in crudo.items()}

        def cociente(a, b):
            x = pd.concat([self.s[a], self.s[b]], axis=1, join="inner")
            return x.iloc[:, 0] / x.iloc[:, 1]

        self.s["hyg_iei"] = cociente("hyg", "iei")
        self.s["iwm_spy"] = cociente("iwm", "spy")
        self.s["spy_gld"] = cociente("spy", "gld")

        self.ff = [(dt.date.fromisoformat(p), v) for p, v in dbnomics("FED/H15/RIFSPFF_N.B")]
        self.walcl = [(dt.date.fromisoformat(p), v) for p, v in dbnomics("FED/H41/RESPPA_N.WW")]
        self.pib = []
        for p, v in dbnomics("BEA/NIPA-T10105/A191RC-Q"):
            y, q = int(p[:4]), int(p[-1])
            fin = dt.date(y, 3 * q, 1) + pd.offsets.MonthEnd(0)
            self.pib.append((y, q, fin.date() if hasattr(fin, "date") else fin, v))

    def t(self, k, semanas_atras=0):
        """Posición de la semana objetivo (menos `semanas_atras`) en la serie k."""
        return len(self.s[k]) - 1 - semanas_atras


# ---------------------------------------------------------------------------
# Filas
# ---------------------------------------------------------------------------

def fila_fed(D, atras=0):
    lun = D.lunes - pd.Timedelta(weeks=atras)
    vie = viernes(lun.date())

    ff_hasta = [x for x in D.ff if x[0] <= vie]
    tipo = ff_hasta[-1][1]
    hace6 = [x for x in D.ff if x[0] <= vie - dt.timedelta(days=182)][-1][1]
    # Última decisión: último salto diario de al menos 15 pb.
    decision = None
    for (d0, v0), (d1, v1) in zip(ff_hasta, ff_hasta[1:]):
        if abs(v1 - v0) >= 0.15:
            decision = (d1, v0, v1)

    w = [x for x in D.walcl if x[0] <= vie]
    roc = (w[-1][1] / w[-14][1] - 1) * 100

    # PIB: se da por publicado 30 días después del fin del trimestre (aproximación declarada).
    usables = [x for x in D.pib if x[2] + dt.timedelta(days=30) <= vie]
    y, q, _, v = usables[-1]
    previo = [x for x in D.pib if x[0] == y - 1 and x[1] == q][0][3]
    pib = (v / previo - 1) * 100

    bono = D.s["tnx"].iloc[D.t("tnx", atras)]
    m_tipo = pib - tipo
    m_bono = pib - bono
    recorte = hace6 - tipo
    cava_tipo = tipo > pib
    cava_balance = roc < -1

    if cava_tipo and cava_balance:
        casilla, hist = "rojo", None
    elif recorte > 0.5:
        casilla, hist = "aviso", 53
    elif m_bono < 1:
        casilla, hist = "aviso", "25-28"
    else:
        casilla, hist = "viento a favor", 11
    return dict(tipo=tipo, hace6=hace6, decision=decision, roc=roc, pib=pib,
                pib_trim=f"{q}T {y}", bono=bono, m_tipo=m_tipo, m_bono=m_bono,
                recorte=recorte, cava_tipo=cava_tipo, cava_balance=cava_balance,
                casilla=casilla, hist=hist)


def texto_fed(D):
    f = fila_fed(D)
    ant = fila_fed(D, 1)
    frases = []
    frases.append({"viento a favor": "Actualmente el dinero no le está saliendo caro a la economía.",
                   "aviso": "Actualmente el dinero empieza a salirle caro a la economía.",
                   "rojo": "Actualmente el dinero le está saliendo caro a la economía."}[f["casilla"]])
    if f["m_tipo"] >= 0:
        frases.append(f"El PIB nominal crece un {pct(f['pib'], 1, False)} y el tipo oficial está en el "
                      f"{num(f['tipo'])}%, lo que deja un margen de {num(f['m_tipo'], 1, True)} puntos.")
    else:
        frases.append(f"El PIB nominal crece un {pct(f['pib'], 1, False)} y el tipo oficial está en el "
                      f"{num(f['tipo'])}%: el tipo oficial supera al PIB ({num(f['m_tipo'], 1, True)} puntos).")
    mb = f["m_bono"]
    if mb > 3:
        frases.append(f"El bono paga más de 3 puntos menos de lo que crece la economía "
                      f"({num(mb, 1, True)}): está recalentada y la Fed va tarde.")
    elif mb >= 1:
        frases.append(f"El bono a 10 años está en el {num(f['bono'])}%, por lo que su margen frente al PIB "
                      f"es de {num(mb, 1, True)} puntos, por encima del punto que marca el corte. Viento a favor.")
    elif mb >= 0:
        frases.append(f"El bono a 10 años está en el {num(f['bono'])}%, por lo que su margen frente al PIB "
                      f"es de {num(mb, 1, True)} puntos, por debajo del punto que marca el corte. Aviso.")
    else:
        frases.append(f"El bono paga más de lo que crece la economía ({num(mb, 1, True)} puntos). Aviso.")
    if f["roc"] > 1:
        frases.append(f"La Fed está metiendo dinero en el sistema ({pct(f['roc'], 2)}).")
    elif f["roc"] >= -1:
        frases.append(f"En cuanto al balance, el ROC de 13 semanas está en {pct(f['roc'], 2)}: "
                      f"la Fed ni mete ni saca dinero, está plana.")
    else:
        frases.append(f"La Fed está sacando dinero del sistema ({pct(f['roc'], 2)}).")
    if f["recorte"] > 0.5:
        frases.append(f"La Fed ha recortado {num(f['recorte'])} puntos en 6 meses. Recortar deprisa no es "
                      f"buena señal: la Fed lo hace cuando algo se rompe.")
    elif f["recorte"] <= -0.15 and f["decision"]:
        d, a, b = f["decision"]
        frases.append(f"La Fed subió los tipos el {fecha(d)} (de {num(a)} a {num(b)}).")
    disparo = f["pib"] - 1
    if mb >= 1:
        frases.append(f"Si el bono pasa del {num(disparo)}%, el margen bajaría de 1 punto y entraría en aviso. "
                      f"Faltan {num((disparo - f['bono']) * 100, 0)} pb.")
    else:
        frases.append(f"Para volver a viento a favor, el bono tiene que bajar del {num(disparo)}%. "
                      f"Faltan {num((f['bono'] - disparo) * 100, 0)} pb.")
    if f["hist"] is not None:
        frases.append(f"En la historia, en esta situación, el SPY ha caído más de un 10% en los 6 meses "
                      f"siguientes el {f['hist']}% de las veces.")
    if not f["cava_tipo"] and not f["cava_balance"]:
        frases.append("El test de Cava está lejos: el tipo oficial no supera al PIB y la Fed no está sacando dinero.")
    elif f["cava_tipo"] and f["cava_balance"]:
        frases.append("Test de Cava en rojo.")
    else:
        mitad = "el tipo oficial supera al PIB" if f["cava_tipo"] else "la Fed está sacando dinero"
        frases.append(f"Se cumple la mitad del test de Cava: {mitad}.")

    ficha = [("PIB nominal interanual", f"{pct(f['pib'])} ({f['pib_trim']})"),
             ("Tipo oficial", f"{num(f['tipo'])}%" + (f" (última decisión el {fecha(f['decision'][0])})" if f["decision"] else "")),
             ("Bono a 10 años", f"{num(f['bono'])}%"),
             ("Margen del tipo oficial", f"{num(f['m_tipo'], 1, True)} puntos"),
             ("Margen del bono (la regla)", f"{num(f['m_bono'], 1, True)} puntos"),
             ("Balance (ROC de 13 semanas)", pct(f["roc"], 2)),
             ("Movimiento de tipos en 6 meses", f"{num(-f['recorte'], 2, True)} puntos")]
    veredicto = f"{f['casilla'].capitalize()}" + (f" ({f['hist']}% histórico)" if f["hist"] is not None else "")
    rec = [fila_fed(D, a) for _, a in RECORRIDO]
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["Margen del bono", *[num(r["m_bono"], 1, True) for r in rec]],
                  ["Tipo oficial", *[num(r["tipo"]) for r in rec]],
                  ["Balance ROC 13", *[pct(r["roc"], 2) for r in rec]]])
    estado = {"Casilla de la Fed": f["casilla"]}
    estado_ant = {"Casilla de la Fed": ant["casilla"]}
    extra = "PIB nuevo esta semana: " + ("sí (las cuentas cambian aunque el bono no se mueva)."
                                          if f["pib_trim"] != ant["pib_trim"] else "no.")
    return dict(titulo="Fed", ficha=ficha, veredicto=veredicto, recorrido=recorrido,
                estado=estado, estado_ant=estado_ant, extra=extra, resumen=" ".join(frases), datos=f)


def zona_move(r):
    return ("calma" if r < 0.9 else "normal" if r < 1.1 else "tensión" if r < 1.3 else "tensión alta")


def texto_move(D):
    m, b = D.s["move"], D.s["tnx"]
    med = m.rolling(52).median()
    rel = m / med
    t, tb = D.t("move"), D.t("tnx")
    r = rel.iloc[t]
    hist = rel.iloc[:t + 1].dropna()
    pctil = (hist < r).mean() * 100
    sem13 = racha(rel > 1.3, t)
    c8 = (b.iloc[tb] - b.iloc[tb - 8]) * 100
    c2 = (b.iloc[tb] - b.iloc[tb - 2]) * 100
    sem49 = racha(b > 4.9, tb)
    z = zona_move(r)
    base = (f"El MOVE está en {num(m.iloc[t], 1)} y su mediana de las últimas 52 semanas es "
            f"{num(med.iloc[t], 1)}, lo que da un cociente de {num(r)}")
    frases = [{"calma": f"Actualmente los bonos están en calma. {base}, por debajo del 0,9.",
               "normal": f"Actualmente los bonos están en zona normal. {base}.",
               "tensión": f"Actualmente se encuentra en tensión. {base}, entre 1,1 y 1,3.",
               "tensión alta": f"Actualmente se encuentra bajo alta tensión. {base}, por encima del 1,3 que marca la tensión alta."}[z]]
    if sem13 >= 1:
        frases.append(f"Lleva {sem13} semanas seguidas por encima de 1,3.")
    tipo = None
    if r > 1.3:
        if c8 > 25:
            tipo = "bolsa todavía arriba"
            frases.append(f"En 8 semanas el bono a 10 años ha subido {num(c8, 0)} pb: es el tipo de tensión que llega "
                          f"con la bolsa todavía arriba. En la historia, en esta situación el SPY ya estaba bajo su EMA el 29% de las semanas.")
        elif c8 < -25:
            tipo = "huida a refugio"
            frases.append(f"En 8 semanas el bono a 10 años ha bajado {num(-c8, 0)} pb: es huida a refugio, la crisis ya ha "
                          f"empezado. En la historia, en esta situación el SPY ya estaba bajo su EMA el 54% de las semanas.")
        else:
            tipo = "sin dirección"
            frases.append(f"En 8 semanas el bono a 10 años se ha movido {num(c8, 0, True)} pb: los tipos no marcan "
                          f"dirección y la tensión no tiene un tipo claro.")
    frases.append(f"En las dos últimas semanas el bono ha {'subido' if c2 >= 0 else 'bajado'} {num(abs(c2), 0)} pb.")
    if b.iloc[tb] > 4.9:
        frases.append(f"Se sitúa en el {num(b.iloc[tb])}%, con {sem49} semanas seguidas por encima del 4,9%. "
                      f"Desde 2008 solo había pasado del 4,9% una semana, la del 20/10/2023.")
    else:
        frases.append(f"Se sitúa en el {num(b.iloc[tb])}%.")
    ficha = [("MOVE relativo (la regla)", f"{num(r)} ({num(m.iloc[t], 1)} ÷ {num(med.iloc[t], 1)}), percentil {num(pctil, 0)}"),
             ("Semanas seguidas por encima de 1,3", str(sem13)),
             ("Dirección de los tipos", f"{num(c8, 0, True)} pb en 8 semanas; {num(c2, 0, True)} pb en las 2 últimas"),
             ("Nivel del 10 años", f"{num(b.iloc[tb])}% ({sem49} semanas por encima del 4,9%)")]
    veredicto = z.capitalize() + (f" — {tipo}" if tipo else "")
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["MOVE relativo", *[num(rel.iloc[t - a]) for _, a in RECORRIDO]],
                  ["Bono a 10 años", *[num(b.iloc[tb - a]) + "%" for _, a in RECORRIDO]]])
    return dict(titulo="MOVE", ficha=ficha, veredicto=veredicto, recorrido=recorrido,
                estado={"Zona del MOVE": z}, estado_ant={"Zona del MOVE": zona_move(rel.iloc[t - 1])},
                resumen=" ".join(frases), datos=dict(rel=r, bono=b.iloc[tb]))


def tramo_hyg(d, ie_arriba):
    if d >= 0:
        return "por encima"
    if d > -2:
        return "0 a −2%"
    if d > -8.6:
        return "−2 a −8,6% (tipos)" if ie_arriba else "−2 a −8,6% (crédito)"
    return "más de −8,6% (tipos)" if ie_arriba else "más de −8,6% (crédito)"


def texto_hyg(D):
    h, ie = D.s["hyg"], D.s["hyg_iei"]
    t, ti = D.t("hyg"), D.t("hyg_iei")
    e = ema(h)
    d = distancia(h)
    die = distancia(ie)
    dd = d.iloc[t]
    ie_arriba = die.iloc[ti] >= 0
    lado = "por encima" if dd >= 0 else "por debajo"
    sem = racha_igual(d >= 0, t)
    frases = [f"Se encuentra {lado} de su EMA ({num(h.iloc[t])} frente a {num(e.iloc[t])})."]
    tr = tramo_hyg(dd, ie_arriba)
    frases.append({"por encima": f"A una distancia de {pct(dd, 2)}.",
                   "0 a −2%": f"A una distancia de {pct(dd, 2)}: lo habitual al cruzar, a menudo se deshace en pocas semanas.",
                   "−2 a −8,6% (tipos)": f"A una distancia de {pct(dd, 2)}. La caída es sobre todo de tipos: el crédito todavía no se está cerrando.",
                   "−2 a −8,6% (crédito)": f"A una distancia de {pct(dd, 2)}. Deterioro real del crédito: los inversores exigen más por prestar a las empresas con más riesgo.",
                   "más de −8,6% (tipos)": f"A una distancia de {pct(dd, 2)}. Caída muy profunda, sobre todo de tipos.",
                   "más de −8,6% (crédito)": f"A una distancia de {pct(dd, 2)}. Crisis de crédito: solo el 10% de las semanas por debajo llegaron aquí."}[tr])
    if dd < 0:
        if sem <= 2:
            frases.append(f"Lleva {sem} semanas por debajo. En la historia, con al menos 1 semana por debajo, llegó a −2% "
                          f"el 38% de las veces y duró 13 semanas o más el 19%.")
        elif sem <= 7:
            frases.append(f"Lleva {sem} semanas por debajo. En la historia, con al menos 3 semanas por debajo, llegó a −2% "
                          f"el 71% de las veces y duró 13 semanas o más el 38%.")
        else:
            frases.append(f"Lleva {sem} semanas por debajo. En la historia, con al menos 8 semanas por debajo, llegó a −2% "
                          f"el 100% de las veces (10 de 10) y duró 13 semanas o más el 80%.")
    else:
        frases.append(f"Lleva {sem} semanas por encima de su EMA.")
    pend = e.diff()
    sp = racha_igual(pend < 0, t)
    if pend.iloc[t] < 0:
        frases.append(f"La pendiente baja desde hace {sp} semanas: la media se va acercando al precio y le pone más fácil volver a cruzarla.")
    else:
        frases.append(f"La pendiente sube desde hace {sp} semanas.")
    techo, suelo = h.iloc[t - 8:t].max(), h.iloc[t - 8:t].min()
    if dd < 0:
        if h.iloc[t] > techo:
            frases.append("Ha cerrado por encima del techo de las últimas 8 semanas: el deterioro se frena.")
        else:
            frases.append(f"Se mueve entre {num(suelo)} y {num(techo)} en las últimas 8 semanas.")
    sie = racha_igual(die >= 0, ti)
    frases.append(f"El HYG/IEI lleva {sie} semanas {'por encima' if ie_arriba else 'por debajo'} de su EMA ({pct(die.iloc[ti], 2)}).")
    ficha = [("Lado (la regla)", f"{lado}: {num(h.iloc[t])} frente a {num(e.iloc[t])}"),
             ("Distancia", pct(dd, 2)),
             ("Pendiente de la EMA", f"{'baja' if pend.iloc[t] < 0 else 'sube'} ({sp} semanas)"),
             ("Semanas seguidas al mismo lado", f"{sem} {lado}"),
             ("Rango de las 8 semanas anteriores", f"{num(suelo)}–{num(techo)}"),
             ("Causa de la caída (HYG/IEI)", f"{'por encima' if ie_arriba else 'por debajo'}: {sie} semanas ({pct(die.iloc[ti], 2)})")]
    tr_ant = tramo_hyg(d.iloc[t - 1], die.iloc[ti - 1] >= 0)
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["Distancia del HYG", *[pct(d.iloc[t - a], 2) for _, a in RECORRIDO]],
                  ["Distancia del HYG/IEI", *[pct(die.iloc[ti - a], 2) for _, a in RECORRIDO]]])
    return dict(titulo="HYG", ficha=ficha, veredicto=f"{lado.capitalize()} de su EMA, tramo {tr}",
                recorrido=recorrido, estado={"Tramo del HYG": tr}, estado_ant={"Tramo del HYG": tr_ant},
                resumen=" ".join(frases), datos=dict(dist=dd, ie_arriba=ie_arriba, sem_ie=sie))


def casilla_russell(dq, di, spy_arriba):
    if not spy_arriba:
        return "no aplica"
    if dq > -2:
        return "sin aviso"
    return "aviso" if di >= 0 else "aviso serio"


def texto_russell(D, fed, move, hyg):
    q, iwm = D.s["iwm_spy"], D.s["iwm"]
    t, ti, ts = D.t("iwm_spy"), D.t("iwm"), D.t("spy")
    dq, di = distancia(q), distancia(iwm)
    spy_arriba = distancia(D.s["spy"]).iloc[ts] >= 0
    c = casilla_russell(dq.iloc[t], di.iloc[ti], spy_arriba)
    c_ant = casilla_russell(dq.iloc[t - 1], di.iloc[ti - 1], distancia(D.s["spy"]).iloc[ts - 1] >= 0)
    frases = [{"sin aviso": f"Sin aviso: el Russell acompaña al SPY (el cociente está a {pct(dq.iloc[t], 2)} de su media). "
                            f"En la historia, el SPY cae más de un 10% en los 6 meses siguientes el 10% de las veces.",
               "aviso": f"Aviso: el Russell se queda atrás (el cociente está a {pct(dq.iloc[t], 2)}), pero no cae. "
                        f"La subida se estrecha: sigue, pero con menos empresas detrás. En la historia, 26%.",
               "aviso serio": "Aviso serio: el Russell se queda atrás y además cae. Más prudencia con las compras. En la historia, 35%.",
               "no aplica": "No aplica: el SPY también está por debajo de su media."}[c]]
    sq = racha(dq < -2, t)
    if sq:
        frases.append(f"Lleva {sq} semanas quedándose atrás.")
    ema_iwm = ema(iwm).iloc[ti]
    if di.iloc[ti] >= 0:
        frases.append(f"El IWM está a {pct(di.iloc[ti], 1)} de su EMA. Si cierra por debajo de {num(ema_iwm, 1)}, pasa a aviso serio.")
    else:
        frases.append(f"El IWM está a {pct(di.iloc[ti], 1)} de su EMA, desde hace {racha(di < 0, ti)} semanas.")
    if c in ("aviso", "aviso serio"):
        frases.append("Este aviso está encendido una de cada tres semanas: solo, no es para actuar; suma a los demás avisos.")
    frases.append(f"Esta semana, en el lado del dinero: bono al {num(fed['bono'])}% · MOVE relativo {num(move['rel'])} · "
                  f"HYG a {pct(hyg['dist'], 1)} de su EMA · HYG/IEI {'por encima' if hyg['ie_arriba'] else 'por debajo'} "
                  f"de su EMA ({hyg['sem_ie']} semanas).")
    ficha = [("¿Se queda atrás? (la regla)", f"IWM/SPY a {pct(dq.iloc[t], 2)} de su EMA ({sq} semanas por debajo del −2%)"),
             ("¿Cae?", f"IWM a {pct(di.iloc[ti], 1)} de su EMA ({num(ema_iwm, 1)})")]
    hist = {"sin aviso": " (10% histórico)", "aviso": " (26% histórico)", "aviso serio": " (35% histórico)", "no aplica": ""}[c]
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["Cociente IWM/SPY (distancia)", *[pct(dq.iloc[t - a], 2) for _, a in RECORRIDO]],
                  ["IWM (distancia)", *[pct(di.iloc[ti - a], 1) for _, a in RECORRIDO]]])
    return dict(titulo="Russell 2000", ficha=ficha, veredicto=c.capitalize() + hist, recorrido=recorrido,
                estado={"Russell": c}, estado_ant={"Russell": c_ant}, resumen=" ".join(frases))


def zona_spy(d):
    return ("subida estirada" if d > 11 else "zona tranquila" if d >= 3.5
            else "zona de vigilancia" if d >= 0 else "ha cruzado")


def texto_spy(D):
    s = D.s["spy"]
    t = D.t("spy")
    e, d = ema(s), distancia(s)
    dd = d.iloc[t]
    lado = "por encima" if dd >= 0 else "por debajo"
    sem = racha_igual(d >= 0, t)
    desde = fecha(viernes(lunes_inicio_racha(s, t, sem)))
    z = zona_spy(dd)
    zonas = d.apply(zona_spy)
    sz = racha_igual(zonas, t)
    frases = [f"Se encuentra {lado} de su EMA ({num(s.iloc[t])} frente a {num(e.iloc[t])}).",
              f"Lleva {sem} semanas seguidas {lado}, desde la semana del {desde}."]
    frases.append({"subida estirada": f"A una distancia de {pct(dd, 1)}: subida estirada. En solo el 10% de las semanas pasó del 11%; "
                                      f"no es señal de venta, pero sí un aviso para no comprar con entusiasmo.",
                   "zona tranquila": f"A una distancia de {pct(dd, 1)}: zona tranquila. Hace falta una semana excepcional para cruzar.",
                   "zona de vigilancia": f"A una distancia de {pct(dd, 1)}: zona de vigilancia. Una semana mala normal basta para cruzar.",
                   "ha cruzado": f"A una distancia de {pct(dd, 1)}: ha cruzado, la regla se activa."}[z])
    frases.append(f"Lleva {sz} semanas seguidas en {z}.")
    frases.append("Distancias de las últimas semanas: " + " → ".join(pct(d.iloc[t - k], 1) for k in (3, 2, 1, 0)) + ".")
    pend = e.diff()
    sp = racha_igual(pend < 0, t)
    frases.append(f"La pendiente de la EMA {'baja' if pend.iloc[t] < 0 else 'sube'} desde hace {sp} semanas.")
    techo, suelo = s.iloc[t - 8:t].max(), s.iloc[t - 8:t].min()
    if s.iloc[t] > techo:
        frases.append(f"Ha cerrado por encima de {num(techo)}: sale del lateral hacia arriba.")
    elif s.iloc[t] < suelo:
        frases.append(f"Ha cerrado por debajo de {num(suelo)}: sale del lateral hacia abajo.")
    else:
        frases.append(f"Se mueve en un lateral entre {num(suelo)} y {num(techo)}.")
    ficha = [("Lado (la regla)", f"{lado}: {num(s.iloc[t])} frente a {num(e.iloc[t])}"),
             ("Distancia", pct(dd, 2)),
             ("Pendiente de la EMA", f"{'baja' if pend.iloc[t] < 0 else 'sube'} ({sp} semanas)"),
             ("Rango de las 8 semanas anteriores", f"{num(suelo)}–{num(techo)}")]
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["Cierre", *[num(s.iloc[t - a]) for _, a in RECORRIDO]],
                  ["Distancia", *[pct(d.iloc[t - a], 1) for _, a in RECORRIDO]]])
    return dict(titulo="S&P 500 (SPY)", ficha=ficha, veredicto=f"{lado.capitalize()} de su EMA, {z}",
                recorrido=recorrido, estado={"Zona del SPY": z}, estado_ant={"Zona del SPY": zona_spy(d.iloc[t - 1])},
                resumen=" ".join(frases), datos=dict(cierre=s.iloc[t], ema=e.iloc[t], dist=dd))


def zona_gld(d):
    return "zona tranquila" if d > 5.2 else "zona de vigilancia" if d >= 0 else "ha cruzado"


def contraccion(dspy, dgld):
    return {(False, False): "ninguno", (True, False): "solo el SPY", (False, True): "solo el oro",
            (True, True): "los dos"}[(dspy < 0, dgld < 0)]


def texto_spygld(D):
    q = D.s["spy_gld"]
    t = D.t("spy_gld")
    e, d = ema(q), distancia(q)
    dd = d.iloc[t]
    dspy, dgld = distancia(D.s["spy"]), distancia(D.s["gld"])
    tsp, tg = D.t("spy"), D.t("gld")
    arriba = dd >= 0
    frases = [f"Se encuentra por encima de su EMA ({num(q.iloc[t], 3)} frente a {num(e.iloc[t], 3)}): el mercado prefiere el riesgo de forma sostenida."
              if arriba else
              f"Se encuentra por debajo de su EMA ({num(q.iloc[t], 3)} frente a {num(e.iloc[t], 3)}): el mercado pasa a preferir el refugio."]
    z = zona_gld(dd)
    frases.append({"zona tranquila": f"A una distancia de {pct(dd, 1)}: zona tranquila. Hace falta una semana excepcional para cruzar.",
                   "zona de vigilancia": f"A una distancia de {pct(dd, 1)}: zona de vigilancia. Una semana mala normal basta para cruzar.",
                   "ha cruzado": f"A una distancia de {pct(dd, 1)}: ha cruzado."}[z])
    sem = racha_igual(d >= 0, t)
    lado = "por encima" if arriba else "por debajo"
    if sem <= 2:
        frases.append(f"Lleva {sem} semanas {lado}. De sus 100 tramos desde 2006, 46 duraron dos semanas o menos: un cruce aislado es casi siempre ruido.")
    else:
        frases.append(f"Lleva {sem} semanas seguidas {lado}, desde la semana del {fecha(viernes(lunes_inicio_racha(q, t, sem)))}.")
    if dd < 5.2:
        frases.append(f"Lleva {racha(d < 5.2, t)} semanas por debajo del 5,2%.")
    frases.append("Distancias de las últimas semanas: " + " → ".join(pct(d.iloc[t - k], 1) for k in (3, 2, 1, 0)) + ".")
    pend = e.diff()
    frases.append(f"La pendiente {'baja' if pend.iloc[t] < 0 else 'sube'} desde hace {racha_igual(pend < 0, t)} semanas.")
    c = contraccion(dspy.iloc[tsp], dgld.iloc[tg])
    if c in ("solo el SPY", "solo el oro"):
        quien, serie, tt = ("SPY", dspy, tsp) if c == "solo el SPY" else ("oro", dgld, tg)
        frases.append(f"El {quien} está por debajo de su EMA desde hace {racha(serie < 0, tt)} semanas: se cumple la mitad de la contracción de liquidez.")
    elif c == "los dos":
        frases.append("El SPY y el oro están los dos por debajo de su EMA: contracción de liquidez, lo más grave que dice esta fila. "
                      "Desde 2006 solo ha pasado en el 6% de las semanas.")
    ficha = [("Lado", f"{lado}: {num(q.iloc[t], 3)} frente a {num(e.iloc[t], 3)}"),
             ("Distancia", pct(dd, 2)),
             ("Semanas seguidas al mismo lado", f"{sem} {lado}"),
             ("Oro (GLD) frente a su EMA", pct(dgld.iloc[tg], 1)),
             ("Contracción de liquidez", c)]
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["Cociente", *[num(q.iloc[t - a], 3) for _, a in RECORRIDO]],
                  ["Distancia", *[pct(d.iloc[t - a], 1) for _, a in RECORRIDO]],
                  ["Oro frente a su EMA", *[pct(dgld.iloc[tg - a], 1) for _, a in RECORRIDO]]])
    return dict(titulo="S&P 500 ÷ Oro (SPY/GLD)", ficha=ficha, veredicto=f"{lado.capitalize()} de su EMA, {z}; contracción: {c}",
                recorrido=recorrido,
                estado={"Zona del SPY/GLD": z, "Contracción de liquidez": c},
                estado_ant={"Zona del SPY/GLD": zona_gld(d.iloc[t - 1]),
                            "Contracción de liquidez": contraccion(dspy.iloc[tsp - 1], dgld.iloc[tg - 1])},
                resumen=" ".join(frases))


def zona_vix(v):
    return "calma" if v < 16 else "antesala" if v < 20 else "inestabilidad" if v < 30 else "pánico"


def texto_vix(D, spy):
    v = D.s["vix"]
    t = D.t("vix")
    x = v.iloc[t]
    z = zona_vix(x)
    frases = [{"calma": f"Cierra en {num(x)}: calma.",
               "antesala": f"Cierra en {num(x)}: antesala, empiezan los nervios.",
               "inestabilidad": f"Cierra en {num(x)}: inestabilidad, movimientos fuertes en los dos sentidos.",
               "pánico": f"Cierra en {num(x)}: pánico (solo el 8% de las semanas)."}[z]]
    banda = x / math.sqrt(52)
    c = spy["cierre"]
    frases.append(f"Lo normal es que la semana que viene el SPY se mueva menos de un ±{num(banda, 1)}%, entre "
                  f"{num(c * (1 - banda / 100), 0)} y {num(c * (1 + banda / 100), 0)}. Se cumple unas 8 de cada 10 semanas.")
    frases.append("En esta zona, el SPY se mueve más de un 3% en una semana " +
                  {"calma": "1 de cada 33", "antesala": "1 de cada 10", "inestabilidad": "1 de cada 4",
                   "pánico": "1 de cada 2"}[z] + " semanas.")
    s20 = racha(v > 20, t)
    if s20 == 0:
        frases.append(f"Lleva {racha(v <= 20, t)} semanas seguidas por debajo de 20.")
    elif s20 <= 2:
        frases.append(f"Lleva {s20} semanas por encima de 20. De los 71 tramos desde 2002, 46 duraron dos semanas o menos: casi siempre es ruido.")
    else:
        frases.append(f"Lleva {s20} semanas seguidas por encima de 20. Desde la 3.ª semana, el SPY cayó más de un 10% en los 6 meses "
                      f"siguientes el 24% de las veces, frente al 7% de una semana cualquiera.")
    cambio = v.pct_change() * 100
    hist = cambio[(cambio.index >= "2002-01-01")].iloc[:-1].abs().dropna()
    cx = cambio.iloc[t]
    pctil = (hist < abs(cx)).mean() * 100
    frases.append(f"Esta semana ha {'subido' if cx >= 0 else 'bajado'} un {num(abs(cx), 1)}% "
                  f"({num(abs(v.iloc[t] - v.iloc[t - 1]))} puntos), un movimiento mayor que el {num(pctil, 0)}% de las semanas desde 2002.")
    ficha = [("Nivel (la regla)", f"{num(x)}: {z}"),
             ("Semanas seguidas por encima de 20", f"{s20}" + ("" if s20 else f" ({racha(v <= 20, t)} por debajo)")),
             ("Cambio semanal", f"{pct(cx, 1)} ({num(v.iloc[t] - v.iloc[t - 1], 2, True)} puntos), percentil {num(pctil, 0)}"),
             ("Banda del SPY la semana que viene", f"±{num(banda, 1)}% ({num(c * (1 - banda / 100), 0)}–{num(c * (1 + banda / 100), 0)})")]
    recorrido = (["", *[n for n, _ in RECORRIDO]], [["VIX", *[num(v.iloc[t - a]) for _, a in RECORRIDO]]])
    return dict(titulo="VIX", ficha=ficha, veredicto=z.capitalize() + (f", {s20} semanas por encima de 20" if s20 else ""),
                recorrido=recorrido, estado={"Zona del VIX": z}, estado_ant={"Zona del VIX": zona_vix(v.iloc[t - 1])},
                resumen=" ".join(frases))


def casilla_kospi(spy_arriba, dk, sk):
    if not spy_arriba:
        return "no hay divergencia (SPY abajo)"
    if dk >= 0:
        return "sin divergencia"
    largo, hondo = sk >= 3, dk < -5
    if largo and hondo:
        return "aviso serio con las dos cosas"
    if largo or hondo:
        return "aviso serio"
    return "aviso flojo"


def texto_kospi(D):
    k = D.s["kospi"]
    t, ts = D.t("kospi"), D.t("spy")
    dk = distancia(k)
    dspy = distancia(D.s["spy"])
    sk = racha(dk < 0, t)
    c = casilla_kospi(dspy.iloc[ts] >= 0, dk.iloc[t], sk)
    c_ant = casilla_kospi(dspy.iloc[ts - 1] >= 0, dk.iloc[t - 1], racha(dk < 0, t - 1))
    d = dk.iloc[t]
    frases = [{"sin divergencia": "Sin divergencia: el SPY y el KOSPI están los dos por encima de su media. El KOSPI no dice nada esta semana. "
                                  "En la historia, el SPY cae más de un 10% en los 6 meses siguientes el 11% de las veces.",
               "aviso flojo": f"Aviso flojo: el KOSPI lleva {sk} semanas por debajo de su media, a {pct(d, 1)}. Muchas veces es ruido. "
                              f"En la historia, el SPY cae más de un 10% en los 6 meses siguientes el 23% de las veces.",
               "aviso serio": f"Aviso serio: el KOSPI lleva {sk} semanas por debajo de su media, a {pct(d, 1)}. Más prudencia con las compras, "
                              f"sobre todo en tecnología. En la historia, 36%.",
               "aviso serio con las dos cosas": f"Aviso serio con las dos cosas: {sk} semanas y {pct(d, 1)}. En la historia, 52%.",
               "no hay divergencia (SPY abajo)": "No hay divergencia: el SPY también está por debajo de su media; la caída ya está en el SPY."}[c]]
    sop = CONFIG["kospi_soporte"]
    bajo, alto = sop["bajo"], sop["alto"]
    zona = f"{num(bajo, 0, miles=True)}-{num(alto, 0, miles=True)}"
    cierre = k.iloc[t]
    if cierre < bajo:
        frases.append(f"Ha cerrado por debajo del soporte {zona}: se borra toda la subida.")
        s_estado = "por debajo"
    elif cierre <= alto:
        frases.append(f"Ha cerrado dentro del soporte {zona}.")
        s_estado = "dentro"
    else:
        frases.append(f"Está a {pct((cierre / alto - 1) * 100, 1)} del soporte {zona}, origen del último tramo al alza.")
        s_estado = "por encima"
    ficha = [("Divergencia (la regla)", c),
             ("Distancia", pct(d, 2)),
             ("Semanas seguidas por debajo", str(sk)),
             ("Soporte (valor fijo)", f"{zona}: cierre {num(cierre, 0, miles=True)}, {s_estado}")]
    hist = {"sin divergencia": " (11% histórico)", "aviso flojo": " (23% histórico)", "aviso serio": " (36% histórico)",
            "aviso serio con las dos cosas": " (52% histórico)"}.get(c, "")
    recorrido = (["", *[n for n, _ in RECORRIDO]],
                 [["Cierre", *[num(k.iloc[t - a], 0, miles=True) for _, a in RECORRIDO]],
                  ["Distancia", *[pct(dk.iloc[t - a], 1) for _, a in RECORRIDO]]])
    return dict(titulo="KOSPI", ficha=ficha, veredicto=c.capitalize() + hist, recorrido=recorrido,
                estado={"KOSPI": c, "Soporte del KOSPI": s_estado},
                estado_ant={"KOSPI": c_ant,
                            "Soporte del KOSPI": "por debajo" if k.iloc[t - 1] < bajo else "dentro" if k.iloc[t - 1] <= alto else "por encima"},
                resumen=" ".join(frases))


# ---------------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------------

def cambios(f):
    lin = [f"{k}: antes {f['estado_ant'][k]}, ahora {v}." for k, v in f["estado"].items() if f["estado_ant"][k] != v]
    return " ".join(lin) if lin else "Sin cambios de tramo frente al sábado anterior."


def escribir_docx(filas, sabado, lunes, ruta, aviso_semana):
    from docx import Document
    from docx.shared import Pt, RGBColor

    doc = Document()
    estilo = doc.styles["Normal"]
    estilo.font.name = "Calibri"
    estilo.font.size = Pt(10)

    def titulo(texto, nivel):
        h = doc.add_heading(texto, level=nivel)
        for r in h.runs:
            r.font.name = "Calibri"
            r.font.color.rgb = RGBColor(0x1F, 0x37, 0x63) if nivel <= 1 else RGBColor(0x2F, 0x54, 0x96)

    def tabla(cab, filas_t):
        tb = doc.add_table(rows=1, cols=len(cab))
        tb.style = "Table Grid"
        for i, c in enumerate(cab):
            tb.rows[0].cells[i].text = c
            for r in tb.rows[0].cells[i].paragraphs[0].runs:
                r.bold = True
        for f in filas_t:
            celdas = tb.add_row().cells
            for i, c in enumerate(f):
                celdas[i].text = str(c)

    def parrafo(etiqueta, texto):
        p = doc.add_paragraph()
        p.add_run(etiqueta).bold = True
        p.add_run(texto)

    titulo(f"Análisis de situación semanal — {sabado.strftime('%d/%m/%Y')}", 0)
    doc.add_paragraph(f"Cierre de la semana del {fecha(lunes)} al {fecha(viernes(lunes))}. "
                      f"Datos: Yahoo Finance y DBnomics; EMA 50 semanal. Comprobar dos números en TradingView "
                      f"(cierre y EMA del SPY, distancia del HYG).")
    if aviso_semana:
        doc.add_paragraph(aviso_semana).runs[0].bold = True

    lados = [("Lado de la Fed", ["Fed", "MOVE", "HYG"]), ("Entre los dos lados", ["Russell 2000"]),
             ("Lado de la bolsa", ["S&P 500 (SPY)", "S&P 500 ÷ Oro (SPY/GLD)", "VIX", "KOSPI"])]
    porti = {f["titulo"]: f for f in filas}
    for lado, nombres in lados:
        titulo(lado, 1)
        for n in nombres:
            f = porti[n]
            titulo(n, 2)
            tabla(["Qué mides", "Esta semana"], f["ficha"])
            parrafo("Veredicto: ", f["veredicto"])
            cab, filas_r = f["recorrido"]
            tabla(cab, filas_r)
            parrafo("Qué ha cambiado: ", cambios(f) + (" " + f["extra"] if f.get("extra") else ""))
            parrafo("Resumen: ", f["resumen"])
    titulo("Conclusiones (las escribe David)", 1)
    for n in ["Conclusión del lado de la Fed (FED + MOVE + HYG)", "El Russell, entre los dos lados",
              "Conclusión del lado de la bolsa (SPY + VIX + SPY/GLD + KOSPI)", "Conclusión final"]:
        titulo(n, 2)
        doc.add_paragraph("")
    doc.save(ruta)


def sabado_por_defecto(hoy):
    # Sábado de esta semana si hoy es sábado o domingo; si no, el último sábado.
    return hoy - dt.timedelta(days=(hoy.weekday() - 5) % 7)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sabado", nargs="?", help="Sábado del informe (AAAA-MM-DD)")
    ap.add_argument("--crear-carpeta", action="store_true")
    ap.add_argument("--sin-docx", action="store_true", help="Solo imprime, no escribe el Word")
    a = ap.parse_args()
    hoy = dt.datetime.now(MADRID).date()
    sabado = dt.date.fromisoformat(a.sabado) if a.sabado else sabado_por_defecto(hoy)
    if sabado.weekday() != 5:
        sys.exit(f"{sabado} no es sábado.")
    lunes = sabado - dt.timedelta(days=5)
    aviso = "" if hoy >= sabado else (f"AVISO: la semana todavía no ha cerrado (hoy es {fecha(hoy)}); "
                                      f"los datos de esta semana son provisionales.")

    D = Datos(lunes)
    fed = texto_fed(D)
    move = texto_move(D)
    hyg = texto_hyg(D)
    spy = texto_spy(D)
    filas = [fed, move, hyg, texto_russell(D, fed["datos"], move["datos"], hyg["datos"]), spy,
             texto_spygld(D), texto_vix(D, spy["datos"]), texto_kospi(D)]

    if aviso:
        print(aviso)
    for f in filas:
        print(f"\n== {f['titulo']}: {f['veredicto']}")
        print("   " + cambios(f) + (" " + f["extra"] if f.get("extra") else ""))
        print("   " + f["resumen"])
    print(f"\nComprobar en TradingView: SPY cierre {num(spy['datos']['cierre'])} y EMA {num(spy['datos']['ema'])}; "
          f"HYG a {pct(hyg['datos']['dist'], 2)} de su EMA.")
    if a.sin_docx:
        return

    base = Path(CONFIG["carpeta_base"]).expanduser()
    carpeta = base / f"informe semanal {sabado.strftime('%d-%m-%Y')}"
    if not carpeta.exists():
        if a.crear_carpeta and base.exists():
            carpeta.mkdir()
        else:
            sys.exit(f"\nNo existe la carpeta {carpeta}. Créala (o vuelve a lanzar con --crear-carpeta).")
    ruta = carpeta / f"Análisis situación semanal {sabado.strftime('%d-%m-%Y')}.docx"
    escribir_docx(filas, sabado, lunes, ruta, aviso)
    print(f"\nInforme guardado en: {ruta}")


if __name__ == "__main__":
    main()
