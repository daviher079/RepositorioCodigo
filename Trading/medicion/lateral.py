import pandas as pd,numpy as np,time
from datos import semanal
T={'SPY':'S&P','GLD':'oro','XLV':'salud','CIBR':'ciber','XLE':'energía','EXXY.DE':'mat.primas','AWK':'AWK','CPR.MI':'Campari','COPX':'cobre','SMH':'semis','IWM':'Russell','EWL':'Suiza','IUS2.DE':'bancos EEUU','EXV1.DE':'bancos EU','XLRE':'REITs','XLP':'consumo','WMIN.DE':'minería','WCLD':'cloud','QQQ':'Nasdaq'}
rows=[]
for t,n in T.items():
    try: w=semanal(t,1420070400)
    except Exception as ex: print('fallo',t,ex); continue
    w=w[w.index<='2026-10-30']; c=w.Close; e=c.ewm(span=50,adjust=False).mean()
    r={'nombre':n,'ticker':t}
    for N in (13,26,39): r[f'banda{N}']=round((c[-N:].max()/c[-N:].min()-1)*100,1)
    r['pend13']=round((e.iloc[-1]/e.iloc[-14]-1)*100,1)
    r['vs_EMA']=round((c.iloc[-1]/e.iloc[-1]-1)*100,1)
    # ruido: mediana histórica de la banda de 26 semanas, para comparar
    b26=(c.rolling(26).max()/c.rolling(26).min()-1)*100
    r['banda26_mediana_hist']=round(b26.median(),1)
    rows.append(r); time.sleep(0.5)
df=pd.DataFrame(rows).sort_values('pend13'); print(df.to_string(index=False))
df.to_csv('lateral_hoy.csv',index=False)
