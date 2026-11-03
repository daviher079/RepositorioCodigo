"""Filtro de candidatos para la especulativa (definido con David el 03/11/2026).

Uso:
    python filtro_candidatos.py XLP WCLD AWK:empresa
    python filtro_candidatos.py XLP --cartera SPY GLD XLE EXXY.DE XLV CIBR

Cada candidato es el ticker del GRÁFICO (donde se decide), no el de la réplica.
Añadir ":empresa" a las acciones sueltas para que se les aplique el filtro 4.

Filtros (semanal, último cierre de semana COMPLETA):
  1. Tendencia: cierre por encima de su EMA 50 semanal.
  2. Fuerza frente al SPY: cociente candidato/SPY por encima de SU EMA 50.
  AVISO: solo si lleva 5 semanas SEGUIDAS pasando 1 y 2 (y pasa el 3).
     Medido el 03/11/2026 en 620 rachas de 15 ETF (medicion_semanas_filtro2.py):
     con 1 semana el 47% son falsas alarmas; con 5, el 32% (el mínimo), a
     cambio de perder el primer retroceso en el 4% de los casos. Decisión de David.
  3. No repetir lo que ya hay: correlación semanal de 2 años contra cada
     posición de la cartera. Aviso si alguna pasa de 0,8 (corte en el que
     quedaron fuera semiconductores, 0,79, y Russell, 0,81, el 02/11/2026).
  4. Solo empresas: últimos resultados (fecha, BPA frente al consenso,
     sorpresa) y reacción del precio. Fuente: Nasdaq, solo EE. UU.; fuera
     de EE. UU. se revisa a mano.

El script INFORMA: no decide si un candidato entra. Eso es criterio de David.
"""

import argparse
import datetime as dt
import json
import subprocess
import sys
import time

import numpy as np
import pandas as pd

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"
CARTERA_DEFECTO = ["SPY", "GLD", "XLE", "EXXY.DE", "XLV", "CIBR"]
CORTE_CORRELACION = 0.8
SEMANAS_CORRELACION = 104
SEMANAS_AVISO = 5


