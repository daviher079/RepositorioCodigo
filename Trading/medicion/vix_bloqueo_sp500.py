"""Añadido 7 (05/11/2026): ¿debería el VIX (3 semanas por encima de 20) bloquear la entrada del S&P 500?

Mide, en las semanas en que el SPY está en un retroceso desde su máximo de 52 semanas, cuántas
bloquearía el VIX y qué rentabilidad tuvo el SPY 26 y 52 semanas después (medianas), bloqueadas
frente a libres. Resultado del 05/11 (cierre del 30/10/2026, desde 2005-12-30):

    −3% a −5%:   110 sem, bloquearía 15%, 52 sem: bloqueadas +13,1%, libres +15,3%
    −5% a −10%:  139 sem, bloquearía 41%, 52 sem: bloqueadas +13,0%, libres +12,6%
    −10% a −20%: 124 sem, bloquearía 76%, 52 sem: bloqueadas +13,0%, libres +18,3%

Decisión: el VIX no bloquea al S&P 500; queda en el gatillo ("VIX girando a la baja").
Límites: un solo periodo, semanas solapadas, sin el stop del 5% de SPYL.

Uso: venv/bin/python vix_bloqueo_sp500.py [AAAA-MM-DD del viernes]
"""
import sys
import datetime as dt
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/estado-cartera/scripts"))
import estado as E  # noqa: E402  (reutiliza la descarga semanal de /estado-cartera)

viernes = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 10, 30)
spy, vix = E.semanal("SPY", viernes), E.semanal("^VIX", viernes)
df = pd.DataFrame({"s": spy.Close, "v": vix.Close}).dropna()
df["dd"] = (df.s / df.s.rolling(52).max() - 1) * 100
df["vix3"] = (df.v > 20).rolling(3).sum() == 3
df["ret26"] = (df.s.shift(-26) / df.s - 1) * 100
df["ret52"] = (df.s.shift(-52) / df.s - 1) * 100

for a_, b_ in [(-3, -5), (-5, -10), (-10, -20)]:
    z = df[(df.dd <= a_) & (df.dd > b_)].dropna(subset=["ret52"])
    a, b = z[z.vix3], z[~z.vix3]
    print(f"retroceso {a_}% a {b_}%: {len(z)} sem | VIX bloquearía {len(a)} ({len(a) / len(z) * 100:.0f}%)"
          f" | 26 sem: bloqueadas {a.ret26.median():+.1f}% (suben {(a.ret26 > 0).mean() * 100:.0f}%),"
          f" libres {b.ret26.median():+.1f}% (suben {(b.ret26 > 0).mean() * 100:.0f}%)"
          f" | 52 sem: bloqueadas {a.ret52.median():+.1f}%, libres {b.ret52.median():+.1f}%")
print("muestra desde", df.dropna().index[0].date())
