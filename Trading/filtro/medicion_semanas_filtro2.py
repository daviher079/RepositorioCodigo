"""Medición del 03/11/2026: ¿cuántas semanas seguidas debe pasar un candidato
los filtros 1 y 2 antes de que el filtro avise?

Universo: los tickers de gráfico de la especulativa en Fichas ETF (15).
El filtro 3 (correlación con la cartera) no entra: depende de qué haya en
cartera en cada momento, y eso no tiene historia.

Para cada racha de semanas seguidas pasando 1 y 2, y cada N:
  - aviso = semana N de la racha (las rachas más cortas que N no avisan).
  - FALSA ALARMA = 8 semanas después del aviso ya no pasa los filtros.
  - RETROCESO PERDIDO = el primer retroceso de la racha (cierre >= 5% bajo el
    máximo de la racha, la misma definición de "entrada en retroceso" de las
    tablas de ruido) llegó ANTES del aviso: esperar te lo hizo perder.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from filtro_candidatos import diario, ema  # noqa: E402

UNIVERSO = ["COPX", "SMH", "CIBR", "XLE", "IWM", "BNKS.L", "EXV1.DE", "EXXY.DE", "XLRE",
            "XLP", "WMIN.DE", "WCLD", "EWL", "XLV", "QQQ"]

spy = diario("SPY", desde="2000-01-01").resample("W-FRI").last().dropna().iloc[:-1]
rows = []
for t in UNIVERSO:
    s = diario(t, desde="2000-01-01").resample("W-FRI").last().dropna().iloc[:-1]
    df = pd.concat({"c": s, "spy": spy}, axis=1).dropna()
    if len(df) < 120:
        continue
    df["ratio"] = df.c / df.spy
    df["pasa"] = (df.c > ema(df.c)) & (df.ratio > ema(df.ratio))
    df = df.iloc[50:]  # arranque de la EMA
    pasa = df.pasa.values
    c = df.c.values
    i = 0
    while i < len(df):
        if not pasa[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(df) and pasa[j + 1]:
            j += 1
        # racha i..j; primer retroceso dentro de la racha
        maxc, retro = c[i], None
        for k in range(i, j + 1):
            maxc = max(maxc, c[k])
            if c[k] <= maxc * 0.95:
                retro = k - i  # semana de la racha (0 = primera)
                break
        rows.append({"ticker": t, "inicio": df.index[i], "largo": j - i + 1,
                     "retro": retro, "fin_idx": j, "i": i, "n_total": len(df),
                     "pasa": pasa})
        i = j + 1

print(f"Rachas medidas: {len(rows)} en {len({r['ticker'] for r in rows})} tickers\n")
print("| N semanas | Avisos | Falsas alarmas (no pasa 8 sem. después) | Primer retroceso perdido "
      "| Avisos buenos con retroceso por delante |")
print("|---|---|---|---|---|")
for n in range(1, 9):
    av = fa = perd = buenos = 0
    for r in rows:
        if r["largo"] < n:
            continue
        aviso = r["i"] + n - 1
        if aviso + 8 >= r["n_total"]:
            continue
        av += 1
        falsa = not r["pasa"][aviso + 8]
        fa += falsa
        perdido = r["retro"] is not None and r["retro"] < n - 1
        perd += perdido
        buenos += (not falsa) and (r["retro"] is not None) and not perdido
    print(f"| {n} | {av} | {fa} ({fa / av * 100:.0f}%) | {perd} ({perd / av * 100:.0f}%) "
          f"| {buenos} ({buenos / av * 100:.0f}%) |")