def _get(url, ua="Mozilla/5.0"):
    # curl y no urllib: el Python del venv no tiene los certificados del sistema
    # (CERTIFICATE_VERIFY_FAILED, 03/11/2026).
    # Yahoo con "Mozilla/5.0" a secas (con el UA largo de navegador devuelve
    # "Too Many Requests"); Nasdaq necesita el UA largo.
    out = subprocess.run(["curl", "-s", "-m", "30", "-A", ua, "-H", "Accept: application/json", url],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def diario(ticker, desde="2018-01-01"):
    """Cierres diarios de Yahoo (quote.close, no adjclose: coincide con TradingView)."""
    p1 = int(pd.Timestamp(desde).timestamp())
    p2 = int(time.time()) + 86400
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?interval=1d&period1={p1}&period2={p2}")
    res = _get(url)["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    idx = pd.to_datetime(res["timestamp"], unit="s").normalize()
    return pd.Series(q["close"], index=idx, name=ticker).dropna()


def semanal(serie):
    """Vela semanal con cierre en viernes; se quita la semana en curso si no ha terminado."""
    w = serie.resample("W-FRI").last().dropna()
    if w.index[-1].date() > dt.date.today() or (
            w.index[-1].date() == dt.date.today() and dt.datetime.now().hour < 23):
        w = w.iloc[:-1]
    return w


def ema(s):
    return s.ewm(span=50, adjust=False).mean()


DIAS_DATO_VIEJO = 135  # un trimestre (~90 días) + ~45 días que tardan en publicar


def fundamentales(ticker):
    """Ingresos y BPA contable REALES por trimestre (Yahoo). No trae lo esperado:
    no hay fuente gratuita de ingresos esperados (comprobado el 03/11/2026)."""
    p2 = int(time.time()) + 86400
    url = ("https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/"
           f"{ticker}?type=quarterlyTotalRevenue,quarterlyDilutedEPS&period1=1577836800&period2={p2}")
    out = {}
    for r in _get(url)["timeseries"]["result"]:
        k = r["meta"]["type"][0]
        out[k] = {pd.Timestamp(x["asOfDate"]): x["reportedValue"]["raw"] for x in (r.get(k) or []) if x}
    return out.get("quarterlyTotalRevenue", {}), out.get("quarterlyDilutedEPS", {})


def imprimir_ingresos(ticker):
    try:
        ingresos, bpa = fundamentales(ticker)
    except Exception as e:  # noqa: BLE001
        print(f"- Ingresos: sin datos de Yahoo ({e.__class__.__name__}): revisar a mano")
        return
    if not ingresos:
        print("- Ingresos: Yahoo no tiene datos: revisar a mano")
        return
    ultimo = max(ingresos)
    edad = (pd.Timestamp.today() - ultimo).days
    print("\n**Ingresos reales frente al mismo trimestre del año anterior** "
          "(crecimiento del negocio, NO sorpresa frente a lo esperado):\n")
    print("| Trimestre cerrado | Ingresos | Un año antes | Crecimiento | BPA contable |")
    print("|---|---|---|---|---|")
    for f in sorted(ingresos)[-4:]:
        previo = [g for g in ingresos if abs((f - pd.DateOffset(years=1) - g).days) <= 15]
        if previo:
            v0 = ingresos[previo[0]]
            crec = f"{(ingresos[f] / v0 - 1) * 100:+.1f}%"
            antes = f"{v0 / 1e6:,.0f} M"
        else:
            crec, antes = "sin trimestre comparable", "—"
        b = bpa.get(f)
        print(f"| {f:%m/%Y} | {ingresos[f] / 1e6:,.0f} M | {antes} | {crec} | {'—' if b is None else round(b, 3)} |")
    if edad > DIAS_DATO_VIEJO:
        print(f"\n- ⚠️ El último trimestre con datos cerró hace {edad // 30} meses ({ultimo:%d/%m/%Y}): "
              "faltan trimestres. **Revisar a mano.**")


def resultados(ticker, diario_precio):
    """Últimos resultados de una empresa de EE. UU. desde Nasdaq."""
    if "." in ticker:
        return None, "fuera de EE. UU.: revisar a mano"
    try:
        data = _get(f"https://api.nasdaq.com/api/company/{ticker}/earnings-surprise", ua=UA)
        filas = data["data"]["earningsSurpriseTable"]["rows"]
    except Exception as e:  # noqa: BLE001
        return None, f"sin datos de Nasdaq ({e.__class__.__name__}): revisar a mano"
    out = []
    for f in filas:
        fecha = pd.Timestamp(dt.datetime.strptime(f["dateReported"], "%m/%d/%Y"))
        antes = diario_precio[diario_precio.index < fecha]
        despues = diario_precio[diario_precio.index > fecha]
        reaccion = None
        if len(antes) and len(despues):
            # cierre del día anterior -> cierre del día siguiente: cubre que publique
            # antes de la apertura o después del cierre
            reaccion = (despues.iloc[0] / antes.iloc[-1] - 1) * 100
        sorpresa = float(f["percentageSurprise"])
        out.append({
            "trimestre": f["fiscalQtrEnd"],
            "fecha": fecha.date(),
            "bpa": f["eps"],
            "consenso": f["consensusForecast"],
            "sorpresa_%": sorpresa,
            "veredicto": "batió" if sorpresa > 0 else ("cumplió" if sorpresa == 0 else "falló"),
            "reaccion_%": None if reaccion is None else round(reaccion, 1),
        })
    return out, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("candidatos", nargs="+", help="TICKER o TICKER:empresa")
    ap.add_argument("--cartera", nargs="+", default=CARTERA_DEFECTO,
                    help="tickers de gráfico de lo que ya está en cartera (filtro 3)")
    args = ap.parse_args()

    cands = []
    for c in args.candidatos:
        t, _, tipo = c.partition(":")
        cands.append((t, tipo == "empresa"))

    tickers = sorted({"SPY", *args.cartera, *[t for t, _ in cands]})
    D = {}
    for t in tickers:
        try:
            D[t] = diario(t)
        except Exception as e:  # noqa: BLE001
            print(f"!! {t}: no se pudo descargar ({e})", file=sys.stderr)
    W = pd.DataFrame({t: semanal(s) for t, s in D.items()}).ffill()
    cierre = W.index[-1].date()
    rets = W.pct_change().tail(SEMANAS_CORRELACION)

    print(f"# Filtro de candidatos — cierre semanal del {cierre:%d/%m/%Y}\n")
    print("| Candidato | 1. Tendencia (vs EMA 50) | 2. Fuerza (vs SPY) | Semanas seguidas pasando 1-2 "
          "| 3. Más parecido a | Aviso |")
    print("|---|---|---|---|---|---|")
    empresas = []
    for t, es_empresa in cands:
        if t not in W:
            print(f"| {t} | sin datos | | | | |")
            continue
        s = W[t].dropna()
        f1 = (s.iloc[-1] / ema(s).iloc[-1] - 1) * 100
        ratio = (W[t] / W["SPY"]).dropna()
        er = ema(ratio)
        f2 = (ratio.iloc[-1] / er.iloc[-1] - 1) * 100
        pasa12 = ((s > ema(s)) & (ratio > er)).dropna()
        racha = 0
        for v in pasa12.values[::-1]:
            if not v:
                break
            racha += 1
        cors = {c: rets[t].corr(rets[c]) for c in args.cartera if c != t and c in rets}
        top = max(cors, key=cors.get)
        ok3 = cors[top] <= CORTE_CORRELACION
        if racha >= SEMANAS_AVISO and ok3:
            aviso = "**SÍ**"
        elif racha and ok3:
            aviso = f"aún no ({racha} de {SEMANAS_AVISO})"
        else:
            aviso = "no"
        print(f"| {t}{' (empresa)' if es_empresa else ''} | {'✅' if f1 > 0 else '❌'} {f1:+.1f}% "
              f"| {'✅' if f2 > 0 else '❌'} {f2:+.1f}% | {racha} "
              f"| {'✅' if ok3 else '❌'} {top} {cors[top]:.2f} | {aviso} |")
        if es_empresa:
            empresas.append(t)

    for t in empresas:
        print(f"\n## 4. Resultados de {t}\n")
        filas, aviso = resultados(t, D[t])
        if aviso:
            print(f"- Sorpresa frente a lo esperado: {aviso}")
        else:
            print("**Beneficio frente a lo esperado** (BPA ajustado, el que comparan los analistas; "
                  "fuente Nasdaq):\n")
            print("| Trimestre | Publicado | BPA ajustado | Esperado | Sorpresa | | Reacción del precio |")
            print("|---|---|---|---|---|---|---|")
            for f in filas:
                r = "—" if f["reaccion_%"] is None else f"{f['reaccion_%']:+.1f}%"
                print(f"| {f['trimestre']} | {f['fecha']:%d/%m/%Y} | {f['bpa']} | {f['consenso']} "
                      f"| {f['sorpresa_%']:+.2f}% | {f['veredicto']} | {r} |")
        imprimir_ingresos(t)

    print(f"\n> Informa, no decide. Aviso con {SEMANAS_AVISO} semanas seguidas pasando 1 y 2 "
          "(aun así, 1 de cada 3 avisos falla: la compra la decide la zona). "
          "Corte de correlación: 0,8.")


if __name__ == "__main__":
    main()
